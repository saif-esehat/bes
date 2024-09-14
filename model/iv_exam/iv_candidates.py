from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
import base64
from io import BytesIO
import xlsxwriter
from datetime import datetime
import xlrd
import logging

_logger = logging.getLogger(__name__)


    
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
    grade_applied = fields.Selection([
        ('1CM', 'First Class Master'),
        ('2CM', 'Second Class Master'),
        ('SER', 'Serang'),
        ('ME', 'Motor Engineer'),
        ('1ED', 'First Class Engine Driver'),
        ('2ED', 'Second Class Engine Driver'),

        ], string='Grade')

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


    candidate_applications = fields.One2many('candidate.applications.line','candidate_id',string="Candidate Applications")



    # @api.constrains('certificate_valid_date')
    # def _check_certificate_valid_date(self):
    #     for record in self:
    #         if not record.certificate_valid_date:
    #             raise ValidationError("The Certificate Valid Date must be filled.")

    @api.constrains('batch_id')
    def _check_batch_id(self):
        for record in self:
            if not record.batch_id:
                raise ValidationError("The Batch must be filled.")


    @api.constrains('dob')
    def _check_dob(self):
        for record in self:
            if not record.dob:
                raise ValidationError("DOB must be filled.")

    # @api.constrains('examination_date')
    # def _check_examination_date(self):
    #     for record in self:
    #         if not record.examination_date:
    #             raise ValidationError("Examination date must be filled.")
            
    def open_written_exams(self):
        candidate_id = self.env['iv.written.exam'].sudo().search([('candidate.id','=',self.id)]).id  # Replace with the actual ID of the record you want to open

        candidate = self.env['iv.written.exam'].browse(candidate_id)
        # import wdb; wdb.set_trace(); 


        if candidate:
            # Open the record in a form view
            
        
            return {
                'name': 'Written Exams',
                'domain': [('candidate.id', '=', self.id)],
                'view_type': 'form',
                'res_model': 'iv.written.exam',
                'view_id': False,
                'view_mode': 'tree,form',
                'type': 'ir.actions.act_window'
            }
        else:
            raise ValidationError("No Records Found")
       

    def open_oral_exams(self):
        candidate_id = self.env['iv.oral.exam'].sudo().search([('candidate.id','=',self.id)]).id  # Replace with the actual ID of the record you want to open

        candidate = self.env['iv.oral.exam'].browse(candidate_id)
        # import wdb; wdb.set_trace(); 


        if candidate:
            # Open the record in a form view
            
        
            return {
                'name': 'Oral Exams',
                'domain': [('candidate.id', '=', self.id)],
                'view_type': 'form',
                'res_model': 'iv.oral.exam',
                'view_id': False,
                'view_mode': 'tree,form',
                'type': 'ir.actions.act_window'
            }
        else:
            raise ValidationError("No Records Found")
    
    
    def action_print_bulk_allotment(self):
        # Logic to handle the printing of bulk allotment data
        return self.env.ref('bes.reports_iv_written_attendance').report_action(self)



class IVCanditateIssuanceAdmitCard(models.AbstractModel):
    _name = 'report.bes.reports_iv_candidate_issuance_admit_card_list'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    @api.model
    def _get_report_values(self, docids, data=None):
        # Get the records
        docs = self.env['iv.candidates'].sudo().browse(docids)
        
        # Define the order of grades
        grade_order = ['1CM', '2CM', 'SER', 'ME', '1ED', '2ED']
        
        # Sort the records based on the grade_applied field
        sorted_docs = docs.sorted(
            key=lambda r: grade_order.index(r.grade_applied) if r.grade_applied in grade_order else len(grade_order)
        )

        return {
            'docids': docids,
            'doc_model': 'iv.candidates',
            'data': data,
            'docs': sorted_docs,  # Sorted by grade order
        }

class CandidateApplicationLine(models.Model):
    _name = 'candidate.applications.line'

    candidate_id = fields.Many2one('iv.candidates',string="Candidate")

    application_id = fields.Many2one('candidates.application',string="Application")