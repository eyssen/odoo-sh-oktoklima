# -*- coding: utf-8 -*-
import base64
import os
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError





class Company(models.Model):

    _inherit = "res.company"


    logo_invoice = fields.Binary(u'Számla logó')