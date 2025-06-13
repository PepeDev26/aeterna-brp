# -*- coding: utf-8 -*-
{
    'name': 'Soldier to Soldier',
    'version': '1.0',
    'summary': 'Gestión de préstamos de armas',
    'description': """
        Módulo para gestionar préstamos de armas entre usuarios del sistema.
    """,
    'category': 'Tools',
    'author': 'Pepe Aguilar',
    'website': '',
    'depends': ['base', 'mail'],
    'data': [
        'security/weapon_loan_security.xml',
        'security/ir.model.access.csv',
        'views/weapon_loan_wizard_views.xml',
        'views/weapon_views.xml',
        'views/weapon_loan_views.xml',
        'views/menus.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': '_assign_groups_to_all_users',
    'license': 'LGPL-3',
}
