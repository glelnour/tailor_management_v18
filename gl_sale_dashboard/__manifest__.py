{
    'name': 'Sale Dashboard',
    'version': '18.0.1.0.0',
    'summary': 'Greenlines Sale Dashboard',
    'author': 'Green Lines',
    'depends': ['base', 'web', 'sale'],
    'data': [
        'views/sale_dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'gl_sale_dashboard/static/src/js/sale_dashboard_v18.js',
            'gl_sale_dashboard/static/src/css/sale_dashboard.css',
            'gl_sale_dashboard/static/src/xml/sale_dashboard.xml',
        ],
    },
    'installable': True,
    'application': True,
}