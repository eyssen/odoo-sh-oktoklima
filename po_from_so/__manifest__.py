# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'PO from SO',
    'version' : '1.0',
    'summary': 'Create Purchase Order from Sale Order',
    'sequence': 15,
    'description': """
Create Purchase Order from Sale Order
    """,
    'category': 'Sale',
    'website': 'https://www.eyssen.hu',
    'depends' : ['sale','purchase'],
    'data': [
        'views/order.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
