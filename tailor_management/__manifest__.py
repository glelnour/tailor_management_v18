# -*- coding: utf-8 -*-

{
    'name': "Tailor Management System",
    'summary': "Tailor Management System",
    'description': "Tailor Management System",
    'author': "Adil Akbar",
    'category': 'Tailor',
    'version': '18.0.0.1',
    'depends': ['crm_check_approve_limiter', 'product_pack', 'pos_sale_poduct_pack', 'sale', 'sale_management', 'account'],
    'sequence': 1,
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/product.xml',
        'views/crm_lead.xml',
        'views/tailor_design_method.xml',
        'views/report_invoice.xml',
    ],
    "license": "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}
