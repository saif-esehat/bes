from odoo import models , fields,api
import json
import base64
from io import BytesIO
from lxml import etree
from odoo.exceptions import UserError,ValidationError




class RepeaterCandidateApproval(models.Model):
    _name = "repeater.candidate.approval"
    _rec_name = "name"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'Repeater Candidate'
    
    
    candidate_image_name = fields.Char("Candidate Image Name",tracking=True)
    candidate_image = fields.Binary(string='Candidate Image', attachment=True, help='Select an image',tracking=True)
    candidate_signature_name = fields.Char("Candidate Signature",tracking=True)
    candidate_signature = fields.Binary(string='Candidate Signature', attachment=True, help='Select an image',tracking=True)
    name = fields.Char("Full Name of Candidate as in INDOS",required=True,tracking=True)
    course = fields.Selection([
        ('gp', 'GP'),
        ('ccmc', 'CCMC')
    ],string="Course",default='gp',tracking=True)
    indos_no = fields.Char("Indos No.",tracking=True)
    candidate_code = fields.Char("Candidate Code No.",tracking=True)
    institute_id = fields.Many2one("bes.institute",string="Institute",required=True,tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ],string="Gender",default='male',tracking=True)
    email = fields.Char("Email",tracking=True)
    phone = fields.Char("Phone",tracking=True)
    state = fields.Selection([
        ('pending', 'Pending Approval'),
        ('approved', 'Approved')
    ],string="State",default='male',tracking=True)

