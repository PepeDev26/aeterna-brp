# -*- coding: utf-8 -*-

from odoo import models, fields, api

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
    order_role = fields.Char(string='Order Role', tracking=True)
    image = fields.Binary(string='Image')
    curiosities = fields.Text(string='Curiosities', tracking=True)
    character_history = fields.Text(string='Historia del personaje')

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, ondelete='restrict')
