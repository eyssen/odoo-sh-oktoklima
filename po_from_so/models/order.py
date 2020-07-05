# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)





class SaleOrder(models.Model):
    
    _inherit = 'sale.order'
    
    
    po_ids = fields.One2many('purchase.order', 'so_id', u'Created Purchase Orders', readonly=True)
    po_ids_nbr = fields.Integer(compute='_compute_po_ids_nbr', string='# of PO')


    @api.depends('po_ids')
    def _compute_po_ids_nbr(self):
        for trans in self:
            trans.po_ids_nbr = len(trans.po_ids)


    def action_view_pos(self):
        action = {
            'name': _('Purchases'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'target': 'current',
        }
        po_ids = self.po_ids.ids
        action['view_mode'] = 'tree,form'
        action['domain'] = [('id', 'in', po_ids)]
        return action
    
    
    def action_create_po(self):
        
        return {
            'name': 'Create Purchase Order',
            'view_mode': 'form',
            'view_id': self.env.ref('purchase.purchase_order_form').id,
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_so_id': self.id,
            }
        }





class PurchaseOrder(models.Model):
    
    _inherit = 'purchase.order'
    
    
    so_id = fields.Many2one('sale.order', u'Creating Sale Order')


    @api.onchange('so_id')
    def _onchange_so_id(self):
        if self.so_id and not self.order_line:
            for Line in self.env['sale.order.line'].search([('order_id', '=', self.so_id.id), ('is_service', '=', False)]):
                self.order_line = [(0, 0, {
                    'order_id': self.env.context.get('active_id', False),
                    'product_id': Line.product_id.id,
                    'name': Line.product_id.name,
                    'product_qty': Line.product_qty,
                    'product_uom': Line.product_uom.id,
                    'price_unit': Line.product_id.list_price,
                    'taxes_id': Line.product_id.taxes_id,
                    'date_planned': fields.datetime.now(),
                })]