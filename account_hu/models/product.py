# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _, tools

import logging
_logger = logging.getLogger(__name__)





class product_template(models.Model):
    
    _inherit = "product.template"
    
    list_price_gross = fields.Float(u'Bruttó eladási ár', compute='_compute_gross_price', readonly=True)
    vtsz_id = fields.Many2one('vtsz', string="VTSZ")
    szj_id = fields.Many2one('szj', string="SZJ")


    @api.depends('list_price', 'taxes_id')
    def _compute_gross_price(self):
        for template in self:
            if template.taxes_id:
                if template.taxes_id[0].amount_type == 'percent':
                    template.list_price_gross = template.list_price * (100 + template.taxes_id[0].amount) / 100
                else:
                    template.list_price_gross = 0
            else:
                template.list_price_gross = 0





class vtsz(models.Model):
    
    _name = "vtsz"
    
    name = fields.Char('VTSZ', required=True)
    description = fields.Char('Megnevezés')
    product_template_ids = fields.One2many('product.template', 'vtsz_id', string="Termékek")





class szj(models.Model):
    
    _name = "szj"
    
    name = fields.Char('SZJ', required=True)
    description = fields.Char('Megnevezés')
    product_template_ids = fields.One2many('product.template', 'szj_id', string="Termékek")
