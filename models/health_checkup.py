# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class EmployeeHealthCheckup(models.Model):
    _name = 'hr.employee.health.checkup'
    _description = 'Employee Health Checkups'
    _order = 'checkup_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', compute='_compute_name', store=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, ondelete='cascade')
    checkup_date = fields.Date(string='Checkup Date', required=True, tracking=True)
    checkup_type = fields.Selection([
        ('routine', 'Routine Annual'),
        ('pre_employment', 'Pre-Employment'),
        ('return_to_work', 'Return to Work'),
        ('exit', 'Exit Medical'),
        ('special', 'Special Assessment')
    ], string='Checkup Type', required=True, tracking=True)

    # Vital Signs
    blood_pressure_systolic = fields.Integer(string='Blood Pressure (Systolic)')
    blood_pressure_diastolic = fields.Integer(string='Blood Pressure (Diastolic)')
    pulse_rate = fields.Integer(string='Pulse Rate')
    temperature = fields.Float(string='Temperature (°C)')
    respiratory_rate = fields.Integer(string='Respiratory Rate')

    # Test Results
    blood_sugar = fields.Float(string='Blood Sugar (mg/dL)')
    cholesterol_total = fields.Float(string='Total Cholesterol')
    cholesterol_hdl = fields.Float(string='HDL Cholesterol')
    cholesterol_ldl = fields.Float(string='LDL Cholesterol')

    # General Assessment
    vision_status = fields.Selection([
        ('normal', 'Normal'),
        ('corrected', 'Corrected to Normal'),
        ('impaired', 'Impaired')
    ], string='Vision Status')
    hearing_status = fields.Selection([
        ('normal', 'Normal'),
        ('mild_loss', 'Mild Hearing Loss'),
        ('moderate_loss', 'Moderate Hearing Loss'),
        ('severe_loss', 'Severe Hearing Loss')
    ], string='Hearing Status')

    overall_health = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor')
    ], string='Overall Health Status', tracking=True)

    fitness_certificate = fields.Selection([
        ('fit', 'Fit to Work'),
        ('fit_with_restrictions', 'Fit with Restrictions'),
        ('temporarily_unfit', 'Temporarily Unfit'),
        ('permanently_unfit', 'Permanently Unfit')
    ], string='Fitness Certificate', tracking=True)

    restrictions = fields.Text(string='Restrictions/Recommendations')
    doctor_name = fields.Char(string='Examining Physician')
    clinic_name = fields.Char(string='Clinic/Hospital')

    next_checkup_date = fields.Date(string='Next Checkup Date')

    # Reports
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'checkup_attachment_rel',
        'checkup_id',
        'attachment_id',
        string='Medical Reports'
    )

    notes = fields.Text(string='Doctor\'s Notes')
    follow_up_required = fields.Boolean(string='Follow-up Required')

    state = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='scheduled', tracking=True)

    @api.depends('employee_id', 'checkup_date')
    def _compute_name(self):
        for record in self:
            if record.employee_id and record.checkup_date:
                record.name = f"{record.employee_id.name} - {record.checkup_date}"
            else:
                record.name = "New Checkup"

    def action_complete(self):
        self.state = 'completed'
        if self.fitness_certificate:
            mapping = {
                'fit': 'fit',
                'fit_with_restrictions': 'restricted',
                'temporarily_unfit': 'unfit',
                'permanently_unfit': 'unfit'
            }
            self.employee_id.fitness_status = mapping.get(self.fitness_certificate, 'pending')

        if self.next_checkup_date:
            self.employee_id.next_checkup_date = self.next_checkup_date
