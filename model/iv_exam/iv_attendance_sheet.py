from math import ceil
from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
import base64
from io import BytesIO
import xlsxwriter
from datetime import datetime
import xlrd
from odoo.exceptions import UserError



    
class IVAttendanceSheet(models.Model):
    _name = "iv.attendance.sheet"
    _description= 'IV Attendance Sheet'

    _rec_name = "candidate_name"
    
    candidate_name = fields.Many2one('iv.candidates',string="Candidate Name", store=True)

    batch_id = fields.Many2one(
        'iv.batches', 
        string="IV Batch", 
       
    )
    
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
    
    indos_no = fields.Char(string="INDOs No")

    candidate_signature = fields.Binary(string="Candidate Signature")
    classroom_no = fields.Char("Classroom No")
   

   
    def action_print_bulk_attendance(self):
        # Logic to handle the printing of bulk allotment data
        return self.env.ref('bes.reports_iv_written_attendance').report_action(self)

    def print_report(self):
        return self.env.ref('bes.action_report_iv_attendance_sheet').report_action(self)

    def print_iv_invigilator_report(self):
        datas = {
            'doc_ids': self.id,
        }

        return self.env.ref('bes.action_report_iv_invigilator').report_action(self, data=datas)



import logging
class IVWrittenAttendance(models.AbstractModel):
    _name = 'report.bes.reports_iv_written_attendance_sheet1'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
  
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['iv.attendance.sheet'].sudo().browse(docids)

        grade_order = ['1CM', '2CM', 'SER', 'ME', '1ED', '2ED']
        
        # Sort the records based on the grade_applied field
        sorted_docs = docs.sorted(
            key=lambda r: grade_order.index(r.grade_applied) if r.grade_applied in grade_order else len(grade_order)
        )

        
        total_records = len(docs)
        records_per_page_pattern = [20, 8]  
        total_pages = 0
        page_splits = []
        
        remaining_records = total_records
        current_start_index = 0

        while remaining_records > 0:
            records_on_this_page = records_per_page_pattern[total_pages % 2]  
            records_on_this_page = min(records_on_this_page, remaining_records)  

            page_splits.append({
                'start': current_start_index,
                'end': current_start_index + records_on_this_page,
            })

            current_start_index += records_on_this_page
            remaining_records -= records_on_this_page
            total_pages += 1

        return {
            'docids': docids,
            'doc_model': 'iv.attendance.sheet',
            'data': data,
            'docs': sorted_docs,
            'page_splits': page_splits,
            'total_pages': total_pages,
        }
