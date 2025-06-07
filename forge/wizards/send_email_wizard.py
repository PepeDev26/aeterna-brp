from odoo import models, fields, api, _

class ForgeSendEmailWizard(models.TransientModel):
    _name = 'forge.send.email.wizard'
    _description = 'Asistente para envío de correos de forja'

    email_template_id = fields.Many2one(
        'mail.template',
        string='Plantilla de Correo',
        domain="[('model', '=', 'forge.weapon')]",
    )
    
    @api.model
    def default_get(self, fields):
        """Pre-cargar la plantilla adecuada según la etapa del arma"""
        res = super().default_get(fields)
        active_id = self.env.context.get('active_id')
        if active_id:
            weapon = self.env['forge.weapon'].browse(active_id)
            # Obtener la plantilla según el progreso
            if weapon.is_requested:
                template = self.env.ref('forge.email_template_weapon_requested', False)
            elif weapon.is_in_progress:
                template = self.env.ref('forge.email_template_weapon_in_progress', False)
            elif weapon.is_ready:
                template = self.env.ref('forge.email_template_weapon_ready', False)
            elif weapon.is_delivered:
                template = self.env.ref('forge.email_template_weapon_delivered', False)
            else:
                template = False
                
            if template:
                res['email_template_id'] = template.id
        return res
    
    def action_send_email(self):
        """Enviar el correo usando la plantilla seleccionada"""
        self.ensure_one()
        active_id = self.env.context.get('active_id')
        if active_id and self.email_template_id:
            weapon = self.env['forge.weapon'].browse(active_id)
            weapon.send_status_email(self.email_template_id.id)
        return {'type': 'ir.actions.act_window_close'}
