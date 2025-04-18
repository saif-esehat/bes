from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
import base64
from io import BytesIO
import xlsxwriter
from datetime import datetime
import xlrd


    
class IVAttendanceSheet(models.Model):
    _name = "iv.oral.attendance.sheet"
    _description= 'IV Attendance Sheet'

    _rec_name = "candidate_name"
    
    candidate_name = fields.Many2one('iv.candidates',string="Candidate Name", store=True)
    
    roll_no = fields.Char(string="Roll No.")
    grade_applied = fields.Selection([
        ('1CM', 'First Class Master'),
        ('2CM', 'Second Class Master'),
        ('SER', 'Serang'),
        ('ME', 'Motor Engineer'),
        ('1ED', 'First Class Engine Driver'),
        ('2ED', 'Second Class Engine Driver'),
        ], string='Grade')

    dob = fields.Date(string="Date of Birth")
    batch_id = fields.Many2one(
        'iv.batches', 
        string="IV Batch", 
       
    )
    
    indos_no = fields.Char(string="Indos No")

    candidate_signature = fields.Binary(string="Candidate Signature")
    class_no = fields.Char(string="Class Room: No.")


    def generate_oral_marksheets(self):
        for record in self:
            record.env['iv.oral.exam'].sudo().create({
                'candidate':record.candidate_name.id,
                'batch_id':record.batch_id.id,
                'grade':record.grade_applied
            })



class IVWrittenAttendance(models.AbstractModel):
    _name = 'report.bes.reports_iv_oral_attendance_sheet1'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['iv.oral.attendance.sheet'].sudo().browse(docids)

        grade_order = ['1CM', '2CM', 'SER', 'ME', '1ED', '2ED']
        
        # Sort the records based on the grade_applied field
        sorted_docs = docs.sorted(
            key=lambda r: grade_order.index(r.grade_applied) if r.grade_applied in grade_order else len(grade_order)
        )

          # Determine records per page pattern (20 on odd pages, 10 on even pages)
        # total_records = len(docs)
        # records_per_page_pattern = [20, 8]  # First page has 20, second has 10, then repeat
        # total_pages = 0
        # page_splits = []
        
        # remaining_records = total_records
        # current_start_index = 0

        # while remaining_records > 0:
        #     records_on_this_page = records_per_page_pattern[total_pages % 2]  # Alternate between 20 and 10
        #     records_on_this_page = min(records_on_this_page, remaining_records)  # Don't exceed remaining records

        #     page_splits.append({
        #         'start': current_start_index,
        #         'end': current_start_index + records_on_this_page,
        #     })

        #     # Update indices for the next iteration
        #     current_start_index += records_on_this_page
        #     remaining_records -= records_on_this_page
        #     total_pages += 1

        return {
            'docids': docids,
            'doc_model': 'iv.oral.attendance.sheet',
            'data': data,
            'docs': sorted_docs,
        }

