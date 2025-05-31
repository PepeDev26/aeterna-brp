from odoo import api, SUPERUSER_ID

def _assign_groups_to_all_users(cr, registry):
    """
    Asigna automáticamente el grupo de usuario de Soldier2Soldier a todos los usuarios
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Obtener el grupo de usuario de Soldier2Soldier
    group_user = env.ref('soldier2soldier.group_weapon_loan_user')

    # Obtener todos los usuarios internos
    users = env['res.users'].search([('share', '=', False)])

    # Asignar el grupo a todos los usuarios
    for user in users:
        user.write({'groups_id': [(4, group_user.id)]})

    return True
