
from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
import random
import logging
import qrcode
import io
import base64
from datetime import datetime , date


class BesBatches(models.Model):
    _name = "bes.exam.schedule"
    _rec_name = "schedule_name"
    _description= 'Schedule'
    schedule_name = fields.Char("Schedule Name",required=True)
    exam_date = fields.Datetime("Exam Date",required=True)
    course = fields.Many2one("course.master",string="Course",required=True)
    state = fields.Selection([
        ('1-draft', 'Draft'),
        ('2-confirm', 'Confirmed'),
        ('3-examiner_assigned', 'Examiner Assigned'),     
        ('4-exam_planned', 'Exam Planned')        
    ], string='State', default='1-draft')
    exam_center = fields.Many2one("exam.center","Exam Region",required=True)
    examiners = fields.Many2many('bes.examiner', string="Examiners")
    # exam_online = fields.One2many("exam.type.online","exam_schedule_id",string="Exam Online")
    # exam_oral_practical = fields.One2many("exam.type.oral.practical","exam_schedule_id",string="Exam Oral Practical")
    candidate_count = fields.Integer(string="Candidate Count", compute="compute_candidate_count")
    
    


    def divide_candidates_among_practical_oral_examiners_and_date(self):

        for i in self.course.subjects:
            subjects = self.exam_oral_practical.filtered(lambda rec: rec.subject.id == i.id)
            if len(subjects) > 0:
                candidates = self.env["exam.schedule.bes.candidate"].search([('exam_schedule_id','=',self.id)]).ids
                sublists = [[] for _ in range(len(subjects))]
                
                for i, num in enumerate(candidates):
                    sublist_index = i % len(subjects)
                    sublists[sublist_index].append(num)
                
                
                for i,subjects in enumerate(subjects):
                    subjects.write({'candidates':sublists[i],'state':'2-confirm'})


    def divide_candidates_among_online_examiners_and_date(self):

        for i in self.course.subjects:
            subjects = self.exam_online.filtered(lambda rec: rec.subject.id == i.id)
            if len(subjects) > 0:
                candidates = self.env["exam.schedule.bes.candidate"].search([('exam_schedule_id','=',self.id)]).ids
                sublists = [[] for _ in range(len(subjects))]
                
                for i, num in enumerate(candidates):
                    sublist_index = i % len(subjects)
                    sublists[sublist_index].append(num)
                
                
                for i,subjects in enumerate(subjects):
                    subjects.write({'candidates':sublists[i]})

    
    
    
    def exam_planned(self):
        
        if len(self.exam_online.ids) == 0:
            raise ValidationError("Please Plan Online Exam")
        
        if len(self.exam_oral_practical.ids) == 0:
            raise ValidationError("Please Plan Practical & Oral Exam")
        
        self.divide_candidates_among_online_examiners_and_date()
        self.divide_candidates_among_practical_oral_examiners_and_date()
        self.write({'state' : '4-exam_planned' })
        
            
            
        
        
        
        #online exam logic
        
        # for i in self.exam_online:
            
        
        
        
        # examiner_online = self.exam_online.ids
        # candidates = self.env["exam.schedule.bes.candidate"].search([('exam_schedule_id','=',self.id)])
        # candidates_ids = candidates.ids
        # self.divide_candidates_among_online_examiners_and_date(candidates_ids,examiner_online)
       
        #prac_oral_examiner logic
        # practical_oral_examiner = self.exam_oral_practical.ids
        # candidates = self.env["exam.schedule.bes.candidate"].search([('exam_schedule_id','=',self.id)])
        # candidates_ids = candidates.ids
        # self.divide_candidates_among_practical_oral_examiners_and_date(candidates_ids,practical_oral_examiner)
        
        # self.state = '4-exam_planned'
    
    
    def compute_candidate_count(self):
        for rec in self:
            count = self.env["exam.schedule.bes.candidate"].search_count([('exam_schedule_id','=',self.id)])
            rec.candidate_count = count
            
                
    
    def exam_confirm(self):
        self.state = '2-confirm'
        
    def open_assign_examiner_wizard(self):
        
        return {
            'name': 'Assign Examiner',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'assign.examiner.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
            'default_course': self.course.id,    
            'default_state_id': self.exam_center.state_id.id,
            'schedule_id':self.id    
            }
        }
    
    def open_exam_candidate(self):
        
        return {
        'name': 'Exam Candidate',
        'domain': [('exam_schedule_id', '=', self.id)],
        'view_type': 'form',
        'res_model': 'exam.schedule.bes.candidate',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        'context': {
            'default_exam_schedule_id': self.id    
            }
        }       
            
class ExamCandidate(models.Model):
    _name = 'exam.schedule.bes.candidate'
    _description = 'Exam Candidate'
    
    # exam_schedule_id = fields.Many2one("bes.exam.schedule",string="Exam Schedule",required=True)
    partner_id = fields.Many2one("res.partner",string="Contacts")
    name = fields.Char("Name of Candidate",)
    indos_no = fields.Char("Indos No.")
    candidate_code = fields.Char("Candidate Code No.")
    roll_no = fields.Char("Roll No.")
    dob = fields.Date("DOB",help="Date of Birth", 
                      widget="date", 
                      date_format="%d-%b-%y")
    street = fields.Char("Street")
    street2 = fields.Char("Street2")
    city = fields.Char("City")
    zip = fields.Char("Zip")
    state_id = fields.Many2one("res.country.state","State",domain=[('country_id.code','=','IN')])
    phone = fields.Char("Phone")
    mobile = fields.Char("Mobile")
    email = fields.Char("Email")
    
    mek_practical_id = fields.Many2one("practical.mek","MEK Practical")
    mek_oral_id = fields.Many2one("oral.mek","MEK Oral Practical")
    gsk_practical_id = fields.Many2one("practical.gsk","GSK Practical")
    gsk_oral_id = fields.Many2one("oral.gsk","GSK Oral")
    
    
    mek_visiblity = fields.Boolean("MEK Visiblity",compute="compute_mek_gsk_visiblity")
    gsk_visiblity = fields.Boolean("GSK Visiblity",compute="compute_mek_gsk_visiblity")
    
    
    def compute_mek_gsk_visiblity(self):
        for record in self:
            # import wdb;wdb.set_trace();
            record.mek_visiblity = False
            record.gsk_visiblity = False
            user = self.env.user
            # Check if the user belongs to a specific group (replace 'your_module.group_name' with the actual group name)
            is_in_examiners_group = user.has_group('bes.group_examiners')
            is_in_bes_admin_group = user.has_group('bes.group_bes_admin')
            if is_in_examiners_group:
                subject_id  = self.env.context.get('subject_id')
                
                subject = self.env['course.master.subject'].search([('id','=',subject_id)])
                
                if subject.name == 'GSK':
                    record.gsk_visiblity = True
                    record.mek_visiblity = False
                elif subject.name == 'MEK':
                    record.mek_visiblity = True
                    record.gsk_visiblity = False
            elif is_in_bes_admin_group:
                 course_subjects = record.exam_schedule_id.course.subjects
                 for subject in course_subjects:
                     if subject.name == 'GSK':
                         record.gsk_visiblity = True
                     if subject.name == 'MEK':
                         record.mek_visiblity = True
                         
                
                                     
                
            else:
                # User is not in the specified group
                # record.mek_visiblity = False
                # record.gsk_visiblity = False
                return "User is not in the group."
            
        
    
    def open_gsk_oral_sheet(self):
        
        if self.gsk_oral_id:
        
            return {
            'name': 'GSK Oral Sheet',
            'view_type': 'form',
            'res_model': 'oral.gsk',
            'view_id': False,
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'res_id': self.self.gsk_oral_id.id,
            }
            
        else:
            
            return {
            'name': 'GSK Oral Sheet',
            'view_type': 'form',
            'res_model': 'oral.gsk',
            'view_id': False,
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'context': {
                'default_exam_bes_candidate_id': self.id  
                }
            }

    
    def open_gsk_practical_sheet(self):
        
        if self.gsk_practical_id:
            
            return {
            'name': 'GSK Practical Sheet',
            'view_type': 'form',
            'res_model': 'practical.gsk',
            'view_id': False,
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'res_id': self.gsk_practical_id.id,
            }
            
        else:
            
            return {
            'name': 'GSK Practical Sheet',
            'view_type': 'form',
            'res_model': 'practical.gsk',
            'view_id': False,
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'context': {
                'default_exam_bes_candidate_id': self.id  
                }
            }
            
    
    
    def open_mek_oral_sheet(self):
        
        if self.mek_oral_id:
        
            return {
            'name': 'MEK Oral Sheet',
            'view_type': 'form',
            'res_model': 'oral.mek',
            'view_id': False,
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'res_id': self.mek_oral_id.id,
            }
            
        else:
            
            return {
            'name': 'MEK Oral Sheet',
            'view_type': 'form',
            'res_model': 'oral.mek',
            'view_id': False,
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'context': {
                'default_exam_bes_candidate_id': self.id  
                }
            }
    
    
    def open_mek_practical_sheet(self):
        
        if self.mek_practical_id:
        
            return {
            'name': 'MEK Practical Sheet',
            'view_type': 'form',
            'res_model': 'practical.mek',
            'view_id': False,
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'res_id': self.mek_practical_id.id,
            }
            
        else:
            
            return {
            'name': 'MEK Practical Sheet',
            'view_type': 'form',
            'res_model': 'practical.mek',
            'view_id': False,
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'context': {
                'default_exam_bes_candidate_id': self.id  
                }
            }
            
class AssignExaminerWizard(models.TransientModel):
    _name = 'assign.examiner.wizard'
    _description = 'Assign Examiner'
    
    course = fields.Many2one("course.master",string="Course")
    state_id = fields.Many2one("res.country.state","State",domain=[('country_id.code','=','IN')])
    examiners = fields.Many2many('bes.examiner', string="Examiners")
    candidate_count = fields.Integer(string="Candidate Count")
    
    
    def assign_examiner(self):
        schedule_id = self.env.context.get('schedule_id')
        exam_schedule = self.env["bes.exam.schedule"].search([('id','=',schedule_id)])
        exam_schedule.write({'examiners':self.examiners,'state':'3-examiner_assigned'})

class ExamOnline(models.Model):
    _name = 'exam.type.online'
    _rec_name = "examiners"
    exam_schedule_id = fields.Many2one("bes.exam.schedule",string="Exam Schedule ID")
    examiners = fields.Many2one('bes.examiner', string="Examiner")
    subject = fields.Many2one("course.master.subject","Subject")
    start_time_online = fields.Datetime("Start Time")
    end_time_online = fields.Datetime("End Time")
    candidate_count = fields.Integer(string="Candidate Count",compute="compute_candidate_count")
    candidates = fields.Many2many("exam.schedule.bes.candidate","exam_type_online_candidate_rel","exam_type_online_id","exam_candidate_id",string="Candidate")
    
    @api.onchange('exam_schedule_id')
    def onchange_exam_schedule_id(self):
        for rec in self:
            return {'domain':{'examiners':[('id','in',rec.exam_schedule_id.examiners.ids)],'subject':[('id','in',rec.exam_schedule_id.course.subjects.ids)]}}

    def compute_candidate_count(self):
        for rec in self:
            count = len(rec.candidates)
            rec.candidate_count = count
      
class ExamOralPractical(models.Model):
    _name = 'exam.type.oral.practical'
    # exam_schedule_id = fields.Many2one("bes.exam.schedule",string="Exam Schedule ID")
    # examiners = fields.Many2one('bes.examiner', string="Examiner")
    # subject = fields.Many2one("course.master.subject","Subject")
    institute_id = fields.Many2one("bes.institute",string="Institute",required=True)
    institute_code = fields.Char(string="Institute Code", related='institute_id.code', required=True)
    dgs_batch = fields.Many2one("dgs.batches",string="DGS Batch",required=True)

    start_time = fields.Datetime("Start Time")
    end_time = fields.Datetime("End Time")
    examiners = fields.One2many("exam.type.oral.practical.examiners","prac_oral_id",string="Examiners")
   
    
    course = fields.Many2one("course.master",string="Course")
    
    subject = fields.Many2one("course.master.subject",string="Subject")


    state = fields.Selection([
        ('1-draft', 'Draft'),
        ('2-confirm', 'Confirmed')     
    ], string='State', default='1-draft')
    
    def confirm(self):
        
        
        if self.course.course_code == 'GP':
            
            if self.subject.name == 'GSK':
            
                gp_marksheets = self.env['gp.exam.schedule'].search([('dgs_batch','=',self.dgs_batch.id),('registered_institute','=',self.institute_id.id),('state','=','1-in_process'),('gsk_oral_prac_status','in',('pending','failed'))]).ids
                
                examiners = self.examiners.ids
                
                assignments = {examiner: [] for examiner in examiners}  # Dictionary to store assignments

            
                for i, candidate in enumerate(gp_marksheets):
                    examiner_index = i % len(examiners)  # Calculate the index of the examiner using modulo
                    examiner = examiners[examiner_index]
                    assignments[examiner].append(candidate)   
                    
                for examiner, assigned_candidates in assignments.items():
                    examiner_id = examiner
                    for i in assigned_candidates:
                        gp_marksheet = self.env['gp.exam.schedule'].browse(i).id
                        gsk_oral = self.env['gp.exam.schedule'].browse(i).gsk_oral.id
                        gsk_prac = self.env['gp.exam.schedule'].browse(i).gsk_prac.id
                        candidate = self.env['gp.exam.schedule'].browse(i).gp_candidate.id
                        self.env['exam.type.oral.practical.examiners.marksheet'].create({ 'examiners_id':examiner_id ,'gp_marksheet':gp_marksheet ,'gp_candidate':candidate , 'gsk_oral':gsk_oral , 'gsk_prac':gsk_prac })
                
                self.write({'state':'2-confirm'})       
            
            elif self.subject.name == 'MEK':
                
                gp_marksheets = self.env['gp.exam.schedule'].search([('dgs_batch','=',self.dgs_batch.id),('registered_institute','=',self.institute_id.id),('state','=','1-in_process'),('mek_oral_prac_status','in',('pending','failed'))]).ids
                
                # import wdb;wdb.set_trace()
                
                
                examiners = self.examiners.ids
                
                assignments = {examiner: [] for examiner in examiners}  # Dictionary to store assignments

            
                for i, candidate in enumerate(gp_marksheets):
                    examiner_index = i % len(examiners)  # Calculate the index of the examiner using modulo
                    examiner = examiners[examiner_index]
                    assignments[examiner].append(candidate)   
                    
                for examiner, assigned_candidates in assignments.items():
                    examiner_id = examiner
                    for i in assigned_candidates:
                        gp_marksheet = self.env['gp.exam.schedule'].browse(i).id
                        gsk_oral = self.env['gp.exam.schedule'].browse(i).mek_oral.id
                        gsk_prac = self.env['gp.exam.schedule'].browse(i).mek_prac.id
                        candidate = self.env['gp.exam.schedule'].browse(i).gp_candidate.id
                        
                        self.env['exam.type.oral.practical.examiners.marksheet'].create({ 'examiners_id':examiner_id ,'gp_marksheet':gp_marksheet,'gp_candidate':candidate , 'mek_oral':gsk_oral , 'mek_prac':gsk_prac })
                
                self.write({'state':'2-confirm'})
                                            

                
            
        elif self.course.course_code == 'CCMC':
            
            # import wdb;wdb.set_trace()
            
            ccmc_marksheets = self.env['ccmc.exam.schedule'].search([('dgs_batch','=',self.dgs_batch.id),('registered_institute','=',self.institute_id.id),('state','=','1-in_process'),('oral_prac_status','=','failed')]).ids
            
            examiners = self.examiners.ids
            
            assignments = {examiner: [] for examiner in examiners}  # Dictionary to store assignments
            
            for i, candidate in enumerate(ccmc_marksheets):
                    examiner_index = i % len(examiners)  # Calculate the index of the examiner using modulo
                    examiner = examiners[examiner_index]
                    assignments[examiner].append(candidate)
            
            
            
            for examiner, assigned_candidates in assignments.items():
                examiner_id = examiner
                for i in assigned_candidates:
                    ccmc_marksheet = self.env['ccmc.exam.schedule'].browse(i).id
                    ccmc_oral = self.env['ccmc.exam.schedule'].browse(i).ccmc_oral.id
                    cookery_bakery = self.env['ccmc.exam.schedule'].browse(i).cookery_bakery.id
                    candidate = self.env['ccmc.exam.schedule'].browse(i).ccmc_candidate.id
                    self.env['exam.type.oral.practical.examiners.marksheet'].create({ 'examiners_id': examiner_id ,'ccmc_marksheet':ccmc_marksheet,'ccmc_candidate':candidate ,'ccmc_oral':ccmc_oral , 'cookery_bakery':cookery_bakery })
            
            self.write({'state':'2-confirm'})       

    

class ExamOralPracticalExaminers(models.Model):
    _name = 'exam.type.oral.practical.examiners'
    dgs_batch = fields.Many2one("dgs.batches",related='prac_oral_id.dgs_batch',string="DGS Batch",required=False)
    
    prac_oral_id = fields.Many2one("exam.type.oral.practical",string="Exam Practical/Oral ID",required=False)
    course = fields.Many2one("course.master",related='prac_oral_id.course',string="Course")
    subject = fields.Many2one("course.master.subject",related='prac_oral_id.subject',string="Subject")
    examiner = fields.Many2one('bes.examiner', string="Examiner")
    exam_date = fields.Date("Exam Date")
    marksheets = fields.One2many('exam.type.oral.practical.examiners.marksheet','examiners_id',string="Candidates")
    
    def open_marksheet_list(self):
        
        if self.prac_oral_id.subject.name == 'GSK':
            views = [(self.env.ref("bes.view_marksheet_gp_tree_gsk").id, 'tree'),  # Define tree view
                    (self.env.ref("bes.view_marksheet_gp_form_gsk").id, 'form')]
        elif self.prac_oral_id.subject.name == 'MEK':
             views = [(self.env.ref("bes.view_marksheet_gp_tree_mek").id, 'tree'),  # Define tree view
                    (self.env.ref("bes.view_marksheet_gp_form_mek").id, 'form')]
        elif self.prac_oral_id.subject.name == 'CCMC':
            views = [(self.env.ref("bes.view_marksheet_ccmc_tree_oral").id, 'tree'),  # Define tree view
                    (self.env.ref("bes.view_marksheet_ccmc_form_oral").id, 'form')]
            
        
        
        return {
            'name': 'GP Marksheet',
            'domain': [('examiners_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',  # Specify both tree and form views
            'res_model': 'exam.type.oral.practical.examiners.marksheet',
            'views': views,
            'target': 'current',
        }
        
class OralPracticalExaminersMarksheet(models.Model):
    _name = 'exam.type.oral.practical.examiners.marksheet'
    
    examiners_id = fields.Many2one("exam.type.oral.practical.examiners",string="Examiners ID")
    gp_candidate = fields.Many2one("gp.candidate",string="GP Candidate")
    gp_marksheet = fields.Many2one("gp.exam.schedule",string="GP Marksheet")
    ccmc_marksheet = fields.Many2one("ccmc.exam.schedule",string="GP Marksheet")
    ccmc_candidate = fields.Many2one("ccmc.candidate",string="CCMC Candidate")
    mek_oral = fields.Many2one("gp.mek.oral.line","MEK Oral")
    mek_prac = fields.Many2one("gp.mek.practical.line","MEK Practical")
    gsk_oral = fields.Many2one("gp.gsk.oral.line","GSK Oral")
    gsk_prac = fields.Many2one("gp.gsk.practical.line","GSK Practical")
    cookery_bakery = fields.Many2one("ccmc.cookery.bakery.line","Cookery And Bakery")
    ccmc_oral = fields.Many2one("ccmc.oral.line","CCMC Oral")

    
    
    
    # def open_oral_prac_candidate(self):
        
    #     candidates_id = self.candidates.ids
            
    #     return {
    #     'name': 'Exam Candidate',
    #     'domain': [('id', 'in', candidates_id)],
    #     'view_type': 'form',
    #     'res_model': 'exam.schedule.bes.candidate',
    #     'view_id': False,
    #     'view_mode': 'tree,form',
    #     'type': 'ir.actions.act_window',
    #     'context': {
    #         'subject_id': self.subject.id
    #     }
    #     }       
        
        
    
    # @api.onchange('exam_schedule_id')
    # def onchange_exam_schedule_id(self):
    #     for rec in self:
    #         return {'domain':{'subject':[('id','in',rec.exam_schedule_id.course.subjects.ids)]}}
    
    
    # def compute_candidate_count(self):
    #     for rec in self:
    #         count = len(rec.candidates)
    #         rec.candidate_count = count
    
    # @api.onchange('exam_schedule_id')
    # def onchange_exam_schedule_id(self):
    #     for rec in self:
    #         return {'domain':{'examiners':[('id','in',rec.exam_schedule_id.examiners.ids)]}}
   

    
    
class GPExam(models.Model):
    _name = "gp.exam.schedule"
    _rec_name = "exam_id"
    _description= 'Schedule'
    
    exam_id = fields.Char("Roll No",required=True, copy=False, readonly=True)

    registered_institute = fields.Many2one("bes.institute",string="Registered Institute")
    
    dgs_batch = fields.Many2one("dgs.batches",string="DGS Batch",required=True)
    certificate_id = fields.Char(string="Certificate ID")
    gp_candidate = fields.Many2one("gp.candidate","GP Candidate")
    # roll_no = fields.Char(string="Roll No",required=True, copy=False, readonly=True,
    #                             default=lambda self: _('New')) 
    
    institute_name = fields.Many2one("bes.institute","Institute Name")
    mek_oral = fields.Many2one("gp.mek.oral.line","MEK Oral")
    mek_prac = fields.Many2one("gp.mek.practical.line","MEK Practical")
    gsk_oral = fields.Many2one("gp.gsk.oral.line","GSK Oral")
    gsk_prac = fields.Many2one("gp.gsk.practical.line","GSK Practical")
    gsk_online = fields.Many2one("survey.user_input","GSK Online")
    mek_online = fields.Many2one("survey.user_input","MEK Online")
    attempt_number = fields.Integer("Attempt Number", default=1, copy=False,readonly=True)
    
    
    gsk_oral_marks = fields.Float("GSK Oral/Journal",readonly=True)
    mek_oral_marks = fields.Float("MEK Oral/Journal",readonly=True)
    gsk_practical_marks = fields.Float("GSK Practical",readonly=True)
    mek_practical_marks = fields.Float("MEK Practical",readonly=True)
    gsk_total = fields.Float("GSK Oral/Practical",readonly=True)
    gsk_percentage = fields.Float("GSK Oral/Practical Precentage",readonly=True)
    
    mek_total = fields.Float("MEK Total",readonly=True)
    mek_percentage = fields.Float("MEK Percentage",readonly=True)
    mek_online_marks = fields.Float("MEK Online",readonly=True, digits=(16,2))
    gsk_online_marks = fields.Float("GSK Online",readonly=True,digits=(16,2))
    mek_online_percentage = fields.Float("MEK Online (%)",readonly=True,digits=(16,2))
    gsk_online_percentage = fields.Float("GSK Online (%)",readonly=True,digits=(16,2))    
    mek_total = fields.Float("MEK Oral/Practical",readonly=True)
    mek_percentage = fields.Float("MEK Oral/Practical Percentage",readonly=True)
    overall_marks = fields.Float("Overall Marks",readonly=True)
    overall_percentage = fields.Float("Overall (%)",readonly=True)
    gsk_oral_prac_status = fields.Selection([
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='GSK Oral/Practical Status', default='pending')
    
    mek_oral_prac_status = fields.Selection([
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='MEK Oral/Practical Status', default='pending')
    
    mek_online_status = fields.Selection([
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='MEK Online Status', default='pending')
    
    gsk_online_status = fields.Selection([
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='GSK Online Status', default='pending')
    
    exam_criteria = fields.Selection([
        ('', ''),
        ('pending', 'Pending'),
        ('passed', 'Complied'),
    ], string='Exam Criteria' , compute="compute_certificate_criteria")
    
    certificate_criteria = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Complied'),
    ], string='Certificate Criteria',compute="compute_pending_certificate_criteria")

    
    stcw_criteria = fields.Selection([
        ('', ''),
        ('pending', 'Pending'),
        ('passed', 'Complied'),
    ], string='STCW Criteria' , compute="compute_certificate_criteria")
    
    ship_visit_criteria = fields.Selection([
        ('', ''),
        ('pending', 'Pending'),
        ('passed', 'Complied'),
    ], string='Ship Visit Criteria' , compute="compute_certificate_criteria")
    
    
    attendance_criteria = fields.Selection([
        ('', ''),
        ('pending', 'Pending'),
        ('passed', 'Complied'),
    ], string='Attendance Criteria' , compute="compute_certificate_criteria")

    
    state = fields.Selection([
        ('1-in_process', 'In Process'),
        ('2-done', 'Done'),
        ('3-certified', 'Certified'),
        ('4-pending', 'Pending'),
    ], string='State', default='1-in_process')

    url = fields.Char("URL",compute="_compute_url")
    qr_code = fields.Binary(string="Admit Card QR Code", compute="_compute_url", store=True)
    certificate_qr_code = fields.Binary(string=" Certificate QR Code", compute="_compute_certificate_url")
    
    dgs_visible = fields.Boolean("DGS Visible",compute="compute_dgs_visible")
    
    exam_pass_date = fields.Date(string="Date of Examination Passed:")
    certificate_issue_date = fields.Date(string="Date of Issue of Certificate:")
    rank = fields.Char("Rank",compute='_compute_rank')
    
    institute_code = fields.Char(string="Institute Code", related='gp_candidate.institute_id.code', required=True)


    
    

    
    @api.depends('overall_percentage','gp_candidate')
    def _compute_rank(self):
        for rec in self:
            sorted_records = self.env['gp.exam.schedule'].search([('dgs_batch','=',rec.dgs_batch.id),('attempt_number','=',1),('state','=','3-certified')],
                                                             order='overall_percentage desc , institute_code asc , gp_candidate asc')
        # import wdb; wdb.set_trace();
        total_records = len(sorted_records)
        top_25_percent = int(total_records * 0.25)

        for record in self:
            # print(record.id)
            try:
                index = sorted_records.ids.index(record.id)
                numeric_rank = index + 1 if index < top_25_percent else 0

                # Convert numeric rank to character format
                if numeric_rank % 10 == 1 and numeric_rank % 100 != 11:
                    suffix = 'st'
                elif numeric_rank % 10 == 2 and numeric_rank % 100 != 12:
                    suffix = 'nd'
                elif numeric_rank % 10 == 3 and numeric_rank % 100 != 13:
                    suffix = 'rd'
                else:
                    suffix = 'th'

                record.rank = f'{numeric_rank}{suffix}'
            except:
                record.rank = "0th"
    
    



    
    @api.depends('certificate_criteria','state')
    def compute_dgs_visible(self):
        for record in self:
            if record.certificate_criteria == 'passed' and record.state == '2-done':
                record.dgs_visible = True
            else:
                record.dgs_visible = False

    @api.depends('certificate_id','state')
    def _compute_certificate_url(self):
        for record in self:
            # print("Working CERT URL Func")

            if record.state == "3-certified":
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                # print("base_url:", base_url)

                certificate_id = record.id
                current_certificate_url = base_url + "verification/gpcerificate/" + str(certificate_id)
                # print("current_url:", current_certificate_url)
                qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
                qr.add_data(current_certificate_url)
                qr.make(fit=True)
                qr_image = qr.make_image()

                # Convert the QR code image to base64 string
                buffered = io.BytesIO()
                qr_image.save(buffered, format="PNG")
                qr_image_base64 = base64.b64encode(buffered.getvalue()).decode()

                # Assign the base64 string to a field in the 'srf' object
                record.certificate_qr_code = qr_image_base64
            else:
                record.certificate_qr_code = None
        


    def _compute_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        current_url = base_url + "verification/gpadmitcard/" + str(self.id)
        self.url = current_url
        print("Current URL:", current_url)
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(current_url)
        qr.make(fit=True)
        qr_image = qr.make_image()

        # Convert the QR code image to base64 string
        buffered = io.BytesIO()
        qr_image.save(buffered, format="PNG")
        qr_image_base64 = base64.b64encode(buffered.getvalue()).decode()

        # Assign the base64 string to a field in the 'srf' object
        self.qr_code = qr_image_base64
        
    
    
    @api.depends('gsk_online_status','mek_online_status','mek_oral_prac_status','gsk_oral_prac_status')
    def compute_certificate_criteria(self):
        for record in self:
            all_passed = all(field == 'passed' for field in [record.gsk_online_status, record.mek_online_status, record.mek_oral_prac_status , record.gsk_oral_prac_status])
            all_course_types = ['pst', 'efa', 'fpff', 'pssr', 'stsdsd']
            course_type_already  = [course.course_name for course in record.gp_candidate.stcw_certificate]
            all_types_exist = all(course_type in course_type_already for course_type in all_course_types)
            
            if all_passed:
                # import wdb; wdb.set_trace();
                record.exam_criteria = 'passed'
            else:
                record.exam_criteria = 'pending'
                
            if all_types_exist:
                # import wdb; wdb.set_trace();
                record.stcw_criteria = 'passed'
            else:
                record.stcw_criteria = 'pending'
                
            if record.gp_candidate.attendance_compliance_1 == 'yes' or record.gp_candidate.attendance_compliance_2 == 'yes':
                record.attendance_criteria = 'passed'
            else:
                record.attendance_criteria = 'pending'
            
            if len(record.gp_candidate.ship_visits) > 0:
                
                record.ship_visit_criteria = 'passed'
                
            else:

                record.ship_visit_criteria = 'pending'
    
    @api.depends('exam_criteria','stcw_criteria','attendance_criteria','ship_visit_criteria')
    def compute_pending_certificate_criteria(self):
        for record in self:
            if record.exam_criteria == record.stcw_criteria == record.attendance_criteria == record.ship_visit_criteria == 'passed':
                record.certificate_criteria = 'passed'
            else:
                record.certificate_criteria = 'pending'

                
        
    # def move_done(self):
    #         if(self.certificate_criteria == 'passed'):
    #             self.certificate_id = self.env['ir.sequence'].next_by_code("gp.exam.schedule")
    #         self.state = '2-done'
    def open_marksheet_wizard(self):
        view_id = self.env.ref('bes.gp_marksheet_creation_wizard_form').id
        
        return {
            'name': 'Add Marksheet',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'gp.marksheet.creation.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }
    
    def dgs_approval(self):
        
            if(self.certificate_criteria == 'passed'):
                # date = self.dgs_batch.from_date
                self.certificate_id = str(self.gp_candidate.candidate_code) + '/' + self.dgs_batch.to_date.strftime('%b %y') + '/' + self.exam_id
                self.state = '3-certified'
                self.certificate_issue_date = self.dgs_batch.certificate_issue_date
                self.exam_pass_date = self.dgs_batch.exam_pass_date
            else:
                self.state = '4-pending'
                
            
    
    
    @api.model
    def create(self, vals):
        if vals.get('gp_candidate'):
            candidate_id = vals['gp_candidate']
            last_attempt = self.search([('gp_candidate', '=', candidate_id)], order='attempt_number desc', limit=1)
            vals['attempt_number'] = last_attempt.attempt_number + 1 if last_attempt else 1

            a = super(GPExam, self).create(vals)   

            if a.gsk_oral_prac_status == "pending":
                self.env['gp.exam.appear'].create(
                    {
                        'gp_exam_schedule_id': a.id,
                        'subject_name': 'GSK Oral/Practical'
                    }
                )    
                
            if a.mek_oral_prac_status == "pending":
                self.env['gp.exam.appear'].create(
                    {
                        'gp_exam_schedule_id': a.id,
                        'subject_name': 'MEK Oral/Practical'
                    }
                )  
                
            if a.gsk_online_status == "pending":
                self.env['gp.exam.appear'].create(
                    {
                        'gp_exam_schedule_id': a.id,
                        'subject_name': 'GSK Online'
                    }
                )
                  
            if a.mek_online_status == "pending":
                self.env['gp.exam.appear'].create(
                    {
                        'gp_exam_schedule_id': a.id,
                        'subject_name': 'MEK Online'
                    }
                )  
                
            return a 
            
    
    # @api.model
    # def create(self,vals):
       
    #     return super(, self).create(vals)
    
    # def apply_unique_sequence_to_existing_data(self):
    #     records_without_sequence = self.search([('roll_no', '=', 'New')])

    #     for record in records_without_sequence:
    #         new_roll_no = self.env['ir.sequence'].next_by_code('gp.exam.schedule')
    #         record.write({'roll_no': new_roll_no})

    # # Run this method to apply the unique sequence to existing records
    # def apply_unique_sequence_to_existing_records(self):
    #     existing_records = self.search([('roll_no', '=', 'New')])
    #     for record in existing_records:
    #         new_roll_no = self.env['ir.sequence'].next_by_code('gp.exam.schedule')
    #         record.write({'roll_no': new_roll_no})
    
    
    
    @api.constrains('gp_candidate')
    def _check_exam_count(self):
        max_exams = 7
        for record in self:
            # import wdb; wdb.set_trace();
            candidate = record.gp_candidate
            exams_count = self.env["gp.exam.schedule"].search_count([('gp_candidate', '=', candidate.id)])
            if exams_count > max_exams:
                raise ValidationError(f"The candidate {candidate.name} already has 7 exams scheduled. "
                                      f"You cannot schedule more than {max_exams} exams for a candidate.")
    
        
        
    def move_done(self):
                # import wdb; wdb.set_trace();

        
        

        mek_oral_draft_confirm = self.mek_oral.mek_oral_draft_confirm == 'confirm'
        mek_practical_draft_confirm = self.mek_prac.mek_practical_draft_confirm == 'confirm'
        gsk_oral_draft_confirm = self.gsk_oral.gsk_oral_draft_confirm == 'confirm'
        gsk_practical_draft_confirm = self.gsk_prac.gsk_practical_draft_confirm == 'confirm'
        
        gsk_online_done = self.gsk_online.state == 'done' 
        mek_online_done = self.mek_online.state == 'done'
        
        if not (len(self.mek_oral) == 0 and len(self.mek_prac) == 0) or not (len(self.gsk_oral) == 0 and len(self.gsk_prac) == 0) or not (len(self.gsk_online) == 0) or not (len(self.mek_online) == 0)  :
            
            if not (len(self.mek_oral) == 0 and len(self.mek_prac) == 0):
                if mek_oral_draft_confirm and mek_practical_draft_confirm: 
                    mek_oral_marks = self.mek_oral.mek_oral_total_marks
                    self.mek_oral_marks = mek_oral_marks
                    mek_practical_marks = self.mek_prac.mek_practical_total_marks
                    self.mek_practical_marks = mek_practical_marks
                    mek_total_marks = mek_oral_marks + mek_practical_marks
                    self.mek_total = mek_total_marks
                    self.mek_percentage = (mek_total_marks/175) * 100
                    
                    if self.mek_percentage >= 60:
                        self.mek_oral_prac_status = 'passed'
                    else:
                        self.mek_oral_prac_status = 'failed'
                else:
                    raise ValidationError("MEK Oral Or Practical Not Confirmed")

            if not (len(self.gsk_oral) == 0 and len(self.gsk_prac) == 0):
                
                if gsk_oral_draft_confirm and gsk_practical_draft_confirm:
                    gsk_oral_marks = self.gsk_oral.gsk_oral_total_marks
                    self.gsk_oral_marks = gsk_oral_marks
                    gsk_practical_marks = self.gsk_prac.gsk_practical_total_marks
                    self.gsk_practical_marks = gsk_practical_marks
                    gsk_total_marks = gsk_oral_marks + gsk_practical_marks
                    self.gsk_total = gsk_total_marks
                    self.gsk_percentage = (gsk_total_marks/175) * 100
                    
                    if self.gsk_percentage >= 60:
                        self.gsk_oral_prac_status = 'passed'
                    else:
                        self.gsk_oral_prac_status = 'failed'
                else:
                    raise ValidationError("GSK Oral Or Practical Not Confirmed")
            
            if not (len(self.gsk_online) == 0):
                
                if gsk_online_done:
                
                    self.gsk_online_marks = self.gsk_online.scoring_total
                    self.gsk_online_percentage = (self.gsk_online_marks/75)*100
                    
                    if self.gsk_online_percentage >= 60 :
                        self.gsk_online_status = 'passed'
                    else:
                        self.gsk_online_status = 'failed'
                else:
                    raise ValidationError("GSK Online Exam Not Done or Confirmed")
            
            if not (len(self.mek_online) == 0):
                if mek_online_done:
                
                    self.mek_online_marks = self.mek_online.scoring_total
                    self.mek_online_percentage = (self.mek_online_marks/75)*100
                    
                    if self.mek_online_percentage >= 60 :
                        self.mek_online_status = 'passed'
                    else:
                        self.mek_online_status = 'failed'
                else:
                    raise ValidationError("MEK Online Exam Not Done or Confirmed")
                
                
            
            # print("Doing Nothing")
            overall_marks = self.gsk_total + self.mek_total + self.mek_online_marks + self.gsk_online_marks
            self.overall_marks = overall_marks
            self.overall_percentage = (overall_marks/500) * 100
            
            self.state = '2-done'
        else:
            
        
        
            if mek_oral_draft_confirm and mek_practical_draft_confirm and gsk_oral_draft_confirm and gsk_practical_draft_confirm and gsk_online_done and mek_online_done:
            
                mek_oral_marks = self.mek_oral.mek_oral_total_marks
                self.mek_oral_marks = mek_oral_marks
                mek_practical_marks = self.mek_prac.mek_practical_total_marks
                self.mek_practical_marks = mek_practical_marks
                mek_total_marks = mek_oral_marks + mek_practical_marks
                self.mek_total = mek_total_marks
                self.mek_percentage = (mek_total_marks/175) * 100
                self.mek_online_marks = self.mek_online.scoring_total
                self.mek_online_percentage = (self.mek_online_marks/75)*100
                
                
                
                if self.mek_percentage >= 60:
                    self.mek_oral_prac_status = 'passed'
                else:
                    self.mek_oral_prac_status = 'failed'


                gsk_oral_marks = self.gsk_oral.gsk_oral_total_marks
                self.gsk_oral_marks = gsk_oral_marks
                gsk_practical_marks = self.gsk_prac.gsk_practical_total_marks
                self.gsk_practical_marks = gsk_practical_marks
                gsk_total_marks = gsk_oral_marks + gsk_practical_marks
                self.gsk_total = gsk_total_marks
                self.gsk_percentage = (gsk_total_marks/175) * 100
                self.gsk_online_marks = self.gsk_online.scoring_total
                self.gsk_online_percentage = (self.gsk_online_marks/75)*100
                
                overall_marks = self.gsk_total + self.mek_total + self.mek_online_marks + self.gsk_online_marks
                self.overall_marks = overall_marks
                self.overall_percentage = (overall_marks/500) * 100
                
                if self.gsk_percentage >= 60:
                    self.gsk_oral_prac_status = 'passed'
                else:
                    self.gsk_oral_prac_status = 'failed'

                
                # self.state = '2-done'
                
                
                
                
                if self.gsk_online_percentage >= 60 :
                    self.gsk_online_status = 'passed'
                else:
                    self.gsk_online_status = 'failed'
                    
                
                if self.mek_online_percentage >= 60 :
                    self.mek_online_status = 'passed'
                else:
                    self.mek_online_status = 'failed'
                
                
                
                
                all_passed = all(field == 'passed' for field in [self.mek_oral_prac_status, self.gsk_oral_prac_status, self.gsk_online_status , self.mek_online_status , self.exam_criteria , self.stcw_criteria , self.ship_visit_criteria , self.attendance_criteria ])

                
                self.state = '2-done'
                    
                    
            
            else:
                raise ValidationError("Not All exam are Confirmed")

    attempting_exam_list = fields.One2many("gp.exam.appear",'gp_exam_schedule_id',string="Attempting Exams Lists")
    


    def send_certificate_email(self):
        print(self,"selffffffffffffffffffffffffffffffffffffffffffff")
        # Replace 'bes.report_gp_certificate' with the correct XML ID of the report template
        report_template = self.env.ref('bes.report_gp_certificate')
        report_pdf = report_template.render_pdf([self.id])
        print(report_pdf, "reportttttttttttttttttttttttttttttttttttttttttttttt")
        
        # Render the report as PDF
        # generated_report = report_template._render_qweb_pdf(self.id)
        # print(generated_report,"genraaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

         # Convert the report to PDF format
        # pdf_content = self.env['ir.actions.report'].convert(
        #         generated_report,
        #         'pdf',
        #         {'model': self._name, 'id': self.ids[0]}
        #     )
        # print(pdf_content,"pdfffffffffffffffffffffffffffffffffffffff")

        # Encode the PDF data
        data_record = base64.b64encode(report_pdf[0])
        

        # Create an attachment record
        ir_values = {
            'name': 'Certificate Report',
            'type': 'binary',
            'datas': data_record,
            'store_fname': 'Certificate_Report.pdf',
            'mimetype': 'application/pdf',
            'res_model': 'gp.exam.schedule',
        }

        print(ir_values,"valuessssssssssssssssssssssssssssssssssssssssssssssssssssssssssss")
        report_attachment = self.env['ir.attachment'].sudo().create(ir_values)
        
        # Get the email template
        email_template = self.env.ref('bes.gp_certificate_mail')
        
        # Prepare email values
        email_values = {
            'email_to': self.gp_candidate.email,  # Use the appropriate recipient's email address
            'email_from': self.env.user.email,
        }
        
        # Attach the PDF to the email template
        if email_template:
            email_template.attachment_ids = [(4, report_attachment.id)]
            
            # Send the email
            email_template.send_mail(self.id, email_values=email_values, force_send=True)
            
            # Remove the attachment from the email template
            email_template.attachment_ids = [(5, 0, 0)]


    
class GPAppearingExam(models.Model):
    _name = 'gp.exam.appear'
    
    gp_exam_schedule_id = fields.Many2one('gp.exam.schedule',string="GP Exam ID")
    subject_name = fields.Char(string="Appearing Exam Lists")
    
    
    
    
    

# class GPCertificate(models.AbstractModel):
#     _name = 'report.bes.report_general_certificate'

#     @api.model
#     def _get_report_values(self, docids, data=None):
#         docs1 = self.env['gp.exam.schedule'].sudo().browse(docids)
        
#         if docs1.certificate_criteria == 'passed' :
#             return {
#                 'docids': docids,
#                 'doc_model': 'gp.exam.schedule',
#                 'data': data,
#                 'docs': docs1
#             }
#         else:
#             raise ValidationError("Certificate criteria not met. Report cannot be generated.")
        
class GPCertificate(models.AbstractModel):
    _name = 'report.bes.report_general_certificate'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs1 = self.env['gp.exam.schedule'].sudo().browse(docids)
        
        if docs1.certificate_criteria == 'passed' and docs1.certificate_id:
            return {
                'docids': docids,
                'doc_model': 'gp.exam.schedule',
                'data': data,
                'docs': docs1
            }
        else:
            raise ValidationError("Certificate criteria not met. Report cannot be generated.")


class CCMCExam(models.Model):
    _name = "ccmc.exam.schedule"
    _rec_name = "exam_id"
    _description= 'Schedule'
    
    dgs_batch = fields.Many2one("dgs.batches",string="DGS Batch",required=True)
    certificate_id = fields.Char(string="Certificate ID")
    institute_name = fields.Many2one("bes.institute","Institute Name")
    exam_id = fields.Char(string="Roll No",required=True, copy=False, readonly=True)
    registered_institute = fields.Many2one("bes.institute",string="Registered Institute")
    ccmc_candidate = fields.Many2one("ccmc.candidate","CCMC Candidate")
    cookery_bakery = fields.Many2one("ccmc.cookery.bakery.line","Cookery And Bakery")
    ccmc_oral = fields.Many2one("ccmc.oral.line","CCMC Oral")
    ccmc_online = fields.Many2one("survey.user_input",string="CCMC Online")

    attempt_number = fields.Integer("Attempt Number", default=1, copy=False,readonly=True)
    
    cookery_practical = fields.Float("Cookery Practical",readonly=True)
    cookery_bakery_percentage = fields.Float("Cookery And Bakery Precentage",readonly=True)
    cookery_gsk_online = fields.Float("Cookery/GSK Online",readonly=True,digits=(16,2))
    overall_marks = fields.Float("Overall Marks",readonly=True)
    overall_percentage = fields.Float("Overall Percentage",readonly=True)
    cookery_gsk_online_percentage = fields.Float("Cookery/GSK Online Percentage",readonly=True)
    cookery_bakery_prac_status = fields.Selection([
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='Cookery And Bakery')
    
    
    cookery_bakery_prac_oral_status = fields.Selection([
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='Cookery And Bakery')
    
    
    cookery_oral = fields.Float("Cookery Oral",readonly=True)
    ccmc_oral_percentage = fields.Float("Cookery Oral Percentage",readonly=True)
    ccmc_oral_prac_status = fields.Selection([
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='CCMC Oral Status')
    
    oral_prac_status = fields.Selection([
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='Oral/Prac Status',compute="compute_oral_prac_status")
    
    attendance_criteria = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Passed'),
    ], string='Attendance Criteria' , compute="compute_certificate_criteria")

    
    
    exam_criteria = fields.Selection([
        ('', ''),
        ('pending', 'Pending'),
        ('passed', 'Passed'),
    ], string='Exam Criteria' , compute="compute_certificate_criteria")
    
    ccmc_online_status = fields.Selection([
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='CCMC Online Status')
    
    
    
    stcw_criteria = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Passed'),
    ], string='STCW Criteria',compute="compute_certificate_criteria")

    ship_visit_criteria = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Passed'),
    ], string='Ship Visit Criteria',compute="compute_certificate_criteria")
    
    
    
    
    state = fields.Selection([
        ('1-in_process', 'In Process'),
        ('2-done', 'Done'),
        ('3-certified', 'Certified'),
        ('4-pending', 'Pending'),
    ], string='State', default='1-in_process')
    
    certificate_criteria = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Complied'),
    ], string='Certificate Criteria',compute="compute_pending_certificate_criteria")
    
    # @api.depends('cookery_bakery_prac_status','ccmc_oral_prac_status','')
    # def compute_certificate_criteria(self):
    
    url = fields.Char("URL",compute="_compute_url")
    qr_code = fields.Binary(string="QR Code", compute="_compute_url", store=True)
    certificate_qr_code = fields.Binary(string=" Certificate QR Code", compute="_compute_certificate_url")

    dgs_visible = fields.Boolean("DGS Visible",compute="compute_dgs_visible")
    
    exam_pass_date = fields.Date(string="Date of Examination Passed:")
    certificate_issue_date = fields.Date(string="Date of Issue of Certificate:")
    ccmc_rank = fields.Char("Rank",compute='_compute_rank')
   
    institute_code = fields.Char("Institute code")
    
    @api.depends('ccmc_oral_prac_status','cookery_bakery_prac_status')
    def compute_oral_prac_status(self):
        for record in self:
            # import wdb; wdb.set_trace()
            if record.cookery_bakery_prac_status == 'failed' or record.ccmc_oral_prac_status == 'failed':
                record.oral_prac_status = 'failed'
            else:
                record.oral_prac_status = ''
                
            
            
        
    
    @api.depends('certificate_criteria','state')
    def compute_dgs_visible(self):
        for record in self:
            if record.certificate_criteria == 'passed' and record.state == '2-done':
                record.dgs_visible = True
            else:
                record.dgs_visible = False

    @api.depends('exam_criteria','stcw_criteria','attendance_criteria','ship_visit_criteria')
    def compute_pending_certificate_criteria(self):
        for record in self:
            if record.exam_criteria == record.stcw_criteria == record.attendance_criteria == record.ship_visit_criteria == 'passed':
                record.certificate_criteria = 'passed'
            else:
                record.certificate_criteria = 'pending'
    
    def _compute_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        print("Base URL:", base_url)
        current_url = base_url + "verification/ccmcadmitcard/" + str(self.id)
        self.url = current_url
        print("Current URL:", current_url)
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(current_url)
        qr.make(fit=True)
        qr_image = qr.make_image()

        # Convert the QR code image to base64 string
        buffered = io.BytesIO()
        qr_image.save(buffered, format="PNG")
        qr_image_base64 = base64.b64encode(buffered.getvalue()).decode()

        # Assign the base64 string to a field in the 'srf' object
        self.qr_code = qr_image_base64

    
    @api.depends('stcw_criteria','ship_visit_criteria','cookery_bakery_prac_status','ccmc_online_status')
    def compute_certificate_criteria(self):
        for record in self:
            
            all_passed = all(field == 'passed' for field in [record.cookery_bakery_prac_status , record.ccmc_online_status, record.ccmc_oral_prac_status])
            all_course_types = ['pst', 'efa', 'fpff', 'pssr', 'stsdsd']
            course_type_already  = [course.course_name for course in record.ccmc_candidate.stcw_certificate]
            all_types_exist = all(course_type in course_type_already for course_type in all_course_types)

            # course_type_already  = [course.course_name for course in record.gp_candidate.stcw_certificate]

            if all_types_exist:
                # import wdb; wdb.set_trace();
                record.stcw_criteria = 'passed'
            else:
                record.stcw_criteria = 'pending'
            
            if record.ccmc_candidate.attendance_compliance_1 == 'yes' or record.ccmc_candidate.attendance_compliance_2 == 'yes':
                record.attendance_criteria = 'passed'
            else:
                record.attendance_criteria = 'pending'

            if all_passed:
                # import wdb; wdb.set_trace();
                record.exam_criteria = 'passed'
            else:
                record.exam_criteria = 'pending'
            
            if len(record.ccmc_candidate.ship_visits) > 0:
                record.ship_visit_criteria = 'passed'
            else:
                record.ship_visit_criteria = 'pending'
                
               
    def dgs_approval(self):
        print(self.state,"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
        if(self.certificate_criteria == 'passed'):
            # date = self.dgs_batch.from_date
            self.certificate_id = str(self.ccmc_candidate.candidate_code) + '/' + self.dgs_batch.to_date.strftime('%b %y') + '/' + self.exam_id
            print(self.certificate_id,"criiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
            self.state = '3-certified'
            self.certificate_issue_date = self.dgs_batch.certificate_issue_date
            self.exam_pass_date = self.dgs_batch.exam_pass_date
        else:
            self.state = '4-pending'
            # self.certificate_issue_date = fields.date.today() 
    
    @api.depends('overall_percentage')
    def _compute_rank(self):
        
        for rec in self:
            sorted_records = self.env['ccmc.exam.schedule'].search([('dgs_batch','=',rec.dgs_batch.id),('attempt_number','=',1),('state','=','3-certified')],
                                                             order='overall_percentage desc , institute_code asc, ccmc_candidate asc')
        
        # import wdb; wdb.set_trace();
        total_records = len(sorted_records)
        top_25_percent = int(total_records * 0.25)

        for record in self:
            print(record.id)
            try:
                index = sorted_records.ids.index(record.id)
                numeric_rank = index + 1 if index < top_25_percent else 0

                # Convert numeric rank to character format
                if numeric_rank % 10 == 1 and numeric_rank % 100 != 11:
                    suffix = 'st'
                elif numeric_rank % 10 == 2 and numeric_rank % 100 != 12:
                    suffix = 'nd'
                elif numeric_rank % 10 == 3 and numeric_rank % 100 != 13:
                    suffix = 'rd'
                else:
                    suffix = 'th'

                record.ccmc_rank = f'{numeric_rank}{suffix}'
            except:
                record.ccmc_rank = "0th"
    

    @api.depends('certificate_id','state')
    def _compute_certificate_url(self):
        for record in self:
            print("Working CERT URL Func")

            if record.state == "3-certified":
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                print("base_url:", base_url)

                certificate_id = record.id
                current_certificate_url = base_url + "verification/ccmccerificate/" + str(certificate_id)
                print("current_url:", current_certificate_url)
                qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
                qr.add_data(current_certificate_url)
                qr.make(fit=True)
                qr_image = qr.make_image()

                # Convert the QR code image to base64 string
                buffered = io.BytesIO()
                qr_image.save(buffered, format="PNG")
                qr_image_base64 = base64.b64encode(buffered.getvalue()).decode()

                # Assign the base64 string to a field in the 'srf' object
                record.certificate_qr_code = qr_image_base64
            else:
                record.certificate_qr_code = None
    
    @api.model
    def create(self, vals):
        if vals.get('ccmc_candidate'):
            candidate_id = vals['ccmc_candidate']
            last_attempt = self.search([('ccmc_candidate', '=', candidate_id)], order='attempt_number desc', limit=1)
            vals['attempt_number'] = last_attempt.attempt_number + 1 if last_attempt else 1
        
        return super(CCMCExam, self).create(vals)

        
    
    
    
    def move_done(self):
        
        # import wdb; wdb.set_trace(); 
        cookery_draft_confirm = self.cookery_bakery.cookery_draft_confirm == 'confirm'
        ccmc_oral_state = self.ccmc_oral.ccmc_oral_draft_confirm == 'confirm'
        ccmc_online_state = self.ccmc_online.state == 'done'
        
        
        if not (len(self.cookery_bakery)==0 and len(self.ccmc_oral)==0 ) or not (len(self.ccmc_online)==0):
            
             if not (len(self.cookery_bakery)==0 and len(self.ccmc_oral)==0 ):
                 
                 if cookery_draft_confirm and ccmc_oral_state:
                     cookery_bakery_marks = self.cookery_bakery.total_mrks
                     ccmc_oral_marks = self.ccmc_oral.toal_ccmc_rating
                     self.ccmc_oral_total = ccmc_oral_marks
                     self.cookery_practical = cookery_bakery_marks
                 else:
                    raise ValidationError("MEK Oral Or Practical Not Confirmed")
                
             if not (len(self.ccmc_online)==0):
                 if ccmc_online_state:
                    cookery_gsk_online = self.ccmc_online.scoring_total
                    self.cookery_gsk_online = cookery_gsk_online
                 else:
                    raise ValidationError("CCMC Online Not Confirmed")
            
             self.overall_marks = self.cookery_practical + self.cookery_oral + self.cookery_gsk_online
            
             #Percentage Calculation
             
             self.cookery_bakery_percentage = (self.cookery_practical/100) * 100
             self.ccmc_oral_percentage = (self.cookery_oral/100) * 100
             self.cookery_gsk_online_percentage = (self.cookery_gsk_online/100) * 100
             self.overall_percentage = (self.overall_marks/300)*100
             
             
             if self.cookery_practical >= 60:
                    self.cookery_bakery_prac_status = 'passed'
             else:
                    self.cookery_bakery_prac_status = 'failed'
                    
             if self.cookery_oral >= 60:
                self.ccmc_oral_prac_status = 'passed'
             else:
                self.ccmc_oral_prac_status = 'failed'
                
                
             if self.cookery_gsk_online  >= 60:
                self.ccmc_online_status = 'passed'
             else:
                self.ccmc_online_status = 'failed'
                    
             all_passed = all(field == 'passed' for field in [self.ccmc_oral_prac_status,self.cookery_bakery_prac_status,self.ccmc_online_status, self.exam_criteria , self.stcw_criteria , self.ship_visit_criteria , self.attendance_criteria ])

             if all_passed:
                self.write({'certificate_criteria':'passed'})
             else:
                self.write({'certificate_criteria':'pending'})
             
             
             
             self.state = '2-done'
                
                     
        
        else:
        
            # import wdb; wdb.set_trace(); 
            if cookery_draft_confirm and ccmc_oral_state and ccmc_online_state:
                
                # All CCMC Marks
                cookery_bakery_marks = self.cookery_bakery.total_mrks
                ccmc_oral_marks = self.ccmc_oral.toal_ccmc_rating
                self.ccmc_oral_total = ccmc_oral_marks
                self.cookery_practical = cookery_bakery_marks
                cookery_gsk_online = self.ccmc_online.scoring_total
                self.cookery_gsk_online = cookery_gsk_online
                self.overall_marks = ccmc_oral_marks + cookery_bakery_marks + cookery_gsk_online
                
                
                
                #All Percentage
                self.cookery_bakery_percentage = (cookery_bakery_marks/100) * 100
                self.ccmc_oral_percentage = (ccmc_oral_marks/100) * 100
                self.cookery_gsk_online_percentage = (cookery_gsk_online/100) * 100
                self.overall_percentage = (self.overall_marks/300) * 100
                
                
                if self.cookery_practical >= 60:
                    self.cookery_bakery_prac_status = 'passed'
                else:
                    self.cookery_bakery_prac_status = 'failed'
                    
                if self.cookery_oral >= 60:
                    self.ccmc_oral_prac_status = 'passed'
                else:
                    self.ccmc_oral_prac_status = 'failed'
                
                
                if self.cookery_gsk_online  >= 60:
                    self.ccmc_online_status = 'passed'
                else:
                    self.ccmc_online_status = 'failed'
                    
                all_passed = all(field == 'passed' for field in [self.ccmc_oral_prac_status,self.cookery_bakery_prac_status,self.ccmc_online_status, self.exam_criteria , self.stcw_criteria , self.ship_visit_criteria , self.attendance_criteria ])

                if all_passed:
                    self.write({'certificate_criteria':'passed'})
                else:
                    self.write({'certificate_criteria':'pending'})
                    
                
                self.state = '2-done'
                
            else:
                raise ValidationError("Not All exam are Confirmed")
            # attempting_exam_list = fields.One2many("gp.exam.appear",'gp_exam_schedule_id',string="Attempting Exams Lists")
                # all_passed = all(field == 'passed' for field in [self.mek_oral_prac_status, self.gsk_oral_prac_status, self.gsk_online_status , self.mek_online_status , self.exam_criteria , self.stcw_criteria , self.ship_visit_criteria , self.attendance_criteria ])
            
        
    def send_certificate_email(self):

        # Replace 'bes.report_gp_certificate' with the correct XML ID of the report template
        report_template = self.env.ref('bes.report_ccmc_certificate')
        report_pdf = report_template.render_pdf([self.id])
        
        # Render the report as PDF
        # generated_report = report_template._render_qweb_pdf(self.id)
        # print(generated_report,"genraaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

        # Convert the report to PDF format
        # pdf_content = self.env['ir.actions.report'].convert(
        #         generated_report,
        #         'pdf',
        #         {'model': self._name, 'id': self.ids[0]}
        #     )
        # print(pdf_content,"pdfffffffffffffffffffffffffffffffffffffff")

        # Encode the PDF data
        data_record = base64.b64encode(report_pdf[0])
        

        # Create an attachment record
        ir_values = {
            'name': 'Certificate Report',
            'type': 'binary',
            'datas': data_record,
            'store_fname': 'Certificate_Report.pdf',
            'mimetype': 'application/pdf',
            'res_model': 'ccmc.exam.schedule',
        }

        print(ir_values,"valuessssssssssssssssssssssssssssssssssssssssssssssssssssssssssss")
        report_attachment = self.env['ir.attachment'].sudo().create(ir_values)
        
        # Get the email template
        email_template = self.env.ref('bes.ccmc_certificate_mail')
        
        # Prepare email values
        email_values = {
            'email_to': self.ccmc_candidate.email,  # Use the appropriate recipient's email address
            'email_from': self.env.user.email,
        }
        
        # Attach the PDF to the email template
        if email_template:
            email_template.attachment_ids = [(4, report_attachment.id)]
            
            # Send the email
            email_template.send_mail(self.id, email_values=email_values, force_send=True)
            
            # Remove the attachment from the email template
            email_template.attachment_ids = [(5, 0, 0)]
            
        # Certificate Logic
class CcmcCertificate(models.AbstractModel):
    _name = 'report.bes.course_certificate'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs1 = self.env['ccmc.exam.schedule'].sudo().browse(docids)

        #If causing error uncomment this line 
        # Check if all records meet the certificate criteria
        # if all(doc.certificate_criteria == 'passed' for doc in docs):
        if docs1.certificate_criteria == 'passed'  :
            return {
                'docids': docids,
                'doc_model': 'ccmc.exam.schedule',
                'data': data,
                'docs': docs1
            }
        else:
            raise ValidationError("Certificate criteria not met. Report cannot be generated.")
    
# class CandidateGPCertificate(models.AbstractModel):
#     _name = 'report.bes.report_general_certificate'
#     _description = 'GP Certificate'
    
    
        
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         docs1 = self.env['gp.exam.schedule'].sudo().browse(docids)
        
        
#         return {
#             'doc_ids': docids,
#             'doc_model': 'gp.exam.schedule',
#             'docs': docs1
#             }

    
        
        
        