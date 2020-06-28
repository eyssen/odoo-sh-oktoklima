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


    kvtd = fields.Boolean(u'A számla környezetvédelmi termékdíjat tartalmaz', default=True)


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