# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

class SoftLoanRequest(models.Model):
    _name = 'soft.loan.request'
    _description = 'Solicitud de Préstamo de Arma'
    _order = 'request_date desc'

    weapon_id = fields.Many2one('soft.weapon', string='Arma', required=True)
    partner_id = fields.Many2one('res.partner', string='Solicitante', required=True, default=lambda self: self.env.user.partner_id)
    request_date = fields.Datetime(string='Fecha de Solicitud', default=fields.Datetime.now, required=True)
    notes = fields.Text(string='Notas', help='Notas adicionales sobre la solicitud')
    state = fields.Selection([
        ('pending', 'Pendiente'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
    ], string='Estado', default='pending', required=True)

    manager_id = fields.Many2one('res.users', string='Gestor')
    response_date = fields.Datetime(string='Fecha de Respuesta')
    response_note = fields.Text(string='Nota de Respuesta')
    loan_id = fields.Many2one('soft.loan', string='Préstamo Generado')

    # Campo computado para la imagen del arma
    weapon_image = fields.Binary(related='weapon_id.image', string='Imagen del Arma')

    def action_approve(self):
        """Aprobar la solicitud y crear el préstamo"""
        self.ensure_one()
        if self.state != 'pending':
            raise ValidationError(_("Solo se pueden aprobar solicitudes pendientes."))

        if self.weapon_id.status != 'available':
            raise ValidationError(_("El arma no está disponible para préstamo."))

        # Crear el préstamo
        loan = self.env['soft.loan'].create({
            'weapon_id': self.weapon_id.id,
            'partner_id': self.partner_id.id,
            'notes': self.notes or '',
        })

        # Actualizar la solicitud
        self.write({
            'state': 'approved',
            'manager_id': self.env.user.id,
            'response_date': fields.Datetime.now(),
            'loan_id': loan.id,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _('Préstamo Creado'),
            'res_model': 'soft.loan',
            'res_id': loan.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_reject(self):
        """Rechazar la solicitud"""
        self.ensure_one()
        if self.state != 'pending':
            raise ValidationError(_("Solo se pueden rechazar solicitudes pendientes."))

        self.write({
            'state': 'rejected',
            'manager_id': self.env.user.id,
            'response_date': fields.Datetime.now(),
        })

    def action_view_loan(self):
        """Ver el préstamo asociado"""
        self.ensure_one()
        if not self.loan_id:
            raise ValidationError(_("No hay préstamo asociado a esta solicitud."))

        return {
            'type': 'ir.actions.act_window',
            'name': _('Préstamo'),
            'res_model': 'soft.loan',
            'res_id': self.loan_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_submit(self):
        """Enviar la solicitud (placeholder para futuras funcionalidades)"""
        self.ensure_one()
        # Aquí se podría agregar lógica para notificaciones, etc.
        pass
