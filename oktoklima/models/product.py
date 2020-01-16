# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)





class ProductTemplate(models.Model):
    
    _inherit = 'product.template'


    family_id = fields.Many2one('product.family', u'Termékcsalád')
    configured_product = fields.Boolean(u'Konfigurált termék')
    configured_component_ids = fields.One2many('product.template.configured.component', 'product_tmpl_id', u'Összetevők')
    
    
    def compute_okto_price(self):
        
        sql_query = """
            SELECT product_template.id, product_template.name, product_supplierinfo.id AS sid, product_supplierinfo.price,
                product_family.discount, product_family.discount, product_product.id AS pid, list_price_margin
            FROM product_template
                JOIN product_supplierinfo ON product_template.id=product_supplierinfo.product_tmpl_id
                JOIN product_product ON product_template.id=product_product.product_tmpl_id
                JOIN product_category ON product_template.categ_id=product_category.id
                LEFT JOIN product_family ON product_template.family_id=product_family.id
        """
        if self.id:
            sql_query += " WHERE product_template.id=" + str(self.id)
        self.env.cr.execute(sql_query)
        ProductTemplateS = self.env.cr.dictfetchall()

        i = 0
        for ProductTemplate in ProductTemplateS:
            i += 1
            if i % 1000 == 0:
                _logger.info('compute_okto_price ' + str(i))
            
            ProductSupplierinfo = self.env['product.supplierinfo'].browse(ProductTemplate['sid'])
            supplier_price = ProductSupplierinfo.currency_id._convert(ProductTemplate['price'], self.env.user.company_id.currency_id, self.env.user.company_id, fields.Date.today())
            
            if 'discount' in ProductTemplate:
                if ProductTemplate['discount'] and ProductTemplate['discount'] > 0:
                    standard_price = supplier_price * ProductTemplate['discount']
                else:
                    standard_price = supplier_price
            else:
                standard_price = supplier_price
            
            # list_price
            list_price = standard_price * ProductTemplate['list_price_margin']
            sql_query = """
                UPDATE product_template
                SET list_price = %s
                WHERE id = %s
            """
            params = (list_price, ProductTemplate['id'])
            self.env.cr.execute(sql_query, params)
            
            # standard_price
            res_id = 'product.product,'+str(ProductTemplate['pid'])
            sql_query = """
                SELECT id
                FROM ir_property
                WHERE company_id=1 AND fields_id=3742 AND name='standard_price' AND res_id=%s
                LIMIT 1
            """
            params = (res_id,)
            self.env.cr.execute(sql_query, params)
            rows = self.env.cr.dictfetchall()
            if rows:
                sql_query = """
                    UPDATE ir_property
                    SET value_float=%s
                    WHERE id=%s
                """
                params = (standard_price, rows[0]['id'])
                self.env.cr.execute(sql_query, params)
            else:
                sql_query = """
                    INSERT INTO ir_property
                    (name, res_id, company_id, fields_id, value_float, type, create_uid, create_date, write_uid, write_date)
                    VALUES
                    ('standard_price', %s, 1, 3742, %s, 'float', 1, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP)
                """
                params = (res_id, standard_price)
                self.env.cr.execute(sql_query, params)





class ProductProduct(models.Model):
    
    _inherit = 'product.product'


    def compute_okto_price(self):
        self.product_tmpl_id.compute_okto_price()





class ProductFamily(models.Model):
    
    _name = 'product.family'
    
    
    name = fields.Char(u'Termékcsalád', required=True)
    categ_id = fields.Many2one('product.category', u'Termékkategória', required=True)
    discount = fields.Float(u'Kedvezmény', default=0, digits=(12,4))
    product_template_ids = fields.One2many('product.template', 'family_id', u'Termékek')

    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'A termékcsalád névnek egyedinek kell lennie!'),
    ]





class ProductCategory(models.Model):
    
    _inherit = 'product.category'


    list_price_margin = fields.Float(u'Eladási ár szorzó', default=0)





class ProductTemplateConfiguredComponent(models.Model):
    
    _name = 'product.template.configured.component'
    
    
    product_tmpl_id = fields.Many2one('product.template', u'Termék', required=True)
    product_comp_id = fields.Many2one('product.template', u'Komponens', required=True)
    qty = fields.Integer(u'Mennyiség', required=True)


    _sql_constraints = [
        ('comp_uniq', 'unique(product_tmpl_id, product_comp_id)', 'Egy komponens egy termékben csak egyszer szerepelhet!'),
    ]
