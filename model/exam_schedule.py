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
    exam_center = fields.Many2one("exam.center","Exam Center",required=True)
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
   

    
    
    