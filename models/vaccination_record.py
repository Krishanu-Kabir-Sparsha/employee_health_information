# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import timedelta

class EmployeeVaccination(models.Model):
    _name = 'hr.employee.vaccination'
    _description = 'Employee Vaccination Records'
    _order = 'vaccination_date desc'
    _rec_name = 'vaccine_name'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, ondelete='cascade')
    vaccine_name = fields.Char(string='Vaccine Name', required=True)
    date_administered = fields.Date(string="Date Administered")
    next_due_date = fields.Date(string="Next Due Date")

    vaccine_type = fields.Selection([
        ('covid19', 'COVID-19'),
        ('influenza', 'Influenza'),
        ('hepatitis_a', 'Hepatitis A'),
        ('hepatitis_b', 'Hepatitis B'),
        ('tetanus', 'Tetanus'),
        ('mmr', 'MMR'),
        ('polio', 'Polio'),
        ('yellow_fever', 'Yellow Fever'),
        ('other', 'Other')
    ], string='Vaccine Type', required=True)

    vaccination_date = fields.Date(string='Vaccination Date', required=True)
    dose_number = fields.Selection([
        ('1', 'First Dose'),
        ('2', 'Second Dose'),
        ('3', 'Third Dose'),
        ('booster', 'Booster'),
        ('annual', 'Annual')
    ], string='Dose', default='1')

    batch_number = fields.Char(string='Batch/Lot Number')
    manufacturer = fields.Char(string='Manufacturer')
    administered_by = fields.Char(string='Administered By')
    vaccination_center = fields.Char(string='Vaccination Center')

    next_dose_date = fields.Date(string='Next Dose Due')
    validity_period = fields.Integer(string='Validity Period (months)')
    expiry_date = fields.Date(string='Expiry Date', compute='_compute_expiry_date', store=True)

    certificate_number = fields.Char(string='Certificate Number')
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'vaccination_attachment_rel',
        'vaccination_id',
        'attachment_id',
        string='Vaccination Certificates'
    )

    side_effects = fields.Text(string='Side Effects (if any)')
    notes = fields.Text(string='Notes')

    @api.depends('vaccination_date', 'validity_period')
    def _compute_expiry_date(self):
        for record in self:
            if record.vaccination_date and record.validity_period:
                record.expiry_date = record.vaccination_date + timedelta(days=record.validity_period*30)
            else:
                record.expiry_date = False

    @api.model
    def check_vaccination_expiry(self):
        today = fields.Date.today()
        expiry_threshold = today + timedelta(days=30)
        expiring_vaccinations = self.search([
            ('expiry_date', '<=', expiry_threshold),
            ('expiry_date', '>=', today)
        ])
        for vacc in expiring_vaccinations:
            vacc.employee_id.message_post(
                body=_("%s vaccination expiring on %s") % (vacc.vaccine_name, vacc.expiry_date),
                subject=_("Vaccination Expiry Reminder"),
                message_type='notification'
            )

    @api.model
    def create(self, vals):
        rec = super(EmployeeVaccination, self).create(vals)
        if rec.vaccine_type == 'covid19':
            doses = self.search_count([('employee_id', '=', rec.employee_id.id), ('vaccine_type', '=', 'covid19')])
            if doses == 1:
                rec.employee_id.covid_vaccination_status = 'partially'
            elif doses == 2:
                rec.employee_id.covid_vaccination_status = 'fully'
            elif doses > 2:
                rec.employee_id.covid_vaccination_status = 'boosted'
        return rec
