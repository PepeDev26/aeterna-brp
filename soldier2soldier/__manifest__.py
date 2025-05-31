{
    'name': 'Soldier to Soldier',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'summary': 'Gestión de préstamos de armas y armaduras entre usuarios',
    'description': """
        Este módulo permite gestionar el préstamo de armas y armaduras entre usuarios.
        Cada usuario puede registrar su equipamiento y prestarlo a otros usuarios.
        Los usuarios solo pueden ver su propio equipamiento o aquel que tienen prestado.

        Accesible para todos los usuarios del sistema.
    """,
    'author': 'PepeDev26',
    'website': 'https://www.aeternanocte.es',
    'depends': ['base', 'mail'],
    'data': [
        'security/security.xml',  # PRIMERO los archivos de definición de grupos
        'security/ir.model.access.csv',  # DESPUÉS los permisos de acceso
        'views/weapon_views.xml',
        'views/weapon_loan_views.xml',
        'views/weapon_loan_wizard_views.xml',
        'views/weapon_loan_menu.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'post_init_hook': '_assign_groups_to_all_users',
}
