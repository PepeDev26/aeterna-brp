{
    'name': 'Gestión de Reclutas',
    'version': '17.0.1.0.0',
    'summary': 'Gestión del proceso de ingreso de reclutas',
    'author': ' Pepe Aguilar',
    'category': 'Human Resources',
    'depends': ['base', 'contacts'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/recruit_process_views.xml',  # Load views with actions first
        'views/recruit_attendance_views.xml',
        'views/menu.xml',  # Then load the menu that references them
        'data/recruit_groups.xml',
        'reports/recruit_list_report.xml',  # Add the new report
    ],
    'installable': True,
    'application': True,
}
