from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
import base64
from io import BytesIO
import xlsxwriter
from datetime import datetime
import xlrd
import qrcode

    


class CandidatesApplication(models.Model):
    _name = "candidates.application"
    # _rec_name = "batch_name"
    # _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'Candidates Application'

    application_no = fields.Char(string="Application No.")
    roll_no = fields.Char(string="Roll No.")


    candidate_image = fields.Binary(string="Candidate Image")
    candidate_signature = fields.Binary(string="Candidate Signature",attachment=True, help='Select an image')

    competency_deck = fields.Char(string="a) Competency (Deck/Engine)")
    grade = fields.Char(string="b) Grade")
    
    # 2. Details of the Candidate
    name = fields.Char(string="a) Name")
    nationality_id = fields.Many2one('res.country', string="b) Nationality")
    education = fields.Char(string="c) Educational Qualification")
    dob = fields.Date(string="d) Date of Birth")
    place_of_birth = fields.Char(string="e) Place of Birth")
    police_thana = fields.Char(string="Police Thana")
    state_ids = fields.Many2one('res.country.state', string="State")
    district = fields.Char(string="District")
    
    user_id = fields.Many2one("res.users",tracking=True)
    street = fields.Char("Street", tracking=True)
    street2 = fields.Char("Street2", tracking=True)
    city = fields.Char("City", tracking=True)
    zip = fields.Char("Zip", tracking=True)
    state_id = fields.Many2one("res.country.state","State",tracking=True)
    mobile = fields.Char("h) Mobile No.", tracking=True)
    email = fields.Char("g) Email", tracking=True)

    height = fields.Char("a) Height in Centimetres", tracking=True)
    idendification = fields.Char("b) Identification Mark", tracking=True)

    number = fields.Char(string="Number")
    certificate_compentency = fields.Binary(string="Certificate of Compentency")
    grade1 = fields.Char(string="Grade")
    where_issued = fields.Char(string="Where Issued")
    date_of_issue = fields.Date(string="Date of Issue")
    suspended = fields.Char(string="if at any time suspended or cancelled, state by which court authority")
    date = fields.Date(string="Date")
    claus = fields.Char(string="Claus")


   

    language_preference = fields.Selection([
        ('marathi', 'Marathi'),
        ('hindi', 'Hindi'),
        ('english', 'English')
        ], string='Language Preference', default='english')



     # 6) detail of fees payments
    
    upi_no = fields.Char(string="UPI/UTR No.")
    transaction_date = fields.Date(string="Date")
    amount = fields.Float(string="Amount")
    qr_code_image = fields.Binary(string="a) Through UPI",compute="generate_qr_code")

    bord_name = fields.Char(string="Exam Bord Name")
    bank_name = fields.Char(string="Bank Name")
    branch_name = fields.Char(string="Branch Name")
    account_no = fields.Integer(string="Account Number")
    ifsc_code = fields.Char(string="IFSC Code")
    transection_id = fields.Char(string="Transection ID")
    transection_date = fields.Date(string="Date")
    transection_amount = fields.Float(string="Amount")

    # 7)List of documents to be Attached

    self_attched = fields.Binary(string="a) Self-attached copy of previous COC (if any)")
    origanal_se_certi = fields.Binary(string="b) Original Sea Service Certificate")
    original_notarize = fields.Binary(string="c) Original Notarize Affidavite")
    attache_passport = fields.Binary(string="d) Self-attached copy of valid Passport OR Original Police Verification Certificate.")
    attched_educatinal = fields.Binary(string="e) Self-attached copy of Educational Qualification Certificate (Minimum 8th Pass)")
    attched_leaving = fields.Binary(string="f) Self-attached copy of School Leaving Certificate (SLC) OR Birth Certificate")
    attched_photo = fields.Binary(string="g) Self-attached Photo copy of the Residential Address Proof")
    attched_modular = fields.Binary(string="h) Self-attached copies of Modular Safety and Security Courses")
    attched_medical = fields.Binary(string="i) Self-attached valid Medical Certificate")
    attched_id_proof = fields.Binary(string="j) Self-attached photo copy of the ID Proof (Issued by Government)")
    attched_upi = fields.Binary(string="k) UPI/NEFT Payment Receipt")
    attched_driver_certificate = fields.Binary(string="l) Other State Serang/2nd Calss Engine Driver Certificate holder - Original Letter From")
  
    declaration_date = fields.Date(string="Date")
    place = fields.Char(string="Place")
    applicant_signature = fields.Binary(string="Signature of the Applicant")

    # 9 For Assessing Officer's Use

    application_eligible = fields.Selection([
        ('eligible', 'Eligible'),
        ('not_eligible', 'Not Eligible'),
        ], string='Application Eligible / Not Eligible', default='eligible')

    clause1 = fields.Char(string="Clause")
    application_date = fields.Date(string="Application Date")
    signature_bes = fields.Binary(string="Signature Of Assessed Officer BES")


#    10) For Office Staff Use Only
  
    name_of_candidate = fields.Char(string="Name Of the Candidate")
    candidate_roll = fields.Integer(string="Candidate's Roll No.")
    grade_appearing = fields.Char(string="Grade Appearing")

#    11) For Examiner use only
        # part A
    date_written_exam = fields.Date(string="Date Of Written Examination")
    written_exam_pf = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ], string='Written Examination Result', default='pass')

    #  Part B
    date_oral_exam = fields.Date(string="Date Of Oral Examination")
    oral_exam_pf = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ], string='Oral Examination Result', default='pass')

    signature_examiner = fields.Binary(string="Examiner's Signature")
    examiner_date = fields.Date(string="Examiner's Date")

    # 12. For Examination Co-ordinator's Use Only

    candidate_pf = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ], string='I hereby, certify that the particulars contained above are correct The above-named candidate has been Declared FINALLY (Pass or Fail)',
           default='pass')
    coordinater_name = fields.Char(string="Name")
    signature_coordinater = fields.Binary(string="Signature")
    coordinater_date = fields.Date(string="Date (Date of Declaration of Result)")





    @api.onchange('nationality_id')
    def _onchange_nationality_id(self):
        if self.nationality_id:
            return {'domain': {'state_ids': [('country_id', '=', self.nationality_id.id)]}}
        else:
            return {'domain': {'state_ids': []}}

    

    @api.depends('upi_no')  # Replace 'upi_no' with the actual field that you want to encode in the QR code
    def generate_qr_code(self):
        for record in self:
            data = record.upi_no  # Replace 'upi_no' with the actual field name
            if data:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(data)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                qr_image_base64 = base64.b64encode(buffer.getvalue())
                record.qr_code_image = qr_image_base64
            else:
                record.qr_code_image = False