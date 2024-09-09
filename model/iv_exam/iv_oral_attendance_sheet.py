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
    
    candidate_name = fields.Char(string="Candidate Name", store=True)
    
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
    class_no = fields.Char(string="Class Room: No.")



class IVWrittenAttendance(models.AbstractModel):
    _name = 'report.bes.reports_iv_oral_attendance1'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['iv.oral.attendance.sheet'].sudo().browse(docids)
        
        
        return {
            'docids': docids,
            'doc_model': 'iv.oral.attendance.sheet',
            'data': data,
            'docs': docs,
        }

