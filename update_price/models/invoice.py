# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)





class AccountMove(models.Model):
    
    _inherit = 'account.move'


    @api.model
    def _get_default_currency(self):
        ''' Get the default currency from either the journal, either the default journal's company. '''
        journal = self._get_default_journal()
        return journal.currency_id or journal.company_id.currency_id
    
    
    currency_id = fields.Many2one('res.currency', store=True, readonly=True, tracking=True, required=True,
        states={'draft': [('readonly', False)]},
        string='Currency',
        default=_get_default_currency)
    show_update_currency = fields.Boolean(string='Has Currency Changed',
        help="Technical Field, True if the currency was changed;\n"
        " this will then display a recomputation button")


    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        if self.invoice_line_ids and self.currency_id and self._origin.currency_id and self._origin.currency_id != self.currency_id:
            self.show_update_currency = True
        else:
            self.show_update_currency = False
    
    def update_prices(self):
        self.ensure_one()
        lines_to_update = []
        for line in self.invoice_line_ids:
            if line.exclude_from_invoice_tab == False:
                line._onchange_product_id()
#             product = line.product_id.with_context(
#                 partner=self.partner_id,
#                 quantity=line.quantity,
#                 date=self.invoice_date,
#                 currency=self.currency_id.id,
#                 uom=line.product_uom_id.id
#             )
#             price_unit = self.env['account.tax']._fix_tax_included_price_company(
#                 line._get_computed_price_unit())
#             lines_to_update.append((1, line.id, {'price_unit': price_unit}))
#         self.update({'invoice_line_ids': lines_to_update})
        self.show_update_currency = False
        self.message_post(body=_("Product prices have been recomputed according to currency <b>%s<b> ") % self.pricelist_id.display_name)
