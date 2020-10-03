# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _, tools
import logging

_logger = logging.getLogger(__name__)


available_nav_payment_methods = [
  ("TRANSFER","Banki átutalás")
, ("CASH", "Készpénz")
, ("CARD", "Bankkártya, hitelkártya, egyéb készpénz helyettesítő eszköz")
, ("VOUCHER", "Utalvány, váltó, egyéb pénzhelyettesítő eszköz")
, ("OTHER", "Egyéb")
]


class account_payment_term(models.Model):
    _name = "account.payment.term"
    _inherit = "account.payment.term"

    nav_payment_method = fields.Selection(selection = available_nav_payment_methods, string = "NAV fizetési mód", required=True)
