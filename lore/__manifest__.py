# -*- coding: utf-8 -*-
{
    'name': 'Fichas de Personajes',
    'version': '1.0',
    'summary': 'Gestión sencilla de fichas de personajes',
    'description': """
        Módulo simple para crear y gestionar fichas de personajes:
        - Información básica del personaje
        - Características físicas
        - Historia y curiosidades
    """,
    'category': 'Eaglestone Suite',
    'author': 'Pepe Aguilar',
    'website': '',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/character_views.xml',
        'views/menus.xml',
        'report/character_profile_reports.xml',
        'report/character_profile_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'lore/static/src/css/character_report.css',
        ],
        'web.report_assets_common': [
            'lore/static/src/css/character_report.css',
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
