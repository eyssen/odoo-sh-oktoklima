# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _, tools

import logging
_logger = logging.getLogger(__name__)





KVTDTYPE = [
    ('Akt.', 'Akkumulátor környezetvédelmi termékdíja'),
    ('Cskt.', 'Csomagolási kv. termékdíja'),
    ('Kkt.', 'Egyéb kőolajtermékek kv. termékdíja'),
    ('Gkt.', 'Gumiabroncs kv. termékdíja'),
    ('Hkkt.', 'Hűtőközeg kv. termékdíja'),
    ('Pkt.', 'Reklámhordozó papírok kv. termékdíja'),
    ('Ekt.', 'Elektromos és elektronikai berendezések kv. termékdíja')
]

class product_template(models.Model):
    
    _inherit = "product.template"
    
    list_price_gross = fields.Float(u'Bruttó eladási ár', compute='_compute_gross_price', readonly=True)
    vtsz_id = fields.Many2one('vtsz', string="VTSZ")
    szj_id = fields.Many2one('szj', string="SZJ")
    kvtd_ids = fields.One2many('product.kvtd', 'product_tmpl_id', u'KVTD')


    @api.depends('list_price', 'taxes_id')
    def _compute_gross_price(self):
        for template in self:
            if template.taxes_id[0].amount_type == 'percent':
                template.list_price_gross = template.list_price * (100 + template.taxes_id[0].amount) / 100
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





class kvtd(models.Model):
    
    _name = "kvtd"
    
    
    name = fields.Char(u'Megnevezés', required=True)
    code = fields.Char(u'KT/CSK kód', required=True)
    type = fields.Selection(KVTDTYPE, u'Termékdíj típus', required=True)
    vtsz_id = fields.Many2one('vtsz', string="VTSZ")
    rate = fields.Float(u'Díjtétel (Ft/kg)', required=True)

    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'A megnevezésnek egyedinek kell lennie!'),
    ]





class product_kvtd(models.Model):

    _name = "product.kvtd"
    
    
    product_tmpl_id = fields.Many2one('product.template', u'Termék', required=True)
    kvtd_id = fields.Many2one('kvtd', u'Termékdíj fajtája', required=True)
    weight = fields.Float(u'Mennyiség (kg)', required=True)

    
    _sql_constraints = [
        ('product_kvtd_uniq', 'unique(product_tmpl_id, kvtd_id)', 'Egy termékdíj fajta csak egyszer szerepelhet egy terméknél!'),
    ]
