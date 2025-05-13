# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

class SoftLoan(models.Model):
    _name = 'soft.loan'
    _description = 'Préstamo de arma de softcombat'
    _order = 'loan_date desc, id desc'

    weapon_id = fields.Many2one('soft.weapon', string='Arma', required=True,
                                domain=[('status', '=', 'available')])
    partner_id = fields.Many2one('res.partner', string='Prestatario', required=True)
    # Cambiados de Date a Datetime para incluir hora
    loan_date = fields.Datetime(string='Fecha y hora de préstamo', default=fields.Datetime.now, required=True)
    return_date = fields.Datetime(string='Fecha y hora de devolución')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('loaned', 'Prestado'),
        ('returned', 'Devuelto'),
    ], string='Estado', default='draft', required=True)
    notes = fields.Text(string='Notas')

    # Imagen del arma relacionada - campo técnico para mostrar la imagen en la vista
    weapon_image = fields.Binary(related='weapon_id.image', string='Foto del arma', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        loans = super(SoftLoan, self).create(vals_list)
        # Al crear, si el estado es prestado, marcamos el arma como prestada
        for loan in loans:
            if loan.state == 'loaned':
                loan.weapon_id.write({'status': 'loaned'})
        return loans

    def write(self, vals):
        # Si estamos cambiando al estado "devuelto"
        if vals.get('state') == 'returned':
            # Si no está establecida la fecha de devolución, la establecemos
            if not vals.get('return_date'):
                vals['return_date'] = fields.Datetime.now()

            # Marcamos las armas como disponibles
            for loan in self.filtered(lambda l: l.state == 'loaned'):
                loan.weapon_id.write({'status': 'available'})

        # Si estamos cambiando al estado "prestado" desde otro estado
        elif vals.get('state') == 'loaned':
            for loan in self:
                # Solo podemos cambiar a prestado si el arma está disponible
                if loan.weapon_id.status != 'available':
                    raise ValidationError(_("No se puede prestar un arma que ya está prestada o retirada."))
                loan.weapon_id.write({'status': 'loaned'})

        return super(SoftLoan, self).write(vals)

    def action_loan(self):
        """Acción para prestar el arma"""
        for loan in self:
            if loan.weapon_id.status != 'available':
                raise ValidationError(_("No se puede prestar un arma que ya está prestada o retirada."))

        return self.write({
            'state': 'loaned',
            'loan_date': fields.Datetime.now(),
        })

    def action_return(self):
        """Acción para devolver el arma"""
        return self.write({
            'state': 'returned',
            'return_date': fields.Datetime.now(),
        })

    @api.ondelete(at_uninstall=False)
    def _unlink_if_not_loaned(self):
        """No permitir eliminar préstamos activos"""
        for loan in self:
            if loan.state == 'loaned':
                raise ValidationError(_("No se puede eliminar un préstamo activo."))
