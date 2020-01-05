# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _, tools





class StockPicking(models.Model):
    
    _inherit = 'stock.picking'
    
    mode_of_delivery = fields.Char(u'Szállítás módja')
    comment = fields.Text(u'Megjegyzés')
