from odoo import models, fields

class ForgeStage(models.Model):
    _name = 'forge.stage'
    _description = 'Forge Stage'
    _order = 'sequence'

    name = fields.Char(string='Stage Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    fold = fields.Boolean(string='Fold in Kanban', help='This stage is folded in the kanban view when there are no records in that stage to display.')

    def __str__(self):
        return self.name
