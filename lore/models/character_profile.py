# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, ValidationError

class CharacterProfile(models.Model):
    _name = 'character.profile'
    _description = 'Ficha de Personaje'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nombre', required=True, tracking=True)
    user_id = fields.Many2one('res.users', string='Propietario', default=lambda self: self.env.user, tracking=True, readonly=True)
    image = fields.Binary('Imagen', attachment=True)
    age = fields.Integer('Edad')
    gender = fields.Selection([
        ('male', 'Masculino'),
        ('female', 'Femenino'),
        ('other', 'Otro')
    ], string='Género')
    height = fields.Char('Altura')
    hair = fields.Char('Cabello')
    skin = fields.Char('Piel')
    iris = fields.Char('Iris')
    constitution = fields.Char('Constitución')
    alignment = fields.Selection([
        ('lawful_good', 'Legal Bueno'),
        ('neutral_good', 'Neutral Bueno'),
        ('chaotic_good', 'Caótico Bueno'),
        ('lawful_neutral', 'Legal Neutral'),
        ('true_neutral', 'Neutral Puro'),
        ('chaotic_neutral', 'Caótico Neutral'),
        ('lawful_evil', 'Legal Maligno'),
        ('neutral_evil', 'Neutral Maligno'),
        ('chaotic_evil', 'Caótico Maligno')
    ], string='Alineamiento')
    order_role = fields.Text('Rol en la Orden')
    curiosities = fields.Text('Curiosidades')
    character_history = fields.Text('Historia del Personaje')

    is_owner = fields.Boolean(compute='_compute_is_owner', string='Es propietario')

    @api.depends('user_id')
    def _compute_is_owner(self):
        for record in self:
            record.is_owner = record.user_id == self.env.user

    def write(self, vals):
        for record in self:
            if not record.is_owner and not self.env.user.has_group('lore.group_lore_admin'):
                raise AccessError(_("Solo el propietario puede modificar este personaje."))
        return super(CharacterProfile, self).write(vals)
