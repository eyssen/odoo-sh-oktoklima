# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)





class ProductTemplate(models.Model):
    
    _inherit = 'product.template'


    family_id = fields.Many2one('product.family', u'Termékcsalád')
    
    
    def _compute_okto_price(self):
        
        ProductTemplateS = self.env['product.template'].search([('seller_ids', '!=', False)])
        for ProductTemplate in ProductTemplateS:
            if ProductTemplate.seller_ids:
                supplier_price = ProductTemplate.seller_ids[0].currency_id._convert(ProductTemplate.seller_ids[0].price, ProductTemplate.currency_id, self.env.user.company_id, fields.Date.today())
                
                if ProductTemplate.family_id:
                    if ProductTemplate.family_id.discount > 0:
                        standard_price = supplier_price * ProductTemplate.family_id.discount
                    else:
                        standard_price = supplier_price
                else:
                    standard_price = supplier_price
                
                ProductTemplate.standard_price = standard_price
                ProductTemplate.list_price = standard_price * ProductTemplate.categ_id.list_price_margin
            




class ProductFamily(models.Model):
    
    _name = 'product.family'
    
    
    name = fields.Char(u'Termékcsalád', required=True)
    discount = fields.Float(u'Kedvezmény', default=0, digits=(12,4))
    product_template_ids = fields.One2many('product.template', 'family_id', u'Termékek')

    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'A termékcsalád névnek egyedinek kell lennie!'),
    ]





class ProductCategory(models.Model):
    
    _inherit = 'product.category'


    list_price_margin = fields.Float(u'Eladási ár szorzó', default=0)