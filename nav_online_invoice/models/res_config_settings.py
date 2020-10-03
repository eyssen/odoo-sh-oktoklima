# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    
    _inherit = 'res.config.settings'


    nav_user = fields.Char(u'Felhasználó', related='company_id.nav_user', readonly=False)
    nav_pass = fields.Char(u'Jelszó', related='company_id.nav_pass', readonly=False)
    nav_sign_key = fields.Char(u'Aláírókulcs', related='company_id.nav_sign_key', readonly=False)
    nav_exchange_key = fields.Char(u'Cserekulcs', related='company_id.nav_exchange_key', readonly=False)
    nav_api_url = fields.Char(u'API Url', related='company_id.nav_api_url', readonly=False)


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            nav_user = get_param('nav_online_invoice.nav_user'),
            nav_pass = get_param('nav_online_invoice.nav_pass'),
            nav_sign_key = get_param('nav_online_invoice.nav_sign_key'),
            nav_exchange_key = get_param('nav_online_invoice.nav_exchange_key'),
            nav_api_url = get_param('nav_online_invoice.nav_api_url'),
        )
        return res

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('nav_online_invoice.nav_user', self.nav_user)
        set_param('nav_online_invoice.nav_pass', self.nav_pass)
        set_param('nav_online_invoice.nav_sign_key', self.nav_sign_key)
        set_param('nav_online_invoice.nav_exchange_key', self.nav_exchange_key)
        set_param('nav_online_invoice.nav_api_url', self.nav_api_url)
