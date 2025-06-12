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
        'security/security.xml',  # Primero cargar seguridad general
        'security/character_security.xml',  # Luego reglas específicas
        'security/ir.model.access.csv',  # Después los permisos de acceso
        # Importante: cargar primero los reportes y luego las vistas
        'report/character_profile_reports.xml',  # Primero definiciones de reporte
        'report/character_profile_templates.xml',  # Y luego las plantillas
        'views/character_views.xml',  # Esta vista debe cargar después de los reportes
        'views/menus.xml',  # Nombre correcto del archivo

    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
