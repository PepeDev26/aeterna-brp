# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError

class CharacterProfile(models.Model):
    _name = 'character.profile'
    _description = 'Character Profile'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    age = fields.Integer(string='Age', tracking=True)
    # Convert string fields to selection fields where appropriate
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender', tracking=True)
    height = fields.Char(string='Height', tracking=True)
    hair = fields.Char(string='Hair', tracking=True)
    skin = fields.Char(string='Skin', tracking=True)
    iris = fields.Char(string='Iris', tracking=True)
    constitution = fields.Char(string='Constitution', tracking=True)
    alignment = fields.Selection([
        ('lawful_good', 'Lawful Good'),
        ('neutral_good', 'Neutral Good'),
        ('chaotic_good', 'Chaotic Good'),
        ('lawful_neutral', 'Lawful Neutral'),
        ('true_neutral', 'True Neutral'),
        ('chaotic_neutral', 'Chaotic Neutral'),
        ('lawful_evil', 'Lawful Evil'),
        ('neutral_evil', 'Neutral Evil'),
        ('chaotic_evil', 'Chaotic Evil')
    ], string='Alignment', tracking=True)

    # Añadir el campo order_role que faltaba
    order_role = fields.Char(string='Rol en la Orden', tracking=True)

    # Modificar el campo user_id para que se asigne automáticamente al usuario actual
    user_id = fields.Many2one('res.users', string='Propietario',
                             default=lambda self: self.env.user,
                             tracking=True, readonly=True)

    image = fields.Binary(string='Image')
    curiosities = fields.Text(string='Curiosities', tracking=True)
    character_history = fields.Text(string='Historia del personaje')

    # Añadir campo computado para determinar si el usuario actual es el propietario
    is_owner = fields.Boolean(compute='_compute_is_owner', string='Es propietario')

    @api.depends('user_id')
    def _compute_is_owner(self):
        """Determina si el usuario actual es el propietario del registro"""
        current_user = self.env.user
        for record in self:
            record.is_owner = (record.user_id.id == current_user.id) or current_user.has_group('lore.group_lore_admin')

    # Sobrescribir método write para añadir comprobación adicional
    def write(self, vals):
        """Prevenir que usuarios no propietarios modifiquen registros"""
        for record in self:
            if not record.is_owner and not self.env.user.has_group('lore.group_lore_admin'):
                raise AccessError(_("Solo el propietario puede modificar este personaje."))
        return super(CharacterProfile, self).write(vals)
