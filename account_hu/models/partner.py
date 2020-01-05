# -*- encoding: utf-8 -*-

import datetime
import random

from dateutil import relativedelta

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, AccessError, ValidationError





class res_partner(models.Model):
    
    _name = "res.partner"
    _inherit = "res.partner"


    vat_hu = fields.Char(u'Adószám')
    reg_number = fields.Char(u'Cégjegyzékszám')


    @api.model
    def _commercial_fields(self):
      return super(res_partner, self)._commercial_fields() + ['vat_hu']
