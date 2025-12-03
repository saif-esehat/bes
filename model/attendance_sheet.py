from odoo import api, models

# class CCMCAttendanceSheetReport(models.AbstractModel):
#     _name = 'report.bes.attendance_sheet_online_ccmc'
#     _description = 'Attendance Sheet Online'
    
    
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         import wdb;wdb.set_trace()
#         docs = self.env['exam.type.oral.practical.examiners'].browse(docids)
#         ccmc_candidates = self.env['gp.exam.schedule'].sudo().browse(data['ccmc_candidates'])

#         examiner_name = data['examiner_name']
#         # Example string date
#         exam_date_str = data['exam_date']

#         # Convert the string to a datetime object
#         exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d')
#         return {
#             'doc_ids': docids,
#             'doc_model': 'ccmc.exam.schedule',
#             'docs': docs,
#             'ccmc_candidates': ccmc_candidates
#         }


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
