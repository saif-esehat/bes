from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
from datetime import datetime, timedelta



class Examiner(models.Model):
    _name = "bes.examiner"
    _description= 'Examiner'
    _rec_name = 'name'
    _inherit = ['mail.thread','mail.activity.mixin']
    examiner_image = fields.Binary(string='Examiner Image', attachment=True, help='Select an image in JPEG format.',tracking=True)
    user_id = fields.Many2one("res.users", "Portal User",tracking=True)
    exam_center = fields.Many2one("exam.center", "Exam Region",tracking=True)

    name = fields.Char("Name",required=True,tracking=True)
    street = fields.Char("Street",tracking=True)
    street2 = fields.Char("Street2",tracking=True)
    city = fields.Char("City",required=True,tracking=True)
    zip = fields.Char("Zip",required=True, validators=[api.constrains('zip')],tracking=True)
    state_id = fields.Many2one("res.country.state","State",required=True,domain=[('country_id.code','=','IN')],tracking=True)
    phone = fields.Char("Phone", validators=[api.constrains('phone')],tracking=True)
    mobile = fields.Char("Mobile", validators=[api.constrains('mobile')],required=True,tracking=True )
    email = fields.Char("Email", validators=[api.constrains('email')],required=True,tracking=True)
    
    pan_no = fields.Char("Pan No .",required=True,tracking=True)
    dob = fields.Date("DOB",help="Date of Birth", required=True,
                      widget="date", 
                      date_format="%d-%b-%y",tracking=True)
    present_designation = fields.Text("Present Designation",required=True)
    name_address_present_employer = fields.Text("Name and address of present employer",required=True,tracking=True)
    designation = fields.Selection([
        ('master', 'Master Mariner'),
        ('chief', 'Chief Engineer'),
        ('catering','Catering Officer')
    ], string='Rank',default='master',tracking=True)
    competency_no = fields.Char("Certificate of competency no.",tracking=True)
    date_of_issue = fields.Date("Date of Issue",required=True,tracking=True)
    member_of_imei_cmmi = fields.Selection([
        ('imei', 'IMEI'),
        ('cmmi', 'CMMI')
    ], string='Are you a member of IMEI or CMMI?',default='no',tracking=True)
    membership_no = fields.Char("Membership No.",tracking=True)
    institute_association = fields.Boolean("Are you associated with any institute conducting ratings training?",tracking=True)
    associated_training_institute = fields.Text("Name & address of the training institute to which you were associated",tracking=True)
    present_employer_clearance = fields.Boolean("Have you taken clearance from your present employer to work on part time basis for BES?",tracking=True)
    subject_id = fields.Many2one("course.master.subject","Subject",tracking=True)
    payment_details = fields.One2many("examiner.assignment","examiner_id","Payment Details",tracking=True)
    acc_no = fields.Char(string="Account Number",tracking=True)
    ifsc_code = fields.Char(string="IFSC Code",tracking=True)
    bank_name = fields.Char(string="Bank Name",tracking=True)
    exam_coordinator = fields.Boolean("Exam Coordinator",tracking=True)
    exam_coordinator_id = fields.Boolean("Exam Coordinator ID",tracking=True)
    assignments = fields.One2many("examiner.assignment","examiner_id","Assignments",tracking=True)
    exam_assignments = fields.One2many("examiner.assignment","examiner_id",string="Exam Assignments",tracking=True)
    
    
    
    state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], string='State',compute="_compute_examiner_state",default="active",tracking=True)
    
    
    def get_examiner_region(self):
        user_id = self.env.user.id
        region = self.env['exam.center'].sudo().search([('exam_co_ordinator','=',user_id)]).id
        return region
    
    
    @api.depends('user_id')
    def _compute_examiner_state(self):
        for record in self:
            if record.user_id and record.user_id.active:
                record.state = "active"
            else:
                record.state = "inactive"
                

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

    @api.constrains('mobile')
    def _check_valid_mobile(self):
        for record in self:
            # Check if mobile has 10 digits
            if record.mobile and not record.mobile.isdigit() or len(record.mobile) != 10:
                raise ValidationError("Mobile number must be 10 digits.")

    @api.constrains('email')
    def _check_valid_email(self):
        for record in self:
            # Check if email has @ symbol
            if record.email and '@' not in record.email:
                raise ValidationError("Invalid email address. Must contain @ symbol.")  
                  
    @api.onchange('designation')
    def _onchange_compute_subject_id(self):
        if self.designation == 'master':
            subject_id = self.env["course.master.subject"].sudo().search([('name','=','GSK')]).id
            self.subject_id = subject_id
        elif self.designation == 'chief':
            subject_id = self.env["course.master.subject"].sudo().search([('name','=','MEK')]).id
            self.subject_id = subject_id
        else:
            self.subject_id = False
    
    
    @api.onchange('designation')
    def _onchange_compute_member_of_imei_cmmi(self):
        if self.designation == 'master':
            rank = 'cmmi'
            self.member_of_imei_cmmi = rank
        elif self.designation == 'chief':
            rank = 'imei'
            self.member_of_imei_cmmi = rank
        else:
            self.member_of_imei_cmmi = False
            


    @api.model
    def create(self, values):
        examiner = super(Examiner, self).create(values)
        group_xml_id = 'bes.group_examiners'
        
        user_values = {
            'name': examiner.name,
            'login': examiner.email,  # You can set the login as the same as the user name
            'password': 12345678,  # Generate a random password
            'sel_groups_1_9_10':1
        }

        group_id = self.env.ref(group_xml_id).id
        print(group_id)
        # import wdb; wdb.set_trace()
        
        portal_user = self.env['res.users'].sudo().create(user_values)
        portal_user.write({'groups_id': [(4, group_id)]  })
        examiner.write({'user_id': portal_user.id})  # Associate the user with the institute
        examiner_tag = self.env.ref('bes.examiner_tags').id
        portal_user.partner_id.write({'email': examiner.email,'phone':examiner.phone,'mobile':examiner.mobile,'street':examiner.street,'street2':examiner.street2,'city':examiner.city,'zip':examiner.zip,'state_id':examiner.state_id.id,'category_id':[examiner_tag]})
        return examiner



class ExaminerAssignment(models.Model):
    _name = "examiner.assignment"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'Examiner Assignment'
    
    
    examiner_id = fields.Many2one("bes.examiner","Examiner",tracking=True)
    assignment_date = fields.Date("Assignment Date",tracking=True)
    exam_region = fields.Many2one('exam.center',"Exam Region",tracking=True)
    # exam_date = fields.Date("Exam Date")
    exam_start_time = fields.Datetime("Exam Start Time",tracking=True)
    exam_end_time = fields.Datetime("Exam End Time",tracking=True)
    gsk_boolean = fields.Boolean("GSK Boolean" ,compute="_compute_boolean",tracking=True)
    mek_boolean = fields.Boolean("MEK Boolean" ,compute="_compute_boolean",tracking=True)
    assigned_to = fields.Selection([
        ('gp_candidate', 'GP Candidate'),
        ('ccmc_candidate', 'CCMC Candidate'),
    ], string='Assigned to',default="gp_candidate",tracking=True)
    course = fields.Many2one("course.master","Course",tracking=True)
    subject_id = fields.Many2one("course.master.subject","Subject",tracking=True)
    institute_id = fields.Many2one('bes.institute',string="Institute",tracking=True)
    gp_batches = fields.Many2one('institute.gp.batches',string="GP Batches",domain="[('institute_id', '=', institute_id)]",tracking=True)
    gp_candidates = fields.Many2many("gp.candidate",string="GP Candidate",compute="_compute_gp_candidates",tracking=True)
    ccmc_batches = fields.Many2one('institute.ccmc.batches',string="CCMC Batches",domain="[('institute_id', '=', institute_id)]",tracking=True)
    ccmc_candidates = fields.Many2many("ccmc.candidate",string="CCMC Candidate",tracking=True)
    gp_oral_prac = fields.One2many("gp.candidate.oral.prac.assignment","assignment_id",string="GP Assignment",tracking=True)
    ccmc_assignment = fields.One2many("ccmc.candidate.assignment","assignment_id",string="CCMC Assignment",tracking=True)

    
    def update_candidate_from_institute(self):
        if not self.institute_id:
            raise ValidationError("Institute Not Selected")
        
        if self.subject_id.name == 'GSK':
            self.gp_oral_prac.unlink()
            practical_line_candidates = set(self.env["gp.gsk.practical.line"].search([('institute_id','=',self.institute_id.id),('gsk_practical_draft_confirm','=','draft')]).mapped('gsk_practical_parent'))
            oral_line_candidates = set(self.env["gp.gsk.oral.line"].search([('institute_id','=',self.institute_id.id),('gsk_oral_draft_confirm','=','draft')]).mapped('gsk_oral_parent'))
            gp_candidates = list(practical_line_candidates.intersection(oral_line_candidates))
            
            for candidate in gp_candidates:
                candidate_id = candidate.id
                gsk_oral_child_line = candidate.gsk_oral_child_line.filtered(lambda r: r.gsk_oral_draft_confirm == 'draft')
                gsk_practical_child_line = candidate.gsk_practical_child_line.filtered(lambda r: r.gsk_practical_draft_confirm == 'draft')
                self.env["gp.candidate.oral.prac.assignment"].create({"assignment_id":self.id,"gsk_oral":gsk_oral_child_line.id,"gsk_prac":gsk_practical_child_line.id,"gp_candidate":candidate_id})
        
        elif self.subject_id.name == 'MEK':
            self.gp_oral_prac.unlink()
            practical_line_candidates = set(self.env["gp.mek.practical.line"].search([('institute_id','=',self.institute_id.id),('mek_practical_draft_confirm','=','draft')]).mapped('mek_parent'))
            oral_line_candidates = set(self.env["gp.mek.oral.line"].search([('institute_id','=',self.institute_id.id),('mek_oral_draft_confirm','=','draft')]).mapped('mek_oral_parent'))
            gp_candidates = list(practical_line_candidates.intersection(oral_line_candidates))
            
            for candidate in gp_candidates:
                candidate_id = candidate.id
                mek_oral_child_line = candidate.mek_oral_child_line.filtered(lambda r: r.mek_oral_draft_confirm == 'draft')
                mek_practical_child_line = candidate.mek_practical_child_line.filtered(lambda r: r.mek_practical_draft_confirm == 'draft')
                self.env["gp.candidate.oral.prac.assignment"].create({"assignment_id":self.id,"mek_oral":mek_oral_child_line.id,"mek_prac":mek_practical_child_line.id,"gp_candidate":candidate_id})
            
        elif self.subject_id.name == 'CCMC':
            self.ccmc_assignment.unlink()
            practical_line_candidates = set(self.env["ccmc.cookery.bakery.line"].search([('institute_id','=',self.institute_id.id),('cookery_draft_confirm','=','draft')]).mapped('cookery_parent'))
            oral_line_candidates = set(self.env["ccmc.oral.line"].search([('institute_id','=',self.institute_id.id),('ccmc_oral_draft_confirm','=','draft')]).mapped('ccmc_oral_parent'))
            ccmc_candidates = list(practical_line_candidates.intersection(oral_line_candidates))
            
            for candidate in ccmc_candidates:
                candidate_id = candidate.id
                ccmc_oral_child_line = candidate.ccmc_oral_child_line.filtered(lambda r: r.ccmc_oral_draft_confirm == 'draft')
                ccmc_practical_child_line = candidate.cookery_child_line.filtered(lambda r: r.cookery_draft_confirm == 'draft')
                self.env["ccmc.candidate.assignment"].create({"assignment_id":self.id,"ccmc_oral":ccmc_oral_child_line.id,"cookery_bakery":ccmc_practical_child_line.id,"ccmc_candidate":candidate_id})
            
            
            
                            
            
    @api.depends('subject_id')
    def _compute_boolean(self):
        for record in self:
            if record.subject_id.name == 'GSK':
                record.gsk_boolean = True
            else :
                record.gsk_boolean = False
                
            if record.subject_id.name == 'MEK':
                record.mek_boolean = True
            else :
                record.mek_boolean = False


    @api.depends('gp_batches')
    def _compute_gp_candidates(self):
        for record in self:
            students = self.env['gp.candidate'].search([('institute_batch_id','=',record.gp_batches.id)])
            # print("Students",students)
            record.gp_candidates = students

    
    
    # @api.constrains('exam_date', 'subject_id', 'gp_candidates')
    # def _check_duplicate_assignment(self):
    #     for record in self:
    #         # Check if the same candidate is assigned to the same subject
    #         # import wdb;wdb.set_trace()
    #         # if len(record.gp_candidates.filtered(lambda c: c in record.subject_id.gp_candidates)) > 1:
    #         #     raise ValidationError("A candidate cannot be assigned twice to the same subject.")

    #         # Check if the same subject is scheduled within 90 days
    #          for candidate in record.gp_candidates:
    #             # Check if the same candidate has an exam for the same subject within 90 days
    #             similar_assignments = self.search([
    #                 ('id', '!=', record.id),
    #                 ('subject_id', '=', record.subject_id.id),
    #                 ('gp_candidates', 'in', candidate.id),
    #                 # ('exam_date', '>=', fields.Date.to_string(fields.Date.from_string(record.exam_date) - timedelta(days=90))),
    #                 # ('exam_date', '<=', record.exam_date)
    #             ])
    #             if similar_assignments:
    #                 raise ValidationError(f"{candidate.name} cannot have an exam for the same subject within 90 days.")



class GPOralPracAssignment(models.Model):
    _name = "gp.candidate.oral.prac.assignment"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'GP Candidate Oral Practical Assignment'
    
    assignment_id = fields.Many2one("examiner.assignment","Assignment ID",tracking=True)
    gp_candidate = fields.Many2one("gp.candidate","Candidate",tracking=True)
    gsk_oral = fields.Many2one("gp.gsk.oral.line","GSK Oral",tracking=True)
    gsk_prac = fields.Many2one("gp.gsk.practical.line","GSK Practical",tracking=True)
    mek_oral = fields.Many2one("gp.mek.oral.line","MEK Oral",tracking=True)
    mek_prac = fields.Many2one("gp.mek.practical.line","MEK Practical",tracking=True)

class CCMCOralPracAssignment(models.Model):
    _name = "ccmc.candidate.assignment"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'CCMC Candidate Assignment'
    
    assignment_id = fields.Many2one("examiner.assignment","Assignment ID",tracking=True)
    ccmc_candidate = fields.Many2one("ccmc.candidate","Candidate",tracking=True)
    cookery_bakery = fields.Many2one("ccmc.cookery.bakery.line","Cookery Bakery",tracking=True)
    ccmc_oral = fields.Many2one("ccmc.oral.line","CCMC Oral",tracking=True)
    
    
class ExaminerTimeSheet(models.Model):
    _name = "examiner.time.sheet"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Examiner Time Sheet'
    
    examiner_id = fields.Many2one('bes.examiner','Examiner',tracking=True)
    assignment_id = fields.Many2one('examiner.assignment','Assignment ID',tracking=True)
    exam_region = fields.Many2one('exam.center', 'Place',tracking=True)
    # date_of_examination = fields.Many2one('')
    remarks = fields.Char('Remakrs')
    remarks_quality = fields.Char('Remarks on the quality of transport and logistics',tracking=True)
    
    state = fields.Selection([
        ('active', '1'),
        ('inactive', '2')
    ], string='State',default="active",tracking=True)
    
    examination_details = fields.One2many('time.sheet.exam','examiner_id','Time Sheet for Examination',tracking=True)
    
    travelling_details = fields.One2many('time.sheet.travel.detail','travel_id',"Travelling Details",tracking=True)
    
    
    
class ExaminerTimeSheetTravelling(models.Model):
    _name = "time.sheet.travel.detail"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Examiner Travelling Details'
    
    
    # examiner_id = fields.Many2one('bes.examiner','Examiner')
    travel_id = fields.Many2one('bes.examiner','Examiner',tracking=True)
    travel_details = fields.Selection([
        ('left_residence','Left Residence'),
        ('arrival_institute','Arrival at the Institute/Hotel'),
        ('left_institute','Left the Institute/Hotel'),
        ('arrival_residence','Arrival at Residence')],string='Travelling Details',tracking=True)
    date_time = fields.Datetime('Date and Time',tracking=True)
    mode_of_travel = fields.Char('Mode of travel',tracking=True)


class ExaminerTimeSheetExaminatopn(models.Model):
    _name = "time.sheet.exam"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Examiner Time Sheet Examination'
    
    examiner_id = fields.Many2one('bes.examiner','Examiner',tracking=True)
    arrival_institute = fields.Datetime('Date & Time of arrival at the Institute',tracking=True)
    exam_start = fields.Datetime('Commencement of Practical/Oral Examination',tracking=True)
    lunch_break = fields.Datetime('Lunch Break',tracking=True)
    time_of_completion = fields.Datetime('Time of completion',tracking=True)
    debriefing_institute = fields.Datetime('Time spent for debriefing the Institute (Last day of examination)',tracking=True)