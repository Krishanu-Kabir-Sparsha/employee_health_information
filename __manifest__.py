# -*- coding: utf-8 -*-
{
    'name': 'Employee Health Information',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Manage Employee Health Information, Medical Records, and Health Compliance',
    'description': """
        Employee Health Information Management
        =======================================
        This module adds comprehensive health information management to Open HRMS:
        - Medical profiles and emergency contacts
        - Vaccination records
        - Health check-up tracking
        - Medical document management
        - Health compliance and reporting
        - Integration with insurance and leave management
    """,
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'depends': [
        'hr',
        'ohrms_core',  # Open HRMS Core dependency
        'hr_holidays',  # For leave integration
        'mail',  # For notifications
        'documents',  # For document management (optional)
    ],
    'data': [
        # Security
        'security/health_security.xml',
        'security/hr_employee_admin_access.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/health_data.xml',
        'data/cron_jobs.xml',
        
        # Views
        'views/hr_employee_health_views.xml',
        'views/medical_history_views.xml',
        'views/vaccination_views.xml',
        'views/health_checkup_views.xml',
        'views/health_menu.xml',
        
        # Reports
        'reports/health_report_templates.xml',
        'reports/health_report_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}