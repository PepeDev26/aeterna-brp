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
    client_id = fields.Many2one('res.partner', string='Client', required=True, tracking=True,
                               help="Client who requested the weapon")

    start_date = fields.Date(string='Start Date', default=fields.Date.today, tracking=True)
    end_date = fields.Date(string='Expected End Date', tracking=True)
    delivery_date = fields.Date(string='Actual Delivery Date', tracking=True)
    materials_notes = fields.Text(string='Materials')
    description = fields.Html(string='Description', help="Detailed description of the weapon")

    # Progress tracking
    progress = fields.Float(string='Progress (%)', default=0.0, tracking=True)
    
    # Campo para agrupar por etapas en la vista kanban
    progress_stage = fields.Selection([
        ('requested', 'Solicitada'),
        ('in_progress', 'En Progreso'),
        ('ready', 'Lista para Entrega'),
        ('delivered', 'Entregada')
    ], string='Etapa', compute='_compute_progress_stage', store=True)

    # Campos computados para indicar la etapa según el progreso
    is_requested = fields.Boolean(string='Es solicitada', compute='_compute_progress_stage')
    is_in_progress = fields.Boolean(string='En progreso', compute='_compute_progress_stage')
    is_ready = fields.Boolean(string='Lista para entrega', compute='_compute_progress_stage')
    is_delivered = fields.Boolean(string='Entregada', compute='_compute_progress_stage')

    # Client information display
    client_email = fields.Char(related='client_id.email', string='Client Email', readonly=True)
    client_phone = fields.Char(related='client_id.phone', string='Client Phone', readonly=True)

    # Campos para la vista
    materials = fields.Text(string='Materials', help="Materials needed for the weapon")
    notes = fields.Text(string='Notes', help="Additional notes about the weapon")

    # Mantener el campo materials_notes para compatibilidad
    materials_notes = fields.Text(string='Materials Notes', help="Notes about materials")

    @api.depends('progress')
    def _compute_progress_stage(self):
        """Calcula etapas basadas en el progreso"""
        for weapon in self:
            # Calcular etapa para agrupación
            if weapon.progress < 10:
                weapon.progress_stage = 'requested'
            elif 10 <= weapon.progress < 90:
                weapon.progress_stage = 'in_progress'
            elif 90 <= weapon.progress < 100:
                weapon.progress_stage = 'ready'
            else:
                weapon.progress_stage = 'delivered'
            
            # Indicadores booleanos para visibilidad en vistas
            weapon.is_requested = weapon.progress < 10
            weapon.is_in_progress = 10 <= weapon.progress < 90
            weapon.is_ready = 90 <= weapon.progress < 100
            weapon.is_delivered = weapon.progress >= 100

    @api.model
    def create(self, vals):
        weapon = super(ForgeWeapon, self).create(vals)
        # Subscribe client to follow the weapon
        if weapon.client_id:
            weapon.message_subscribe(partner_ids=[weapon.client_id.id])
        # Send initial notification to client (requested)
        if weapon.progress < 10:
            self._send_notification_by_progress(weapon)
        return weapon

    def write(self, vals):
        old_progress = self.progress
        result = super(ForgeWeapon, self).write(vals)

        # Si cambia el progreso, enviar notificación
        if 'progress' in vals and self.progress != old_progress:
            # Enviar notificación por correo según el nuevo progreso
            self._send_notification_by_progress(self)

        # If client changed, update followers
        if 'client_id' in vals:
            # Remove old client if exists
            if hasattr(self, '_origin') and self._origin.client_id:
                self.message_unsubscribe(partner_ids=[self._origin.client_id.id])
            # Add new client
            if self.client_id:
                self.message_subscribe(partner_ids=[self.client_id.id])

        return result

    @api.model
    def _send_notification_by_progress(self, weapon):
        """Envía notificación según el progreso del arma"""
        if not weapon.client_id or not weapon.client_id.email:
            return

        template = None
        if weapon.progress < 10:
            # Solicitada
            template_id = self.env.ref('forge.email_template_weapon_requested', False)
        elif 10 <= weapon.progress < 90:
            # En progreso
            template_id = self.env.ref('forge.email_template_weapon_in_progress', False)
        elif 90 <= weapon.progress < 100:
            # Lista para entrega
            template_id = self.env.ref('forge.email_template_weapon_ready', False)
        elif weapon.progress >= 100:
            # Entregada
            template_id = self.env.ref('forge.email_template_weapon_delivered', False)

        if template_id:
            try:
                weapon.send_status_email(template_id.id)
            except Exception as e:
                _logger.warning(f"Failed to send email notification: {str(e)}")
                weapon.message_post(
                    body=_("Failed to send email notification: %s") % str(e),
                    subtype_id=self.env.ref('mail.mt_note').id
                )

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

        # Obtener el usuario actual para las variables {{ user.X }}
        current_user = self.env.user

        # Reemplazar variables básicas
        text = text.replace("{{ object.name }}", self.name or "")
        text = text.replace("{{ object.client_id.name }}", self.client_id.name or "")
        text = text.replace("{{ object.responsible_id.name }}", self.responsible_id.name or "")

        # Variables del usuario actual
        text = text.replace("{{ user.email or '' }}", current_user.email or "")
        text = text.replace("{{ user.name }}", current_user.name or "")

        # Email del responsable con fallback
        responsible_email = self.responsible_id.email if self.responsible_id and self.responsible_id.email else "Contactar por teléfono"
        text = text.replace("{{ object.responsible_id.email or 'Contactar por teléfono' }}", responsible_email)

        # Fecha de inicio
        start_date_str = self.start_date.strftime('%d/%m/%Y') if self.start_date else ""
        text = text.replace("{{ object.start_date }}", start_date_str)

        # Fecha estimada de fin (con valor por defecto)
        end_date_str = self.end_date.strftime('%d/%m/%Y') if self.end_date else "Por determinar"
        text = text.replace("{{ object.end_date or 'Por determinar' }}", end_date_str)

        # Fecha de entrega
        delivery_date_str = self.delivery_date.strftime('%d/%m/%Y') if self.delivery_date else "Hoy"
        text = text.replace("{{ object.delivery_date or 'Hoy' }}", delivery_date_str)

        # Progreso (asegurar que se muestra como entero)
        text = text.replace("{{ object.progress }}", str(int(self.progress)))

        # Tipo de arma traducido
        weapon_type_selection = dict(self._fields['weapon_type'].selection)
        weapon_type_name = weapon_type_selection.get(self.weapon_type, "")
        text = text.replace("{{ dict(object._fields['weapon_type'].selection).get(object.weapon_type) }}", weapon_type_name)

        # Estado basado en progreso (para mantener compatibilidad)
        if self.progress < 10:
            estado = "Solicitada"
        elif 10 <= self.progress < 90:
            estado = "En Progreso"
        elif 90 <= self.progress < 100:
            estado = "Lista para Entrega"
        else:
            estado = "Entregada"

        text = text.replace("Estado actual: Pedida", f"Estado actual: {estado}")
        text = text.replace("Estado: Realizada - En proceso de forjado", f"Estado: {estado}")
        text = text.replace("Estado: Lista para entrega", f"Estado: {estado}")
        text = text.replace("Estado: Entregada", f"Estado: {estado}")

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

    # Acciones para actualizar el progreso
    def action_mark_requested(self):
        """Marca el arma como solicitada (0%)"""
        self.write({
            'progress': 0.0,
        })

    def action_mark_in_progress(self):
        """Marca el arma como en progreso (50%)"""
        self.write({
            'progress': 50.0,
        })

    def action_mark_ready(self):
        """Marca el arma como lista para entrega (95%)"""
        self.write({
            'progress': 95.0,
        })

    def action_mark_delivered(self):
        """Marca el arma como entregada (100%)"""
        self.write({
            'progress': 100.0,
            'delivery_date': fields.Date.today()
        })

    # Acciones para enviar correos (adaptadas para trabajar sin estado)
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
            'context': {'default_progress': 0.0},
            'target': 'current',
        }
