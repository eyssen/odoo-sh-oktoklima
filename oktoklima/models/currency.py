# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)





class Currency(models.Model):
    
    _inherit = 'res.currency'


    okto_euro_exchange_rate = fields.Float(u'Fix Euro árfolyam Oktoklíma index árfolyamokhoz')
