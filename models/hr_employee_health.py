# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class HrEmployeeHealth(models.Model):
    _inherit = 'hr.employee'

    # ============ Basic Health Information ============
    blood_group = fields.Selection([
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-')
    ], string='Blood Group', groups="hr.group_hr_user")

    height = fields.Float(string='Height (cm)', groups="hr.group_hr_user")
    weight = fields.Float(string='Weight (kg)', groups="hr.group_hr_user")
    bmi = fields.Float(string='BMI', compute='_compute_bmi', store=True, groups="hr.group_hr_user")

    allergies = fields.Text(string='Allergies', groups="hr.group_hr_user")
    chronic_conditions = fields.Text(string='Chronic Conditions', groups="hr.group_hr_user")
    current_medications = fields.Text(string='Current Medications', groups="hr.group_hr_user")

    # ============ Emergency Information ============
    emergency_contact_name = fields.Char(string='Emergency Contact Name', groups="hr.group_hr_user")
    emergency_contact_relationship = fields.Char(string='Relationship', groups="hr.group_hr_user")
    emergency_contact_phone = fields.Char(string='Emergency Phone', groups="hr.group_hr_user")
    emergency_contact_phone2 = fields.Char(string='Alternative Phone', groups="hr.group_hr_user")
    emergency_blood_bank = fields.Char(string='Preferred Blood Bank', groups="hr.group_hr_user")

    # ============ Medical Insurance ============
    health_insurance_provider = fields.Char(string='Insurance Provider', groups="hr.group_hr_user")
    health_insurance_number = fields.Char(string='Insurance Policy Number', groups="hr.group_hr_user")
    health_insurance_expiry = fields.Date(string='Insurance Expiry Date', groups="hr.group_hr_user")
    health_insurance_type = fields.Selection([
        ('basic', 'Basic Coverage'),
        ('standard', 'Standard Coverage'),
        ('premium', 'Premium Coverage'),
        ('family', 'Family Coverage')
    ], string='Insurance Type', groups="hr.group_hr_user")

    # ============ Health Status ============
    disability_status = fields.Boolean(string='Has Disability', groups="hr.group_hr_user")
    disability_description = fields.Text(string='Disability Description', groups="hr.group_hr_user")
    fitness_status = fields.Selection([
        ('fit', 'Fit to Work'),
        ('restricted', 'Restricted Duties'),
        ('unfit', 'Temporarily Unfit'),
        ('pending', 'Pending Assessment')
    ], string='Fitness Status', default='fit', groups="hr.group_hr_user")


    # ============ Vaccination Records ============
    vaccination_ids = fields.One2many(
        'hr.employee.vaccination',
        'employee_id',
        string='Vaccination Records',
        groups="hr.group_hr_user"
    )
    covid_vaccination_status = fields.Selection([
        ('not_vaccinated', 'Not Vaccinated'),
        ('partially', 'Partially Vaccinated'),
        ('fully', 'Fully Vaccinated'),
        ('boosted', 'Boosted')
    ], string='COVID-19 Vaccination Status', groups="hr.group_hr_user")

    # ============ Medical History ============
    medical_history_ids = fields.One2many(
        'hr.employee.medical.history',
        'employee_id',
        string='Medical History',
        groups="hr.group_hr_user"
    )

    # ============ Health Checkups ============
    health_checkup_ids = fields.One2many(
        'hr.employee.health.checkup',
        'employee_id',
        string='Health Checkups',
        groups="hr.group_hr_user"
    )
    last_checkup_date = fields.Date(
        string='Last Health Checkup',
        compute='_compute_checkup_dates',
        store=True,
        groups="hr.group_hr_user"
    )
    next_checkup_date = fields.Date(
        string='Next Health Checkup Due',
        compute='_compute_checkup_dates',
        store=True,
        groups="hr.group_hr_user"
    )

    # ============ Medical Documents ============
    medical_document_ids = fields.Many2many(
        'ir.attachment',
        'employee_medical_doc_rel',
        'employee_id',
        'attachment_id',
        string='Medical Documents',
        groups="hr.group_hr_user"
    )

    # ============ Occupational Health ============
    occupational_hazards = fields.Text(string='Occupational Hazards Exposure', groups="hr.group_hr_user")
    ppe_required = fields.Text(string='Required PPE', groups="hr.group_hr_user")
    work_restrictions = fields.Text(string='Work Restrictions', groups="hr.group_hr_user")

    # =================== Compute Methods ===================
    @api.depends('height', 'weight')
    def _compute_bmi(self):
        for record in self:
            if record.height and record.weight:
                height_m = record.height / 100
                record.bmi = round(record.weight / (height_m ** 2), 2)
            else:
                record.bmi = 0

    @api.depends('health_checkup_ids.checkup_date', 'health_checkup_ids.next_checkup_date', 'health_checkup_ids.state')
    def _compute_checkup_dates(self):
        for record in self:
            completed_checkups = record.health_checkup_ids.filtered(lambda x: x.state == 'completed').sorted('checkup_date', reverse=True)
            if completed_checkups:
                last = completed_checkups[0]
                record.last_checkup_date = last.checkup_date
                record.next_checkup_date = last.next_checkup_date
            else:
                record.last_checkup_date = False
                record.next_checkup_date = False

    # =================== Constraints ===================
    @api.constrains('emergency_contact_phone', 'emergency_contact_phone2')
    def _check_emergency_phone(self):
        for record in self:
            for phone in [record.emergency_contact_phone, record.emergency_contact_phone2]:
                if phone and len(phone) < 10:
                    raise ValidationError(_("Emergency contact phone must be at least 10 digits"))

    # =================== Actions ===================
    def action_schedule_checkup(self):
        self.ensure_one()
        return {
            'name': _('Schedule Health Checkup'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee.health.checkup',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_employee_id': self.id, 'default_checkup_type': 'routine'}
        }

    def action_add_vaccination(self):
        self.ensure_one()
        return {
            'name': _('Add Vaccination Record'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee.vaccination',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_employee_id': self.id}
        }

    def action_add_medical_history(self):
        self.ensure_one()
        return {
            'name': _('Add Medical History'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee.medical.history',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_employee_id': self.id}
        }
    
    def action_schedule_checkup(self):
        self.ensure_one()
        return {
            'name': _('Schedule Health Checkup'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee.health.checkup',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_employee_id': self.id,
                'default_checkup_type': 'routine',
                'form_view_ref': 'employee_health_information.view_health_checkup_form',
            },
            'views': [(False, 'form')],
        }

    # =================== Cron Job Methods ===================
    @api.model
    def check_insurance_expiry(self):
        today = fields.Date.today()
        expiry_date = today + timedelta(days=30)
        employees = self.search([
            ('health_insurance_expiry', '<=', expiry_date),
            ('health_insurance_expiry', '>=', today)
        ])
        for employee in employees:
            employee.message_post(
                body=_("Health insurance expiring on %s. Please renew.") % employee.health_insurance_expiry,
                subject=_("Insurance Expiry Reminder"),
                message_type='notification',
            )

    @api.model
    def check_health_checkup_reminders(self):
        today = fields.Date.today()
        threshold = today + timedelta(days=30)
        employees = self.search([
            ('next_checkup_date', '!=', False),
            ('next_checkup_date', '<=', threshold)
        ])
        for emp in employees:
            emp.message_post(
                body=_("Health checkup due on %s") % emp.next_checkup_date,
                subject=_("Health Checkup Reminder"),
                message_type='notification'
            )
