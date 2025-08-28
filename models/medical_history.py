# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class EmployeeMedicalHistory(models.Model):
    _name = 'hr.employee.medical.history'
    _description = 'Employee Medical History'
    _order = 'date desc'
    _rec_name = 'condition'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, ondelete='cascade')
    date = fields.Date(string='Date', required=True, default=fields.Date.today)
    condition = fields.Char(string='Medical Condition', required=True)
    diagnosis_date = fields.Date(string="Diagnosis Date")
    condition_type = fields.Selection([
        ('illness', 'Illness'),
        ('injury', 'Injury'),
        ('surgery', 'Surgery'),
        ('chronic', 'Chronic Condition'),
        ('allergy', 'Allergy'),
        ('other', 'Other')
    ], string='Type', required=True)

    severity = fields.Selection([
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
        ('critical', 'Critical')
    ], string='Severity')

    treatment = fields.Text(string='Treatment')
    doctor_name = fields.Char(string='Doctor/Hospital')
    recovery_date = fields.Date(string='Recovery Date')
    is_ongoing = fields.Boolean(string='Ongoing Condition')

    medications = fields.Text(string='Medications Prescribed')
    follow_up_required = fields.Boolean(string='Follow-up Required')
    follow_up_date = fields.Date(string='Follow-up Date')

    notes = fields.Text(string='Additional Notes')
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'medical_history_attachment_rel',
        'history_id',
        'attachment_id',
        string='Medical Reports'
    )

    # Work Impact
    sick_leave_days = fields.Integer(string='Sick Leave Days')
    work_restrictions = fields.Text(string='Work Restrictions')

    @api.model
    def create(self, vals):
        record = super(EmployeeMedicalHistory, self).create(vals)
        if record.follow_up_required and record.follow_up_date:
            user_id = record.employee_id.user_id.id or self.env.user.id
            record.employee_id.activity_schedule(
                'mail.mail_activity_data_todo',
                date_deadline=record.follow_up_date,
                summary=_("Medical follow-up for %s") % record.condition,
                user_id=user_id
            )
        return record
