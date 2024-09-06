from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
import base64
from io import BytesIO
import xlsxwriter
from datetime import datetime
import xlrd


    
class IVAttendanceSheet(models.Model):
    _name = "iv.attendance.sheet"
    _description= 'IV Attendance Sheet'

    _rec_name = "candidate_name"
    
    candidate_name = fields.Char(string="Candidate Name", store=True)
    
    roll_no = fields.Char(string="Roll No.")
    grade_applied = fields.Char(string="Grade")

    dob = fields.Date(string="Date of Birth")
    
    indos_no = fields.Char(string="INDOs No")

    candidate_signature = fields.Binary(string="Candidate Signature")