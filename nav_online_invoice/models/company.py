# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResCompany(models.Model):

    _inherit = 'res.company'

    nav_user = fields.Char(u'Felhasználó')
    nav_pass = fields.Char(u'Jelszó')
    nav_sign_key = fields.Char(u'Aláírókulcs')
    nav_exchange_key = fields.Char(u'Cserekulcs')
    nav_api_url = fields.Char(u'API Url')
