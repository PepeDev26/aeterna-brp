# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError

class CharacterProfile(models.Model):
    _name = 'character.profile'
    _description = 'Character Profile'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nombre', required=True, tracking=True)
    age = fields.Integer(string='Edad', tracking=True)
    gender = fields.Selection([
        ('male', 'Masculino'),
        ('female', 'Femenino'),
        ('other', 'Otro')
    ], string='Género', tracking=True)
    height = fields.Char(string='Altura', tracking=True)
    hair = fields.Char(string='Cabello', tracking=True)
    skin = fields.Char(string='Tez', tracking=True)
    iris = fields.Char(string='Iris', tracking=True)
    constitution = fields.Char(string='Constitución', tracking=True)
    alignment = fields.Selection([
        ('lawful_good', 'Legal Bueno'),
        ('neutral_good', 'Neutral Bueno'),
        ('chaotic_good', 'Caótico Bueno'),
        ('lawful_neutral', 'Legal Neutral'),
        ('true_neutral', 'Neutral'),
        ('chaotic_neutral', 'Caótico Neutral'),
        ('lawful_evil', 'Legal Maligno'),
        ('neutral_evil', 'Neutral Maligno'),
        ('chaotic_evil', 'Caótico Maligno'),
        # Mantener compatibilidad con códigos antiguos
        ('lg', 'Legal Bueno'),
        ('ng', 'Neutral Bueno'),
        ('cg', 'Caótico Bueno'),
        ('ln', 'Legal Neutral'),
        ('tn', 'Neutral'),
        ('cn', 'Caótico Neutral'),
        ('le', 'Legal Maligno'),
        ('ne', 'Neutral Maligno'),
        ('ce', 'Caótico Maligno'),
    ], string='Alineamiento', tracking=True)

    order_role = fields.Char(string='Rol en la Orden', tracking=True)
    user_id = fields.Many2one('res.users', string='Propietario',
                             default=lambda self: self.env.user,
                             tracking=True, readonly=True)
    image = fields.Binary(string='Imagen')
    curiosities = fields.Text(string='Curiosidades', tracking=True)
    character_history = fields.Text(string='Historia del personaje')

    # Campo computado para determinar si el usuario actual es el propietario
    is_owner = fields.Boolean(compute='_compute_is_owner', string='Es propietario')

    @api.depends('user_id')
    @api.depends_context('uid')
    def _compute_is_owner(self):
        current_user = self.env.user
        for record in self:
            record.is_owner = (record.user_id.id == current_user.id) or current_user.has_group('lore.group_lore_admin')

    def write(self, vals):
        for record in self:
            if not record.is_owner and not self.env.user.has_group('lore.group_lore_admin'):
                raise AccessError(_("Solo el propietario puede modificar este personaje."))
        return super(CharacterProfile, self).write(vals)
