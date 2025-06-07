{
    'name': 'Forge Manager',
    'version': '1.0',
    'category': 'Manufacturing',
    'summary': 'Manage handcrafted weapons in a forge',
    'description': """
        Gestor de Forja
        ===============
        Module to manage the creation process of handcrafted weapons in the forge.
    """,
    'author': 'Pepe Aguilar',
    'depends': ['base', 'mail'],
    'data': [
        'security/forge_security.xml',
        'security/ir.model.access.csv',
        'views/forge_stage_views.xml',
        'views/forge_weapon_views.xml',
        'data/forge_stage_data.xml',
        'data/forge_email_templates.xml',
        'views/forge_menus.xml',
    ],

    'installable': True,
    'application': True,
}
