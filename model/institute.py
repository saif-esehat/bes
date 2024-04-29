from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
from datetime import datetime
import random
import string



class Institute(models.Model):
    _name = "bes.institute"
    _description= 'Course Master'
    _rec_name = 'name'
    _inherit = ['mail.thread','mail.activity.mixin']

    code = fields.Char("Code",tracking=True)
    name = fields.Char("Name",tracking=True)
    
    institute_repeater = fields.Boolean("Repeater Institute",tracking=True)
    repeater = fields.Boolean("repeaters",tracking=True)

    email = fields.Char("Email",tracking=True)
    state = fields.Many2one("res.country.state","State",domain=[('country_id.code','=','IN')],tracking=True)
    mti = fields.Char("MTI no.",tracking=True)
    courses = fields.One2many("institute.courses","institute_id","Courses",tracking=True)
    user_id = fields.Many2one("res.users", "Portal User",tracking=True)
    exam_center = fields.Many2one("exam.center", "Exam Region",tracking=True)
    street = fields.Char("Street",tracking=True)
    street2 = fields.Char("Street2",tracking=True)
    city = fields.Char("City",required=True,tracking=True)
    zip = fields.Char("Zip",required=True, validators=[api.constrains('zip')],tracking=True)
    
    principal_name = fields.Char("Name of Principal / Trustee of Training Institute",tracking=True)
    # ,  validators=[api.constrains('principal_phone')]
    principal_phone = fields.Char("Phone No. of Principal / Trustee of Training Institute" )
    principal_mobile = fields.Char("Mobile No. of Principal / Trustee of Training Institute", validators=[api.constrains('principal_mobile')],tracking=True)
    principal_email= fields.Char("E-mail of Principal / Trustee of Training Institute", validators=[api.constrains('principal_email')],tracking=True)
    
    ip_address = fields.Char("IP Address",tracking=True)
    #  validators=[api.constrains('admin_phone')]
    
    admin_phone = fields.Char("Phone No. of Admin Officer of Training Institute",tracking=True)
    admin_mobile = fields.Char("Mobile No. of Admin Officer of Training Institute",  validators=[api.constrains('admin_mobile')],tracking=True)
    admin_email= fields.Char("E-mail of Admin Officer of Training Institute",  validators=[api.constrains('admin_email')],tracking=True)
    
    name_of_second_authorized_person = fields.Char("Name of the second authorised person representing the Institute",tracking=True)
    
    institute_computer_lab = fields.Boolean("Does the institue have inhouse Computer Lab",tracking=True)
    computer_lab_pc_count = fields.Integer("How many PC does the computer Lab Have",tracking=True)
    internet_strength = fields.Char("Strength of Internet connection",tracking=True)
    institute_approved_conduct_stcw = fields.Boolean("Is the Institute Approved to conduct STCW and Security Courses",tracking=True)
    is_lab_used_for_stcw_exit_exam = fields.Boolean("IS the Lab being used for STCW exit exams",tracking=True)
    documents = fields.One2many("lod.institute","institute_id","Documents",tracking=True)

    #------- Faculty
    faculty_ids= fields.One2many('institute.faculty','institute_id',string="Faculty",tracking=True)

    # -------- Payement Slip
    payment_slip_ids= fields.One2many('institute.payment.slip.line','payment_slip_id',string="Payment Slip",tracking=True)

    ccmc_present = fields.Boolean(string='CCMC',compute="_compute_ccmc_present",tracking=True)
    gp_present = fields.Boolean(string='GP',compute="_compute_gp_present",tracking=True)

    @api.depends('courses')
    def _compute_ccmc_present(self):
        for record in self:
            record.ccmc_present = False
            for course in self.courses:
                if course.course.course_code == "CCMC" or course.course.course_code == "ccmc":
                    record.ccmc_present = True
                


    @api.depends('courses')
    def _compute_gp_present(self):
        for record in self:
            record.gp_present = False
            for course in self.courses:
                if course.course.course_code == "GP" or course.course.course_code == "gp":
                    record.gp_present = True
                


            



    # @api.constrains('principal_phone')
    # def _check_valid_phone(self):
    #     for record in self:
    #         # Check if phone has 8 digits
    #         if record.principal_phone and not record.principal_phone.isdigit() or len(record.principal_phone) != 8:
    #             raise ValidationError("Principal Phone number must be 8 digits.")

    @api.constrains('zip')
    def _check_valid_zip(self):
        for record in self:
            if record.zip and not record.zip.isdigit() or len(record.zip) != 6:
                raise ValidationError("Zip code must be 6 digits.")

    @api.constrains('principal_mobile')
    def _check_valid_mobile(self):
        for record in self:
            # Check if mobile has 10 digits
            if record.principal_mobile and not record.principal_mobile.isdigit() or len(record.principal_mobile) != 10:
                raise ValidationError("Principal Mobile number must be 10 digits.")

    @api.constrains('principal_email')
    def _check_valid_email(self):
        for record in self:
            # Check if email has @ symbol
            if record.principal_email and '@' not in record.principal_email:
                raise ValidationError("Invalid Principal email address. Must contain @ symbol.")

    # @api.constrains('admin_phone')
    # def _check_valid_phone(self):
    #     for record in self:
    #         # Check if phone has 8 digits
    #         if record.admin_phone and not record.admin_phone.isdigit() or len(record.admin_phone) != 10:
    #             raise ValidationError("Admin Phone number must be 8 digits.")

    @api.constrains('admin_mobile')
    def _check_valid_mobile(self):
        for record in self:
            # Check if mobile has 10 digits
            if record.admin_mobile and not record.admin_mobile.isdigit() or len(record.admin_mobile) != 10:
                raise ValidationError("Admin Mobile number must be 10 digits.")

    @api.constrains('admin_email')
    def _check_valid_email(self):
        for record in self:
            # Check if email has @ symbol
            if record.admin_email and '@' not in record.admin_email:
                raise ValidationError("Invalid Admin email address. Must contain @ symbol.")

    def open_create_institute_batches_wizard(self):
        # Create a new instance of the wizard
        wizard = self.env['create.institute.batches.wizard'].create({
            'batch_name': '',  # Set default values if needed
        })
        
        # import wdb; wdb.set_trace()
        dgs_batch_id = self.env['dgs.batches'].search([('is_current_batch', '=', True)]).id
        
        if not dgs_batch_id:
            raise ValidationError("Please Create Current DGS Batch")

        # Open the wizard view
        return {
            'name': 'Create Institute Batches',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'create.institute.batches.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                    'default_dgs_batch': dgs_batch_id
                },  
        }

    def _generate_password(self, length=8):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for i in range(length))
    

    @api.model
    def create(self, values):
        institute = super(Institute, self).create(values)
        group_xml_ids = [
            'bes.group_institute',
            'base.group_portal'
            # Add more XML IDs as needed
        ]
        
        group_ids = [self.env.ref(xml_id).id for xml_id in group_xml_ids]

        # group_id = self.env.ref('bes.group_institute')
        user_values = {
            'name': institute.name,
            'login': institute.email,  # You can set the login as the same as the user name
            'password': 12345678,  # Generate a random password
            'sel_groups_1_9_10':9,
            'groups_id':  [(4, group_id, 0) for group_id in group_ids]
        }
 
        portal_user = self.env['res.users'].sudo().create(user_values)
        institute.write({'user_id': portal_user.id})  # Associate the user with the institute
        # import wdb; wdb.set_trace()
        institute_tag = self.env.ref('bes.institute_tag').id
        portal_user.partner_id.write({'email': institute.email,'state_id':institute.state.id,'category_id':[institute_tag]})
        
        principal_contact_values = {
            'type':'contact',
            'name': institute.principal_name,
            'phone': institute.principal_phone,
            'mobile': institute.principal_mobile,
            'email': institute.principal_email,
            'function': 'Principal'
        }
        
        
        contact_partner = self.env['res.partner'].create(principal_contact_values)
    
        # Link the contact partner with the user's partner
        portal_user.partner_id.write({'child_ids': [(4, contact_partner.id)]})
        
        
        # Create a contact under the partner_id
        admin_contact_values = {
            'type':'contact',
            'name': institute.name_of_second_authorized_person,
            'phone': institute.admin_phone,
            'mobile': institute.admin_mobile,
            'email': institute.admin_email,
            'function': 'Office Administrator'
        }
        
        
        contact_partner = self.env['res.partner'].create(admin_contact_values)
    
        # Link the contact partner with the user's partner
        portal_user.partner_id.write({'child_ids': [(4, contact_partner.id)]})
        
        
        

        
        return institute
    
    def faculty_button(self):
        
        return {
        'name': 'Faculty',
        'domain': [('institute_id', '=', self.id)],
        'view_type': 'form',
        'res_model': 'institute.faculty',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        'context': {
            'default_institute_id': self.id    
            }
        }
    
    def ccmc_button(self):
        
        return {
        'name': 'CCMC Batch',
        'domain': [('institute_id', '=', self.id)],
        'view_type': 'form',
        'res_model': 'institute.ccmc.batches',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        'context': {
            'default_institute_id': self.id    
            }
        }
    
    def batch_button(self):
        
        return {
        'name': 'GP Batch',
        'domain': [('institute_id', '=', self.id)],
        'view_type': 'form',
        'res_model': 'institute.gp.batches',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        'context': {
            'default_institute_id': self.id    
            }
        }
    
    def open_faculty_gp(self):
        
        return {
        'name': 'Faculty',
        'domain': [('gp_batches_id', '=', self.id)],
        'view_type': 'form',
        'res_model': 'institute.faculty',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        'context': {
            'default_gp_batches_id': self.id,
            # 'default_gp_or_ccmc_batch': 'gp'    
            }
        }

    def open_faculty_ccmc(self):
        
        return {
        'name': 'Faculty',
        'domain': [('ccmc_batches_id', '=', self.id)],
        'view_type': 'form',
        'res_model': 'institute.faculty',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        'context': {
            'default_ccmc_batches_id': self.id,
            # 'default_gp_or_ccmc_batch': 'gp'    
            }
        }
    


class ListofDcoument(models.Model):
    _name = "lod.institute"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'Institute Document'
    
    institute_id = fields.Many2one("bes.institute","Institute ID",tracking=True)
    document_name = fields.Char("Name of Document",tracking=True)
    upload_date = fields.Date("Upload Date",tracking=True)
    documents_name = fields.Char("Name of Document",tracking=True)
    document_file = fields.Binary(string='Upload Document',tracking=True)



    


class InstituteCourses(models.Model):
    _name = "institute.courses"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'Institute Courses'
    _sql_constraints = [
        ('unique_course_per_institute', 'unique(institute_id, course)', 'Course must be unique per institute.'),
    ]
    institute_id = fields.Many2one("bes.institute","Institute ID",tracking=True)
    course = fields.Many2one("course.master","Course",tracking=True)
    approved_capacity = fields.Integer("Approved Capacity",tracking=True)
    approved_date = fields.Date("Approved Date",tracking=True)


class InstituteFaculty(models.Model):
    _name = "institute.faculty"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'Institute Faculty'
    _rec_name = 'faculty_name'
    
    institute_id = fields.Many2one("bes.institute","Institute ID",tracking=True)
    gp_or_ccmc_batch = fields.Selection([('gp','GP'),('ccmc','CCMC')],string="GP / CCMC",tracking=True)
    gp_batches_id = fields.Many2one('institute.gp.batches',string="Batch",tracking=True)

    ccmc_batches_id = fields.Many2one('institute.ccmc.batches',string="Batch",tracking=True)


    course_name = fields.Many2one("course.master","Course",tracking=True)
    faculty_name = fields.Char(string='Name of the Faculty', required=True,tracking=True)
    faculty_photo = fields.Binary(string='Faculty Photo',tracking=True)
    faculty_photo_name = fields.Char(string="Photo name",tracking=True)
    dob = fields.Date(string='Date of Birth of the Faculty',tracking=True)
    designation = fields.Char(string='Designation of the Faculty',tracking=True)
    qualification = fields.Text(string='Qualification of Faculty',tracking=True)
    contract_terms = fields.Text(string='Contract Terms',tracking=True)
    courses_taught = fields.Many2many('course.master', string='Courses Being Taught',tracking=True)

    # @api.model
    # def create(self, values):
    #     gp_faculty = super(InstituteFaculty, self).create(values)
    #     self.gp_batches_id.write({'model_id':self.id})
    #     return gp_faculty

class InstitutePaymentSlip(models.Model):
    _name = "institute.payment.slip.line"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'Institute Payment Slip'
    
    payment_slip_id = fields.Many2one("bes.institute","Payment Slip ID",tracking=True)

    sr_no = fields.Integer(string="Sr.No.",readonly=True, copy=False,default="1",tracking=True)
    name_of_payment = fields.Char('Name Of The Payment',tracking=True)
    pay_method = fields.Selection([('1','Cheque'),('2','Bank Draft'),('3','Cash'),('4','UPI')],string='Payment Method',tracking=True)
    pay_date = fields.Date(string="Payment Date",tracking=True) 
    invoice_generated = fields.Boolean(string="Invoice Generated and Sent",tracking=True)
    invoice_number = fields.Char("Invoice Number",tracking=True)
    invoive_date = fields.Date(string="Invoice Date",tracking=True)




    
    

    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('payment_slip_id'):
            existing_records = self.search([('payment_slip_id', '=', vals['payment_slip_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(InstitutePaymentSlip, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1  

    
    
    

