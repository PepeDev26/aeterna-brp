from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Weapon(models.Model):
    _name = 'weapon.weapon'
    _description = 'Información de armas y armaduras'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nombre', required=True, tracking=True)
    serial_number = fields.Char('Número de Serie', tracking=True)
    item_type = fields.Selection([
        ('firearm', 'Arma de Fuego'),
        ('melee', 'Arma Cuerpo a Cuerpo'),
        ('armor_piece', 'Pieza de Armadura'),
        ('armor_set', 'Conjunto de Armadura'),
        ('other', 'Otro')
    ], string='Tipo', required=True, default='other', tracking=True)
    description = fields.Text('Descripción', tracking=True)
    image = fields.Binary('Imagen')

    # Para piezas de armadura
    armor_position = fields.Selection([
        ('head', 'Cabeza'),
        ('chest', 'Pecho'),
        ('legs', 'Piernas'),
        ('arms', 'Brazos'),
        ('feet', 'Pies'),
        ('hands', 'Manos'),
        ('shield', 'Escudo'),
        ('full', 'Armadura Completa'),
        ('other', 'Otra')
    ], string='Posición de la Armadura', tracking=True)

    owner_id = fields.Many2one('res.users', string='Propietario',
                               required=True, default=lambda self: self.env.user,
                               tracking=True)
    current_holder_id = fields.Many2one('res.users', string='Tenedor Actual',
                                       default=lambda self: self.env.user,
                                       tracking=True)

    loan_ids = fields.One2many('weapon.loan', 'weapon_id', string='Historial de Préstamos')
    is_loaned = fields.Boolean('En Préstamo', compute='_compute_is_loaned', store=True)
    active = fields.Boolean(default=True)

    @api.depends('current_holder_id', 'owner_id')
    def _compute_is_loaned(self):
        for weapon in self:
            weapon.is_loaned = weapon.current_holder_id and weapon.current_holder_id != weapon.owner_id

    def action_loan_wizard(self):
        self.ensure_one()
        return {
            'name': _('Prestar Equipamiento'),
            'type': 'ir.actions.act_window',
            'res_model': 'weapon.loan.wizard',
            'view_mode': 'form',
            'context': {
                'default_weapon_id': self.id,
                'default_loaner_id': self.env.user.id,
            },
            'target': 'new',
        }

    def action_view_loan_history(self):
        self.ensure_one()
        # Modificamos para mostrar solo préstamos del usuario actual
        return {
            'name': _('Historial de Préstamos'),
            'type': 'ir.actions.act_window',
            'res_model': 'weapon.loan',
            'view_mode': 'tree,form',
            'domain': [
                ('weapon_id', '=', self.id),
                '|',
                ('loaner_id', '=', self.env.user.id),
                ('borrower_id', '=', self.env.user.id)
            ],
            'context': {'create': False},
        }

    @api.model
    def create(self, vals):
        """Asegurar que el propietario y el poseedor actual sean el usuario actual al crear"""
        if not vals.get('owner_id'):
            vals['owner_id'] = self.env.user.id

        if not vals.get('current_holder_id'):
            vals['current_holder_id'] = self.env.user.id

        return super(Weapon, self).create(vals)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """Asegurar que los usuarios solo vean su propio equipamiento o el que tienen prestado"""
        if not self.env.user.has_group('soldier2soldier.group_weapon_loan_manager'):
            domain = domain or []
            domain = ['|', ('owner_id', '=', self.env.user.id), ('current_holder_id', '=', self.env.user.id)] + domain
        return super(Weapon, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """Asegurar que los usuarios solo vean su propio equipamiento o el prestado en agrupaciones"""
        if not self.env.user.has_group('soldier2soldier.group_weapon_loan_manager'):
            domain = domain or []
            domain = ['|', ('owner_id', '=', self.env.user.id), ('current_holder_id', '=', self.env.user.id)] + domain
        return super(Weapon, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
