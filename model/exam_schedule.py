from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import random

from datetime import datetime


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
    exam_online = fields.One2many("exam.type.online","exam_schedule_id",string="Exam Online")
    exam_oral_practical = fields.One2many("exam.type.oral.practical","exam_schedule_id",string="Exam Oral Practical")
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
    
    exam_schedule_id = fields.Many2one("bes.exam.schedule",string="Exam Schedule",required=True)
    partner_id = fields.Many2one("res.partner",string="Contacts")
    name = fields.Char("Name of Candidate",)
    indos_no = fields.Char("Indos No.")
    candidate_code = fields.Char("Candidate Code No.")
    roll_no = fields.Char("Roll No.")
    dob = fields.Date("DOB")
    street = fields.Char("Street")
    street2 = fields.Char("Street2")
    city = fields.Char("City")
    zip = fields.Char("Zip")
    state_id = fields.Many2one("res.country.state","State",domain=[('country_id.code','=','IN')])
    phone = fields.Char("Phone")
    mobile = fields.Char("Mobile")
    email = fields.Char("Email")
    
    mek_practical_id = fields.Many2one("practical.mek","Mek Practical")
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
    _rec_name = "examiners"
    exam_schedule_id = fields.Many2one("bes.exam.schedule",string="Exam Schedule ID")
    examiners = fields.Many2one('bes.examiner', string="Examiner")
    subject = fields.Many2one("course.master.subject","Subject")
    start_time_online = fields.Datetime("Start Time")
    end_time_online = fields.Datetime("End Time")
    candidate_count = fields.Integer(string="Candidate Count",compute="compute_candidate_count")
    candidates = fields.Many2many("exam.schedule.bes.candidate","exam_type_practical_oral_candidate_rel","exam_type_prac_oral_id","exam_candidate_id",string="Candidate")

    state = fields.Selection([
        ('1-draft', 'Draft'),
        ('2-confirm', 'Confirmed'),
        ('3-in_progress','In-Progress'),   
        ('4-done','Done'),
        ('5-completed','Completed')     
    ], string='State', default='1-draft')
    
    def open_oral_prac_candidate(self):
        
        candidates_id = self.candidates.ids
            
        return {
        'name': 'Exam Candidate',
        'domain': [('id', 'in', candidates_id)],
        'view_type': 'form',
        'res_model': 'exam.schedule.bes.candidate',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        'context': {
            'subject_id': self.subject.id
        }
        }       
        
        
    
    @api.onchange('exam_schedule_id')
    def onchange_exam_schedule_id(self):
        for rec in self:
            return {'domain':{'subject':[('id','in',rec.exam_schedule_id.course.subjects.ids)]}}
    
    
    def compute_candidate_count(self):
        for rec in self:
            count = len(rec.candidates)
            rec.candidate_count = count
    
    @api.onchange('exam_schedule_id')
    def onchange_exam_schedule_id(self):
        for rec in self:
            return {'domain':{'examiners':[('id','in',rec.exam_schedule_id.examiners.ids)]}}
   

    
    
class GPExam(models.Model):
    _name = "gp.exam.schedule"
    _rec_name = "exam_id"
    _description= 'Schedule'
    
    exam_id = fields.Char("Exam ID",required=True, copy=False, readonly=True,
                                default=lambda self: self.env['ir.sequence'].next_by_code('gp.exam.sequence'))
    
    certificate_id = fields.Char(string="Certificate ID")
    gp_candidate = fields.Many2one("gp.candidate","GP Candidate")
    mek_oral = fields.Many2one("gp.mek.oral.line","Mek Oral")
    mek_prac = fields.Many2one("gp.mek.practical.line","Mek Practical")
    gsk_oral = fields.Many2one("gp.gsk.oral.line","GSK Oral")
    gsk_prac = fields.Many2one("gp.gsk.practical.line","GSK Practical")
    gsk_online = fields.Many2one("survey.user_input","GSK Online")
    mek_online = fields.Many2one("survey.user_input","MEK Online")
    attempt_number = fields.Integer("Attempt Number", default=1, copy=False,readonly=True)
    
    gsk_total = fields.Float("GSK Total",readonly=True)
    gsk_percentage = fields.Float("GSK Precentage",readonly=True)
   
    
    
    mek_total = fields.Float("Mek Total",readonly=True)
    mek_percentage = fields.Float("Mek Percentage",readonly=True)
    gsk_oral_prac_status = fields.Selection([
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='GSK Oral/Practical Status')
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
    
    exam_criteria = fields.Selection([
        ('', ''),
        ('pending', 'Pending'),
        ('passed', 'Passed'),
    ], string='Exam Criteria' , compute="compute_certificate_criteria")
    
    certificate_criteria = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Passed'),
    ], string='Certificate Criteria')

    
    stcw_criteria = fields.Selection([
        ('', ''),
        ('pending', 'Pending'),
        ('passed', 'Passed'),
    ], string='STCW Criteria' , compute="compute_certificate_criteria")
    
    ship_visit_criteria = fields.Selection([
        ('', ''),
        ('pending', 'Pending'),
        ('passed', 'Passed'),
    ], string='Ship Visit Criteria' , compute="compute_certificate_criteria")
    
    
    attendance_criteria = fields.Selection([
        ('', ''),
        ('pending', 'Pending'),
        ('passed', 'Passed'),
    ], string='Attendance Criteria' , compute="compute_certificate_criteria")

    
    state = fields.Selection([
        ('1-in_process', 'In Process'),
        ('2-done', 'Done'),
    ], string='State', default='1-in_process')
    
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
        
    # def move_done(self):
    #         if(self.certificate_criteria == 'passed'):
    #             self.certificate_id = self.env['ir.sequence'].next_by_code("gp.exam.schedule")
    #         self.state = '2-done'
            
            
    
    
    @api.model
    def create(self, vals):
        if vals.get('gp_candidate'):
            candidate_id = vals['gp_candidate']
            last_attempt = self.search([('gp_candidate', '=', candidate_id)], order='attempt_number desc', limit=1)
            vals['attempt_number'] = last_attempt.attempt_number + 1 if last_attempt else 1

        return super(GPExam, self).create(vals)
    
    
    
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
        
        
        if mek_oral_draft_confirm and mek_practical_draft_confirm and gsk_oral_draft_confirm and gsk_practical_draft_confirm and gsk_online_done and mek_online_done:
        
            mek_oral_marks = self.mek_oral.mek_oral_total_marks
            mek_practical_marks = self.mek_prac.mek_practical_total_marks
            mek_total_marks = mek_oral_marks + mek_practical_marks
            self.mek_total = mek_total_marks
            self.mek_percentage = (mek_total_marks/175) * 100
            
            
            if self.mek_percentage >= 60:
                self.mek_oral_prac_status = 'passed'
            else:
                self.mek_oral_prac_status = 'failed'


            gsk_oral_marks = self.gsk_oral.gsk_oral_total_marks
            gsk_practical_marks = self.gsk_prac.gsk_practical_total_marks
            gsk_total_marks = gsk_oral_marks + gsk_practical_marks
            self.gsk_total = gsk_total_marks
            self.gsk_percentage = (gsk_total_marks/175) * 100
            
            
            if self.gsk_percentage >= 60:
                self.gsk_oral_prac_status = 'passed'
            else:
                self.gsk_oral_prac_status = 'failed'

            
            self.state = '2-done'
            
            
            if self.gsk_online.scoring_success:
                self.gsk_online_status = 'passed'
            else:
                self.gsk_online_status = 'failed'
                
            
            if self.mek_online.scoring_success:
                self.mek_online_status = 'passed'
            else:
                self.mek_online_status = 'failed'
            
            all_passed = all(field == 'passed' for field in [self.mek_oral_prac_status, self.gsk_oral_prac_status, self.gsk_online_status , self.mek_online_status , self.exam_criteria , self.stcw_criteria , self.ship_visit_criteria , self.attendance_criteria ])

            # import wdb; wdb.set_trace();
            if all_passed:
                
                self.write({'certificate_criteria':'passed'})
                # self.certificate_criteria = 'passed'
            else:
                self.write({'certificate_criteria':'pending'})

                # self.certificate_criteria = 'failed'
            
            if(self.certificate_criteria == 'passed'):
                self.certificate_id = self.env['ir.sequence'].next_by_code("gp.exam.schedule")
            
            self.state = '2-done'
                
                
        
        else:
             raise ValidationError("Not All exam are Confirmed")


class CCMCExam(models.Model):
    _name = "ccmc.exam.schedule"
    _rec_name = "exam_id"
    _description= 'Schedule'
    
    certificate_id = fields.Char(string="Certificate ID")
    exam_id = fields.Char("Exam ID",required=True, copy=False, readonly=True,
                                default=lambda self: self.env['ir.sequence'].next_by_code('ccmc.exam.sequence'))
    
    ccmc_candidate = fields.Many2one("ccmc.candidate","CCMC Candidate")
    cookery_bakery = fields.Many2one("ccmc.cookery.bakery.line","Cookery And Bakery")
    ccmc_oral = fields.Many2one("ccmc.oral.line","CCMC Oral")
    ccmc_online = fields.Many2one("survey.user_input",string="CCMC Online")

    attempt_number = fields.Integer("Attempt Number", default=1, copy=False,readonly=True)
    
    cookery_bakery_total = fields.Float("Cookery And Bakery / CCMC Oral Total",readonly=True)
    cookery_bakery_percentage = fields.Float("Cookery And Bakery Precentage",readonly=True)
    cookery_bakery_prac_status = fields.Selection([
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='Cookery And Bakery / Oral Status')
    
    
    ccmc_oral_total = fields.Float("CCMC Oral Total",readonly=True)
    ccmc_oral_percentage = fields.Float("CCMC Oral Percentage",readonly=True)
    ccmc_oral_prac_status = fields.Selection([
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='CCMC Oral Status')
    
    
    
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
    ], string='State', default='1-in_process')
    
    certificate_criteria = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Passed'),
    ], string='Certificate Criteria')
    
    # @api.depends('cookery_bakery_prac_status','ccmc_oral_prac_status','')
    # def compute_certificate_criteria(self):
    
    @api.depends('stcw_criteria','ship_visit_criteria','cookery_bakery_prac_status','ccmc_online_status')
    def compute_certificate_criteria(self):
        for record in self:
            # all_passed = all(field == 'passed' for field in [record.gsk_online_status, record.mek_online_status, record.mek_oral_prac_status , record.gsk_oral_prac_status])
            all_passed = all(field == 'passed' for field in [record.cookery_bakery_prac_status , record.ccmc_online_status])
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
                
                
            

    
    @api.model
    def create(self, vals):
        if vals.get('ccmc_candidate'):
            candidate_id = vals['ccmc_candidate']
            last_attempt = self.search([('ccmc_candidate', '=', candidate_id)], order='attempt_number desc', limit=1)
            vals['attempt_number'] = last_attempt.attempt_number + 1 if last_attempt else 1

        return super(CCMCExam, self).create(vals)
    

    def move_done(self):
        
        cookery_draft_confirm = self.cookery_bakery.cookery_draft_confirm == 'confirm'
        ccmc_oral = self.ccmc_oral.ccmc_oral_draft_confirm == 'confirm'
        ccmc_online = self.ccmc_online.state == 'done'
        
        # import wdb; wdb.set_trace(); 
        if cookery_draft_confirm and ccmc_oral and ccmc_online:
            cookery_bakery_marks = self.cookery_bakery.total_mrks
            ccmc_oral_marks = self.ccmc_oral.toal_ccmc_rating
            ccmc_total_marks = cookery_bakery_marks + ccmc_oral_marks
            self.cookery_bakery_total = ccmc_total_marks
            self.cookery_bakery_percentage = (ccmc_total_marks/120) * 100
            
            
            if self.cookery_bakery_percentage >= 60:
                self.cookery_bakery_prac_status = 'passed'
            else:
                self.cookery_bakery_prac_status = 'failed'
            
            
            if self.ccmc_online.scoring_success:
                self.ccmc_online_status = 'passed'
            else:
                self.ccmc_online_status = 'failed'
                
            all_passed = all(field == 'passed' for field in [self.cookery_bakery_prac_status,self.ccmc_online_status, self.exam_criteria , self.stcw_criteria , self.ship_visit_criteria , self.attendance_criteria ])

            if all_passed:
                self.write({'certificate_criteria':'passed'})
            else:
                self.write({'certificate_criteria':'pending'})
                
            
            
            if(self.certificate_criteria == 'passed'):
                self.certificate_id = self.env['ir.sequence'].next_by_code("ccmc.exam.schedule")
            self.state = '2-done'
            # all_passed = all(field == 'passed' for field in [self.mek_oral_prac_status, self.gsk_oral_prac_status, self.gsk_online_status , self.mek_online_status , self.exam_criteria , self.stcw_criteria , self.ship_visit_criteria , self.attendance_criteria ])

                
            
            
        else:
            raise ValidationError("Not All exam are Confirmed")

            
        
        
            
    
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

    
        
        
        