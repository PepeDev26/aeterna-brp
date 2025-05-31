from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError
from datetime import timedelta

class WeaponLoan(models.Model):
    _name = 'weapon.loan'
    _description = 'Préstamo de Armas'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, id desc'

    name = fields.Char('Referencia', compute='_compute_name', store=True)

    weapon_id = fields.Many2one('weapon.weapon', string='Arma', required=True, tracking=True,
                               domain="[('owner_id', '=', loaner_id), ('current_holder_id', '=', loaner_id)]")
    loaner_id = fields.Many2one('res.users', string='Prestador', required=True,
                                default=lambda self: self.env.user, tracking=True)
    borrower_id = fields.Many2one('res.users', string='Prestatario', required=True, tracking=True)

    # Cambiamos los campos de Date a Datetime
    date_start = fields.Datetime('Fecha y Hora de Inicio', default=fields.Datetime.now, required=True, tracking=True)
    date_end = fields.Datetime('Fecha y Hora Prevista de Devolución', tracking=True)
    date_return = fields.Datetime('Fecha y Hora de Devolución Real', tracking=True)

    notes = fields.Text('Notas', tracking=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('returned', 'Devuelto'),
        ('cancelled', 'Cancelado'),
    ], string='Estado', default='draft', tracking=True)

    @api.depends('weapon_id', 'date_start')
    def _compute_name(self):
        for loan in self:
            if loan.weapon_id and loan.date_start:
                # Formateamos la fecha y hora
                formatted_date = fields.Datetime.to_string(loan.date_start)
                loan.name = f"{loan.weapon_id.name} - {formatted_date}"
            else:
                loan.name = _('Nuevo Préstamo')

    @api.constrains('loaner_id', 'borrower_id')
    def _check_different_users(self):
        for loan in self:
            if loan.loaner_id == loan.borrower_id:
                raise ValidationError(_('El prestador y el prestatario no pueden ser el mismo usuario.'))

    @api.constrains('weapon_id', 'loaner_id')
    def _check_weapon_owner(self):
        for loan in self:
            if loan.state != 'draft' and loan.weapon_id.current_holder_id != loan.loaner_id:
                raise ValidationError(_('Solo puedes prestar un arma que poseas actualmente.'))

    def action_confirm(self):
        for loan in self:
            # Actualizar el tenedor actual del arma
            loan.weapon_id.current_holder_id = loan.borrower_id
            loan.state = 'confirmed'

    def action_return(self):
        for loan in self:
            # Devolver el arma a su prestador
            loan.weapon_id.current_holder_id = loan.loaner_id
            loan.date_return = fields.Datetime.now()
            loan.state = 'returned'

    def action_cancel(self):
        for loan in self:
            if loan.state == 'confirmed':
                # Devolver el arma a su prestador si ya estaba prestada
                loan.weapon_id.current_holder_id = loan.loaner_id
            loan.state = 'cancelled'

    def check_access_rule(self, operation):
        """Sobrescribimos este método para verificar que solo el prestamista y el prestatario
        puedan acceder a cada préstamo específico."""
        result = super(WeaponLoan, self).check_access_rule(operation)

        # Los administradores y responsables pueden ver todos los préstamos
        if self.env.su or self.env.user.has_group('soldier2soldier.group_weapon_loan_manager'):
            return result

        # Verificamos acceso para cada registro
        for record in self:
            if self.env.user.id not in [record.loaner_id.id, record.borrower_id.id]:
                raise AccessError(_('Solo puedes acceder a tus propios préstamos (como prestamista o prestatario).'))

        return result

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, access_rights_uid=None):
        """Sobrescribimos _search para filtrar los préstamos si no es administrador o responsable"""
        if self.env.su or self.env.user.has_group('soldier2soldier.group_weapon_loan_manager'):
            return super(WeaponLoan, self)._search(
                args, offset=offset, limit=limit, order=order,
                access_rights_uid=access_rights_uid)

        # Filtrar para mostrar solo los préstamos del usuario actual
        args = args or []
        args = ['|', ('loaner_id', '=', self.env.user.id), ('borrower_id', '=', self.env.user.id)] + args

        return super(WeaponLoan, self)._search(
            args, offset=offset, limit=limit, order=order,
            access_rights_uid=access_rights_uid)
