from odoo import models, api

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    @api.model
    def _get_report_from_name(self, report_name):
        res = super(IrActionsReport, self)._get_report_from_name(report_name)
        if res and res.report_name in [
            'employee_health_information.report_health_card_template',
            'employee_health_information.report_health_summary_template'
        ]:
            # This will trigger the prt_report_attachment_preview functionality
            res = res.with_context(
                force_report_rendering=True,
                download_only=False
            )
        return res