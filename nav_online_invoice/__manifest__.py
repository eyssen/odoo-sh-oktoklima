# -*- coding: utf-8 -*-
{
    'name': u'NAV Online Invoice',
    'description': u'NAV online számla adatszolgáltatás',
    'category': 'Accounting',
    'version': '2.0',
    'author': 'eYssen Informatika',
    'website': 'https://eyssen.hu/',
    'depends': [
        'account_hu',
        'report_xml',
    ],
    'data': [
        'views/account_invoice_form.xml',
        'views/account_payment_term_form.xml',
        'views/company.xml',
        'views/res_config_settings_views.xml',
        'views/nav_invoice.xml',
        'views/uom.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
