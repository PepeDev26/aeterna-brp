from odoo import models, fields, api

class RecruitProcess(models.Model):
    _name = 'recruit.process'
    _description = 'Recruit Process Management'

    partner_id = fields.Many2one('res.partner', string='Recruit', required=True)
    start_date = fields.Date(string='Start Date', required=True)
    tiene_arma = fields.Boolean(string='Has Weapon', default=False)
    attendance_count = fields.Integer(string='Attendance Count', default=0)
    status = fields.Selection([
        ('in_progress', 'In Progress'),
        ('extended', 'Extended'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='in_progress')
    extension_weeks = fields.Selection([
        ('0', 'No Extension'),
        ('4', '4 Weeks Extension'),
        ('8', '8 Weeks Extension')
    ], string='Extension Weeks', default='0')
    promotion_date = fields.Date(string='Promotion Date')

    @api.model
    def create(self, vals):
        record = super(RecruitProcess, self).create(vals)
        return record

    def increment_attendance(self):
        for record in self:
            record.attendance_count += 1
            if record.attendance_count >= 4 and record.tiene_arma:
                record.status = 'approved'
                record.promotion_date = fields.Date.today()

    def extend_period(self, weeks):
        for record in self:
            if record.status != 'approved':
                record.extension_weeks = str(weeks)  # Convert to string to match selection field
                record.status = 'extended'

    def approve_recruit(self):
        for record in self:
            record.status = 'approved'
            record.promotion_date = fields.Date.today()

    def reject_recruit(self):
        for record in self:
            record.status = 'rejected'

    def action_add_attendance(self):
        return self.increment_attendance()

    def action_extend_period(self):
        return self.extend_period(4)  # Pass integer instead of string

    def action_approve_recruit(self):
        return self.approve_recruit()

    def action_reject_recruit(self):
        return self.reject_recruit()
