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
    
    kvtd_ids = fields.One2many('product.kvtd', 'product_tmpl_id', u'KVTD')





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