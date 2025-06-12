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
        'security/security.xml',
        'security/character_security.xml',
        'security/ir.model.access.csv',
        'report/character_profile_reports.xml',
        'report/character_profile_templates.xml',
        'views/character_views.xml',
        'views/menus.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
