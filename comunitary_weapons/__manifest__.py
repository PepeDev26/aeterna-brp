# -*- coding: utf-8 -*-
{
    'name': "Armas Comunitarias",
    'summary': "Gestión de préstamo de armas comunitarias para softcombat",
    'description': """
        Este módulo permite:
        - Registrar armas disponibles para préstamo (espadas, hachas, escudos, etc.).
        - Gestionar los préstamos activos: quién tomó qué arma, en qué fecha, y cuándo fue devuelta.
        - Historial completo de uso, para trazabilidad y gestión del desgaste.
        - Limitar acceso a préstamos: solo usuarios autorizados (organizadores) pueden prestar armas.
        - Solicitar préstamos por parte de usuarios sin permisos de gestión.
    """,
    'author': "Pepe Aguilar",
    'website': "https://github.com/aeternabrp",
    'category': 'Eaglestone Suite',
    'version': '0.1',
    'depends': ['base', 'web'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'report/soft_loan_report.xml',
        'views/soft_weapon_views.xml',
        'views/soft_loan_views.xml',
        'views/soft_loan_request_views.xml',
        'views/request_menu.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
