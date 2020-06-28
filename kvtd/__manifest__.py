# -*- coding: utf-8 -*-
{
    'name': u'KVTD',
    'description': u'Környezetvédelmi termékdíj',
    'category': 'Accounting',
    'version': '1.0',
    'author': 'eYssen IT Services',
    'website': 'https://eyssen.hu/',
    'depends': [
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product.xml',
        'views/account_move.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
