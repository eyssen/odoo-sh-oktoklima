# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _, tools

import logging
_logger = logging.getLogger(__name__)





NAV_UOM = [
    ('PIECE', 'Darab'),
    ('KILOGRAM', 'Kilogramm'),
    ('TON', 'Metrikus tonna'),
    ('KWH', 'Kilowatt óra'),
    ('DAY', 'Nap'),
    ('HOUR', 'Óra'),
    ('MINUTE', 'Perc'),
    ('MONTH', 'Hónap'),
    ('LITER', 'Liter'),
    ('KILOMETER', 'Kilométer'),
    ('CUBIC_METER', 'Köbméter'),
    ('METER', 'Méter'),
    ('LINEAR_METER', 'Folyóméter'),
    ('CARTON', 'Karton'),
    ('PACK', 'Csomag'),
    ('OWN', 'Saját mennyiségi egység megnevezés'),
]





class Uom(models.Model):

    _inherit = "uom.uom"

    nav_uom = fields.Selection(NAV_UOM, u'NAV mennyiség egység típusai', required=True)
