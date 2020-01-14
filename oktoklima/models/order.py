# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)





class SaleOrder(models.Model):
    
    _inherit = 'sale.order'


    def wizard_merge_into_product(self):
        
        context = {}
        context['default_order_id'] = self.id
        
        return {
            'name'      : u'Új termék létrehozása termékekből',
            'type'      : 'ir.actions.act_window',
            'res_model' : 'sale.order.product.wizard',
            'view_id'   : self.env.ref('oktoklima.sale_order_product_wizard_view_form').id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target'    : 'new',
            'context'   : context,
        }





class SaleOrderProductWizard(models.TransientModel):
    
    _name = 'sale.order.product.wizard'
    
    
    name = fields.Char(u'Új termék neve', required=True)
    default_code = fields.Char(u'Új termék cikkszáma', required=True)
    order_id = fields.Many2one('sale.order', u'Árajánlat', required=True)
    list_price = fields.Float(u'Eladási ár', compute='_compute')
    standard_price = fields.Float(u'Beszerzési ár')
    description = fields.Text(u'Leírás', compute='_compute')
    
    
    @api.depends('order_id')
    def _compute(self):

        self.list_price = self.order_id.amount_untaxed * (1 / self.order_id.currency_rate)
        
        description = ""
        for line in self.order_id.order_line:
            description += str(line.product_uom_qty) + ' ' + line.product_uom.name + ' ' + line.name + '\n'
        self.description = description


    def action_create_product(self):
        
        ProductTemplate = self.env['product.template'].create({
            'name': self.name,
            'default_code': self.default_code,
            'list_price': self.list_price,
            'standard_price': self.standard_price,
            'description': self.description,
        })
        ProductProduct = self.env['product.product'].search([('product_tmpl_id', '=', ProductTemplate.id)], limit=1)
        
        for line in self.order_id.order_line:
            line.unlink()
        
        self.env['sale.order.line'].create({
            'order_id': self.order_id.id,
            'product_id': ProductProduct.id,
        })