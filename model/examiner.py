from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
from datetime import datetime, timedelta



class Examiner(models.Model):
    _name = "bes.examiner"
    _description= 'Examiner'
    _rec_name = 'name'

    examiner_image = fields.Binary(string='Examiner Image', attachment=True, help='Select an image in JPEG format.')
    user_id = fields.Many2one("res.users", "Portal User")
    name = fields.Char("Name",required=True)
    street = fields.Char("Street")
    street2 = fields.Char("Street2")
    city = fields.Char("City",required=True)
    zip = fields.Char("Zip",required=True)
    state_id = fields.Many2one("res.country.state","State",required=True,domain=[('country_id.code','=','IN')])
    phone = fields.Char("Phone")
    mobile = fields.Char("Mobile",required=True)
    
    pan_no = fields.Char("Pan No .",required=True)
    email = fields.Char("Email .",required=True)
    dob = fields.Date("DOB",required=True)
    present_designation = fields.Text("Present Designation",required=True)
    name_address_present_employer = fields.Text("Name and address of present employer",required=True)
    designation = fields.Selection([
        ('master', 'Master'),
        ('chief', 'Chief')
    ], string='Rank',default='master')
    competency_no = fields.Char("Certificate of competency no.",required=True)
    date_of_issue = fields.Date("Date of Issue",required=True)
    member_of_imei_cmmi = fields.Selection([
        ('imei', 'IMEI'),
        ('cmmi', 'CMMI')
    ], string='Are you a member of IMEI or CMMI?',default='no')
    membership_no = fields.Char("Membership No.")
    institute_association = fields.Boolean("Are you associated with any institute conducting ratings training?")
    associated_training_institute = fields.Text("Name & address of the training institute to which you were associated")
    present_employer_clearance = fields.Boolean("Have you taken clearance from your present employer to work on part time basis for BES?")
    subject_id = fields.Many2one("course.master.subject","Subject")
    assignments = fields.One2many("examiner.assignment","examiner_id","Assignments")

    
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
        portal_user = self.env['res.users'].sudo().create(user_values)
        portal_user.write({'groups_id': [(4, group_id)]  })
        examiner.write({'user_id': portal_user.id})  # Associate the user with the institute
        # import wdb; wdb.set_trace()
        examiner_tag = self.env.ref('bes.examiner_tags').id
        portal_user.partner_id.write({'email': examiner.email,'phone':examiner.phone,'mobile':examiner.mobile,'street':examiner.street,'street2':examiner.street2,'city':examiner.city,'zip':examiner.zip,'state_id':examiner.state_id.id,'category_id':[examiner_tag]})
        return examiner



class ExaminerAssignment(models.Model):
    _name = "examiner.assignment"
    _description= 'Examiner Assignment'
    
    
    examiner_id = fields.Many2one("bes.examiner","Examiner")
    assignment_date = fields.Date("Assignment Date")
    exam_date = fields.Date("Exam Date")
    subject_id = fields.Many2one("course.master.subject","Subject")
    gp_candidates = fields.Many2many("gp.candidate",string="GP Candidate")
    ccmc_candidates = fields.Many2many("ccmc.candidate",string="CCMC Candidate")
    
    
    @api.constrains('exam_date', 'subject_id', 'gp_candidates')
    def _check_duplicate_assignment(self):
        for record in self:
            # Check if the same candidate is assigned to the same subject
            # import wdb;wdb.set_trace()
            # if len(record.gp_candidates.filtered(lambda c: c in record.subject_id.gp_candidates)) > 1:
            #     raise ValidationError("A candidate cannot be assigned twice to the same subject.")

            # Check if the same subject is scheduled within 90 days
             for candidate in record.gp_candidates:
                # Check if the same candidate has an exam for the same subject within 90 days
                similar_assignments = self.search([
                    ('id', '!=', record.id),
                    ('subject_id', '=', record.subject_id.id),
                    ('gp_candidates', 'in', candidate.id),
                    ('exam_date', '>=', fields.Date.to_string(fields.Date.from_string(record.exam_date) - timedelta(days=90))),
                    ('exam_date', '<=', record.exam_date)
                ])
                if similar_assignments:
                    raise ValidationError(f"{candidate.name} cannot have an exam for the same subject within 90 days.")
