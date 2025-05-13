# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SoftWeapon(models.Model):
    _name = 'soft.weapon'
    _description = 'Arma para Softcombat'
    _order = 'name'

    name = fields.Char(string='Nombre', required=True)
    weapon_type = fields.Selection([
        ('sword', 'Espada'),
        ('greatsword', 'Mandoble'),
        ('spear', 'Lanza'),
        ('axe', 'Hacha'),
        ('mace', 'Maza'),
        ('bow', 'Arco'),
        ('other', 'Otro'),
    ], string='Tipo de Arma', required=True)
    serial = fields.Char(string='Número de serie', required=True)
    status = fields.Selection([
        ('available', 'Disponible'),
        ('loaned', 'Prestada'),
        ('retired', 'Retirada'),
    ], string='Estado', default='available', required=True)
    notes = fields.Text(string='Notas')
    # Nuevo campo para la imagen del arma
    image = fields.Binary(string='Foto del arma')

    # Relación con los préstamos
    loan_ids = fields.One2many('soft.loan', 'weapon_id', string='Historial de préstamos')
    active_loan_id = fields.Many2one('soft.loan', string='Préstamo activo',
                                    compute='_compute_active_loan', store=False)

    _sql_constraints = [
        ('serial_unique', 'UNIQUE(serial)', 'El número de serie debe ser único')
    ]

    @api.depends('loan_ids')
    def _compute_active_loan(self):
        for weapon in self:
            active_loans = weapon.loan_ids.filtered(lambda l: l.state == 'loaned')
            weapon.active_loan_id = active_loans[0] if active_loans else False

    def action_create_loan(self):
        """Acción para crear un nuevo préstamo a partir del arma actual"""
        self.ensure_one()
        if self.status != 'available':
            raise ValidationError(_("No se puede prestar un arma que ya está prestada o retirada."))

        return {
            'name': _('Nuevo Préstamo'),
            'type': 'ir.actions.act_window',
            'res_model': 'soft.loan',
            'view_mode': 'form',
            'context': {'default_weapon_id': self.id},
            'target': 'new',
        }
