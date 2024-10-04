from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
import base64
from io import BytesIO
import xlsxwriter
from datetime import datetime
import xlrd

    
class SepCandidates(models.Model):
    _name = "sep.candidates"
    _description= 'Sep Candidate'
    
    name = fields.Char(string="Sep Candidate", store=True)
    batch_id = fields.Many2one(
        'sep.batches', 
        string="Sep Batch", 
       
    )
    certificate_no = fields.Char(string="Certificate No.")

    dob = fields.Date(string="Date of Birth")
    photo = fields.Binary(string="Candidate Photo")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone Number")
    
    indos_no = fields.Char(string="INDOs No")
    cdc_no = fields.Char(string="CDC No")

    first_day_signature = fields.Binary(string="1st Day Signature")
    second_day_signature = fields.Binary(string="2nd Day Signature")
    vaccination_rtpcr = fields.Char(string="Vaccination/RTPCR")
    remark = fields.Text(string="Remark")


class SepCandidateCertificate(models.AbstractModel):
    _name = 'report.bes.report_sep_candidate_certificate'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs1 = self.env['sep.candidates'].sudo().browse(docids)
        
        return {
            'docids': docids,
            'doc_model': 'sep.candidates',
            'data': data,
            'docs': docs1
        }
        
   