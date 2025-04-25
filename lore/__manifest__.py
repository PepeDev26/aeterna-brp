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
    'category': 'Entretenimiento',
    'author': 'PepeDev26',
    'website': '',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/character_views.xml',
        'views/menus.xml',
    ],
    'assets': {},
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
