# -*- coding: utf-8 -*-
{
    'name': "Extend - Jazzy Theme",
    'version': "1.0",
    'description': """Extend - Jazzy Theme""",
    'summary': "Jazzy Theme Customisation",
    'depends': ['jazzy_backend_theme', 'web'],
    'data': [
        'data/ir_config_parameter_data.xml',
        'views/webclient_templates.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'gl_jazzy_theme_extension/static/src/scss/variables.scss',
            'gl_jazzy_theme_extension/static/src/scss/sidebar.scss',
            'gl_jazzy_theme_extension/static/src/scss/kanban.scss',
            'gl_jazzy_theme_extension/static/src/scss/list.scss',
            'gl_jazzy_theme_extension/static/src/scss/dashboard_bg.scss',
            'gl_jazzy_theme_extension/static/src/components/app_menu/side_menu.xml',
        ],
        'web.assets_frontend': [
            'gl_jazzy_theme_extension/static/src/scss/login.scss'
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
}
