from odoo import models, fields, api, _
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

        # If stage changed, send notification
        if 'stage_id' in vals and self.stage_id != old_stage:
            self._send_stage_notification()
            # Update progress based on stage
            self._update_progress_by_stage()

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

    def _send_stage_notification(self):
        """Send email notification when stage changes"""
        if not self.client_id or not self.client_id.email:
            return

        template = self._get_stage_email_template()
        if template:
            try:
                template.send_mail(self.id, force_send=True, raise_exception=False)
            except Exception as e:
                # Log error but don't block the operation
                _logger.warning(f"Failed to send email notification: {str(e)}")

    def _get_stage_email_template(self):
        """Get the appropriate email template for current stage"""
        template_xmlids = {
            'Pedida': 'forge.email_template_weapon_requested',
            'Realizada': 'forge.email_template_weapon_in_progress',
            'Lista': 'forge.email_template_weapon_ready',
            'Entregada': 'forge.email_template_weapon_delivered',
        }

        xmlid = template_xmlids.get(self.stage_id.name)
        if xmlid:
            return self.env.ref(xmlid, raise_if_not_found=False)
        return None

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
