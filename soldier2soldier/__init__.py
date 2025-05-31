# -*- coding: utf-8 -*-

from . import models

def _assign_groups_to_all_users(env):
    """
    Función post-instalación para asignar grupos por defecto a usuarios existentes
    Esta función se ejecuta después de instalar el módulo
    """
    import logging
    _logger = logging.getLogger(__name__)

    try:
        # Obtener todos los usuarios internos (no portal, no public)
        users = env['res.users'].search([
            ('share', '=', False),
            '!', ('id', '=', env.ref('base.user_root').id),
        ])

        # Obtener el grupo básico de préstamos de armas
        try:
            base_group = env.ref('soldier2soldier.group_weapon_loan_user')
            _logger.info("Grupo encontrado: %s", base_group.name)

            if users:
                _logger.info("Asignando %s usuarios al grupo %s", len(users), base_group.name)
                # Asignar el grupo básico a todos los usuarios internos
                for user in users:
                    base_group.users = [(4, user.id, 0)]

                _logger.info("Usuarios asignados correctamente")
                # Commit para asegurar que los cambios se guardan
                env.cr.commit()
        except Exception as e:
            _logger.error("Error al obtener el grupo: %s", str(e))

    except Exception as e:
        # Log error pero no interrumpir la instalación
        _logger.error("Error durante la asignación de grupos: %s", str(e))
