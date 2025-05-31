from odoo import models, fields, api

class RecruitAttendance(models.Model):
    _name = 'recruit.attendance'
    _description = 'Recruit Attendance Management'

    recruit_id = fields.Many2one('recruit.process', string='Recruit', required=True)
    date = fields.Date(string='Date', required=True)

    def action_save(self):
        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}
