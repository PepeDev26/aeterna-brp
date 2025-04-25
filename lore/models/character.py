# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Character(models.Model):
    _name = 'character.profile'
    _description = 'Ficha de Personaje'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre", required=True, tracking=True)
    age = fields.Integer(string="Edad", tracking=True)
    gender = fields.Selection([
        ('male', 'Masculino'),
        ('female', 'Femenino'),
        ('other', 'Otro')
    ], string="Género", tracking=True)
    height = fields.Char(string="Altura", tracking=True)
    hair = fields.Char(string="Cabello", tracking=True)
    skin = fields.Char(string="Tez", tracking=True)
    iris = fields.Char(string="Iris", tracking=True)
    constitution = fields.Char(string="Constitución", tracking=True)
    alignment = fields.Selection([
        ('lg', 'Legal Bueno'),
        ('ng', 'Neutral Bueno'),
        ('cg', 'Caótico Bueno'),
        ('ln', 'Legal Neutral'),
        ('tn', 'Neutral'),
        ('cn', 'Caótico Neutral'),
        ('le', 'Legal Maligno'),
        ('ne', 'Neutral Maligno'),
        ('ce', 'Caótico Maligno'),
    ], string="Alineación", tracking=True)
    order_role = fields.Char(string="Rol en la orden", tracking=True)
    curiosities = fields.Text(string="Curiosidades", tracking=True)
    history = fields.Html(string="Historia", tracking=True)
    image = fields.Binary(string="Imagen", attachment=True)

    user_id = fields.Many2one('res.users', string="Usuario", default=lambda self: self.env.user)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'El nombre del personaje debe ser único!')
    ]
