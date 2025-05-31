from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class WeaponLoanWizard(models.TransientModel):
    _name = 'weapon.loan.wizard'
    _description = 'Asistente para préstamo de equipamiento'

    weapon_id = fields.Many2one('weapon.weapon', string='Equipamiento', required=True,
                              domain="[('owner_id', '=', loaner_id), ('current_holder_id', '=', loaner_id)]",
                              readonly=True)
    loaner_id = fields.Many2one('res.users', string='Prestador', required=True,
                              readonly=True)
    borrower_id = fields.Many2one('res.users', string='Prestatario', required=True)

    # Cambiamos los campos de Date a Datetime
    date_start = fields.Datetime('Fecha y Hora de Inicio', default=fields.Datetime.now, required=True)
    date_end = fields.Datetime('Fecha y Hora Prevista de Devolución')

    notes = fields.Text('Notas')

    @api.onchange('loaner_id')
    def _onchange_loaner_id(self):
        """Actualizar el dominio del prestatario para excluir al prestador"""
        if self.loaner_id:
            return {'domain': {'borrower_id': [('id', '!=', self.loaner_id.id)]}}

    @api.model
    def default_get(self, fields_list):
        res = super(WeaponLoanWizard, self).default_get(fields_list)
        weapon_id = self.env.context.get('default_weapon_id')

        # Verificar que el equipamiento exista
        if weapon_id:
            weapon = self.env['weapon.weapon'].browse(weapon_id)

            # Verificar que el usuario sea el propietario y el poseedor actual
            if weapon.owner_id.id != self.env.user.id or weapon.current_holder_id.id != self.env.user.id:
                raise ValidationError(_('Solo puedes prestar equipamiento que sea de tu propiedad y que tengas actualmente.'))

            if weapon.is_loaned:
                raise ValidationError(_('Este equipamiento ya está prestado a %s') % weapon.current_holder_id.name)

        return res

    def action_create_loan(self):
        self.ensure_one()

        if self.loaner_id == self.borrower_id:
            raise ValidationError(_('No puedes prestarte equipamiento a ti mismo.'))

        loan_vals = {
            'weapon_id': self.weapon_id.id,
            'loaner_id': self.loaner_id.id,
            'borrower_id': self.borrower_id.id,
            'date_start': self.date_start,
            'date_end': self.date_end,
            'notes': self.notes,
            'state': 'draft'
        }

        loan = self.env['weapon.loan'].create(loan_vals)
        loan.action_confirm()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Préstamo Creado'),
            'res_model': 'weapon.loan',
            'res_id': loan.id,
            'view_mode': 'form',
            'target': 'current',
        }
