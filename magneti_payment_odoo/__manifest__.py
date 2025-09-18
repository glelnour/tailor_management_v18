# -*- coding: utf-8 -*-
{
    'name': "GL Magneti Odoo Payment",
    'version': "1.0",
    'description': """GL Magneti Payment""",
    'summary': "GL Magneti Payment Integration",
    'depends': ['base', 'sale'],
    'data': [
        # 'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/res_company_view.xml',
        'views/portal_templates.xml',
        'views/sale_order_view.xml',
        'views/account_move_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
}
