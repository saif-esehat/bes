from odoo import api, fields, models , _, exceptions
from odoo.exceptions import UserError,ValidationError
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import datetime 


class CandidateUserInactiveWizard(models.TransientModel):
    _name = 'candidate.inactive.wizard'
    _description = 'Candidate Inactive Wizard'

    inactivation_reason = fields.Text(string='Inactivation Reason')
    
    
    def inactivate_user(self):
        # import wdb; wdb.set_trace();
        record_id = self.env.context.get('active_id')
        active_model = self.env.context.get('active_model')
        
        user_id = self.env.context.get('user_id')
        user = self.env['res.users'].sudo().search([('id','=',user_id)])
        user.write({
            'active':False
        })
        parent_record = self.env[active_model].browse(record_id)
        parent_record.message_post(body=self.inactivation_reason)

        


class GPCandidate(models.Model):
    _name = 'gp.candidate'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'GP Candidate'
    
    institute_batch_id = fields.Many2one("institute.gp.batches","Pre Sea Institute Batch",tracking=True)
    dgs_batch = fields.Many2one("dgs.batches",string="Exam Batch",related="institute_batch_id.dgs_batch",store=True)

    institute_id = fields.Many2one("bes.institute",string="Name of Institute",tracking=True)
    previous_repeater = fields.Boolean(string='Previous Attempted')
    candidate_image_name = fields.Char("Candidate Image Name",tracking=True)
    candidate_image = fields.Binary(string='Candidate Image', attachment=True, help='Select an image',tracking=True)
    candidate_signature_name = fields.Char("Candidate Signature",tracking=True)
    candidate_signature = fields.Binary(string='Candidate Signature', attachment=True, help='Select an image',tracking=True)
    name = fields.Char("Full Name of Candidate as in INDOS",required=True,tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ],string="Gender",default='male',tracking=True)
    age = fields.Float("Age",compute="_compute_age",tracking=True)
    indos_no = fields.Char("Indos No.",tracking=True)
    candidate_code = fields.Char("GP Candidate Code No.",tracking=True)
    roll_no = fields.Char("Roll No.",tracking=True,compute="_update_rollno")
    dob = fields.Date("DOB",help="Date of Birth", 
                      widget="date", 
                      date_format="%d-%b-%y",tracking=True)
    user_id = fields.Many2one("res.users", "Portal User",tracking=True)
    street = fields.Char("Street",tracking=True)
    street2 = fields.Char("Street2",tracking=True)
    city = fields.Char("City",tracking=True)
    zip = fields.Char("Zip", validators=[api.constrains('zip')],tracking=True)
    state_id = fields.Many2one("res.country.state","State",domain=[('country_id.code','=','IN')],tracking=True)
    phone = fields.Char("Phone",tracking=True)
    mobile = fields.Char("Mobile", validators=[api.constrains('mobile')],tracking=True)
    email = fields.Char("Email", validators=[api.constrains('email')],tracking=True)
    eighth_percent = fields.Boolean("8th Std Passed",tracking=True)
    tenth_percent = fields.Integer("% Xth Std in Eng.",tracking=True)
    twelve_percent = fields.Integer("% 12th Std in Eng.",tracking=True)
    iti_percent = fields.Integer("% ITI",tracking=True)
    sc_st = fields.Selection([
        ('general','General'),
        ('sc','SC'),
        ('st','ST'),
        ('obc','OBC')
    ],default='general',string="To be mentioned if SC /ST /OBC",tracking=True)
    ship_visits_count = fields.Char("No. of Ship Visits",tracking=True)
    exam_region = fields.Many2one("exam.center",string="Exam Region",store=True,related="institute_id.exam_center",tracking=True)

    elligiblity_criteria = fields.Selection([
        ('elligible', 'Elligible'),
        ('not_elligible', 'Not Elligible')
    ],string="Elligiblity Criteria", default='not_elligible',tracking=True)
    
    fees_paid = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ],string="Fees Paid by Institute", default='no',tracking=True)
    
    fees_paid_candidate = fields.Char("Fees Paid by Candidate",tracking=True,compute="_fees_paid_by_candidate")
    black_listed = fields.Boolean("Black Listed",tracking=True)

    def _fees_paid_by_candidate(self):
        for rec in self:
            last_exam = self.env['gp.exam.schedule'].search([('gp_candidate','=',rec.id)], order='attempt_number desc', limit=1)
            last_exam_dgs_batch = last_exam.dgs_batch.id
            invoice = self.env['account.move'].sudo().search([('repeater_exam_batch','=',last_exam_dgs_batch),('gp_candidate','=',rec.id)],order='date desc')
            if invoice:
                batch = invoice.repeater_exam_batch.to_date.strftime("%B %Y")
                if invoice.payment_state == 'paid':
                    rec.fees_paid_candidate = batch + ' - Paid'
                else:
                    rec.fees_paid_candidate = batch + ' - Not Paid'
            else:
                rec.fees_paid_candidate = 'No Fees Paid'
            
            
            
    
    invoice_no = fields.Char("Invoice No",compute="_compute_invoice_no",store=True,tracking=True)
    batch_exam_registered = fields.Boolean("Batch Registered",tracking=True)
    invoice_generated = fields.Boolean("Invoice Generated")
    qualification = fields.Selection([
        ('eight', '8th std'),
        ('tenth', '10th std'),
        ('twelve', '12th std'),
        ('iti', 'ITI')
    ],string="Qualification", default='tenth',tracking=True)

    candidate_attendance_record = fields.Integer("Candidate Attendance Record",tracking=True)
    
    
    attendance_compliance_1 = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ],string="Whether Attendance record of the candidate comply with DGS training circular 1 of 2018 as per para 3.2 for GP / 7 of 2010 as per para 3.3 for CCMC (YES/ NO)", default='no',tracking=True)
    
    attendance_compliance_2 = fields.Selection([
         ('yes', 'Yes'),
         ('no', 'No'),
         ('na', 'N/A')
    ], string="Attendance record of the candidate not comply with DGS training circular 1 of 2018 as per para 3.2 for GP / 7 of 2010 as per para 3.3 for CCMC and whether same has been informed to the DGS (YES/ NO)", default='no',tracking=True)

    stcw_certificate = fields.One2many("gp.candidate.stcw.certificate","candidate_id",string="STCW Certificate",tracking=True)
    
    
    # attendance_compliance_2 = fields.Boolean([
    #     ('yes', 'Yes'),
    #     ('no', 'No')
    # ],string="Attendance record of the candidate not comply with DGS Guidelines 1 of 2018 as per para 3.2 for GP / 7 of 2010 as per para 3.3 for CCMC and whether same has been informed to the DGS (YES/ NO)", default='no')
    
    ship_visited = fields.Boolean("Ship Visited",tracking=True)
    ship_visits = fields.One2many("gp.candidate.ship.visits","candidate_id",string="Ship Visit",tracking=True)
    
    
    ## Mek and GSK Online Exam
    mek_online = fields.One2many("survey.user_input","gp_candidate",domain=[("survey_id.subject.name", "=", 'GSK')],string="MEK Online",tracking=True)
    gsk_online = fields.One2many("survey.user_input","gp_candidate",domain=[("survey_id.subject.name", "=", 'MEK')],string="GSK Online",tracking=True)
    
    # @api.constrains('institute_batch_id')
    # def _check_record_number_constraint(self):
    #     for record in self:
    #         capacity = record.institute_batch_id.dgs_approved_capacity
    #         self.env["gp.candidate"].sudo().search_count([('institute_batch_id','=',)])
           
    user_state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], string='User Status',compute="_compute_user_state",store=True,default="inactive",tracking=True)
    
    stcw_criteria = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Complied'),
    ], string='STCW Criteria',store=True,compute="_check_stcw_certificate")

    ship_visit_criteria = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Complied'),
    ], string='Ship Visit Criteria',store=True ,compute='_check_ship_visit_criteria')

    attendance_criteria = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Complied'),
    ], string='Attendance Criteria',store=True,compute="_check_attendance_criteria")
    
    candidate_image_status = fields.Selection([
        ('pending', 'Pending'),
        ('done', 'Done'),
    ],string="Candidate-Image",store=True,default="pending",compute="_check_image")
   
    candidate_signature_status = fields.Selection([
        ('pending', 'Pending'),
        ('done', 'Done'),

    ],string="Candidate-Sign",store=True,default="pending",compute="_check_sign")

    candidate_user_invoice_criteria = fields.Boolean('Criteria',compute= "_check_criteria",store=True)
    gp_exam = fields.Many2many("gp.exam.schedule",string="Exam",tracking=True)
    result_status = fields.Selection([
        ('absent','Absent'),
        ('pending','Pending'),
        ('failed','Failed'),
        ('passed','Passed'),
    ],string='Result',tracking=True,related="gp_exam.result_status")

    withdrawn_state =  fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='User Withdrawn',default="no",tracking=True)
    
    exam_registered = fields.Boolean("Exam Registered")

    withdrawn_reason = fields.Char("Withdraw Reason",tracking=True)
    ceo_override = fields.Boolean("CEO Override",default=False,tracking=True)

    edit_profile_status = fields.Boolean('edit_marksheet_status',compute='_compute_is_in_group',store=False)

    @api.depends('fees_paid')
    def _compute_is_in_group(self):
        for record in self:
            user = self.env.user
            # import wdb; wdb.set_trace()
            # Check if user belongs to the group
            has_group_access = user.has_group('bes.group_expense_approval_ceo')
            if record.fees_paid != 'yes':
                # Editable for all users if fees_paid is not 'yes'
                record.edit_profile_status = True
            else:
                # Editable only if the user has group access
                record.edit_profile_status = has_group_access



    def action_ceo_overriden(self):
        for record in self:
            record.ceo_override = not record.ceo_override
            record._check_stcw_certificate()
            record._check_ship_visit_criteria()
            record._check_attendance_criteria()

    @api.depends('candidate_signature_status','candidate_image_status','indos_no')
    def _check_criteria(self):
        for record in self:
            # candidate_image
            if record.candidate_image_status == 'done' and record.candidate_signature_status == 'done' and record.indos_no:
                record.candidate_user_invoice_criteria = True
            else:
                record.candidate_user_invoice_criteria = False



    @api.depends('gp_exam')
    def _update_rollno(self):
        # import wdb; wdb.set_trace();
        for record in self:
            # Initialize roll_no to None
            record.roll_no = None
            # Get the latest exam attempt record for the current candidate
            last_exam_record = self.env['gp.exam.schedule'].search(
                [('gp_candidate', '=', record.id)],
                order='attempt_number desc',
                limit=1
            )

            if last_exam_record:
                # Check if the latest exam attempt is certified
                if last_exam_record.state == "3-certified":
                    record.roll_no = last_exam_record.exam_id
                else:
                    # Set roll_no to the latest attempt's exam_id even if not certified
                    record.roll_no = last_exam_record.exam_id

    @api.depends('candidate_image')
    def _check_image(self):
        for record in self:
            
            
            # candidate_image
            if record.candidate_image:
                
                
                record.candidate_image_status = 'done'
            else:
                record.candidate_image_status = 'pending'

    @api.depends('candidate_signature')
    def _check_sign(self):
        for record in self:
            # candidate-sign
            if record.candidate_signature:
                record.candidate_signature_status = 'done'
            else:
                record.candidate_signature_status = 'pending'



    @api.depends('user_id.active')
    def _compute_user_state(self):
        for record in self:
            if record.user_id and record.user_id.active:
                record.user_state = "active"
            else:
                record.user_state = "inactive"

    @api.constrains('zip')
    def _check_valid_zip(self):
        for record in self:
            if record.zip and not record.zip.isdigit() or len(record.zip) != 6:
                raise ValidationError("Zip code must be 6 digits.")

    def check_combination_exists(self,array):
        
        target_combinations = [['pst', 'efa', 'fpff', 'pssr', 'stsdsd'], ['bst', 'stsdsd']]
        
        for combination in target_combinations:
            if all(item in array for item in combination):
                return True
        
        return False

    @api.depends('stcw_certificate')
    def _check_stcw_certificate(self):
         for record in self:
            # Retrieve all the STCW certificate records
            stcw_certificates = record.stcw_certificate
            course_type_already  = [course.course_name for course in record.stcw_certificate]
            gp_exam_count = self.env['gp.exam.schedule'].sudo().search_count([('gp_candidate','=',record.id)])          

            all_types_exist = record.check_combination_exists(course_type_already)

            all_cert_nos_present = all(cert.candidate_cert_no for cert in stcw_certificates)
            if all_types_exist and all_cert_nos_present or record.ceo_override:
                record.stcw_criteria = 'passed'
            else:
                record.stcw_criteria = 'pending'
        
    
    @api.depends('ship_visits')
    def _check_ship_visit_criteria(self):
        for record in self:
            # import wdb; wdb.set_trace();
            if len(record.ship_visits) > 0 or record.ceo_override:
                record.ship_visit_criteria = 'passed'
            else:
                record.ship_visit_criteria = 'pending'
    
    
    @api.depends('attendance_compliance_1','attendance_compliance_2')
    def _check_attendance_criteria(self):
       for record in self:
            if record.attendance_compliance_1 == 'yes' or record.attendance_compliance_2 == 'yes' or record.ceo_override:
                record.attendance_criteria = 'passed'
            else:
                record.attendance_criteria = 'pending'


    @api.constrains('email')
    def _check_valid_email(self):
        for record in self:
            # Check if email has @ symbol
            if record.email and '@' not in record.email:
                raise ValidationError("Invalid email address. Must contain @ symbol.")

    def user_inactive(self):
        
        user_id = self.user_id.id
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Candidate Inactivation Form',
            'res_model': 'candidate.inactive.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('bes.candidate_inactive_wizard_id').id,
            'target': 'new',
            'context': {
                "user_id":user_id
                },
        }
        # self.user_id.sudo().write({
        #     'active':False
        # })

    def user_active(self):
        self.user_id.sudo().write({
            'active':True
        })

    def open_register_for_exam_wizard(self):
        view_id = self.env.ref('bes.candidate_gp_register_exam_wizard').id
                
        last_exam_record = self.env['gp.exam.schedule'].search([('gp_candidate','=',self.id)], order='attempt_number desc', limit=1)
        
        current_dgs_batch  = self.env['dgs.batches'].search([('is_current_batch', '=', True)]).id

        
        if len(last_exam_record) <= 0:
            raise ValidationError("No previous Exam Found . This Candidate Must be registered through batches")
        
        if last_exam_record.state == '1-in_process':
            raise ValidationError("Last Exam Still In Process")

        # import wdb;wdb.set_trace()
        
        exam_month = self.detect_current_month()
        
        if exam_month == 'dec_feb' or exam_month== 'jul_aug':
            institute_ids = self.env["bes.institute"].search([('institute_repeater','=',True)]).ids
        else:
            institute_ids = []
        
        
        return {
            'name': 'Register For Exam',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'candidate.gp.register.exam.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
            # 'default_batches_id': self.id
            'default_candidate_id': self.id,
            'default_gp_exam': last_exam_record.id,
            'default_previous_attempt': last_exam_record.attempt_number,
            "default_gsk_oral_prac_status": last_exam_record.gsk_oral_prac_status,
            "default_mek_oral_prac_status": last_exam_record.mek_oral_prac_status,
            "default_mek_online_status": last_exam_record.mek_online_status,
            "default_gsk_online_status":last_exam_record.gsk_online_status,
            "default_exam_month" : self.detect_current_month(),
            "default_dgs_batch" : current_dgs_batch,
            "default_institute_ids" : institute_ids
            }
        }
        
    @api.depends('dob')
    def _compute_age(self):
        for record in self:
            if record.dob:
                birthdate = datetime.datetime.strptime(str(record.dob), '%Y-%m-%d').date()
                today = datetime.datetime.now().date()
                delta = today - birthdate
                record.age = delta.days // 365
            else:
                record.age = 0
    
    
    def detect_current_month(self):
    # Get the current month as an integer (1 for January, 2 for February, etc.)
        current_month = datetime.datetime.now().month
        
        # Define the month ranges
        winter_months = [12, 1, 2]
        spring_months = [3, 4, 5, 6]
        summer_months = [7, 8]
        fall_months = [9, 10, 11]

        # Check which range the current month falls into
        if current_month in winter_months:
            return "dec_feb"
        elif current_month in spring_months:
            return "mar_jun"
        elif current_month in summer_months:
            return "jul_aug"
        elif current_month in fall_months:
            return "sep_nov"
        else:
            return "Invalid month."

    
    
    
    def open_gp_candidate_exams(self):
        
        
        
        return {
                    'name': _('GP Exam'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'gp.exam.schedule',
                    'type': 'ir.actions.act_window',
                    'view_id': False,
                    'target': 'current',
                    'domain': [('gp_candidate', '=', self.id)],
                    'context':{
                        'default_gp_candidate': self.id    
                     }
                }
    
    def open_add_marksheet(self):
        
        
        
        return {
                    'name': _('Add Marksheet'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'gp.marksheet.creation.wizard',
                    'type': 'ir.actions.act_window',
                    'view_id': False,
                    'target': 'new'
                }
    
    # @api.model
    def unlink(self):
        # users_to_delete = self.mapped('user_id')
        # print
        if self.user_id:
            self.user_id.unlink()
        result = super(GPCandidate, self).unlink()
        
        
        return result



    
    
    @api.model
    def create(self, values):
        # import wdb; wdb.set_trace()
        institute_batch_id  = int(values['institute_batch_id'])

        gp_batches = self.env["institute.gp.batches"].search([('id','=',institute_batch_id)])
        # gp_batches = self.institute_batch_id
        
        capacity = gp_batches.dgs_approved_capacity - 1
        # capacity = gp_batches.dgs_approved_capacity 
        
        candidate_count = self.env["gp.candidate"].sudo().search_count([('institute_batch_id','=',institute_batch_id)])  
       
        if candidate_count <= capacity:
            if values["dob"]:
                birthdate = datetime.datetime.strptime(str(values["dob"]), '%Y-%m-%d').date()
                today = datetime.datetime.now().date()
                delta = today - birthdate
                values['age'] = delta.days // 365
            else:
                values['age'] = 0
            gp_candidate = super(GPCandidate, self).create(values)
        else:
            raise ValidationError("DGS approved Capacity Exceeded")
        
        ### Comment Out for enable Login creation automatically
        
        # group_xml_ids = [
        #     'bes.group_gp_candidates',
        #     'base.group_portal'
        # ]
        
        # group_ids = [self.env.ref(xml_id).id for xml_id in group_xml_ids]
        
        # user_values = {
        #     'name': gp_candidate.name,
        #     'login': gp_candidate.indos_no,  # You can set the login as the same as the user name
        #     'password': 12345678,  # Generate a random password
        #     'sel_groups_1_9_10':9,
        #     'groups_id':  [(4, group_id, 0) for group_id in group_ids]
        # }

        # portal_user = self.env['res.users'].sudo().create(user_values)
        # gp_candidate.write({'user_id': portal_user.id})  # Associate the user with the institute
        # # import wdb; wdb.set_trace()
        # candidate_tag = self.env.ref('bes.candidates_tags').id
        # portal_user.partner_id.write({'email': gp_candidate.email,'phone':gp_candidate.phone,'mobile':gp_candidate.mobile,'street':gp_candidate.street,'street2':gp_candidate.street2,'city':gp_candidate.city,'zip':gp_candidate.zip,'state_id':gp_candidate.state_id.id,'category_id':[candidate_tag]})
        
        return gp_candidate


    @api.depends('fees_paid')
    def _compute_invoice_no(self):
        for candidate in self:
            if candidate.fees_paid == 'yes':
                candidate.invoice_no = candidate.institute_batch_id.account_move.name
            else:
                candidate.invoice_no = ''    
    
    
    @api.depends('name', 'age', 'indos_no', 'candidate_code', 'roll_no', 'dob', 'street', 'street2',
                 'city', 'zip', 'state_id', 'phone', 'mobile', 'email', 'sc_st', 'qualification','tenth_percent','twelve_percent','iti_percent')
    def _compute_eligibility(self):
        for candidate in self:
            # candidate.elligibility_criteria = 'not_elligible'
            # Check if all the fields are filled
            # import wdb; wdb.set_trace()
            all_fields_filled = all([candidate.name, candidate.age, candidate.indos_no, candidate.candidate_code, candidate.roll_no,
                    candidate.dob, candidate.street, candidate.street2, candidate.city, candidate.zip,
                    candidate.state_id, candidate.phone, candidate.mobile, candidate.email, candidate.sc_st,
                    candidate.qualification])

            if all_fields_filled:
                # import wdb; wdb.set_trace()
                if candidate.qualification == 'tenth' and candidate.tenth_percent > 40 or candidate.qualification == 'twelve' and candidate.twelve_percent > 40 or candidate.qualification == 'iti' and candidate.iti_percent > 50:
                   candidate.elligiblity_criteria = 'elligible'                
                else:
                   candidate.elligiblity_criteria = 'not_elligible'
            else:
                candidate.elligiblity_criteria = 'not_elligible'       
    
    
    

    # MEK Practical

    mek_practical_child_line = fields.One2many("gp.mek.practical.line","mek_parent",string="MEK Practical")
                    
    # MEK ORAL

    mek_oral_child_line = fields.One2many("gp.mek.oral.line","mek_oral_parent",string="MEK Oral")


    # GSK Practical

    gsk_practical_child_line = fields.One2many("gp.gsk.practical.line","gsk_practical_parent",string="GSK Practical")

    
    # GSK Oral

    gsk_oral_child_line = fields.One2many("gp.gsk.oral.line","gsk_oral_parent",string="GSK Oral")
        

class GPSTCWCandidate(models.Model):
    _name = 'gp.candidate.stcw.certificate'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'STCW'
    
    candidate_id = fields.Many2one("gp.candidate","Candidate",tracking=True)

    course_name =  fields.Selection([
        ('pst', 'PST'),
        ('efa', 'EFA'),
        ('fpff', 'FPFF'),
        ('pssr', 'PSSR'),
        ('stsdsd', 'STSDSD'),
        ('bst', 'BST')
    ],string="Course",tracking=True)
    institute_name = fields.Many2one("bes.institute","Institute Name",tracking=True)
    other_institute = fields.Char("Other Institute Name",tracking=True)
    marine_training_inst_number = fields.Char("MTI Number",tracking=True)
    mti_indos_no = fields.Char("Indos No.",tracking=True)
    candidate_cert_no = fields.Char("Candidate Certificate Number",tracking=True)
    course_start_date = fields.Date(string="Course Start Date",tracking=True)
    course_end_date = fields.Date(string="Course End Date",tracking=True)
    file_name = fields.Char('File Name',tracking=True)
    certificate_upload = fields.Binary("Certificate Upload",tracking=True)
    






    

class GPCandidateShipVisits(models.Model):
    _name = 'gp.candidate.ship.visits'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'GP Ship Visits'
    
    institute_batch_id = fields.Many2one("institute.gp.batches","Batch",related="candidate_id.institute_batch_id",tracking=True)
    ship_visit_id = fields.Many2one("gp.batches.ship.visit",string="Ship Visit",tracking=True)
    
    dgs_batch = fields.Many2one("dgs.batches",string="Exam Batch",related="candidate_id.institute_batch_id.dgs_batch",store=True)
    institute = fields.Many2one("bes.institute",string="Name of Institute",related="candidate_id.institute_id",store=True,tracking=True)
    institute_code = fields.Char(string="Code No.",related="institute.code",store=True)
    candidate_count = fields.Integer("Number of Candidates",related="institute_batch_id.admit_card_alloted",tracking=True)
    exam_region = fields.Many2one("exam.center",string="Exam Region",store=True,related="institute.exam_center",tracking=True)
    candidate_id = fields.Many2one("gp.candidate","Candidate",tracking=True)
    name_of_ships = fields.Char("Name of  the Ship Visited / Ship in Campus",tracking=True)
    imo_no = fields.Char("Ship IMO Number",tracking=True)
    name_of_ports_visited = fields.Char("Name of the Port Visited / Place of SIC",tracking=True)
    date_of_visits = fields.Date("Date Of Visit",tracking=True)
    time_spent_on_ship = fields.Float("Hours",tracking=True)
    bridge = fields.Boolean("Bridge",tracking=True)
    eng_room = fields.Boolean("Eng. Room",tracking=True)
    cargo_area = fields.Boolean("Cargo Area",tracking=True)
    
    
    
    

class CCMCCandidate(models.Model):
    _name = 'ccmc.candidate'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'CCMC Candidate'
    
    institute_batch_id = fields.Many2one("institute.ccmc.batches","Pre Sea Institute Batch",tracking=True)
    dgs_batch = fields.Many2one("dgs.batches",string="Exam Batch",related="institute_batch_id.dgs_batch",store=True)
    institute_id = fields.Many2one("bes.institute",string="Name of Institute",required=True,tracking=True)
    candidate_image_name = fields.Char("Candidate Image Name",tracking=True)
    candidate_image = fields.Binary(string='Candidate Image', attachment=True, help='Select an image in JPEG format.',tracking=True)
    candidate_signature_name = fields.Char("Candidate Signature",tracking=True)
    candidate_signature = fields.Binary(string='Candidate Signature', attachment=True, help='Select an image',tracking=True)
    previous_repeater = fields.Boolean(string='Previous Attempted')
    name = fields.Char("Full Name of Candidate as in INDOS",required=True,tracking=True)
    gender = fields.Selection([
        ('male','Male'),
        ('female','Female')
    ],string="Gender",default='male',tracking=True)
    invoice_generated = fields.Boolean("Invoice Generated")
    user_id = fields.Many2one("res.users", "Portal User",tracking=True)    
    age = fields.Float("Age",compute="_compute_age",tracking=True)
    indos_no = fields.Char("Indos No.",tracking=True)
    candidate_code = fields.Char("CCMC Candidate Code No.",tracking=True)
    roll_no = fields.Char("Roll No.",tracking=True,compute="_update_rollno")
    dob = fields.Date("DOB",help="Date of Birth", 
                      widget="date", 
                      date_format="%d-%b-%y",tracking=True)
    
    street = fields.Char("Street",tracking=True)
    street2 = fields.Char("Street2",tracking=True)
    city = fields.Char("City",tracking=True)
    zip = fields.Char("Zip", validators=[api.constrains('zip')],tracking=True)
    state_id = fields.Many2one("res.country.state","State",domain=[('country_id.code','=','IN')],tracking=True)
    phone = fields.Char("Phone", validators=[api.constrains('phone')],tracking=True)
    mobile = fields.Char("Mobile", validators=[api.constrains('mobile')],tracking=True)
    email = fields.Char("Email", validators=[api.constrains('email')],tracking=True)
    eighth_percent = fields.Boolean("8th Std Passed",tracking=True)
    tenth_percent = fields.Char("% Xth Std in Eng.",tracking=True)
    twelve_percent = fields.Char("% 12th Std in Eng.",tracking=True)
    iti_percent = fields.Char("% ITI",tracking=True)
    sc_st = fields.Selection([
        ('general','General'),
        ('sc','SC'),
        ('st','ST'),
        ('obc','OBC')
    ],default='general',string="To be mentioned if SC /ST /OBC",tracking=True)
    
    ship_visits_count = fields.Char("No. of Ship Visits",tracking=True)
    ccmc_exam = fields.Many2many("ccmc.exam.schedule",string="Exam",tracking=True)
    qualification = fields.Selection([
        ('eight', '8th std'),
        ('tenth', '10th std'),
        ('twelve', '12th std'),
        ('iti', 'ITI')
    ],string="Qualification", default='tenth',tracking=True)
    
    batch_exam_registered = fields.Boolean("Batch Registered",tracking=True)
    exam_region = fields.Many2one("exam.center",string="Exam Region",store=True,related="institute_id.exam_center",tracking=True)
    
    candidate_attendance_record = fields.Integer("Candidate Attendance Record",tracking=True)
    
    elligiblity_criteria = fields.Selection([
        ('elligible', 'Elligible'),
        ('not_elligible', 'Not Elligible')
    ],string="Elligiblity Criteria", default='not_elligible',tracking=True)
    
    
    attendance_compliance_1 = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ],string="Whether Attendance record of the candidate comply with DGS training circular 1 of 2018 as per para 3.2 for GP / 7 of 2010 as per para 3.3 for CCMC (YES/ NO)", default='no',tracking=True)
    
    attendance_compliance_2 = fields.Selection([
         ('yes', 'Yes'),
         ('no', 'No'),
         ('na', 'N/A')
    ], string="Attendance record of the candidate not comply with DGS training circular 1 of 2018 as per para 3.2 for GP / 7 of 2010 as per para 3.3 for CCMC and whether same has been informed to the DGS (YES/ NO)", default='no',tracking=True)

    stcw_certificate = fields.One2many("ccmc.candidate.stcw.certificate","candidate_id",string="STCW Certificate",tracking=True)
    
    # attendance_compliance_2 = fields.Boolean([
    #     ('yes', 'Yes'),
    #     ('no', 'No')
    # ],string="Attendance record of the candidate not comply with DGS Guidelines 1 of 2018 as per para 3.2 for GP / 7 of 2010 as per para 3.3 for CCMC and whether same has been informed to the DGS (YES/ NO)", default='no')
    
        # Ship Visits
    ship_visited = fields.Boolean("Ship Visited",tracking=True)
    ship_visits = fields.One2many("ccmc.candidate.ship.visits","candidate_id",string="Ship Visit",tracking=True)


        # Cookery an Bakery
    cookery_child_line = fields.One2many("ccmc.cookery.bakery.line","cookery_parent",string="Cookery & Bakery",tracking=True)
    

        # Start CCMC rating Oral

    ccmc_oral_child_line = fields.One2many("ccmc.oral.line","ccmc_oral_parent",string="CCMC Oral",tracking=True)
    ccmc_gsk_oral_child_line = fields.One2many("ccmc.gsk.oral.line","ccmc_oral_parent",string="CCMC Oral",tracking=True)

    ccmc_online = fields.One2many("survey.user_input","ccmc_candidate",domain=[("survey_id.subject.name", "=", 'CCMC')],string="CCMC Online",tracking=True)


    fees_paid = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ],string="Fees Paid by Institute", default='no',tracking=True)
    
    fees_paid_candidate = fields.Char("Fees Paid by Candidate",tracking=True,compute="_fees_paid_by_candidate",store=True)
    
    def _fees_paid_by_candidate(self):
        for rec in self:
            last_exam = self.env['ccmc.exam.schedule'].search([('ccmc_candidate','=',rec.id)], order='attempt_number desc', limit=1)
            last_exam_dgs_batch = last_exam.dgs_batch.id
            invoice = self.env['account.move'].sudo().search([('repeater_exam_batch','=',last_exam_dgs_batch),('ccmc_candidate','=',rec.id)],order='date desc')
            if invoice:
                batch = invoice.repeater_exam_batch.to_date.strftime("%B %Y")
                if invoice.payment_state == 'paid':
                    rec.fees_paid_candidate = batch + ' - Paid'
                else:
                    rec.fees_paid_candidate = batch + ' - Not Paid'
            else:
                rec.fees_paid_candidate = 'No Fees Paid'
                
            

    invoice_no = fields.Char("Invoice No",compute="_compute_invoice_no",store=True,tracking=True)
    
    ccmc_user_state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], string='User Status',compute="_compute_user_state",default="inactive",tracking=True)
    
    stcw_criteria = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Complied'),
    ], string='STCW Criteria' ,store=True,default="pending",compute="_check_stcw_certificate")

    ship_visit_criteria = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Complied'),
    ], string='Ship Visit Criteria',store=True,default="pending" ,compute='_check_ship_visit_criteria')

    attendance_criteria = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Complied'),
    ], string='Attendance Criteria',store=True,default="pending",compute="_check_attendance_criteria")
    
    candidate_image_status = fields.Selection([
        ('pending', 'Pending'),
        ('done', 'Done'),
    ],string="Candidate-Image",store=True,default="pending",compute="_check_image")
   
    candidate_signature_status = fields.Selection([
        ('pending', 'Pending'),
        ('done', 'Done'),

    ],string="Candidate-Sign",store=True,default="pending",compute="_check_sign")
    
    candidate_user_invoice_criteria = fields.Boolean('Criteria',compute= "_check_criteria",store=True)
    black_listed = fields.Boolean("Black Listed",tracking=True)
    
    withdrawn_state =  fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='User Withdrawn',default="no",tracking=True)
    
    withdrawn_reason = fields.Char("Withdraw Reason",tracking=True)

    ceo_override = fields.Boolean("CEO Override",default=False,tracking=True)
    
    edit_profile_status = fields.Boolean('edit_marksheet_status',compute='_compute_is_in_group',store=False)

    @api.depends('fees_paid')
    def _compute_is_in_group(self):
        for record in self:
            user = self.env.user
            # import wdb; wdb.set_trace()
            # Check if user belongs to the group
            has_group_access = user.has_group('bes.group_expense_approval_ceo')
            if record.fees_paid != 'yes':
                # Editable for all users if fees_paid is not 'yes'
                record.edit_profile_status = True
            else:
                # Editable only if the user has group access
                record.edit_profile_status = has_group_access
    def action_ceo_overriden(self):
        for record in self:
            record.ceo_override = not record.ceo_override
            record._check_stcw_certificate()
            record._check_ship_visit_criteria()
            record._check_attendance_criteria()

    @api.depends('candidate_signature_status','candidate_image_status','indos_no')
    def _check_criteria(self):
        for record in self:
            # candidate_image
            if record.candidate_image_status == 'done' and record.candidate_signature_status == 'done' and record.indos_no:
                record.candidate_user_invoice_criteria = True
            else:
                record.candidate_user_invoice_criteria = False

    @api.depends('ccmc_exam')
    def _update_rollno(self):
        # import wdb; wdb.set_trace();
        for record in self:
            # Initialize roll_no to None
            record.roll_no = None
            # Get the latest exam attempt record for the current candidate
            last_exam_record = self.env['ccmc.exam.schedule'].search(
                [('ccmc_candidate', '=', record.id)],
                order='attempt_number desc',
                limit=1
            )

            if last_exam_record:
                # Check if the latest exam attempt is certified
                if last_exam_record.state == "3-certified":
                    record.roll_no = last_exam_record.exam_id
                else:
                    # Set roll_no to the latest attempt's exam_id even if not certified
                    record.roll_no = last_exam_record.exam_id


    @api.depends('candidate_image')
    def _check_image(self):
        for record in self:
            # candidate_image
            if record.candidate_image:
                record.candidate_image_status = 'done'
            else:
                record.candidate_image_status = 'pending'

    @api.depends('candidate_signature')
    def _check_sign(self):
        for record in self:
            # candidate-sign
            if record.candidate_signature:
                record.candidate_signature_status = 'done'
            else:
                record.candidate_signature_status = 'pending'


    @api.depends('user_id')
    def _compute_user_state(self):
        for record in self:
            if record.user_id and record.user_id.active:
                record.ccmc_user_state = "active"
            else:
                record.ccmc_user_state = "inactive"
                
    def check_combination_exists(self,array):
        
        target_combinations = [['pst', 'efa', 'fpff', 'pssr', 'stsdsd'], ['bst', 'stsdsd']]
        
        for combination in target_combinations:
            if all(item in array for item in combination):
                return True
        
        return False

    @api.constrains('stcw_certificate')
    def _check_stcw_certificate(self):
         for record in self:
            # Retrieve all the STCW certificate records
            stcw_certificates = record.stcw_certificate

            course_type_already  = [course.course_name for course in record.stcw_certificate]
            # import wdb; wdb.set_trace();    
            exam_count = self.env['ccmc.exam.schedule'].sudo().search_count([('ccmc_candidate','=',record.id)])          

            # all_types_exist = all(course_type in course_type_already for course_type in all_course_types)
            all_types_exist = self.check_combination_exists(course_type_already)
            # Check if the candidate_cert_no is present for all the STCW certificates
            all_cert_nos_present = all(cert.candidate_cert_no for cert in stcw_certificates)

            # if all_types_exist and all_cert_nos_present:

            # if exam_count > 1:
            #     if all_types_exist:
            #         record.stcw_criteria = 'passed'
            #     else:
            #         record.stcw_criteria = 'pending'
            # elif exam_count in [0,1]:
            if all_types_exist and all_cert_nos_present:
                record.stcw_criteria = 'passed'
            else:
                record.stcw_criteria = 'pending'
        
    
    @api.depends('ship_visits')
    def _check_ship_visit_criteria(self):
        for record in self:
            if len(record.ship_visits) > 0:
                record.ship_visit_criteria = 'passed'
            else:
                record.ship_visit_criteria = 'pending'
    
    
    @api.constrains('attendance_compliance_1','attendance_compliance_2')
    def _check_attendance_criteria(self):
       for record in self:
            if record.attendance_compliance_1 == 'yes' or record.attendance_compliance_2 == 'yes':
                record.attendance_criteria = 'passed'
            else:
                record.attendance_criteria = 'pending'




    @api.depends('dob')
    def _compute_age(self):
        for record in self:
            if record.dob:
                birthdate = datetime.datetime.strptime(str(record.dob), '%Y-%m-%d').date()
                today = datetime.datetime.now().date()
                delta = today - birthdate
                record.age = delta.days // 365
            else:
                record.age = 0
    
    def open_ccmc_candidate_exams(self):
        
        
        
        return {
                'name': _('CCMC Exam'), 
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'ccmc.exam.schedule',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'target': 'current',
                'domain': [('ccmc_candidate', '=', self.id)],
                'context':{
                    'default_ccmc_candidate': self.id    
                }
                }
    
    
    # def open_add_marksheet(self):
        
        
        
    #     return {
    #                 'name': _('Add Marksheet'),
    #                 'view_type': 'form',
    #                 'view_mode': 'form',
    #                 'res_model': 'ccmc.marksheet.creation.wizard',
    #                 'type': 'ir.actions.act_window',
    #                 'view_id': False,
    #                 'target': 'new'
    #             }

    def user_inactive(self):
        
        user_id = self.user_id.id
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Candidate Inactivation Form',
            'res_model': 'candidate.inactive.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('bes.candidate_inactive_wizard_id').id,
            'target': 'new',
            'context': {
                "user_id":user_id
                },
        }
        
        # print("insavrtttttttttttt")
        # self.user_id.write({
        #     'active':False
        # })

    def user_active(self):
        print("Activeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
        self.user_id.write({
            'active':True
        })

    def unlink(self):
        # users_to_delete = self.mapped('user_id')
        # print
        if self.user_id:
            self.user_id.unlink()
        result = super(CCMCCandidate, self).unlink()
        
        
        return result
    
    def detect_current_month(self):
    # Get the current month as an integer (1 for January, 2 for February, etc.)
        current_month = datetime.datetime.now().month
        
        # Define the month ranges
        winter_months = [12, 1, 2]
        spring_months = [3, 4, 5, 6]
        summer_months = [7, 8]
        fall_months = [9, 10, 11]

        # Check which range the current month falls into
        if current_month in winter_months:
            return "dec_feb"
        elif current_month in spring_months:
            return "mar_jun"
        elif current_month in summer_months:
            return "jul_aug"
        elif current_month in fall_months:
            return "sep_nov"
        else:
            return "Invalid month."

    @api.constrains('zip')
    def _check_valid_zip(self):
        for record in self:
            if record.zip and not record.zip.isdigit() or len(record.zip) != 6:
                raise ValidationError("Zip code must be 6 digits.")

    # @api.constrains('phone')
    # def _check_valid_phone(self):
    #     for record in self:
    #         # Check if phone has 8 digits
    #         if record.phone and not record.phone.isdigit() or len(record.phone) != 8:
    #             raise ValidationError("Phone number must be 8 digits.")

    # @api.constrains('mobile')
    # def _check_valid_mobile(self):
    #     for record in self:
    #         # Check if mobile has 10 digits
    #         if record.mobile and not record.mobile.isdigit() or len(record.mobile) != 10:
    #             raise ValidationError("Mobile number must be 10 digits.")

    @api.constrains('email')
    def _check_valid_email(self):
        for record in self:
            # Check if email has @ symbol
            if record.email and '@' not in record.email:
                raise ValidationError("Invalid email address. Must contain @ symbol.")


    @api.depends('fees_paid')
    def _compute_invoice_no(self):
        for candidate in self:
            if candidate.fees_paid == 'yes':
                candidate.invoice_no = candidate.institute_batch_id.ccmc_account_move.name
            else:
                candidate.invoice_no = ''




    @api.model
    def create(self, values):
        institute_batch_id  = int(values['institute_batch_id'])
        
        ccmc_batches = self.env["institute.ccmc.batches"].search([('id','=',institute_batch_id)])
        
        capacity = ccmc_batches.dgs_approved_capacity - 1
        
        candidate_count = self.env["ccmc.candidate"].sudo().search_count([('institute_batch_id','=',institute_batch_id)])
        
        if candidate_count <= capacity:
            if values["dob"]:
                birthdate = datetime.datetime.strptime(str(values["dob"]), '%Y-%m-%d').date()
                today = datetime.datetime.now().date()
                delta = today - birthdate
                values['age'] = delta.days // 365
            else:
                values['age'] = 0
            ccmc_candidate = super(CCMCCandidate, self).create(values)
        else:
            raise ValidationError("DGS approved Capacity Exceeded")


        ### Comment Out for enable Login creation automatically
        # group_xml_ids = [
        #     'bes.group_ccmc_candidates',
        #     'base.group_portal'
        #     # Add more XML IDs as needed
        # ]
        
        # group_ids = [self.env.ref(xml_id).id for xml_id in group_xml_ids]
        
        # user_values = {
        #     'name': ccmc_candidate.name,
        #     'login': ccmc_candidate.indos_no,  # You can set the login as the same as the user name
        #     'password': 12345678,  # Generate a random password
        #     'sel_groups_1_9_10':9,
        #     'groups_id':  [(4, group_id, 0) for group_id in group_ids]
        # }

        # portal_user = self.env['res.users'].sudo().create(user_values)
        # ccmc_candidate.write({'user_id': portal_user.id})  # Associate the user with the institute
        # # import wdb; wdb.set_trace()
        # candidate_tag = self.env.ref('bes.candidates_tags').id
        # portal_user.partner_id.write({'email': ccmc_candidate.email,
        #                               'phone':ccmc_candidate.phone,
        #                               'mobile':ccmc_candidate.mobile,
        #                               'street':ccmc_candidate.street,
        #                               'street2':ccmc_candidate.street2,
        #                               'city':ccmc_candidate.city,
        #                               'zip':ccmc_candidate.zip,
        #                               'state_id':ccmc_candidate.state_id.id,'category_id':[candidate_tag]})
        return ccmc_candidate    
    
    
    
    @api.depends('name', 'age', 'indos_no', 'candidate_code', 'roll_no', 'dob', 'street', 'street2',
                 'city', 'zip', 'state_id', 'phone', 'mobile', 'email', 'sc_st', 'qualification','tenth_percent','twelve_percent','iti_percent')
    def _compute_eligibility(self):
        for candidate in self:
            # candidate.elligibility_criteria = 'not_elligible'
            # Check if all the fields are filled
            # import wdb; wdb.set_trace()
            all_fields_filled = all([candidate.name, candidate.age, candidate.indos_no, candidate.candidate_code, candidate.roll_no,
                    candidate.dob, candidate.street, candidate.street2, candidate.city, candidate.zip,
                    candidate.state_id, candidate.phone, candidate.mobile, candidate.email, candidate.sc_st,
                    candidate.qualification])

            if all_fields_filled:
                # import wdb; wdb.set_trace()
                if candidate.qualification == 'tenth' and candidate.tenth_percent > 40 or candidate.qualification == 'twelve' and candidate.twelve_percent > 40 or candidate.qualification == 'iti' and candidate.iti_percent > 50:
                   candidate.elligiblity_criteria = 'elligible'                
                else:
                   candidate.elligiblity_criteria = 'not_elligible'
            else:
                candidate.elligiblity_criteria = 'not_elligible'
     

    def open_register_for_exam_wizard(self):
        view_id = self.env.ref('bes.candidate_ccmc_register_exam_wizard').id
                
        last_exam_record = self.env['ccmc.exam.schedule'].search([('ccmc_candidate','=',self.id)], order='attempt_number desc', limit=1)
        
        if len(last_exam_record) <= 0:
            raise ValidationError("No previous Exam Found . This Candidate Must be registered through batches")
        
        if last_exam_record.state == '1-in_process':
            raise ValidationError("Last Exam Still In Process")

        # import wdb;wdb.set_trace()
        
        exam_month = self.detect_current_month()
        
        if exam_month == 'dec_feb' or exam_month== 'jul_aug':
            institute_ids = self.env["bes.institute"].search([('institute_repeater','=',True)]).ids
        else:
            institute_ids = []
        
        
        return {
            'name': 'Register For Exam',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'candidate.ccmc.register.exam.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
            # 'default_batches_id': self.id
            'default_candidate_id': self.id,
            'default_ccmc_exam': last_exam_record.id,
            'default_previous_attempt': last_exam_record.attempt_number,
            "default_exam_month" : self.detect_current_month(),
            "default_institute_ids" : institute_ids
            }
        }       

    
class CCMCSTCWCandidate(models.Model):
    _name = 'ccmc.candidate.stcw.certificate'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'STCW'
    
    candidate_id = fields.Many2one("ccmc.candidate","Candidate",tracking=True)
    course_name =  fields.Selection([
        ('pst', 'PST'),
        ('efa', 'EFA'),
        ('fpff', 'FPFF'),
        ('pssr', 'PSSR'),
        ('stsdsd', 'STSDSD'),
        ('bst', 'BST')
    ],string="Course",tracking=True)
    institute_name = fields.Many2one("bes.institute","Institute Name",tracking=True)
    other_institute = fields.Char("Other Institute Name",tracking=True)
    marine_training_inst_number = fields.Char("Marine Training Institute Number",tracking=True)
    mti_indos_no = fields.Char("MTI Indos No.",tracking=True)
    candidate_cert_no = fields.Char("Candidate Certificate Number",tracking=True)
    file_name = fields.Char('File Name',tracking=True)
    certificate_upload = fields.Binary("Certificate Upload",tracking=True)
    course_start_date = fields.Date(string="Course Start Date",tracking=True)
    course_end_date = fields.Date(string="Course End Date",tracking=True)


    

class CCMCCandidateShipVisits(models.Model):
    _name = 'ccmc.candidate.ship.visits'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'CCMC Ship Visits'

    institute_batch_id = fields.Many2one("institute.gp.batches","Batch",related="candidate_id.institute_batch_id",tracking=True)
    dgs_batch = fields.Many2one("dgs.batches",string="Exam Batch",related="candidate_id.institute_batch_id.dgs_batch",store=True)
    ship_visit_id = fields.Many2one("ccmc.batches.ship.visit",string="Ship Visit")
    institute = fields.Many2one("bes.institute",string="Name of Institute",related="candidate_id.institute_id",store=True,tracking=True)
    institute_code = fields.Char(string="Code No.",related="institute.code",store=True)
    candidate_count = fields.Integer("Number of Candidates",related="candidate_id.institute_batch_id.admit_card_alloted",tracking=True)
    exam_region = fields.Many2one("exam.center",string="Exam Region",store=True,related="institute.exam_center",tracking=True)
    candidate_id = fields.Many2one("ccmc.candidate","Candidate",tracking=True)
    name_of_ships = fields.Char("Name of  the Ship Visited / Ship in Campus",tracking=True)
    imo_no = fields.Char("Ship IMO Number",tracking=True)
    name_of_ports_visited = fields.Char("Name of the Port Visited / Place of SIC",tracking=True)
    date_of_visits = fields.Date("Date Of Visit",tracking=True)
    time_spent_on_ship = fields.Float("Hours",tracking=True)
    bridge = fields.Boolean("Bridge",tracking=True)
    eng_room = fields.Boolean("Eng. Room",tracking=True)
    cargo_area = fields.Boolean("Cargo Area",tracking=True)

class CookeryBakeryLine(models.Model):
    _name = 'ccmc.cookery.bakery.line'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Cookery and Bakery Line'

    cookery_parent = fields.Many2one("ccmc.candidate",string="Cookery & Bakery Parent",tracking=True)
    institute_id = fields.Many2one("bes.institute",string="Name of Institute",tracking=True)
    exam_id = fields.Many2one("ccmc.exam.schedule",string="Exam Id",tracking=True)
    # exam_attempt_number = fields.Integer(string="Exam Attempt No.")
    exam_attempt_number = fields.Integer(string="Exam Attempt No.", readonly=True,tracking=True)
    cookery_exam_date = fields.Date(string="Exam Date")
    hygien_grooming = fields.Integer("Hygiene & Grooming")
    appearance = fields.Integer("Appearance(Dish 1)")
    taste = fields.Integer("Taste(Dish 1)")
    texture = fields.Integer("Texture(Dish 1)")
    appearance_2 = fields.Integer("Appearance(Dish 2)")
    taste_2 = fields.Integer("Taste(Dish 2)")
    texture_2 = fields.Integer("Texture(Dish 2)")
    appearance_3 = fields.Integer("Appearance(Dish 3)")
    taste_3 = fields.Integer("Taste(Dish 3)")
    texture_3 = fields.Integer("Texture(Dish 3)")
    identification_ingredians = fields.Integer("identification of ingredients")
    knowledge_of_menu = fields.Integer("Knowledge of menu")
    total_mrks = fields.Integer("Total", compute="_compute_total_mrks", store=True)
    cookery_examiner = fields.Many2one("bes.examiner",string="Examiner")
    cookery_bekary_start_time = fields.Datetime(string="Start Time")
    cookery_bekary_end_time = fields.Datetime(string="End Time")
    cookery_draft_confirm = fields.Selection([('draft','Draft'),('confirm','Confirm')],string="Status",default="draft")
    cookery_practical_remarks = fields.Char(" Remarks Mention if Absent / Good  /Average / Weak ")

    
    
    @api.depends(
        'hygien_grooming', 'appearance', 'taste', 'texture', 'appearance_2', 'taste_2',
        'texture_2', 'appearance_3', 'taste_3', 'texture_3', 'identification_ingredians', 'knowledge_of_menu'
    )
    def _compute_total_mrks(self):
        for record in self:
            total = (
                record.hygien_grooming +
                record.appearance +
                record.taste +
                record.texture +
                record.appearance_2 +
                record.taste_2 +
                record.texture_2 +
                record.appearance_3 +
                record.taste_3 +
                record.texture_3 +
                record.identification_ingredians +
                record.knowledge_of_menu
            )
            record.total_mrks = total

    @api.onchange('hygien_grooming', 'appearance', 'taste', 'texture', 'appearance_2', 'taste_2', 'texture_2', 'appearance_3', 'taste_3', 'texture_3', 'identification_ingredians', 'knowledge_of_menu')
    def _onchange_ccmc_oral_marks_limit(self):
        if self.hygien_grooming > 10:
            raise UserError("In Cookery & Bakery, Hygiene & Grooming marks should not be greater than 10.")
        if self.appearance > 10:
            raise UserError("In Cookery & Bakery, Appearance(Dish 1) marks should not be greater than 10.")
        if self.taste > 10:
            raise UserError("In Cookery & Bakery, Taste(Dish 1) marks should not be greater than 10.")
        if self.texture > 9:
            raise UserError("In Cookery & Bakery, Texture(Dish 1) marks should not be greater than 9.")
        if self.appearance_2 > 10:
            raise UserError("In Cookery & Bakery, Appearance(Dish 2) marks should not be greater than 10.")
        if self.taste_2 > 10:
            raise UserError("In Cookery & Bakery, taste(Dish2) marks should not be greater than 10.")
        if self.texture_2 > 9:
            raise UserError("In Cookery & Bakery, Texture(Dish2) marks should not be greater than 9.")
        if self.appearance_3 > 5:
            raise UserError("In Cookery & Bakery, Appearance(Dish3) marks should not be greater than 5.")
        if self.taste_3 > 5:
            raise UserError("In Cookery & Bakery, Taste(Dish3) marks should not be greater than 5.")
        if self.texture_3 > 5:
            raise UserError("In Cookery & Bakery, Texture(Dish3) marks should not be greater than 5.")
        if self.identification_ingredians > 9:
            raise UserError("In Cookery & Bakery, Identification of Ingredians marks should not be greater than 9.")
        if self.knowledge_of_menu > 8:
            raise UserError("In Cookery & Bakery, Knowledge Of Menu marks should not be greater than 8.")

    

    @api.model
    def create(self, vals):
        if vals.get('exam_attempt_number', 0) == 0:
            # Calculate the next serial number
            last_attempt_number = self.search([('cookery_parent', '=', vals.get('cookery_parent'))], order="exam_attempt_number desc", limit=1)
            next_attempt_number = last_attempt_number.exam_attempt_number + 1 if last_attempt_number else 1

            vals['exam_attempt_number'] = next_attempt_number

        return super(CookeryBakeryLine, self).create(vals)

    @api.constrains('exam_attempt_number')
    def _check_attempt_number_limit(self):
        for record in self:
            if record.exam_attempt_number > 7:
                raise ValidationError("A candidate can't have more than 7 exam attempts in Cookery & Bakery.")

    # def unlink(self):
    #     # raise UserError("YOU CAN'T DELETE CANDIDATE EXAM RECORDS.")
    #     return super(CookeryBakeryLine, self - undeletable_records).unlink()



class MekPrcticalLine(models.Model):
    _name = 'gp.mek.practical.line'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'MEK Practical Line'

    mek_parent = fields.Many2one("gp.candidate",string="Parent",tracking=True)
    exam_id = fields.Many2one("gp.exam.schedule",string="Exam Id",tracking=True)
    institute_id = fields.Many2one("bes.institute",string="Institute",tracking=True)
    mek_prcatical_attempt_no = fields.Integer(string="Exam Attempt No.", readonly=True,tracking=True)
    mek_practical_exam_date = fields.Date(string="Exam Date",tracking=True)
    # using_hand_plumbing_tools_task_1 = fields.Integer("Using Hand & Plumbing Tools (Task 1)",tracking=True)
    # using_hand_plumbing_tools_task_2 = fields.Integer("Using Hand & Plumbing Tools (Task 2)",tracking=True)
    using_hand_plumbing_tools_task_3 = fields.Integer("Using Hand & Plumbing Tools (Task 3)",tracking=True)
    use_of_chipping_tools_paint = fields.Integer("Use of Chipping Tools & paint Brushes",tracking=True)
    # use_of_carpentry = fields.Integer("Use of Carpentry Tools",tracking=True)
    # use_of_measuring_instruments = fields.Integer("Use of Measuring Instruments",tracking=True)
    welding_lathe = fields.Integer("Welding (1 Task),Lathe Work (1 Task)",tracking=True)
    # lathe = fields.Integer("Lathe Work (1 Task)",tracking=True)
    electrical = fields.Integer("Electrical (1 Task)",tracking=True)
    
    mek_practical_total_marks = fields.Integer("Total Marks", compute="_compute_mek_practical_total_marks", store=True,tracking=True)
    
    mek_practical_remarks = fields.Text(" Remarks Mention if Absent / Good  /Average / Weak ",tracking=True)
    mek_practical_draft_confirm = fields.Selection([('draft','Draft'),('confirm','Confirm')],string="Status",default="draft",tracking=True)



    @api.onchange('using_hand_plumbing_tools_task_3','use_of_chipping_tools_paint', 'welding_lathe', 'electrical')
    def _onchange_ccmc_oral_marks_limit(self):
        # if self.using_hand_plumbing_tools_task_1 > 10:
        #     raise UserError("In MEK Practical, Using Hand & Plumbing Tools (Task 1) Marks cannot exceed 10.")
        # if self.using_hand_plumbing_tools_task_2 > 10:
        #     raise UserError("In MEK Practical, Using Hand & Plumbing Tools (Task 2) Marks cannot exceed 10.")
        if self.using_hand_plumbing_tools_task_3 > 30:
            raise UserError("In MEK Practical, Using Hand & Plumbing Tools (Task 3) Marks cannot exceed 30.")
        if self.use_of_chipping_tools_paint > 30:
            raise UserError("In MEK Practical, Use of Chipping Tools & paint Brushes Marks cannot exceed 30.")
        # if self.use_of_carpentry > 10:
        #     raise UserError("In MEK Practical, Use of Carpentry Tools Marks cannot exceed 10.")
        # if self.use_of_measuring_instruments > 10:
        #     raise UserError("In MEK Practical, Use of Measuring Instruments Marks cannot exceed 10.")
        if self.welding_lathe > 30:
            raise UserError("In MEK Practical, Welding (1 Task) Marks cannot exceed 30.")
        # if self.lathe > 10:
        #     raise UserError("In MEK Practical, Lathe Work (1 Task) Marks cannot exceed 10.")
        if self.electrical > 10:
            raise UserError("In MEK Practical, Electrical (1 Task) Marks cannot exceed 10.")
  
    
    @api.depends('using_hand_plumbing_tools_task_3','use_of_chipping_tools_paint', 'welding_lathe', 'electrical')
    def _compute_mek_practical_total_marks(self):
        for record in self:
            total = (
                # record.using_hand_plumbing_tools_task_1 +
                # record.using_hand_plumbing_tools_task_2 +
                record.using_hand_plumbing_tools_task_3 +
                record.use_of_chipping_tools_paint +
                # record.use_of_carpentry +
                # record.use_of_measuring_instruments +
                record.welding_lathe +
                # record.lathe +
                record.electrical
            )
            record.mek_practical_total_marks = total
    
    
    # @api.constrains('using_hand_plumbing_tools_task_1', 'using_hand_plumbing_tools_task_2', 'using_hand_plumbing_tools_task_3', 'use_of_chipping_tools_paint_brushes', 'use_of_carpentry', 'use_of_measuring_instruments', 'welding', 'lathe', 'electrical')
    # def _check_values(self):
    #     for record in self:
    #         fields_to_check = {
    #             'using_hand_plumbing_tools_task_1': "Using Hand & Plumbing Tools (Task 1)",
    #             'using_hand_plumbing_tools_task_2': "Using Hand & Plumbing Tools (Task 2)",
    #             'using_hand_plumbing_tools_task_3': "Using Hand & Plumbing Tools (Task 3)",
    #             'use_of_chipping_tools_paint_brushes': "Use of Chipping Tools & Paint Brushes",
    #             'use_of_carpentry': "Use of Carpentry Tools",
    #             'use_of_measuring_instruments': "Use of Measuring Instruments",
    #             'welding': "Welding (1 Task)",
    #             'lathe': "Lathe Work (1 Task)",
    #             'electrical': "Electrical (1 Task)",
    #         }

    #         for field_name, field_label in fields_to_check.items():
    #             field_value = record[field_name]
    #             if field_name == 'welding' and field_value > 20:
    #                 raise ValidationError(f"In MEK Practical, {field_label} Marks cannot exceed 20.")
    #             elif field_value > 10:
    #                 raise ValidationError(f"In MEK Practical, {field_label} Marks cannot exceed 10.")

    @api.model
    def create(self, vals):
        if vals.get('mek_prcatical_attempt_no', 0) == 0:
            # Calculate the next serial number
            last_attempt_no = self.search([('mek_parent', '=', vals.get('mek_parent'))], order="mek_prcatical_attempt_no desc", limit=1)
            next_attempt_no = last_attempt_no.mek_prcatical_attempt_no + 1 if last_attempt_no else 1

            vals['mek_prcatical_attempt_no'] = next_attempt_no

        return super(MekPrcticalLine, self).create(vals)

    @api.constrains('mek_prcatical_attempt_no')
    def _check_attempt_no_limit(self):
        for record in self:
            if record.mek_prcatical_attempt_no > 7:
                raise ValidationError("A candidate can't have more than 7 exam attempts in MEK Practical.")

    # def unlink(self):
    #     # raise UserError("YOU CAN'T DELETE CANDIDATE EXAM RECORDS.")
    #     return super(MekPrcticalLine, self - undeletable_records).unlink()

class MekOralLine(models.Model):
    _name = 'gp.mek.oral.line'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'MEK Oral Line'

    mek_oral_parent = fields.Many2one("gp.candidate", string="Parent",tracking=True)
    institute_id = fields.Many2one("bes.institute",string="Institute",tracking=True)
    exam_id = fields.Many2one("gp.exam.schedule",string="Exam ID",tracking=True)
    mek_oral_attempt_no = fields.Integer(string="Exam Attempt No.", readonly=True,tracking=True)
    mek_oral_exam_date = fields.Date(string="Exam Date",tracking=True)
    using_of_tools = fields.Integer("Uses of Hand/Plumbing/Carpentry Tools & Chipping Tools & Brushes & Paints",tracking=True)
    # use_of_chipping_tools_paints = fields.Integer("Use of Chipping Tools & Brushes & Paints",tracking=True)
    welding_lathe_drill_grinder = fields.Integer("Welding & Lathe/Drill/Grinder",tracking=True)
    # lathe_drill_grinder = fields.Integer("Lathe/Drill/Grinder",tracking=True)
    electrical = fields.Integer("Electrical",tracking=True)
    journal = fields.Integer("Journal",tracking=True)

    mek_oral_total_marks = fields.Integer("Total Marks", compute="_compute_mek_oral_total_marks", store=True,tracking=True)

    mek_oral_remarks = fields.Text("Remarks Mention if Absent / Good / Average / Weak",tracking=True)
    mek_oral_draft_confirm = fields.Selection([('draft','Draft'),('confirm','Confirm')],string="Status",default="draft",tracking=True)


    

    @api.depends('using_of_tools', 'welding_lathe_drill_grinder', 'electrical', 'journal')
    def _compute_mek_oral_total_marks(self):
        for record in self:
            total = (
                record.using_of_tools +
                record.welding_lathe_drill_grinder +
                # record.welding +
                # record.lathe_drill_grinder +
                record.electrical +
                record.journal
            )
            record.mek_oral_total_marks = total

    @api.onchange('using_of_tools', 'welding_lathe_drill_grinder','electrical', 'journal')
    def _onchange_ccmc_oral_marks_limit(self):
        if self.using_of_tools > 20:
            raise UserError("In MEK Oral, Uses of Hand/Plumbing/Carpentry Tools & Chipping Tools & Brushes & Paints Marks cannot exceed 20.")
        # if self.use_of_chipping_tools_paints > 10:
        #     raise UserError("In MEK Oral, Use of Chipping Tools & Brushes & Paints Marks cannot exceed 10.")
        if self.welding_lathe_drill_grinder > 20:
            raise UserError("In MEK Oral, Welding & Lathe/Drill/Grinder Marks cannot exceed 20.")
        # if self.lathe_drill_grinder > 10:
        #     raise UserError("In MEK Oral, Lathe/Drill/Grinder Marks cannot exceed 10.")
        if self.electrical > 10:
            raise UserError("In MEK Oral, Electrical Marks cannot exceed 10.")
        if self.journal > 25:
            raise UserError("In MEK Oral, Journal Marks cannot exceed 25.")



    @api.model
    def create(self, vals):
        if vals.get('mek_oral_attempt_no', 0) == 0:
            # Calculate the next serial number
            last_attempt_no = self.search([('mek_oral_parent', '=', vals.get('mek_oral_parent'))], order="mek_oral_attempt_no desc", limit=1)
            next_attempt_no = last_attempt_no.mek_oral_attempt_no + 1 if last_attempt_no else 1

            vals['mek_oral_attempt_no'] = next_attempt_no

        return super(MekOralLine, self).create(vals)

    @api.constrains('mek_oral_attempt_no')
    def _check_mek_oral_attempt(self):
        for record in self:
            if record.mek_oral_attempt_no > 7:
                raise ValidationError("A candidate can't have more than 7 exam attempts in MEK Oral.")

    # def unlink(self):
    #     # raise UserError("YOU CAN'T DELETE CANDIDATE EXAM RECORDS.")
    #     return super(MekOralLine, self - undeletable_records).unlink()



class GskPracticallLine(models.Model):
    _name = 'gp.gsk.practical.line'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'GSK Practical Line'

    gsk_practical_parent = fields.Many2one("gp.candidate", string="Parent",tracking=True)
    exam_id = fields.Many2one("gp.exam.schedule",string="Exam ID",tracking=True)
    institute_id = fields.Many2one("bes.institute",string="Institute",tracking=True)
    gsk_practical_attempt_no = fields.Integer(string="Exam Attempt No.", default=0, readonly=True,tracking=True)
    gsk_practical_exam_date = fields.Date(string="Exam Date",tracking=True)
    climbing_mast_bosun_chair= fields.Integer("Climb the mast with safe practices , Prepare and throw Heaving Line,Rigging Bosun's Chair and self lower and hoist",tracking=True)
    buoy_flags_recognition = fields.Integer("·Recognise buyos and flags .Hoisting a Flag correctly .Steering and Helm Orders",tracking=True)
    # bosun_chair = fields.Integer("Rigging Bosun's Chair and self lower and hoist",tracking=True)
    rig_stage_rig_pilot_rig_scaffolding = fields.Integer("Rig a stage for painting shipside,Rig a Pilot Ladder,Rig scaffolding to work at a height",tracking=True)
    # rig_pilot = fields.Integer("Rig a Pilot Ladder",tracking=True)
    # rig_scaffolding = fields.Integer("Rig scaffolding to work at a height",tracking=True) 
    fast_ropes_knots_bend_sounding_rod = fields.Integer("·Making fast Ropes and Wires ·Use Rope-Stopper / Chain Stopper.Knots, Bends, Hitches .Whippings/Seizing/Splicing Ropes/Wires .Reeve 3- fold / 2 fold purchase·Taking Soundings with sounding rod / sounding taps ·Reading of Draft .Mannual lifting of weight",tracking=True)
    
    # knots_bend = fields.Integer(".Knots, Bends, Hitches .Whippings/Seizing/Splicing Ropes/Wires .Reeve 3- fold / 2 fold purchase",tracking=True)
    # sounding_rod = fields.Integer("·Taking Soundings with sounding rod / sounding taps ·Reading of Draft .Mannual lifting of weight",tracking=True)
    
    gsk_practical_total_marks = fields.Integer("Total Marks",compute="_compute_gsk_practical_total_marks",store=True,tracking=True)
    gsk_practical_remarks = fields.Text(" Remarks Mention if Absent / Good  /Average / Weak ",tracking=True)
    gsk_practical_draft_confirm = fields.Selection([('draft','Draft'),('confirm','Confirm')],string="Status",default="draft",tracking=True)


      
    @api.depends('climbing_mast_bosun_chair', 'buoy_flags_recognition','rig_stage_rig_pilot_rig_scaffolding', 'fast_ropes_knots_bend_sounding_rod')
    def _compute_gsk_practical_total_marks(self):
        for record in self:
            total_marks = 0
            total_marks += record.climbing_mast_bosun_chair
            total_marks += record.buoy_flags_recognition
            # total_marks += record.bosun_chair
            total_marks += record.rig_stage_rig_pilot_rig_scaffolding
            # total_marks += record.rig_pilot
            # total_marks += record.rig_scaffolding
            total_marks += record.fast_ropes_knots_bend_sounding_rod
            # total_marks += record.knots_bend
            # total_marks += record.sounding_rod
            record.gsk_practical_total_marks = total_marks

    @api.onchange('climbing_mast_bosun_chair','buoy_flags_recognition','rig_stage_rig_pilot_rig_scaffolding','fast_ropes_knots_bend_sounding_rod')
    def _onchange_gsk_practicals_marks_limit(self):
        if self.climbing_mast_bosun_chair> 30:
            raise UserError("Climb the mast with safe practices , Prepare and throw Heaving Line marks should not be greater than 12.")
        if self.buoy_flags_recognition > 10:
            raise UserError("·Recognise buyos and flags .Hoisting a Flag correctly .Steering and Helm Orders marks should not be greater than 12.")
        # if self.bosun_chair > 8:
        #     raise UserError("Rigging Bosun's Chair and self lower and hoist marks should not be greater than 8.")
        if self.rig_stage_rig_pilot_rig_scaffolding > 30:
            raise UserError("Rig a stage for painting shipside marks should not be greater than 30.")
        # if self.rig_pilot > 8:
        #     raise UserError("Rig a Pilot Ladder marks should not be greater than 8.")
        # if self.rig_scaffolding > 8:
        #     raise UserError("Rig scaffolding to work at a height marks should not be greater than 8.")
        if self.fast_ropes_knots_bend_sounding_rod > 30:
            raise UserError("·Making fast Ropes and Wires ·Use Rope-Stopper / Chain Stopper marks should not be greater than 30.")
        # if self.knots_bend > 18:
        #     raise UserError(".Knots, Bends, Hitches .Whippings/Seizing/Splicing Ropes/Wires .Reeve 3- fold / 2 fold purchase marks should not be greater than 18.")
        # if self.sounding_rod > 18:
        #     raise UserError("·Taking Soundings with sounding rod / sounding taps ·Reading of Draft .Mannual lifting of weight marks should not be greater than 18.")

    
    @api.model
    def create(self, vals):
        if vals.get('gsk_practical_attempt_no', 0) == 0:
            # Calculate the next serial number
            last_attempt_no = self.search([('gsk_practical_parent', '=', vals.get('gsk_practical_parent'))], order="gsk_practical_attempt_no desc", limit=1)
            next_attempt_no = last_attempt_no.gsk_practical_attempt_no + 1 if last_attempt_no else 1

            vals['gsk_practical_attempt_no'] = next_attempt_no

        return super(GskPracticallLine, self).create(vals)

    @api.constrains('gsk_practical_attempt_no')
    def _check_attempt_gsk_practical(self):
        for record in self:
            if record.gsk_practical_attempt_no > 7:
                raise ValidationError("A candidate can't have more than 7 exam attempts in GSK Practical.")

    # def unlink(self):
    #     # raise UserError("YOU CAN'T DELETE CANDIDATE EXAM RECORDS.")
    #     return super(GskPracticallLine, self - undeletable_records).unlink()



class GskOralLine(models.Model):
    _name = 'gp.gsk.oral.line'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'GSK Oral Line'

    gsk_oral_parent = fields.Many2one("gp.candidate", string="Parent",tracking=True)
    exam_id = fields.Many2one("gp.exam.schedule",string="Exam ID",tracking=True)
    institute_id = fields.Many2one("bes.institute",string="Institute",tracking=True)
    gsk_oral_attempt_no = fields.Integer(string="Exam Attempt No.", default=0,readonly=True,tracking=True)
    gsk_oral_exam_date = fields.Date(string="Exam Date",tracking=True)

    subject_area_1_2_3 = fields.Integer("Subject Area 1, 2, 3 ",tracking=True)
    # subject_area_2 = fields.Integer("Subject Area 2",tracking=True)
    # subject_area_3 = fields.Integer("Subject Area 3",tracking=True)
    subject_area_4_5_6 = fields.Integer("Subject Area 4, 5, 6",tracking=True)
    # subject_area_5 = fields.Integer("Subject Area 5",tracking=True)
    # subject_area_6 = fields.Integer("Subject Area 6",tracking=True)
    practical_record_journals = fields.Integer("Practical Record Book and Journal",tracking=True)
    
    
    gsk_oral_total_marks = fields.Integer("Total Marks",compute='_compute_gsk_oral_total_marks', store=True,tracking=True)
    gsk_oral_remarks = fields.Text(" Remarks Mention if Absent / Good  /Average / Weak ",tracking=True)
    gsk_oral_draft_confirm = fields.Selection([('draft','Draft'),('confirm','Confirm')],string="Status",default="draft",tracking=True)


    

    @api.depends('subject_area_1_2_3', 'subject_area_4_5_6', 'practical_record_journals')
    def _compute_gsk_oral_total_marks(self):
        for record in self:
            total_marks = sum([
                record.subject_area_1_2_3,
                record.subject_area_4_5_6,
                # record.subject_area_3,
                # record.subject_area_4,
                # record.subject_area_5,
                # record.subject_area_6,
                record.practical_record_journals,
            ])

            record.gsk_oral_total_marks = total_marks
    

    @api.onchange('subject_area_1_2_3','subject_area_4_5_6','practical_record_journals')
    def _onchange_gsk_oral__marks_limit(self):
        if self.subject_area_1_2_3 > 25:
            raise UserError("Subject Area 1 marks should not be greater than 25.")
        if self.subject_area_4_5_6 > 25:
            raise UserError("Subject Area 2 marks should not be greater than 25.")
        # if self.subject_area_3 > 9:
        #     raise UserError("Subject Area 3 marks should not be greater than 9.")
        # if self.subject_area_4 > 9:
        #     raise UserError("Subject Area 4 marks should not be greater than 9.")
        # if self.subject_area_5 > 12:
        #     raise UserError("Subject Area 5 marks should not be greater than 12.")
        # if self.subject_area_6 > 5:
        #     raise UserError("Subject Area 6 marks should not be greater than 5.")
        if self.practical_record_journals > 25:
            raise UserError("Practical Record Book and Journal marks should not be greater than 25.")


    @api.model
    def create(self, vals):
        if vals.get('gsk_oral_attempt_no', 0) == 0:
            # Calculate the next serial number
            last_attempt_no = self.search([('gsk_oral_parent', '=', vals.get('gsk_oral_parent'))], order="gsk_oral_attempt_no desc", limit=1)
            next_attempt_no = last_attempt_no.gsk_oral_attempt_no + 1 if last_attempt_no else 1
            vals['gsk_oral_attempt_no'] = next_attempt_no

        return super(GskOralLine, self).create(vals)

    @api.constrains('gsk_oral_attempt_no')
    def _check_attempt_no_limit(self):
        for record in self:
            if record.gsk_oral_attempt_no > 7:
                raise ValidationError("A candidate can't have more than 7 exam attempts in GSK Oral.")

    # def unlink(self):
    #     # raise UserError("YOU CAN'T DELETE CANDIDATE EXAM RECORDS.")
    #     return super(GskOralLine, self - undeletable_records).unlink()


class CcmcOralLine(models.Model):
    _name = 'ccmc.oral.line'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'CCMC Oral Line'


    institute_id = fields.Many2one("bes.institute",string="Institute",tracking=True)
    ccmc_oral_parent = fields.Many2one("ccmc.candidate", string="Parent",tracking=True)
    exam_id = fields.Many2one("ccmc.exam.schedule",string="Exam ID",tracking=True)
    ccmc_oral_attempt_no = fields.Integer(string="Exam Attempt No.", default=0, readonly=True,tracking=True)
    ccmc_oral_exam_date = fields.Date(string="Exam Date",tracking=True)
    
    house_keeping = fields.Integer("House Keeping")
    f_b = fields.Integer("F & B service Practical")
    orals_house_keeping = fields.Integer("Orals on Housekeeping and F& B Service")
    attitude_proffessionalism = fields.Integer("Attitude & Proffesionalism")
    equipment_identification = fields.Integer("Identification of Equipment")
    
    gsk_ccmc = fields.Integer("GSK",related = 'exam_id.ccmc_gsk_oral.toal_ccmc_oral_rating')
    # safety_ccmc = fields.Integer("Safety",tracking=True)
    toal_ccmc_rating = fields.Integer("Total", compute="_compute_ccmc_rating_total", store=True)
    ccmc_oral_draft_confirm = fields.Selection([('draft','Draft'),('confirm','Confirm')],string="Status",default="draft")
    ccmc_oral_remarks = fields.Char(" Remarks Mention if Absent / Good  /Average / Weak ")
    

    @api.depends(
        'gsk_ccmc','house_keeping','f_b','orals_house_keeping','attitude_proffessionalism','equipment_identification'
    )
    def _compute_ccmc_rating_total(self):
        for record in self:
            rating_total = (
                # record.gsk_ccmc +
                # record.safety_ccmc+
                record.house_keeping+
                record.f_b+
                record.orals_house_keeping+
                record.attitude_proffessionalism+
                record.equipment_identification
            )
            
            record.toal_ccmc_rating = rating_total


    @api.onchange('gsk_ccmc')
    def _onchange_ccmc_oral_marks_limit(self):
        if self.gsk_ccmc > 20:
            raise UserError("In CCMC Oral, GSK marks should not be greater than 20.")
        # if self.safety_ccmc > 10:
        #     raise UserError("In CCMC Oral, Safety marks should not be greater than 10.")


    @api.model
    def create(self, vals):
        print(vals)
        if vals.get('ccmc_oral_attempt_no', 0) == 0:
            # Calculate the next attempt number
            last_attempt = self.search([
                ('ccmc_oral_parent', '=', vals.get('ccmc_oral_parent')),
            ], order='ccmc_oral_attempt_no desc', limit=1)
            next_attempt = last_attempt.ccmc_oral_attempt_no + 1 if last_attempt else 1
            vals['ccmc_oral_attempt_no'] = next_attempt
        return super(CcmcOralLine , self).create(vals)


    @api.constrains('ccmc_oral_attempt_no')
    def _check_attempt_no(self):
        for record in self:
            if record.ccmc_oral_attempt_no > 7:
                raise ValidationError("A Candidate can't have more than 7 exam attempts in CCMC Oral.")

    # def unlink(self):
    #     # raise UserError("YOU CAN'T DELETE CANDIDATE EXAM RECORDS.")
    #     return super(CcmcOralLine, self - undeletable_records).unlink()


class CcmcGSKOralLine(models.Model):
    _name = 'ccmc.gsk.oral.line'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'CCMC GSK Oral Line'


    institute_id = fields.Many2one("bes.institute",string="Institute",tracking=True)
    ccmc_oral_parent = fields.Many2one("ccmc.candidate", string="Parent",tracking=True)
    exam_id = fields.Many2one("ccmc.exam.schedule",string="Exam ID",tracking=True)
    ccmc_gsk_oral_attempt_no = fields.Integer(string="Exam Attempt No.", default=0, readonly=True,tracking=True)
    ccmc_gsk_oral_exam_date = fields.Date(string="Exam Date",tracking=True)
    gsk_ccmc = fields.Integer("GSK")
    safety_ccmc = fields.Integer("Safety")
    toal_ccmc_oral_rating = fields.Integer("Total", compute="_compute_ccmc_rating_total", store=True)
    ccmc_oral_draft_confirm = fields.Selection([('draft','Draft'),('confirm','Confirm')],string="State",default="draft")
    ccmc_gsk_oral_remarks = fields.Char(" Remarks Mention if Absent / Good  /Average / Weak ")
    

    @api.depends(
        'gsk_ccmc', 'safety_ccmc'
    )
    def _compute_ccmc_rating_total(self):
        for record in self:
            rating_total = (
                record.gsk_ccmc +
                record.safety_ccmc
            )
            
            record.toal_ccmc_oral_rating = rating_total


    @api.onchange('gsk_ccmc','safety_ccmc')
    def _onchange_ccmc_oral_marks_limit(self):
        if self.gsk_ccmc > 10:
            raise UserError("In CCMC Oral, GSK marks should not be greater than 10.")
        if self.safety_ccmc > 10:
            raise UserError("In CCMC Oral, Safety marks should not be greater than 10.")


    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace();
        if vals.get('ccmc_gsk_oral_attempt_no', 0) == 0:
            
            # Calculate the next attempt number
            last_attempt = self.search([
                ('ccmc_oral_parent', '=', vals.get('ccmc_oral_parent')),
            ], order='ccmc_gsk_oral_attempt_no desc', limit=1)
            next_attempt = last_attempt.ccmc_gsk_oral_attempt_no + 1 if last_attempt else 1
            vals['ccmc_gsk_oral_attempt_no'] = next_attempt
        return super(CcmcGSKOralLine, self).create(vals)


    @api.constrains('ccmc_gsk_oral_attempt_no')
    def _check_attempt_no(self):
        for record in self:
            if record.ccmc_gsk_oral_attempt_no > 7:
                raise ValidationError("A Candidate can't have more than 7 exam attempts in CCMC Oral.")

    # def unlink(self):
    #     # raise UserError("YOU CAN'T DELETE CANDIDATE EXAM RECORDS.")
    #     return super(CcmcOralLine, self - undeletable_records).unlink()



class CandidateRegisterExamWizard(models.TransientModel):
    _name = 'candidate.gp.register.exam.wizard'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Register Exam'
    
    exam_region = fields.Many2one("exam.center",string="Exam Region",tracking=True)
    institute_ids = fields.Many2many("bes.institute",string="Institute",compute="_compute_institute_ids",tracking=True)
    institute_id = fields.Many2one("bes.institute",string="Institute",tracking=True)
    candidate_id = fields.Many2one("gp.candidate",string="Candidate",required=True,tracking=True)
    
    mek_survey_qb = fields.Many2one("survey.survey",string="Mek Question Bank",tracking=True)
    gsk_survey_qb = fields.Many2one("survey.survey",string="Gsk Question Bank",tracking=True)
    dgs_batch = fields.Many2one("dgs.batches",string="Exam Batch",required=False,tracking=True)
    gp_exam = fields.Many2one("gp.exam.schedule",string="GP Exam",required=True,tracking=True)
    
    
    previous_attempt =  fields.Integer("Previous Attempt No.",tracking=True)
    deffereds =  fields.Boolean("Deffered")
    # batch_id = fields.Many2one("institute.gp.batches",string="Batches",required=True)

    
    exam_month = fields.Selection([
        ('dec_feb', 'Dec - Feb'),
        ('mar_jun', 'Mar - Jun'),
        ('jul_aug', 'Jul - Aug'),
        ('sep_nov', 'Sep - Nov'),
    ], string='Exam Month',tracking=True)
    
    
    gsk_oral_prac_status = fields.Selection([
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='GSK Oral/Practical Status',tracking=True)
    
    
    mek_total = fields.Float("MEK Total",readonly=True,tracking=True)
    mek_percentage = fields.Float("MEK Percentage",readonly=True,tracking=True)
    mek_oral_prac_status = fields.Selection([
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='Mek Oral/Practical Status',tracking=True)
    
    mek_online_status = fields.Selection([
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='Mek Online Status',tracking=True)
    
    gsk_online_status = fields.Selection([
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='Gsk Online Status',tracking=True)
    
    
    @api.depends('exam_region')
    def _compute_institute_ids(self):
        for record in self:
            
            exam_region = record.exam_region.id
            record.institute_ids = self.env["bes.institute"].search([('exam_center','=',exam_region)])
            
    
            
    
    
    def register_exam(self):
        
        # import wdb; wdb.set_trace()
        dgs_exam = self.dgs_batch.id
        
        exam_id = self.env['ir.sequence'].next_by_code("gp.exam.sequence")

        
        gp_exam_schedule = self.env["gp.exam.schedule"].create({'gp_candidate':self.candidate_id.id , "dgs_batch": dgs_exam  , "exam_id":exam_id })

        
        if self.gsk_oral_prac_status == 'failed':
            gsk_practical = self.env["gp.gsk.practical.line"].create({"exam_id":gp_exam_schedule.id,'gsk_practical_parent':self.candidate_id.id,'institute_id': self.institute_id.id})
            gsk_oral = self.env["gp.gsk.oral.line"].create({"exam_id":gp_exam_schedule.id,'gsk_oral_parent':self.candidate_id.id,'institute_id': self.institute_id.id})
        
            gsk_practical_marks = self.gp_exam.gsk_practical_marks
            gsk_oral_marks = self.gp_exam.gsk_oral_marks
            gsk_total = self.gp_exam.gsk_total
            gsk_percentage = self.gp_exam.gsk_percentage
            gsk_oral_prac_carry_forward = False
        
        else:
            gsk_practical = self.gp_exam.gsk_prac
            gsk_oral =self.gp_exam.gsk_oral
            
            gsk_practical_marks = self.gp_exam.gsk_practical_marks
            gsk_oral_marks = self.gp_exam.gsk_oral_marks
            gsk_total = self.gp_exam.gsk_total
            gsk_percentage = self.gp_exam.gsk_percentage
            gsk_oral_prac_carry_forward = True

        
        
        if self.mek_oral_prac_status == 'failed':
            mek_practical = self.env["gp.mek.practical.line"].create({"exam_id":gp_exam_schedule.id,'mek_parent':self.candidate_id.id,'institute_id': self.institute_id.id})
            mek_oral = self.env["gp.mek.oral.line"].create({"exam_id":gp_exam_schedule.id,'mek_oral_parent':self.candidate_id.id,'institute_id': self.institute_id.id})
            mek_practical_marks = self.gp_exam.mek_practical_marks
            mek_oral_marks = self.gp_exam.mek_oral_marks
            mek_total = self.gp_exam.mek_total
            mek_percentage = self.gp_exam.mek_percentage
            mek_oral_prac_carry_forward = False
            
        else:
            mek_practical = self.gp_exam.mek_prac
            mek_oral =self.gp_exam.mek_oral
            mek_oral_prac_carry_forward = True
            mek_practical_marks = self.gp_exam.mek_practical_marks
            mek_oral_marks = self.gp_exam.mek_oral_marks
            mek_total = self.gp_exam.mek_total
            mek_percentage = self.gp_exam.mek_percentage
            
        
        if self.mek_online_status == 'failed' and  self.gsk_online_status == 'failed':
            
            ## MEK QB Assigning
            mek_survey_qb_input = self.mek_survey_qb._create_answer(user=self.candidate_id.user_id)
            token = mek_survey_qb_input.generate_unique_string()
            mek_survey_qb_input.write({'gp_candidate':self.candidate_id.id ,'dgs_batch':dgs_exam  })
            mek_online_carry_forward = False
            mek_online_marks = self.gp_exam.mek_online_marks
            mek_online_percentage = self.gp_exam.mek_online_percentage
            
            ## GSK QB Assigning
            gsk_survey_qb_input = self.gsk_survey_qb._create_answer(user=self.candidate_id.user_id)
            token = gsk_survey_qb_input.generate_unique_string()
            gsk_survey_qb_input.write({'gp_candidate':self.candidate_id.id , 'dgs_batch':dgs_exam})
            gsk_online_carry_forward = False
            gsk_online_marks = self.gp_exam.gsk_online_marks
            gsk_online_percentage = self.gp_exam.gsk_online_percentage
        
        elif self.gsk_online_status == 'failed' and not self.mek_online_status == 'failed':
            
            ## GSK QB Assigning
            gsk_survey_qb_input = self.gsk_survey_qb._create_answer(user=self.candidate_id.user_id)
            token = gsk_survey_qb_input.generate_unique_string()
            gsk_survey_qb_input.write({'gp_candidate':self.candidate_id.id , 'dgs_batch':dgs_exam})
            gsk_online_carry_forward = False
            gsk_online_marks = self.gp_exam.gsk_online_marks
            gsk_online_percentage = self.gp_exam.gsk_online_percentage
            

            ## MEK Marks Forwarding
            mek_survey_qb_input = self.gp_exam.mek_online
            mek_online_carry_forward = True
            mek_online_marks = self.gp_exam.mek_online_marks
            mek_online_percentage = self.gp_exam.mek_online_percentage
            print("MEK Forwarding")
            
        elif not self.gsk_online_status == 'failed' and  self.mek_online_status == 'failed':
           
            ## GSK Marks Forwarding
            print("GSK Forwarding")

            gsk_survey_qb_input = self.gp_exam.gsk_online
            gsk_online_marks = self.gp_exam.gsk_online_marks
            gsk_online_percentage = self.gp_exam.gsk_online_percentage
            gsk_online_carry_forward = True
            ## MEK QB Assigning
            
            mek_survey_qb_input = self.mek_survey_qb._create_answer(user=self.candidate_id.user_id)
            token = mek_survey_qb_input.generate_unique_string()
            mek_survey_qb_input.write({'gp_candidate':self.candidate_id.id ,'dgs_batch':dgs_exam  })
            mek_online_carry_forward = False
            mek_online_marks = self.gp_exam.mek_online_marks
            mek_online_percentage = self.gp_exam.mek_online_percentage
        else:
            # GSK Marks Forwarding
            gsk_survey_qb_input = self.gp_exam.gsk_online
            gsk_online_marks = self.gp_exam.gsk_online_marks
            gsk_online_percentage = self.gp_exam.gsk_online_percentage
            gsk_online_carry_forward = True
            
            ## MEK Marks Forwarding
            mek_survey_qb_input = self.gp_exam.mek_online
            mek_online_carry_forward = True
            mek_online_marks = self.gp_exam.mek_online_marks
            mek_online_percentage = self.gp_exam.mek_online_percentage
            

            
        overall_marks = self.gp_exam.overall_marks
        
        overall_percentage = self.gp_exam.overall_percentage
        
            
        
        gp_exam_schedule.write({
                                "registered_institute":self.institute_id.id,
                                "mek_oral":mek_oral.id,
                                "mek_prac":mek_practical.id,
                                "gsk_oral":gsk_oral.id,
                                "gsk_prac":gsk_practical.id , 
                                "gsk_online":gsk_survey_qb_input.id, 
                                "mek_online":mek_survey_qb_input.id,
                                "gsk_practical_marks":gsk_practical_marks,
                                "gsk_oral_marks":gsk_oral_marks,
                                "gsk_total":gsk_total,
                                "gsk_percentage":gsk_percentage,
                                "mek_practical_marks":mek_practical_marks,
                                "mek_oral_marks":mek_oral_marks,
                                "mek_total":mek_total,
                                "mek_percentage":mek_percentage,
                                "mek_online_marks":mek_online_marks,
                                "mek_online_percentage":mek_online_percentage,
                                "gsk_online_marks":gsk_online_marks,
                                "gsk_online_percentage":gsk_online_percentage,
                                "overall_marks":overall_marks,
                                "overall_percentage":overall_percentage,
                                "gsk_oral_prac_carry_forward":gsk_oral_prac_carry_forward,
                                "mek_oral_prac_carry_forward":mek_oral_prac_carry_forward,
                                "mek_online_carry_forward":mek_online_carry_forward,
                                "gsk_online_carry_forward":gsk_online_carry_forward
                                
                                })

        # gp_exam_schedule.write({"gsk_online":gsk_survey_qb_input.id,"mek_online":mek_survey_qb_input.id})
    
    # def register_exam(self):
        # dgs_exam = self.dgs_batch.id
        # exam_id = self.env['ir.sequence'].next_by_code("gp.exam.sequence")

        # gp_exam_schedule_vals = {
        #     'gp_candidate': self.candidate_id.id,
        #     'dgs_batch': dgs_exam,
        #     'exam_id': exam_id
        # }

        # if self.gsk_oral_prac_status == 'failed':
        #     gsk_practical_vals = {"exam_id": None, 'gsk_practical_parent': self.candidate_id.id, 'institute_id': self.institute_id.id}
        #     gsk_oral_vals = {"exam_id": None, 'gsk_oral_parent': self.candidate_id.id, 'institute_id': self.institute_id.id}
        # else:
        #     gsk_practical_vals = {}
        #     gsk_oral_vals = {}

        # if self.mek_oral_prac_status == 'failed':
        #     mek_practical_vals = {"exam_id": None, 'mek_parent': self.candidate_id.id, 'institute_id': self.institute_id.id}
        #     mek_oral_vals = {"exam_id": None, 'mek_oral_parent': self.candidate_id.id, 'institute_id': self.institute_id.id}
        # else:
        #     mek_practical_vals = {}
        #     mek_oral_vals = {}

        # if self.mek_online_status == 'failed':
        #     mek_survey_qb_input = self.mek_survey_qb._create_answer(user=self.candidate_id.user_id)
        # else:
        #     mek_survey_qb_input = None

        # if self.gsk_online_status == 'failed':
        #     gsk_survey_qb_input = self.gsk_survey_qb._create_answer(user=self.candidate_id.user_id)
        # else:
        #     gsk_survey_qb_input = None

        # gp_exam_schedule_vals.update({
        #     'mek_oral': mek_oral_vals.get('id'),
        #     'mek_prac': mek_practical_vals.get('id'),
        #     'gsk_oral': gsk_oral_vals.get('id'),
        #     'gsk_prac': gsk_practical_vals.get('id'),
        #     'gsk_online': gsk_survey_qb_input.id if gsk_survey_qb_input else None,
        #     'mek_online': mek_survey_qb_input.id if mek_survey_qb_input else None
        # })

        # gp_exam_schedule = self.env["gp.exam.schedule"].create(gp_exam_schedule_vals)

        # if self.gsk_oral_prac_status == 'failed':
        #     gsk_practical_vals['exam_id'] = gp_exam_schedule.id
        #     gsk_oral_vals['exam_id'] = gp_exam_schedule.id
        #     gsk_practical = self.env["gp.gsk.practical.line"].create(gsk_practical_vals)
        #     gsk_oral = self.env["gp.gsk.oral.line"].create(gsk_oral_vals)
        # else:
        #     gsk_practical = self.gp_exam.gsk_prac
        #     gsk_oral = self.gp_exam.gsk_oral
            
        #     gsk_practical_marks = self.gp_exam.gsk_practical_marks
        #     gsk_oral_marks = self.gp_exam.gsk_oral_marks
        #     gsk_total = self.gp_exam.gsk_total

        # if self.mek_oral_prac_status == 'failed':
        #     mek_practical_vals['exam_id'] = gp_exam_schedule.id
        #     mek_oral_vals['exam_id'] = gp_exam_schedule.id
        #     mek_practical = self.env["gp.mek.practical.line"].create(mek_practical_vals)
        #     mek_oral = self.env["gp.mek.oral.line"].create(mek_oral_vals)
        # else:
        #     mek_practical = self.gp_exam.mek_prac
        #     mek_oral = self.gp_exam.mek_oral
            
        #     mek_practical_marks = self.gp_exam.mek_practical_marks
        #     mek_oral_marks = self.gp_exam.mek_oral_marks
        #     mek_total = self.gp_exam.mek_total


        # gp_exam_schedule.write({
        #     "mek_oral": mek_oral.id,
        #     "mek_prac": mek_practical.id,
        #     "gsk_oral": gsk_oral.id,
        #     "gsk_prac": gsk_practical.id
        # })

        # return gp_exam_schedule



class CandidateCCMCRegisterExamWizard(models.TransientModel):
    _name = 'candidate.ccmc.register.exam.wizard'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Register Exam'
    
    exam_region = fields.Many2one("exam.center",string="Exam Region",tracking=True)
    dgs_batch = fields.Many2one("dgs.batches",string="Exam Batch",required=False,tracking=True)

    institute_ids = fields.Many2many("bes.institute",string="Institute",compute="_compute_institute_ids",tracking=True)
    institute_id = fields.Many2one("bes.institute",string="Institute",tracking=True)
    candidate_id = fields.Many2one("ccmc.candidate",string="Candidate",required=True,tracking=True)
    
    cookery_bakery_qb = fields.Many2one("survey.survey",string="Cookery Bakery Question Bank Template",tracking=True)


    ccmc_exam = fields.Many2one("ccmc.exam.schedule",string="CCMC Exam",required=True,tracking=True)
    
    
    previous_attempt =  fields.Integer("Previous Attempt No.",tracking=True)
    # batch_id = fields.Many2one("institute.gp.batches",string="Batches",required=True)

    
    exam_month = fields.Selection([
        ('dec_feb', 'Dec - Feb'),
        ('mar_jun', 'Mar - Jun'),
        ('jul_aug', 'Jul - Aug'),
        ('sep_nov', 'Sep - Nov'),
    ], string='Exam Month',tracking=True)
    
    
    cookery_bakery_status = fields.Selection([
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='Cookery Bakery Oral/Prac Status',compute="_compute_cookery_bakery_status",tracking=True)
    
    
    
    # ccmc_oral_status = fields.Selection([
    #     ('failed', 'Failed'),
    #     ('passed', 'Passed'),
    # ], string='CCMC Oral Status',compute="_compute_ccmc_oral_status")
    
    
    ccmc_online = fields.Selection([
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='CCMC Online',compute="_compute_ccmc_online",tracking=True)
    

    @api.depends('ccmc_exam')
    def _compute_cookery_bakery_status(self):
         for record in self:
             
             if record.ccmc_exam.cookery_bakery_prac_status == 'passed' and record.ccmc_exam.ccmc_oral_prac_status == 'passed':
                record.cookery_bakery_status = 'passed'
             else:
                record.cookery_bakery_status = 'failed'
             
    
    
    @api.depends('ccmc_exam')
    def _compute_ccmc_online(self):
         for record in self:
             record.ccmc_online = record.ccmc_exam.ccmc_online_status
    
    # @api.depends('ccmc_exam')
    # def _compute_ccmc_oral_status(self):
    #      for record in self:
    #          record.ccmc_oral_status = record.ccmc_exam.ccmc_oral_prac_status
    
    
    @api.depends('exam_region')
    def _compute_institute_ids(self):
        for record in self:
            
            exam_region = record.exam_region.id
            record.institute_ids = self.env["bes.institute"].search([('exam_center','=',exam_region)])
            
    
    def register_exam(self):
        
        dgs_batch = self.dgs_batch.id
        exam_id  = self.env['ir.sequence'].next_by_code("ccmc.exam.schedule")
        
        # Marks
        cookery_practical = self.ccmc_exam.cookery_practical
        cookery_oral = self.ccmc_exam.cookery_oral
        cookery_gsk_online = self.ccmc_exam.cookery_gsk_online
        overall_marks = self.ccmc_exam.overall_marks
        
        #Mark Percentage
        cookery_bakery_percentage = self.ccmc_exam.cookery_bakery_percentage
        ccmc_oral_percentage = self.ccmc_exam.ccmc_oral_percentage
        cookery_gsk_online_percentage = self.ccmc_exam.cookery_gsk_online_percentage
        overall_percentage = self.ccmc_exam.overall_percentage
        
        ccmc_exam_schedule = self.env["ccmc.exam.schedule"].create({
            'registered_institute':self.institute_id.id,
            'ccmc_candidate':self.candidate_id.id,
            'exam_id':exam_id,
            'dgs_batch':dgs_batch,
            'cookery_practical':cookery_practical,
            'cookery_oral':cookery_oral,
            'cookery_gsk_online':cookery_gsk_online,
            'overall_marks':overall_marks ,
            'cookery_bakery_percentage':cookery_bakery_percentage,
            'ccmc_oral_percentage':ccmc_oral_percentage,
            'cookery_gsk_online_percentage':cookery_gsk_online_percentage,
            'overall_percentage':overall_percentage,
            'cookery_bakery_prac_status':self.ccmc_exam.cookery_bakery_prac_status,
            'ccmc_oral_prac_status':self.ccmc_exam.ccmc_oral_prac_status
            
            })

        
        if self.cookery_bakery_status == 'failed':
            cookery_bakery = self.env["ccmc.cookery.bakery.line"].create({"exam_id":ccmc_exam_schedule.id,'cookery_parent':self.candidate_id.id,'institute_id': self.institute_id.id})
            ccmc_oral = self.env["ccmc.oral.line"].create({"exam_id":ccmc_exam_schedule.id,'ccmc_oral_parent':self.candidate_id.id,'institute_id': self.institute_id.id})
            ccmc_gsk_oral = self.env["ccmc.gsk.oral.line"].create({"exam_id":ccmc_exam_schedule.id,'ccmc_oral_parent':self.candidate_id.id,'institute_id': self.institute_id.id})
            
        else:
            cookery_bakery = self.ccmc_exam.cookery_bakery
            ccmc_oral =self.ccmc_exam.ccmc_oral
        
        
        
        
        if self.ccmc_online == 'failed':
            cookery_bakery_qb_input = self.cookery_bakery_qb._create_answer(user=self.candidate_id.user_id)
            cookery_bakery_qb_input.write({'ccmc_candidate':self.candidate_id.id})
        else:
            cookery_bakery_qb_input = self.ccmc_exam.ccmc_online
        

            
        
        ccmc_exam_schedule.write({"cookery_bakery":cookery_bakery.id,"ccmc_oral":ccmc_oral.id,"ccmc_online":cookery_bakery_qb_input.id})
        

        
        
        # gp_exam_schedule.write({"gsk_online":gsk_survey_qb_input.id,"mek_online":mek_survey_qb_input.id})


            
        # gsk_survey_qb_input = gsk_survey_qb._create_answer(user=candidate.user_id)
            
            
            
        
        
        
        # xw("ok")
        
    
    # @api.onchange('exam_month')
    # def _onchange_exam_month(self):
    #     # Example: Set a domain to only allow child records with age greater than 5
    #     # import wdb; wdb.set_trace(); 
    #     if self.exam_month == 'dec_feb' or self.exam_month== 'jul_aug':
            
    #         return {
    #             'domain': {
    #                 'institute_id': [('institute_repeater', '=', True)]
    #             }
    #         }
    #     else:
    #         return {}
    
    
    # def register(self):
    #     gp_exam = self.env["gp.exam.schedule"].sudo().create({})
    #     if self.mek_oral_prac_status == 'failed':
            
            
            
class SEPCandidate(models.Model):
    _name = 'sep.candidate'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'GP Candidate'
    
    institute_batch_id = fields.Many2one("institute.gp.batches","Batch",tracking=True)

    gsk_candidate_child_line = fields.One2many("sep.candidate.line","sep_candidate_parent",string="SEP Registration",tracking=True)
    def name_get(self):
        result = []
        for record in self:
            name = f"{record.institute_batch_id.batch_name} "  # Customize the display name as needed
            result.append((record.id, name))
        return result
        
        
        
        
class SEPCandidateLine(models.Model):
    _name = 'sep.candidate.line'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'GP Candidate Line'
    _rec_name = 'institute_batch_id'
    
    institute_batch_id = fields.Many2one("institute.gp.batches","Batch",tracking=True)

    sep_candidate_parent = fields.Many2one("sep.candidate",string="SEP Registration Line",tracking=True)
    name = fields.Char("Name of the Rating's",tracking=True)
    dob = fields.Date("DOB",help="Date of Birth", 
                      widget="date", 
                      date_format="%d-%b-%y",tracking=True)
    indos_no= fields.Char("Indos No",tracking=True)
    cdc_no= fields.Char("CDC No",tracking=True)
    contact= fields.Char("Contact No",tracking=True)
    email= fields.Char("Email ID",tracking=True)
    attendance1= fields.Boolean("1st Day Attendance",tracking=True)
    attendance2= fields.Boolean("2nd Day Attendance",tracking=True)
    vaccination= fields.Boolean("Vaccination/RTPCR",tracking=True)
    remarks= fields.Char("Remark",tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ],compute='_compute_state', string='Status', default='draft' ,tracking=True)

    @api.depends('attendance1', 'attendance2')
    def _compute_state(self):
        for record in self:
            if record.attendance1 and record.attendance2:
                record.state = 'confirmed'
            else:
                record.state = 'draft'

    def print_certificate(self):
        return self.env.ref('bes.action_report_certificate').report_action(self)
        

class SEPCertificateReport(models.AbstractModel):
    _name = 'report.bes.sep_certificate'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'SEP Certificate Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        records = self.env['sep.candidate.line'].browse(docids)
        if not records:
            raise ValueError("No records found for docids: %s" % docids)
        return {
            'records': records,
            'data': data,
        }


# class ComingGPRepeatersCandidates(models.Model):
#     _name = 'coming.gp.repeater.candidate'
#     _inherit = ['mail.thread','mail.activity.mixin']
#     _description = 'Coming Repeater Candidates'
#     _rec_name = 'indos_no'
    
    
#     indos_no = fields.Char("Indos No",tracking=True)
#     name = fields.Char("Name",tracking=True)
#     candidate_code = fields.Char("Candidate Code",tracking=True)

# class ComingCCMCRepeatersCandidates(models.Model):
#     _name = 'coming.ccmc.repeater.candidate'
#     _inherit = ['mail.thread','mail.activity.mixin']
#     _description = 'Coming Repeater Candidates'
#     _rec_name = 'indos_no'
    
    
#     indos_no = fields.Char("Indos No",tracking=True)
#     name = fields.Char("Name",tracking=True)
#     candidate_code = fields.Char("Candidate Code",tracking=True)