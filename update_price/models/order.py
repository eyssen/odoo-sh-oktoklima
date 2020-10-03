# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)





class SaleOrder(models.Model):
    
    _inherit = 'sale.order'
    
    
    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', check_company=True,  # Unrequired company
        required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=1, 
        help="If you change the pricelist, only newly added lines will be affected.")
    show_update_pricelist = fields.Boolean(string='Has Pricelist Changed',
        help="Technical Field, True if the pricelist was changed;\n"
        " this will then display a recomputation button")


    @api.onchange('pricelist_id')
    def _onchange_pricelist_id(self):
        if self.order_line and self.pricelist_id and self._origin.pricelist_id and self._origin.pricelist_id != self.pricelist_id:
            self.show_update_pricelist = True
        else:
            self.show_update_pricelist = False
    
    def update_prices(self):
        self.ensure_one()
        lines_to_update = []
        for line in self.order_line.filtered(lambda line: not line.display_type):
            product = line.product_id.with_context(
                partner=self.partner_id,
                quantity=line.product_uom_qty,
                date=self.date_order,
                pricelist=self.pricelist_id.id,
                uom=line.product_uom.id
            )
            price_unit = self.env['account.tax']._fix_tax_included_price_company(
                line._get_display_price(product), line.product_id.taxes_id, line.tax_id, line.company_id)
            lines_to_update.append((1, line.id, {'price_unit': price_unit}))
        self.update({'order_line': lines_to_update})
        self.show_update_pricelist = False
        self.message_post(body=_("Product prices have been recomputed according to pricelist <b>%s<b> ") % self.pricelist_id.display_name)
