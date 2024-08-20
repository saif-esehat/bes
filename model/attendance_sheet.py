from odoo import api, models

class AttendanceSheetReport(models.AbstractModel):
    _name = 'report.bes.attendance_sheet_online_ccmc'
    _description = 'Attendance Sheet Online'
    
    
    @api.model
    def _get_report_values(self, docids, data=None):
        # import wdb;wdb.set_trace()
        docs = self.env['exam.type.oral.practical.examiners'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'exam.type.oral.practical.examiners',
            'docs': docs,
        }


class GPAttendanceSheetReport(models.AbstractModel):
    _name = 'report.bes.attendance_sheet_online_gp'
    _description = 'Attendance Sheet Online'
    
    
    @api.model
    def _get_report_values(self, docids, data=None):
        # import wdb;wdb.set_trace()
        docs = self.env['exam.type.oral.practical.examiners'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'exam.type.oral.practical.examiners',
            'docs': docs,
        }
