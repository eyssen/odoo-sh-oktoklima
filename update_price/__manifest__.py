# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Update Price',
    'version' : '1.0',
    'summary': 'Update Price in Quotetion, Order and Invoice',
    'sequence': 15,
    'description': """
Update Price in Quotetion, Order and Invoice
    """,
    'category': 'Sale',
    'website': 'https://www.eyssen.hu',
    'depends' : ['sale', 'account'],
    'data': [
        'views/order.xml',
        'views/invoice.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
