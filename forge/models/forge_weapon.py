from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class ForgeWeapon(models.Model):
    _name = 'forge.weapon'
    _description = 'Forge Weapon'
    _order = 'start_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Weapon Name', required=True, tracking=True)
    weapon_type = fields.Selection([
        ('sword', 'Sword'),
        ('shield', 'Shield'),
        ('spear', 'Spear'),
        ('axe', 'Axe'),
        ('hammer', 'Hammer'),
        ('bow', 'Bow'),
        ('other', 'Other')
    ], string='Weapon Type', required=True, tracking=True)

    responsible_id = fields.Many2one('res.users', string='Responsible', required=True,
                                   default=lambda self: self.env.user, tracking=True)
    stage_id = fields.Many2one('forge.stage', string='Stage', required=True,
                              default=lambda self: self.env['forge.stage'].search([], limit=1, order='sequence'),
                              tracking=True)
    client_id = fields.Many2one('res.partner', string='Client', required=True, tracking=True,
                               help="Client who requested the weapon")

    start_date = fields.Date(string='Start Date', default=fields.Date.today, tracking=True)
    end_date = fields.Date(string='Expected End Date', tracking=True)
    delivery_date = fields.Date(string='Actual Delivery Date', tracking=True)
    materials_notes = fields.Text(string='Materials')
    description = fields.Html(string='Description', help="Detailed description of the weapon")

    # Progress tracking
    progress = fields.Float(string='Progress (%)', default=0.0, tracking=True)

    # Client information display
    client_email = fields.Char(related='client_id.email', string='Client Email', readonly=True)
    client_phone = fields.Char(related='client_id.phone', string='Client Phone', readonly=True)

    # Campo estado con sus posibles valores
    state = fields.Selection([
        ('requested', 'Solicitada'),
        ('in_progress', 'En Progreso'),
        ('ready', 'Lista para Entrega'),
        ('delivered', 'Entregada'),
        ('cancelled', 'Cancelada')
    ], string='Estado', default='requested', tracking=True)

    # Campos para la vista
    materials = fields.Text(string='Materials', help="Materials needed for the weapon")
    notes = fields.Text(string='Notes', help="Additional notes about the weapon")

    # Mantener el campo materials_notes para compatibilidad
    materials_notes = fields.Text(string='Materials Notes', help="Notes about materials")

    @api.model
    def create(self, vals):
        weapon = super(ForgeWeapon, self).create(vals)
        # Subscribe client to follow the weapon
        if weapon.client_id:
            weapon.message_subscribe(partner_ids=[weapon.client_id.id])
        # Send initial notification to client
        weapon._send_stage_notification()
        return weapon

    def write(self, vals):
        old_stage = self.stage_id
        result = super(ForgeWeapon, self).write(vals)

        # Si cambia la etapa, enviar notificación y actualizar estado y progreso
        if 'stage_id' in vals and self.stage_id != old_stage:
            # Actualizar estado basado en la etapa
            if self.stage_id.stage_state:
                self.state = self.stage_id.stage_state

            # Actualizar progreso basado en la etapa
            if self.stage_id.progress_value:
                self.progress = self.stage_id.progress_value

            # Enviar notificación por correo
            self._send_stage_notification()

        # If client changed, update followers
        if 'client_id' in vals:
            # Remove old client if exists
            if old_stage and hasattr(self, '_origin') and self._origin.client_id:
                self.message_unsubscribe(partner_ids=[self._origin.client_id.id])
            # Add new client
            if self.client_id:
                self.message_subscribe(partner_ids=[self.client_id.id])

        return result

    def _update_progress_by_stage(self):
        """Update progress percentage based on current stage"""
        stage_progress = {
            'Pedida': 0.0,
            'Realizada': 70.0,
            'Lista': 95.0,
            'Entregada': 100.0,
        }

        progress = stage_progress.get(self.stage_id.name, 0.0)
        self.write({'progress': progress})

    def _replace_template_variables(self, text):
        """
        Reemplaza manualmente las variables de la plantilla con sus valores reales

        Args:
            text: Texto de la plantilla con variables {{ object.field }}
        Returns:
            Texto con las variables reemplazadas
        """
        if not text:
            return ""

        # Reemplazar variables básicas
        text = text.replace("{{ object.name }}", self.name or "")
        text = text.replace("{{ object.client_id.name }}", self.client_id.name or "")
        text = text.replace("{{ object.responsible_id.name }}", self.responsible_id.name or "")

        # Fecha de inicio
        start_date_str = self.start_date.strftime('%d/%m/%Y') if self.start_date else ""
        text = text.replace("{{ object.start_date }}", start_date_str)

        # Fecha estimada de fin (con valor por defecto)
        end_date_str = self.end_date.strftime('%d/%m/%Y') if self.end_date else "Por determinar"
        text = text.replace("{{ object.end_date or 'Por determinar' }}", end_date_str)

        # Fecha de entrega
        delivery_date_str = self.delivery_date.strftime('%d/%m/%Y') if self.delivery_date else "Hoy"
        text = text.replace("{{ object.delivery_date or 'Hoy' }}", delivery_date_str)

        # Progreso
        text = text.replace("{{ object.progress }}", str(int(self.progress)))

        # Tipo de arma traducido
        weapon_type_selection = dict(self._fields['weapon_type'].selection)
        weapon_type_name = weapon_type_selection.get(self.weapon_type, "")
        text = text.replace("{{ dict(object._fields['weapon_type'].selection).get(object.weapon_type) }}", weapon_type_name)

        return text

    def send_status_email(self, template_id):
        """
        Método mejorado para reemplazar manualmente las variables en las plantillas

        Args:
            template_id: ID de la plantilla de correo a utilizar
        """
        self.ensure_one()
        template = self.env['mail.template'].browse(template_id)

        # Verificamos que el cliente tenga email
        if not self.client_id.email:
            raise UserError(_("El cliente no tiene un correo electrónico configurado"))

        try:
            # Obtenemos los textos originales
            subject = template.subject or ""
            body_html = template.body_html or ""
            email_from = template.email_from or ""

            # Reemplazamos manualmente las variables
            subject = self._replace_template_variables(subject)
            body_html = self._replace_template_variables(body_html)
            email_from = self._replace_template_variables(email_from)

            # Creamos y enviamos el correo directamente
            mail_values = {
                'subject': subject,
                'body_html': body_html,
                'email_from': email_from,
                'email_to': self.client_id.email,
                'model': 'forge.weapon',
                'res_id': self.id,
                'auto_delete': True,
            }

            mail = self.env['mail.mail'].create(mail_values)
            mail.send(raise_exception=False)

            # Registrar el envío en el chatter
            self.message_post(
                body=_("Email '%s' enviado a %s") % (template.name, self.client_id.email),
                subtype_id=self.env.ref('mail.mt_note').id
            )

            return mail.id

        except Exception as e:
            _logger.error("Error al enviar correo desde plantilla %s: %s", template.name, str(e))
            self.message_post(
                body=_("Error al enviar correo: %s") % str(e),
                subtype_id=self.env.ref('mail.mt_note').id
            )
            raise UserError(_("Error al enviar el correo: %s") % str(e))

    def _send_stage_notification(self):
        """Send email notification when stage changes"""
        if not self.client_id or not self.client_id.email:
            return

        template = self._get_stage_email_template()
        if template:
            try:
                # Usamos el método mejorado en lugar del send_mail directo
                self.send_status_email(template.id)
            except Exception as e:
                # Log error but don't block the operation
                _logger.warning(f"Failed to send email notification: {str(e)}")
                self.message_post(
                    body=_("Failed to send email notification: %s") % str(e),
                    subtype_id=self.env.ref('mail.mt_note').id
                )

    def _get_stage_email_template(self):
        """Get the appropriate email template for current stage"""
        # Comprobar si la etapa tiene una plantilla asociada
        if self.stage_id.email_template_id:
            return self.stage_id.email_template_id

        # Fallback al método anterior basado en nombres
        # Usamos un enfoque más seguro para obtener el nombre de la etapa
        stage_name = self.stage_id.get_name_safe() if self.stage_id else False

        template_xmlids = {
            'Pedida': 'forge.email_template_weapon_requested',
            'Realizada': 'forge.email_template_weapon_in_progress',
            'Lista': 'forge.email_template_weapon_ready',
            'Entregada': 'forge.email_template_weapon_delivered',
        }

        xmlid = template_xmlids.get(stage_name)
        if xmlid:
            return self.env.ref(xmlid, raise_if_not_found=False)
        return None

    def action_send_delivered_email(self):
        """Acción para enviar el correo de arma entregada desde un botón en la UI"""
        self.ensure_one()
        template_id = self.env.ref('forge.email_template_weapon_delivered').id
        return self.send_status_email(template_id)

    def action_send_requested_email(self):
        """Acción para enviar el correo de arma solicitada desde un botón en la UI"""
        self.ensure_one()
        template_id = self.env.ref('forge.email_template_weapon_requested').id
        return self.send_status_email(template_id)

    def action_send_in_progress_email(self):
        """Acción para enviar el correo de arma en progreso desde un botón en la UI"""
        self.ensure_one()
        template_id = self.env.ref('forge.email_template_weapon_in_progress').id
        return self.send_status_email(template_id)

    def action_send_ready_email(self):
        """Acción para enviar el correo de arma lista desde un botón en la UI"""
        self.ensure_one()
        template_id = self.env.ref('forge.email_template_weapon_ready').id
        return self.send_status_email(template_id)

    # Smart buttons
    def action_mark_delivered(self):
        delivered_stage = self.env['forge.stage'].search([('name', '=', 'Entregada')], limit=1)
        if delivered_stage:
            self.write({
                'stage_id': delivered_stage.id,
                'delivery_date': fields.Date.today()
            })

    def action_view_client(self):
        """Action to view client details"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Client'),
            'res_model': 'res.partner',
            'res_id': self.client_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    # Acción para crear nueva arma desde kanban
    def action_create_new(self):
        """Action para crear una nueva arma desde la vista kanban"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'forge.weapon',
            'view_mode': 'form',
            'view_id': self.env.ref('forge.forge_weapon_view_form').id,
            'context': {'default_stage_id': self.env['forge.stage'].search([], limit=1, order='sequence').id},
            'target': 'current',
        }
