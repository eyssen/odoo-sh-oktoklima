# -*- encoding: utf-8 -*-

import datetime
import random

from dateutil import relativedelta

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.misc import formatLang, format_date

import logging
_logger = logging.getLogger(__name__)





class AccountMove(models.Model):
    
    _inherit = "account.move"


    fulfillment_date = fields.Date(u'Teljesítés időpontja', readonly=True, states={'draft':[('readonly',False)]})
    currency_rate = fields.Float('Rate', readonly=True)
    intermediary_services = fields.Boolean(u'A számla közvetített szolgáltatást tartalmaz')
    kvtd = fields.Boolean(u'A számla környezetvédelmi termékdíjat tartalmaz', default=True)


    def action_post(self):
        
        if self.mapped('line_ids.payment_id') and any(post_at == 'bank_rec' for post_at in self.mapped('journal_id.post_at')):
            raise UserError(_("A payment journal entry generated in a journal configured to post entries only when payments are reconciled with a bank statement cannot be manually posted. Those will be posted automatically after performing the bank reconciliation."))
        
        if self.type in ['out_invoice','out_refund']:
            # Partner adatok ellenőrzése
            if not self.partner_id:
                raise UserError(_("Nincs megadva a partner!"))
            if not self.partner_id.country_id:
                raise UserError(_("Nincs megadva a partner országa!"))
            if not self.partner_id.city:
                raise UserError(_("Nincs megadva a partner városa!"))
            if not self.partner_id.zip:
                raise UserError(_("Nincs megadva a partner irányítószáma!"))
            if not self.partner_id.street:
                raise UserError(_("Nincs megadva a partner utca/házszáma!"))
            if self.partner_id.company_type == 'company':
                if self.fiscal_position_id.name == 'EU partner':
                    if not self.partner_id.vat:
                        raise UserError(_("Nincs megadva a partner közösségi adószáma!"))
                else:
                    if not self.partner_id.vat_hu:
                        raise UserError(_("Nincs megadva a partner adószáma!"))
            # Számla adatok ellenőrzése
            if not self.invoice_payment_term_id and not self.invoice_date_due:
                raise UserError(_("Nincs beállítva fizetési feltétel!"))
            if not self.invoice_date:
                raise UserError(_("Nincs megadva a számla kelte!"))
            if not self.fulfillment_date:
                raise UserError(_("Nincs megadva a teljesítés időpontja!"))
            if not self.invoice_partner_bank_id:
                raise UserError(_("Nincs megadva bankszámla!"))
            if not self.currency_rate:
                #TODO: a kerekítést a valuta alapján kéne csinálni
                if self.fiscal_position_id:
                    # Árfolyam: számla kelte alapján (meg van adva költségvetési pozíció)
                    currency_id = self.currency_id.with_context(date=self.invoice_date)
                    self.currency_rate = round(currency_id._convert(1, self.company_id.currency_id, self.company_id, self.invoice_date), 2)
                else:
                    if self.fulfillment_date > self.invoice_date:
                        # Árfolyam: számla kelte alapján (jövőbeni teljesítés)
                        currency_id = self.currency_id.with_context(date=self.invoice_date)
                        self.currency_rate = round(currency_id._convert(1, self.company_id.currency_id, self.company_id, self.invoice_date), 2)
                    else:
                        # Árfolyam: teljesítés időpontja alapján (normál számla)
                        currency_id = self.currency_id.with_context(date=self.fulfillment_date)
                        self.currency_rate = round(currency_id._convert(1, self.company_id.currency_id, self.company_id, self.fulfillment_date), 2)

        return self.post()


    def _reverse_moves(self, default_values_list=None, cancel=False):
        ''' Reverse a recordset of account.move.
        If cancel parameter is true, the reconcilable or liquidity lines
        of each original move will be reconciled with its reverse's.

        :param default_values_list: A list of default values to consider per move.
                                    ('type' & 'reversed_entry_id' are computed in the method).
        :return:                    An account.move recordset, reverse of the current self.
        '''
        if not default_values_list:
            default_values_list = [{} for move in self]

        if cancel:
            lines = self.mapped('line_ids')
            # Avoid maximum recursion depth.
            if lines:
                lines.remove_move_reconcile()

        reverse_type_map = {
            'entry': 'entry',
            'out_invoice': 'out_refund',
            'out_refund': 'entry',
            'in_invoice': 'in_refund',
            'in_refund': 'entry',
            'out_receipt': 'entry',
            'in_receipt': 'entry',
        }

        move_vals_list = []
        for move, default_values in zip(self, default_values_list):
            default_values.update({
                'type': reverse_type_map[move.type],
                'reversed_entry_id': move.id,
                'fulfillment_date': move.fulfillment_date,
                'currency_rate': move.currency_rate,
            })
            move_vals_list.append(move._reverse_move_vals(default_values, cancel=cancel))

        reverse_moves = self.env['account.move'].create(move_vals_list)
        for move, reverse_move in zip(self, reverse_moves.with_context(check_move_validity=False)):
            # Update amount_currency if the date has changed.
            if move.date != reverse_move.date:
                for line in reverse_move.line_ids:
                    if line.currency_id:
                        line._onchange_currency()
            reverse_move._recompute_dynamic_lines(recompute_all_taxes=False)
        reverse_moves._check_balanced()

        # Reconcile moves together to cancel the previous one.
        if cancel:
            reverse_moves.with_context(move_reverse_cancel=cancel).post()
            for move, reverse_move in zip(self, reverse_moves):
                accounts = move.mapped('line_ids.account_id') \
                    .filtered(lambda account: account.reconcile or account.internal_type == 'liquidity')
                for account in accounts:
                    (move.line_ids + reverse_move.line_ids)\
                        .filtered(lambda line: line.account_id == account and line.balance)\
                        .reconcile()

        return reverse_moves


    @api.depends('line_ids.price_subtotal', 'line_ids.tax_base_amount', 'line_ids.tax_line_id', 'partner_id', 'currency_id')
    def _compute_invoice_taxes_by_group(self):
        ''' Helper to get the taxes grouped according their account.tax.group.
        This method is only used when printing the invoice.
        '''
        for move in self:
            lang_env = move.with_context(lang=move.partner_id.lang).env
            tax_lines = move.line_ids.filtered(lambda line: line.tax_line_id)
            res = {}
            # There are as many tax line as there are repartition lines
            done_taxes = set()
            for line in tax_lines:
                res.setdefault(line.tax_line_id.tax_group_id, {'base': 0.0, 'amount': 0.0})
                res[line.tax_line_id.tax_group_id]['amount'] += line.price_subtotal
                tax_key_add_base = tuple(move._get_tax_key_for_group_add_base(line))
                if tax_key_add_base not in done_taxes:
                    # The base should be added ONCE
                    res[line.tax_line_id.tax_group_id]['base'] += line.tax_base_amount
                    done_taxes.add(tax_key_add_base)
                res[line.tax_line_id.tax_group_id]['percent'] = line.tax_line_id.amount
                res[line.tax_line_id.tax_group_id]['description'] = line.tax_line_id.description
            res = sorted(res.items(), key=lambda l: l[0].sequence)
            move.amount_by_group = [(
                group.name,
                amounts['amount'],
                amounts['base'],
                formatLang(lang_env, amounts['amount'], currency_obj=move.currency_id),
                formatLang(lang_env, amounts['base'], currency_obj=move.currency_id),
                len(res),
                group.id,
                formatLang(lang_env, amounts['amount']+amounts['base'], currency_obj=move.currency_id),
                amounts['description'],
            ) for group, amounts in res]

    
    def _recalculate_kvtd_lines(self):

        if self.kvtd:
            for invoice_line in self.invoice_line_ids:
                if invoice_line.product_id.kvtd_ids:
                    if not invoice_line.kvtd_ids:
                        _logger.info('CREATE')
                        for product_kvtd_line in invoice_line.product_id.kvtd_ids:
                            self.env['account.move.line.kvtd'].sudo().create({
                                'line_id': invoice_line.id,
                                'kvtd_id': product_kvtd_line.kvtd_id.id,
                                'weight': product_kvtd_line.weight * invoice_line.quantity,
                                'rate': product_kvtd_line.weight * invoice_line.quantity * product_kvtd_line.kvtd_id.rate
                            })
                    else:
                        _logger.info('UPDATE')
                        #TODO: ezt meg kell csinálni

        else:
            _logger.info('DELETE')
            l = self.env['account.move.line.kvtd'].search([('line_id.move_id', '=', self.id)])
            l.unlink()

    @api.model_create_multi
    def create(self, vals):
        line = super(AccountMove, self).create(vals)
        self._recalculate_kvtd_lines()
        return line


    def write(self, vals):
        result = super(AccountMove, self).write(vals)       
        self._recalculate_kvtd_lines()
        return result
 



class AccountMoveLine(models.Model):
    
    _inherit = 'account.move.line'
    
    
    kvtd_ids = fields.One2many('account.move.line.kvtd', 'line_id', u'Sorok', readonly=True)
    kvtd = fields.Boolean(u'A számla környezetvédelmi termékdíjat tartalmaz', readonly=True, related='move_id.kvtd')





class AccountMoveLineKvtd(models.Model):
    
    _name = 'account.move.line.kvtd'
    
    
    line_id = fields.Many2one('account.move.line', u'Számlasor', required=True)
    kvtd_id = fields.Many2one('kvtd', u'KVTD', required=True)
    weight = fields.Float(u'Súly (kg)', required=True)
    rate = fields.Float(u'Díjtétel (Ft)', required=True)
