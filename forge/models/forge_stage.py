from odoo import models, fields, api

class ForgeStage(models.Model):
    _name = 'forge.stage'
    _description = 'Forge Stage'
    _order = 'sequence, id'

    # Usamos translate=True de manera adecuada
    name = fields.Char(string='Stage Name', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    description = fields.Text(string='Description', translate=True)
    fold = fields.Boolean(string='Folded in Kanban View')
    active = fields.Boolean(string='Active', default=True)

    # Relacionar cada etapa con una plantilla de correo electrónico
    email_template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        domain=[('model', '=', 'forge.weapon')],
        help="Email template that will be sent automatically when a weapon reaches this stage"
    )

    # Cambiamos a un nombre no traducible para el mapeo
    stage_state = fields.Selection([
        ('requested', 'Solicitada'),
        ('in_progress', 'En Progreso'),
        ('ready', 'Lista para Entrega'),
        ('delivered', 'Entregada'),
        ('cancelled', 'Cancelada')
    ], string='Estado asociado',
       help="Este campo asocia la etapa con un estado interno del sistema")

    progress_value = fields.Float(
        string='Progress Value (%)',
        default=0.0,
        help="Default progress percentage for weapons in this stage"
    )

    # Método para obtener el nombre sin problemas de traducción
    def get_name_safe(self):
        """Obtiene el nombre de la etapa de manera segura para evitar problemas de traducción"""
        self.ensure_one()
        return self.name
