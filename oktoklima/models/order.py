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



class SaleOrderLine(models.Model):
    
    _inherit = 'sale.order.line'
    
    
    supplierinfo_popover = fields.Text(u'Supplierinfo PopOver', compute='_supplierinfo_popover', readonly=True)
    
    
    @api.depends('product_id')
    def _supplierinfo_popover(self):
        for line in self:
            supplierinfo_popover = ''
            for s in line.product_id.seller_ids:
                supplierinfo_popover += str(s.price) + ' ' + str(s.currency_id.name) + ' (' + str(s.name.name) + ')\n'
            line.supplierinfo_popover = supplierinfo_popover





class SaleOrderProductWizard(models.TransientModel):
    
    _name = 'sale.order.product.wizard'
    
    
    name = fields.Char(u'Új termék neve', required=True)
    default_code = fields.Char(u'Új termék cikkszáma', required=True)
    order_id = fields.Many2one('sale.order', u'Árajánlat', required=True)
    list_price = fields.Float(u'Eladási ár', compute='_compute')
    standard_price = fields.Float(u'Beszerzési ár', compute='_compute')
    line_ids = fields.Many2many('sale.order.line', 'merge_product_rel', 'wizard_id', 'line_id', string='Sorok' , domain="[('order_id', '=', order_id),('product_id.product_tmpl_id.configured_product', '=', False)]")
    
    
    @api.model
    def default_get(self, fields):
        
        vals = super(SaleOrderProductWizard, self).default_get(fields)
        vals['line_ids'] = self.env['sale.order.line'].search([('order_id', '=', self._context.get('active_ids')[0]),('product_id.product_tmpl_id.configured_product', '=', False)]).ids
        return vals


    @api.depends('line_ids')
    @api.onchange('line_ids')
    def _compute(self):
        list_price = 0
        standard_price = 0
        for line in self.line_ids:
            list_price += line.product_id.list_price
            standard_price += line.product_id.standard_price
        self.list_price = list_price
        self.standard_price = standard_price


    def action_create_product(self):
        
        ProductTemplate = self.env['product.template'].create({
            'name': self.name,
            'default_code': self.default_code,
            'list_price': self.list_price,
            'standard_price': self.standard_price,
            'configured_product': True
        })
        ProductProduct = self.env['product.product'].search([('product_tmpl_id', '=', ProductTemplate.id)], limit=1)
        for line in self.line_ids:
            self.env['product.template.configured.component'].create({
                'product_tmpl_id': ProductTemplate.id,
                'product_comp_id': line.product_id.product_tmpl_id.id,
                'qty': line.product_uom_qty
            })
            line.unlink();
        
        self.env['sale.order.line'].create({
            'order_id': self.order_id.id,
            'product_id': ProductProduct.id,
        })