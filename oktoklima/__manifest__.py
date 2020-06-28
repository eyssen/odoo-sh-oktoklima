# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Oktoklima',
    'version' : '1.0',
    'summary': 'Oktoklima Addon',
    'sequence': 15,
    'description': """
Oktoklima Addon
    """,
    'category': 'Other',
    'website': 'https://www.eyssen.hu',
    'depends' : ['sale','product'],
    'data': [
        'security/ir.model.access.csv',
        'views/product.xml',
        'views/currency.xml',
        'views/order.xml',
        'views/account.xml',
        #'report/order.xml',
    ],
    'qweb': ['static/src/xml/supplierinfo.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
