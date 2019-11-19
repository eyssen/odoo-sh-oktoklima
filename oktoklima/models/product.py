# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError





class ProductTemplate(models.Model):
    
    _inherit = 'product.template'


    family_id = fields.Many2one('product.family', u'Termékcsalád')





class ProductFamily(models.Model):
    
    _name = 'product.family'
    
    
    name = fields.Char(u'Termékcsalád', required=True)
    discount = fields.Float(u'Kedvezmény', default=0)
    product_template_ids = fields.One2many('product.template', 'family_id', u'Termékek')

    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'A termékcsalád névnek egyedinek kell lennie!'),
    ]
