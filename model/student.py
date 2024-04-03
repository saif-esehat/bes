from odoo import api, fields, models , _, exceptions
from odoo.exceptions import UserError,ValidationError
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import datetime 


class GPCandidate(models.Model):
    _name = 'gp.candidate'
    _description = 'GP Candidate'
    
    institute_batch_id = fields.Many2one("institute.gp.batches","Batch")

    institute_id = fields.Many2one("bes.institute",string="Name of Institute")
    candidate_image_name = fields.Char("Candidate Image Name")
    candidate_image = fields.Binary(string='Candidate Image', attachment=True, help='Select an image')
    candidate_signature_name = fields.Char("Candidate Signature")
    candidate_signature = fields.Binary(string='Candidate Signature', attachment=True, help='Select an image')
    name = fields.Char("Full Name of Candidate as in INDOS",required=True)
    age = fields.Float("Age",compute="_compute_age")
    indos_no = fields.Char("Indos No.")
    candidate_code = fields.Char("GP Candidate Code No.")
    roll_no = fields.Char("Roll No.")
    dob = fields.Date("DOB",help="Date of Birth", 
                      widget="date", 
                      date_format="%d-%b-%y")
    user_id = fields.Many2one("res.users", "Portal User")
    street = fields.Char("Street")
    street2 = fields.Char("Street2")
    city = fields.Char("City")
    zip = fields.Char("Zip", validators=[api.constrains('zip')])
    state_id = fields.Many2one("res.country.state","State",domain=[('country_id.code','=','IN')])
    phone = fields.Char("Phone")
    mobile = fields.Char("Mobile", validators=[api.constrains('mobile')])
    email = fields.Char("Email", validators=[api.constrains('email')])
    tenth_percent = fields.Integer("% Xth Std in Eng.")
    twelve_percent = fields.Integer("% 12th Std in Eng.")
    iti_percent = fields.Integer("% ITI")
    sc_st = fields.Boolean("To be mentioned if Candidate SC/ST")
    ship_visits_count = fields.Char("No. of Ship Visits")
    elligiblity_criteria = fields.Selection([
        ('elligible', 'Elligible'),
        ('not_elligible', 'Not Elligible')
    ],string="Elligiblity Criteria",compute="_compute_eligibility", default='not_elligible')
    
    fees_paid = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ],string="Fees Paid", default='no')
    
    invoice_no = fields.Char("Invoice No",compute="_compute_invoice_no",store=True)
    batch_exam_registered = fields.Boolean("Batch Registered")
    qualification = fields.Selection([
        ('tenth', '10th std'),
        ('twelve', '12th std'),
        ('iti', 'ITI')
    ],string="Qualification", default='tenth')

    candidate_attendance_record = fields.Integer("Candidate Attendance Record")
    
    
    attendance_compliance_1 = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ],string="Whether Attendance record of the candidate comply with DGS Guidelines 1 of 2018 as per para 3.2 for GP / 7 of 2010 as per para 3.3 for CCMC (YES/ NO)", default='no')
    
    attendance_compliance_2 = fields.Selection([
         ('yes', 'Yes'),
         ('no', 'No')
    ], string="Attendance record of the candidate not comply with DGS Guidelines 1 of 2018 as per para 3.2 for GP / 7 of 2010 as per para 3.3 for CCMC and whether same has been informed to the DGS (YES/ NO)", default='no')

    stcw_certificate = fields.One2many("gp.candidate.stcw.certificate","candidate_id",string="STCW Certificate")
    
    
    # attendance_compliance_2 = fields.Boolean([
    #     ('yes', 'Yes'),
    #     ('no', 'No')
    # ],string="Attendance record of the candidate not comply with DGS Guidelines 1 of 2018 as per para 3.2 for GP / 7 of 2010 as per para 3.3 for CCMC and whether same has been informed to the DGS (YES/ NO)", default='no')
    
    
    ship_visits = fields.One2many("gp.candidate.ship.visits","candidate_id",string="Ship Visit")
    
    
    ## Mek and GSK Online Exam
    mek_online = fields.One2many("survey.user_input","gp_candidate",domain=[("survey_id.subject.name", "=", 'GSK')],string="MEK Online")
    gsk_online = fields.One2many("survey.user_input","gp_candidate",domain=[("survey_id.subject.name", "=", 'MEK')],string="GSK Online")
    
    # @api.constrains('institute_batch_id')
    # def _check_record_number_constraint(self):
    #     for record in self:
    #         capacity = record.institute_batch_id.dgs_approved_capacity
    #         self.env["gp.candidate"].sudo().search_count([('institute_batch_id','=',)])
           

    
    @api.constrains('zip')
    def _check_valid_zip(self):
        for record in self:
            if record.zip and not record.zip.isdigit() or len(record.zip) != 6:
                raise ValidationError("Zip code must be 6 digits.")

    # @api.constrains('phone')
    # def _check_valid_phone(self):
    #     for record in self:
    #         # Check if phone has 8 digits
    #         if record.phone and not record.phone.isdigit() or len(record.phone) != 8 or len(record.phone) != 0:
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
        institute_batch_id  = int(values['institute_batch_id'])

        gp_batches = self.env["institute.gp.batches"].search([('id','=',institute_batch_id)])
        # gp_batches = self.institute_batch_id

        
        capacity = gp_batches.dgs_approved_capacity - 1
        # capacity = gp_batches.dgs_approved_capacity 
        
        candidate_count = self.env["gp.candidate"].sudo().search_count([('institute_batch_id','=',institute_batch_id)])  
       
        if candidate_count <= capacity:
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
    _description = 'STCW'
    
    candidate_id = fields.Many2one("gp.candidate","Candidate")

    course_name =  fields.Selection([
        ('pst', 'PST'),
        ('efa', 'EFA'),
        ('fpff', 'FPFF'),
        ('pssr', 'PSSR'),
        ('stsdsd', 'STSDSD'),
        ('bst', 'BST')
    ],string="Course")
    institute_name = fields.Many2one("bes.institute","Institute Name")
    marine_training_inst_number = fields.Char("MTI Number")
    mti_indos_no = fields.Char("Indos No.")
    candidate_cert_no = fields.Char("Candidate Certificate Number")
    course_start_date = fields.Date(string="Course Start Date")
    course_end_date = fields.Date(string="Course End Date")
    file_name = fields.Char('File Name')
    certificate_upload = fields.Binary("Certificate Upload")
    






    

class GPCandidateShipVisits(models.Model):
    _name = 'gp.candidate.ship.visits'
    _description = 'Ship Visits'
    candidate_id = fields.Many2one("gp.candidate","Candidate")
    name_of_ships = fields.Char("Name of  the Ship Visited / Ship in Campus")
    imo_no = fields.Char("Ship IMO Number")
    name_of_ports_visited = fields.Char("Name of the Port Visited / Place of SIC")
    date_of_visits = fields.Date("Date Of Visit")
    time_spent_on_ship = fields.Float("Hours")
    bridge = fields.Boolean("Bridge")
    eng_room = fields.Boolean("Eng. Room")
    cargo_area = fields.Boolean("Cargo Area")
    
    

class CCMCCandidate(models.Model):
    _name = 'ccmc.candidate'
    _description = 'CCMC Candidate'
    
    institute_batch_id = fields.Many2one("institute.ccmc.batches","Batch")
    institute_id = fields.Many2one("bes.institute",string="Name of Institute",required=True)
    candidate_image_name = fields.Char("Candidate Image Name")
    candidate_image = fields.Binary(string='Candidate Image', attachment=True, help='Select an image in JPEG format.')
    candidate_signature_name = fields.Char("Candidate Signature")
    candidate_signature = fields.Binary(string='Candidate Signature', attachment=True, help='Select an image')
    
    name = fields.Char("Full Name of Candidate as in INDOS",required=True)
    user_id = fields.Many2one("res.users", "Portal User")    
    age = fields.Char("Age",compute="_compute_age")
    indos_no = fields.Char("Indos No.")
    candidate_code = fields.Char("CCMC Candidate Code No.")
    roll_no = fields.Char("Roll No.")
    dob = fields.Date("DOB",help="Date of Birth", 
                      widget="date", 
                      date_format="%d-%b-%y")
                      
    street = fields.Char("Street")
    street2 = fields.Char("Street2")
    city = fields.Char("City",required=True)
    zip = fields.Char("Zip",required=True, validators=[api.constrains('zip')])
    state_id = fields.Many2one("res.country.state","State",domain=[('country_id.code','=','IN')],required=True)
    phone = fields.Char("Phone", validators=[api.constrains('phone')])
    mobile = fields.Char("Mobile", validators=[api.constrains('mobile')])
    email = fields.Char("Email", validators=[api.constrains('email')])
    tenth_percent = fields.Char("% Xth Std in Eng.")
    twelve_percent = fields.Char("% 12th Std in Eng.")
    iti_percent = fields.Char("% ITI")
    sc_st = fields.Boolean("To be mentioned if Candidate SC/ST")
    ship_visits_count = fields.Char("No. of Ship Visits")
    
    qualification = fields.Selection([
        ('tenth', '10th std'),
        ('twelve', '12th std'),
        ('iti', 'ITI')
    ],string="Qualification", default='tenth')
    
    candidate_attendance_record = fields.Integer("Candidate Attendance Record")
    
    elligiblity_criteria = fields.Selection([
        ('elligible', 'Elligible'),
        ('not_elligible', 'Not Elligible')
    ],string="Elligiblity Criteria",compute="_compute_eligibility", default='not_elligible')
    
    
    attendance_compliance_1 = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ],string="Whether Attendance record of the candidate comply with DGS Guidelines 1 of 2018 as per para 3.2 for GP / 7 of 2010 as per para 3.3 for CCMC (YES/ NO)", default='no')
    
    attendance_compliance_2 = fields.Selection([
         ('yes', 'Yes'),
         ('no', 'No')
    ], string="Attendance record of the candidate not comply with DGS Guidelines 1 of 2018 as per para 3.2 for GP / 7 of 2010 as per para 3.3 for CCMC and whether same has been informed to the DGS (YES/ NO)", default='no')

    stcw_certificate = fields.One2many("ccmc.candidate.stcw.certificate","candidate_id",string="STCW Certificate")
    
    # attendance_compliance_2 = fields.Boolean([
    #     ('yes', 'Yes'),
    #     ('no', 'No')
    # ],string="Attendance record of the candidate not comply with DGS Guidelines 1 of 2018 as per para 3.2 for GP / 7 of 2010 as per para 3.3 for CCMC and whether same has been informed to the DGS (YES/ NO)", default='no')
    
        # Ship Visits
    ship_visits = fields.One2many("ccmc.candidate.ship.visits","candidate_id",string="Ship Visit")


        # Cookery an Bakery
    cookery_child_line = fields.One2many("ccmc.cookery.bakery.line","cookery_parent",string="Cookery & Bakery")
    

        # Start CCMC rating Oral

    ccmc_oral_child_line = fields.One2many("ccmc.oral.line","ccmc_oral_parent",string="CCMC Oral")

    ccmc_online = fields.One2many("survey.user_input","ccmc_candidate",domain=[("survey_id.subject.name", "=", 'CCMC')],string="CCMC Online")


    fees_paid = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ],string="Fees Paid", default='no')

    invoice_no = fields.Char("Invoice No",compute="_compute_invoice_no",store=True)
    
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
    _description = 'STCW'
    
    candidate_id = fields.Many2one("ccmc.candidate","Candidate")
    course_name =  fields.Selection([
        ('pst', 'PST'),
        ('efa', 'EFA'),
        ('fpff', 'FPFF'),
        ('pssr', 'PSSR'),
        ('stsdsd', 'STSDSD'),
        ('bst', 'BST')
    ],string="Course")
    institute_name = fields.Many2one("bes.institute","Institute Name")
    marine_training_inst_number = fields.Char("Marine Training Institute Number")
    mti_indos_no = fields.Char("MTI Indos No.")
    candidate_cert_no = fields.Char("Candidate Certificate Number")
    file_name = fields.Char('File Name')
    certificate_upload = fields.Binary("Certificate Upload")
    course_start_date = fields.Date(string="Course Start Date")
    course_end_date = fields.Date(string="Course End Date")


    

class CCMCCandidateShipVisits(models.Model):
    _name = 'ccmc.candidate.ship.visits'
    _description = 'Ship Visits'
    candidate_id = fields.Many2one("ccmc.candidate","Candidate")
    name_of_ships = fields.Char("Name of  the Ship Visited / Ship in Campus")
    imo_no = fields.Char("Ship IMO Number")
    name_of_ports_visited = fields.Char("Name of the Port Visited / Place of SIC")
    date_of_visits = fields.Date("Date Of Visit")
    time_spent_on_ship = fields.Float("Hours")
    bridge = fields.Boolean("Bridge")
    eng_room = fields.Boolean("Eng. Room")
    cargo_area = fields.Boolean("Cargo Area")

class CookeryBakeryLine(models.Model):
    _name = 'ccmc.cookery.bakery.line'
    _description = 'Cookery and Bakery Line'

    cookery_parent = fields.Many2one("ccmc.candidate",string="Cookery & Bakery Parent")
    institute_id = fields.Many2one("bes.institute",string="Name of Institute")
    exam_id = fields.Many2one("ccmc.exam.schedule",string="Exam Id")
    # exam_attempt_number = fields.Integer(string="Exam Attempt No.")
    exam_attempt_number = fields.Integer(string="Exam Attempt No.", readonly=True)
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
    cookery_draft_confirm = fields.Selection([('draft','Draft'),('confirm','Confirm')],string="State",default="draft")


    
    
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
    _description = 'MEK Practical Line'

    mek_parent = fields.Many2one("gp.candidate",string="Parent")
    exam_id = fields.Many2one("gp.exam.schedule",string="Exam Id")
    institute_id = fields.Many2one("bes.institute",string="Institute")
    mek_prcatical_attempt_no = fields.Integer(string="Exam Attempt No.", readonly=True)
    mek_practical_exam_date = fields.Date(string="Exam Date")
    using_hand_plumbing_tools_task_1 = fields.Integer("Using Hand & Plumbing Tools (Task 1)")
    using_hand_plumbing_tools_task_2 = fields.Integer("Using Hand & Plumbing Tools (Task 2)")
    using_hand_plumbing_tools_task_3 = fields.Integer("Using Hand & Plumbing Tools (Task 3)")
    use_of_chipping_tools_paint_brushes = fields.Integer("Use of Chipping Tools & paint Brushes")
    use_of_carpentry = fields.Integer("Use of Carpentry Tools")
    use_of_measuring_instruments = fields.Integer("Use of Measuring Instruments")
    welding = fields.Integer("Welding (1 Task)")
    lathe = fields.Integer("Lathe Work (1 Task)")
    electrical = fields.Integer("Electrical (1 Task)")
    
    mek_practical_total_marks = fields.Integer("Total Marks", compute="_compute_mek_practical_total_marks", store=True)
    
    mek_practical_remarks = fields.Text(" Remarks Mention if Absent / Good  /Average / Weak ")
    mek_practical_draft_confirm = fields.Selection([('draft','Draft'),('confirm','Confirm')],string="State",default="draft")



    @api.onchange('using_hand_plumbing_tools_task_1', 'using_hand_plumbing_tools_task_2', 'using_hand_plumbing_tools_task_3',
                 'use_of_chipping_tools_paint_brushes', 'use_of_carpentry', 'use_of_measuring_instruments',
                 'welding', 'lathe', 'electrical')
    def _onchange_ccmc_oral_marks_limit(self):
        if self.using_hand_plumbing_tools_task_1 > 10:
            raise UserError("In MEK Practical, Using Hand & Plumbing Tools (Task 1) Marks cannot exceed 10.")
        if self.using_hand_plumbing_tools_task_2 > 10:
            raise UserError("In MEK Practical, Using Hand & Plumbing Tools (Task 2) Marks cannot exceed 10.")
        if self.using_hand_plumbing_tools_task_3 > 10:
            raise UserError("In MEK Practical, Using Hand & Plumbing Tools (Task 3) Marks cannot exceed 10.")
        if self.use_of_chipping_tools_paint_brushes > 10:
            raise UserError("In MEK Practical, Use of Chipping Tools & paint Brushes Marks cannot exceed 10.")
        if self.use_of_carpentry > 10:
            raise UserError("In MEK Practical, Use of Carpentry Tools Marks cannot exceed 10.")
        if self.use_of_measuring_instruments > 10:
            raise UserError("In MEK Practical, Use of Measuring Instruments Marks cannot exceed 10.")
        if self.welding > 20:
            raise UserError("In MEK Practical, Welding (1 Task) Marks cannot exceed 20.")
        if self.lathe > 10:
            raise UserError("In MEK Practical, Lathe Work (1 Task) Marks cannot exceed 10.")
        if self.electrical > 10:
            raise UserError("In MEK Practical, Electrical (1 Task) Marks cannot exceed 10.")
  
    
    @api.depends('using_hand_plumbing_tools_task_1', 'using_hand_plumbing_tools_task_2', 'using_hand_plumbing_tools_task_3',
                 'use_of_chipping_tools_paint_brushes', 'use_of_carpentry', 'use_of_measuring_instruments',
                 'welding', 'lathe', 'electrical')
    def _compute_mek_practical_total_marks(self):
        for record in self:
            total = (
                record.using_hand_plumbing_tools_task_1 +
                record.using_hand_plumbing_tools_task_2 +
                record.using_hand_plumbing_tools_task_3 +
                record.use_of_chipping_tools_paint_brushes +
                record.use_of_carpentry +
                record.use_of_measuring_instruments +
                record.welding +
                record.lathe +
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
    _description = 'MEK Oral Line'

    mek_oral_parent = fields.Many2one("gp.candidate", string="Parent")
    institute_id = fields.Many2one("bes.institute",string="Institute")
    exam_id = fields.Many2one("gp.exam.schedule",string="Exam ID")
    mek_oral_attempt_no = fields.Integer(string="Exam Attempt No.", readonly=True)
    mek_oral_exam_date = fields.Date(string="Exam Date")
    using_hand_plumbing_carpentry_tools = fields.Integer("Uses of Hand/Plumbing/Carpentry Tools")
    use_of_chipping_tools_paints = fields.Integer("Use of Chipping Tools & Brushes & Paints")
    welding = fields.Integer("Welding")
    lathe_drill_grinder = fields.Integer("Lathe/Drill/Grinder")
    electrical = fields.Integer("Electrical")
    journal = fields.Integer("Journal")

    mek_oral_total_marks = fields.Integer("Total Marks", compute="_compute_mek_oral_total_marks", store=True)

    mek_oral_remarks = fields.Text("Remarks Mention if Absent / Good / Average / Weak")
    mek_oral_draft_confirm = fields.Selection([('draft','Draft'),('confirm','Confirm')],string="State",default="draft")


    

    @api.depends('using_hand_plumbing_carpentry_tools', 'use_of_chipping_tools_paints', 'welding', 'lathe_drill_grinder', 'electrical', 'journal')
    def _compute_mek_oral_total_marks(self):
        for record in self:
            total = (
                record.using_hand_plumbing_carpentry_tools +
                record.use_of_chipping_tools_paints +
                record.welding +
                record.lathe_drill_grinder +
                record.electrical +
                record.journal
            )
            record.mek_oral_total_marks = total

    @api.onchange('using_hand_plumbing_carpentry_tools', 'use_of_chipping_tools_paints', 'welding', 'lathe_drill_grinder', 'electrical', 'journal')
    def _onchange_ccmc_oral_marks_limit(self):
        if self.using_hand_plumbing_carpentry_tools > 10:
            raise UserError("In MEK Oral, Uses of Hand/Plumbing/Carpentry Tools Marks cannot exceed 10.")
        if self.use_of_chipping_tools_paints > 10:
            raise UserError("In MEK Oral, Use of Chipping Tools & Brushes & Paints Marks cannot exceed 10.")
        if self.welding > 10:
            raise UserError("In MEK Oral, Welding Marks cannot exceed 10.")
        if self.lathe_drill_grinder > 10:
            raise UserError("In MEK Oral, Lathe/Drill/Grinder Marks cannot exceed 10.")
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
    _description = 'GSK Practical Line'

    gsk_practical_parent = fields.Many2one("gp.candidate", string="Parent")
    exam_id = fields.Many2one("gp.exam.schedule",string="Exam ID")
    institute_id = fields.Many2one("bes.institute",string="Institute")
    gsk_practical_attempt_no = fields.Integer(string="Exam Attempt No.", default=0, readonly=True)
    gsk_practical_exam_date = fields.Date(string="Exam Date")
    climbing_mast = fields.Integer("Climb the mast with safe practices , Prepare and throw Heaving Line ")
    buoy_flags_recognition = fields.Integer("·Recognise buyos and flags .Hoisting a Flag correctly .Steering and Helm Orders")
    bosun_chair = fields.Integer("Rigging Bosun's Chair and self lower and hoist")
    rig_stage = fields.Integer("Rig a stage for painting shipside")
    rig_pilot = fields.Integer("Rig a Pilot Ladder")
    rig_scaffolding = fields.Integer("Rig scaffolding to work at a height") 
    fast_ropes = fields.Integer("·Making fast Ropes and Wires ·Use Rope-Stopper / Chain Stopper")
    
    knots_bend = fields.Integer(".Knots, Bends, Hitches .Whippings/Seizing/Splicing Ropes/Wires .Reeve 3- fold / 2 fold purchase")
    sounding_rod = fields.Integer("·Taking Soundings with sounding rod / sounding taps ·Reading of Draft .Mannual lifting of weight")
    
    gsk_practical_total_marks = fields.Integer("Total Marks",compute="_compute_gsk_practical_total_marks",store=True)
    gsk_practical_remarks = fields.Text(" Remarks Mention if Absent / Good  /Average / Weak ")
    gsk_practical_draft_confirm = fields.Selection([('draft','Draft'),('confirm','Confirm')],string="State",default="draft")


      
    @api.depends('climbing_mast', 'buoy_flags_recognition', 'bosun_chair', 'rig_stage', 'rig_pilot', 'rig_scaffolding', 'fast_ropes', 'knots_bend', 'sounding_rod')
    def _compute_gsk_practical_total_marks(self):
        for record in self:
            total_marks = 0
            total_marks += record.climbing_mast
            total_marks += record.buoy_flags_recognition
            total_marks += record.bosun_chair
            total_marks += record.rig_stage
            total_marks += record.rig_pilot
            total_marks += record.rig_scaffolding
            total_marks += record.fast_ropes
            total_marks += record.knots_bend
            total_marks += record.sounding_rod
            record.gsk_practical_total_marks = total_marks

    @api.onchange('climbing_mast','buoy_flags_recognition','bosun_chair','rig_stage','rig_pilot','rig_scaffolding','fast_ropes','knots_bend','sounding_rod')
    def _onchange_gsk_practicals_marks_limit(self):
        if self.climbing_mast > 12:
            raise UserError("Climb the mast with safe practices , Prepare and throw Heaving Line marks should not be greater than 12.")
        if self.buoy_flags_recognition > 12:
            raise UserError("·Recognise buyos and flags .Hoisting a Flag correctly .Steering and Helm Orders marks should not be greater than 12.")
        if self.bosun_chair > 8:
            raise UserError("Rigging Bosun's Chair and self lower and hoist marks should not be greater than 8.")
        if self.rig_stage > 8:
            raise UserError("Rig a stage for painting shipside marks should not be greater than 8.")
        if self.rig_pilot > 8:
            raise UserError("Rig a Pilot Ladder marks should not be greater than 8.")
        if self.rig_scaffolding > 8:
            raise UserError("Rig scaffolding to work at a height marks should not be greater than 8.")
        if self.fast_ropes > 8:
            raise UserError("·Making fast Ropes and Wires ·Use Rope-Stopper / Chain Stopper marks should not be greater than 8.")
        if self.knots_bend > 18:
            raise UserError(".Knots, Bends, Hitches .Whippings/Seizing/Splicing Ropes/Wires .Reeve 3- fold / 2 fold purchase marks should not be greater than 18.")
        if self.sounding_rod > 18:
            raise UserError("·Taking Soundings with sounding rod / sounding taps ·Reading of Draft .Mannual lifting of weight marks should not be greater than 18.")

    
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
    _description = 'GSK Oral Line'

    gsk_oral_parent = fields.Many2one("gp.candidate", string="Parent")
    exam_id = fields.Many2one("gp.exam.schedule",string="Exam ID")
    institute_id = fields.Many2one("bes.institute",string="Institute")
    gsk_oral_attempt_no = fields.Integer(string="Exam Attempt No.", default=0,readonly=True)
    gsk_oral_exam_date = fields.Date(string="Exam Date")
    subject_area_1 = fields.Integer("Subject Area 1")
    subject_area_2 = fields.Integer("Subject Area 2")
    subject_area_3 = fields.Integer("Subject Area 3")
    subject_area_4 = fields.Integer("Subject Area 4")
    subject_area_5 = fields.Integer("Subject Area 5")
    subject_area_6 = fields.Integer("Subject Area 6")
    practical_record_journals = fields.Integer("Practical Record Book and Journal")
    
    
    gsk_oral_total_marks = fields.Integer("Total Marks",compute='_compute_gsk_oral_total_marks', store=True)
    gsk_oral_remarks = fields.Text(" Remarks Mention if Absent / Good  /Average / Weak ")
    gsk_oral_draft_confirm = fields.Selection([('draft','Draft'),('confirm','Confirm')],string="State",default="draft")


    

    @api.depends('subject_area_1', 'subject_area_2', 'subject_area_3', 'subject_area_4', 'subject_area_5', 'subject_area_6', 'practical_record_journals')
    def _compute_gsk_oral_total_marks(self):
        for record in self:
            total_marks = sum([
                record.subject_area_1,
                record.subject_area_2,
                record.subject_area_3,
                record.subject_area_4,
                record.subject_area_5,
                record.subject_area_6,
                record.practical_record_journals,
            ])

            record.gsk_oral_total_marks = total_marks
    

    @api.onchange('subject_area_1','subject_area_2','subject_area_3','subject_area_4','subject_area_5','subject_area_6','practical_record_journals')
    def _onchange_gsk_oral__marks_limit(self):
        if self.subject_area_1 > 9:
            raise UserError("Subject Area 1 marks should not be greater than 9.")
        if self.subject_area_2 > 6:
            raise UserError("Subject Area 2 marks should not be greater than 6.")
        if self.subject_area_3 > 9:
            raise UserError("Subject Area 3 marks should not be greater than 9.")
        if self.subject_area_4 > 9:
            raise UserError("Subject Area 4 marks should not be greater than 9.")
        if self.subject_area_5 > 12:
            raise UserError("Subject Area 5 marks should not be greater than 12.")
        if self.subject_area_6 > 5:
            raise UserError("Subject Area 6 marks should not be greater than 5.")
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
    _description = 'CCMC Oral Line'


    institute_id = fields.Many2one("bes.institute",string="Institute")
    ccmc_oral_parent = fields.Many2one("ccmc.candidate", string="Parent")
    exam_id = fields.Many2one("ccmc.exam.schedule",string="Exam ID")
    ccmc_oral_attempt_no = fields.Integer(string="Exam Attempt No.", default=0, readonly=True)
    ccmc_oral_exam_date = fields.Date(string="Exam Date")
    
    house_keeping = fields.Integer("House Keeping")
    f_b = fields.Integer("F & B service Practical")
    orals_house_keeping = fields.Integer("Orals on Housekeeping and F& B Service")
    attitude_proffessionalism = fields.Integer("Attitude & Proffesionalism")
    equipment_identification = fields.Integer("Identification of Equipment")
    
    gsk_ccmc = fields.Integer("GSK")
    safety_ccmc = fields.Integer("Safety")
    toal_ccmc_rating = fields.Integer("Total", compute="_compute_ccmc_rating_total", store=True)
    ccmc_oral_draft_confirm = fields.Selection([('draft','Draft'),('confirm','Confirm')],string="State",default="draft")

    

    @api.depends(
        'gsk_ccmc', 'safety_ccmc','house_keeping','attitude_proffessionalism','equipment_identification'
    )
    def _compute_ccmc_rating_total(self):
        for record in self:
            rating_total = (
                record.gsk_ccmc +
                record.safety_ccmc+
                record.house_keeping+
                record.attitude_proffessionalism+
                record.equipment_identification
            )
            
            record.toal_ccmc_rating = rating_total


    @api.onchange('gsk_ccmc','safety_ccmc')
    def _onchange_ccmc_oral_marks_limit(self):
        if self.gsk_ccmc > 10:
            raise UserError("In CCMC Oral, GSK marks should not be greater than 10.")
        if self.safety_ccmc > 10:
            raise UserError("In CCMC Oral, Safety marks should not be greater than 10.")


    @api.model
    def create(self, vals):
        if vals.get('ccmc_oral_attempt_no', 0) == 0:
            # Calculate the next attempt number
            last_attempt = self.search([
                ('ccmc_oral_parent', '=', vals.get('ccmc_oral_parent')),
            ], order='ccmc_oral_attempt_no desc', limit=1)
            next_attempt = last_attempt.ccmc_oral_attempt_no + 1 if last_attempt else 1
            vals['ccmc_oral_attempt_no'] = next_attempt
        return super(CcmcOralLine, self).create(vals)


    @api.constrains('ccmc_oral_attempt_no')
    def _check_attempt_no(self):
        for record in self:
            if record.ccmc_oral_attempt_no > 7:
                raise ValidationError("A Candidate can't have more than 7 exam attempts in CCMC Oral.")

    # def unlink(self):
    #     # raise UserError("YOU CAN'T DELETE CANDIDATE EXAM RECORDS.")
    #     return super(CcmcOralLine, self - undeletable_records).unlink()



class CandidateRegisterExamWizard(models.TransientModel):
    _name = 'candidate.gp.register.exam.wizard'
    _description = 'Register Exam'
    
    exam_region = fields.Many2one("exam.center",string="Exam Region")
    institute_ids = fields.Many2many("bes.institute",string="Institute",compute="_compute_institute_ids")
    institute_id = fields.Many2one("bes.institute",string="Institute")
    candidate_id = fields.Many2one("gp.candidate",string="Candidate",required=True)
    
    mek_survey_qb = fields.Many2one("survey.survey",string="Mek Question Bank")
    gsk_survey_qb = fields.Many2one("survey.survey",string="Gsk Question Bank")
    dgs_batch = fields.Many2one("dgs.batches",string="DGS Batch",required=False)
    gp_exam = fields.Many2one("gp.exam.schedule",string="GP Exam",required=True)
    
    
    previous_attempt =  fields.Integer("Previous Attempt No.")
    deffereds =  fields.Boolean("Deffered")
    # batch_id = fields.Many2one("institute.gp.batches",string="Batches",required=True)

    
    exam_month = fields.Selection([
        ('dec_feb', 'Dec - Feb'),
        ('mar_jun', 'Mar - Jun'),
        ('jul_aug', 'Jul - Aug'),
        ('sep_nov', 'Sep - Nov'),
    ], string='Exam Month')
    
    
    gsk_oral_prac_status = fields.Selection([
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='GSK Oral/Practical Status')
    
    
    mek_total = fields.Float("MEK Total",readonly=True)
    mek_percentage = fields.Float("MEK Percentage",readonly=True)
    mek_oral_prac_status = fields.Selection([
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='Mek Oral/Practical Status')
    
    mek_online_status = fields.Selection([
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='Mek Online Status')
    
    gsk_online_status = fields.Selection([
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='Gsk Online Status')
    
    
    @api.depends('exam_region')
    def _compute_institute_ids(self):
        for record in self:
            
            exam_region = record.exam_region.id
            record.institute_ids = self.env["bes.institute"].search([('exam_center','=',exam_region)])
            
    
    
    def register_exam(self):
        
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
        
        
        if self.mek_online_status == 'failed':
            mek_survey_qb_input = self.mek_survey_qb._create_answer(user=self.candidate_id.user_id)
            mek_survey_qb_input.write({'gp_candidate':self.candidate_id.id})
            mek_online_carry_forward = False
            mek_online_marks = self.gp_exam.mek_online_marks
            mek_online_percentage = self.gp_exam.mek_online_percentage
        else:
            mek_survey_qb_input = self.gp_exam.mek_online
            mek_online_carry_forward = True
            mek_online_marks = self.gp_exam.mek_online_marks
            mek_online_percentage = self.gp_exam.mek_online_percentage
        
        
        if self.gsk_online_status == 'failed':
            gsk_survey_qb_input = self.gsk_survey_qb._create_answer(user=self.candidate_id.user_id)
            gsk_survey_qb_input.write({'gp_candidate':self.candidate_id.id})
            gsk_online_carry_forward = False
            gsk_online_marks = self.gp_exam.gsk_online_marks
            gsk_online_percentage = self.gp_exam.gsk_online_percentage
        else:
            gsk_survey_qb_input = self.gp_exam.gsk_online
            gsk_online_marks = self.gp_exam.gsk_online_marks
            gsk_online_percentage = self.gp_exam.gsk_online_percentage
            gsk_online_carry_forward = True
            
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
    _description = 'Register Exam'
    
    exam_region = fields.Many2one("exam.center",string="Exam Region")
    dgs_batch = fields.Many2one("dgs.batches",string="DGS Batch",required=False)

    institute_ids = fields.Many2many("bes.institute",string="Institute",compute="_compute_institute_ids")
    institute_id = fields.Many2one("bes.institute",string="Institute")
    candidate_id = fields.Many2one("ccmc.candidate",string="Candidate",required=True)
    
    cookery_bakery_qb = fields.Many2one("survey.survey",string="Cookery Bakery Question Bank Template")


    ccmc_exam = fields.Many2one("ccmc.exam.schedule",string="CCMC Exam",required=True)
    
    
    previous_attempt =  fields.Integer("Previous Attempt No.")
    # batch_id = fields.Many2one("institute.gp.batches",string="Batches",required=True)

    
    exam_month = fields.Selection([
        ('dec_feb', 'Dec - Feb'),
        ('mar_jun', 'Mar - Jun'),
        ('jul_aug', 'Jul - Aug'),
        ('sep_nov', 'Sep - Nov'),
    ], string='Exam Month')
    
    
    cookery_bakery_status = fields.Selection([
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='Cookery Bakery Oral/Prac Status',compute="_compute_cookery_bakery_status")
    
    
    
    # ccmc_oral_status = fields.Selection([
    #     ('failed', 'Failed'),
    #     ('passed', 'Passed'),
    # ], string='CCMC Oral Status',compute="_compute_ccmc_oral_status")
    
    
    ccmc_online = fields.Selection([
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='CCMC Online',compute="_compute_ccmc_online")
    

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
        else:
            cookery_bakery = self.ccmc_exam.cookery_bakery
            ccmc_oral =self.ccmc_exam.ccmc_oral
        
        
        # if self.mek_oral_prac_status == 'failed':
        #     mek_practical = self.env["gp.mek.practical.line"].create({"exam_id":gp_exam_schedule.id,'mek_parent':self.candidate_id.id,'institute_id': self.institute_id.id})
        #     mek_oral = self.env["gp.mek.oral.line"].create({"exam_id":gp_exam_schedule.id,'mek_oral_parent':self.candidate_id.id,'institute_id': self.institute_id.id})
        # else:
        #     mek_practical = self.gp_exam.mek_prac
        #     mek_oral =self.gp_exam.mek_oral
        
        
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
    _description = 'GP Candidate'
    
    institute_batch_id = fields.Many2one("institute.gp.batches","Batch")

    gsk_candidate_child_line = fields.One2many("sep.candidate.line","sep_candidate_parent",string="SEP Registration")
    def name_get(self):
        result = []
        for record in self:
            name = f"{record.institute_batch_id.batch_name} "  # Customize the display name as needed
            result.append((record.id, name))
        return result
        
        
        
        
class SEPCandidateLine(models.Model):
    _name = 'sep.candidate.line'
    _description = 'GP Candidate Line'
    rec_name = 'institute_batch_id'
    
    institute_batch_id = fields.Many2one("institute.gp.batches","Batch")

    sep_candidate_parent = fields.Many2one("sep.candidate",string="SEP Registration Line")
    name = fields.Char("Name of the Rating's")
    dob = fields.Date("DOB",help="Date of Birth", 
                      widget="date", 
                      date_format="%d-%b-%y")
    indos_no= fields.Char("Indos No")
    cdc_no= fields.Char("CDC No")
    contact= fields.Char("Contact No")
    email= fields.Char("Email ID")
    attendance1= fields.Boolean("1st Day Attendance")
    attendance2= fields.Boolean("2nd Day Attendance")
    vaccination= fields.Boolean("Vaccination/RTPCR")
    remarks= fields.Char("Remark")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ],compute='_compute_state', string='Status', default='draft' )

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