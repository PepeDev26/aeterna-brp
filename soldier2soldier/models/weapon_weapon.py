from odoo import models, fields, api, _
from odoo.exceptions import AccessError

class WeaponWeapon(models.Model):
    _name = 'weapon.weapon'
    _description = 'Arma'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nombre', required=True, tracking=True)
    description = fields.Text('Descripción', tracking=True)
    owner_id = fields.Many2one('res.users', string='Propietario', required=True,
                                default=lambda self: self.env.user, tracking=True)
    current_holder_id = fields.Many2one('res.users', string='Tenedor Actual', tracking=True)

    def check_access_rule(self, operation):
        """Sobrescribimos este método para verificar que solo el propietario pueda
        acceder a sus propias armas."""
        result = super(WeaponWeapon, self).check_access_rule(operation)

        # Los administradores pueden ver todas las armas
        if self.env.su or self.env.user.has_group('soldier2soldier.group_weapon_manager'):
            return result

        # Verificamos acceso para cada registro
        for record in self:
            if record.owner_id.id != self.env.user.id:
                raise AccessError(_('Solo puedes acceder a tus propias armas.'))

        return result

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, access_rights_uid=None):
        """Sobrescribimos _search para filtrar las armas si no es administrador"""
        if self.env.su or self.env.user.has_group('soldier2soldier.group_weapon_manager'):
            return super(WeaponWeapon, self)._search(
                args, offset=offset, limit=limit, order=order,
                access_rights_uid=access_rights_uid)

        # Filtrar para mostrar solo las armas del usuario actual
        args = args or []
        args = [('owner_id', '=', self.env.user.id)] + args

        return super(WeaponWeapon, self)._search(
            args, offset=offset, limit=limit, order=order,
            access_rights_uid=access_rights_uid)
