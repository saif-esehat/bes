from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
import base64
from io import BytesIO
import xlsxwriter
from datetime import datetime
import xlrd

    
class IVCandidates(models.Model):
    _name = "iv.candidates"
    _description= 'IV Candidate'
    
    name = fields.Char(string="Candidate Name", store=True)
    batch_id = fields.Many2one(
        'iv.batches', 
        string="IV Batch", 
       
    )
    
    ranking_name = fields.Char(string="Name of the Rating’s")
    certificate_no = fields.Char(string="Certificate No.")
    roll_no = fields.Char(string="Roll No.")
    grade_applied = fields.Char(string="Grade")

    dob = fields.Date(string="Date of Birth")
    photo = fields.Binary(string="Candidate Photo")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone Number")
    
    indos_no = fields.Char(string="INDOs No")
    cdc_no = fields.Char(string="CDC No")

    candidate_signature = fields.Binary(string="Candidate Signature")
    # second_day_signature = fields.Binary(string="2nd Day Signature")
    vaccination_rtpcr = fields.Char(string="Vaccination/RTPCR")
    remark = fields.Text(string="Remark")
    examination_date = fields.Date(string="Examination Date")
    certificate_valid_date = fields.Date(string="Certificate Valid Date")
