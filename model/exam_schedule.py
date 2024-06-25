
from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
import random
import logging
import qrcode
import io
import base64
from datetime import datetime , date
import math
from odoo.http import content_disposition, request , Response
from odoo.tools import date_utils
import xlsxwriter




class BesBatches(models.Model):
    _name = "bes.exam.schedule"
    _rec_name = "schedule_name"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'Schedule'
    schedule_name = fields.Char("Schedule Name",required=True,tracking=True)
    exam_date = fields.Datetime("Exam Date",required=True,tracking=True)
    course = fields.Many2one("course.master",string="Course",required=True,tracking=True)
    state = fields.Selection([
        ('1-draft', 'Draft'),
        ('2-confirm', 'Confirmed'),
        ('3-examiner_assigned', 'Examiner Assigned'),     
        ('4-exam_planned', 'Exam Planned')        
    ], string='State', default='1-draft',tracking=True)
    exam_center = fields.Many2one("exam.center","Exam Region",required=True,tracking=True)
    examiners = fields.Many2many('bes.examiner', string="Examiners",tracking=True)
    # exam_online = fields.One2many("exam.type.online","exam_schedule_id",string="Exam Online")
    # exam_oral_practical = fields.One2many("exam.type.oral.practical","exam_schedule_id",string="Exam Oral Practical")
    candidate_count = fields.Integer(string="Candidate Count", compute="compute_candidate_count",tracking=True)
    
    


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
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Exam Candidate'
    
    # exam_schedule_id = fields.Many2one("bes.exam.schedule",string="Exam Schedule",required=True)
    partner_id = fields.Many2one("res.partner",string="Contacts",tracking=True)
    name = fields.Char("Name of Candidate",tracking=True)
    indos_no = fields.Char("Indos No.",tracking=True)
    candidate_code = fields.Char("Candidate Code No.",tracking=True)
    roll_no = fields.Char("Roll No.",tracking=True)
    dob = fields.Date("DOB",help="Date of Birth", 
                      widget="date", 
                      date_format="%d-%b-%y",tracking=True)
    street = fields.Char("Street",tracking=True)
    street2 = fields.Char("Street2",tracking=True)
    city = fields.Char("City",tracking=True)
    zip = fields.Char("Zip",tracking=True)
    state_id = fields.Many2one("res.country.state","State",domain=[('country_id.code','=','IN')],tracking=True)
    phone = fields.Char("Phone",tracking=True)
    mobile = fields.Char("Mobile",tracking=True)
    email = fields.Char("Email",tracking=True)
    
    mek_practical_id = fields.Many2one("practical.mek","MEK Practical",tracking=True)
    mek_oral_id = fields.Many2one("oral.mek","MEK Oral Practical",tracking=True)
    gsk_practical_id = fields.Many2one("practical.gsk","GSK Practical",tracking=True)
    gsk_oral_id = fields.Many2one("oral.gsk","GSK Oral",tracking=True)
    
    
    mek_visiblity = fields.Boolean("MEK Visiblity",compute="compute_mek_gsk_visiblity",tracking=True)
    gsk_visiblity = fields.Boolean("GSK Visiblity",compute="compute_mek_gsk_visiblity",tracking=True)
    
    
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
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Assign Examiner'
    
    course = fields.Many2one("course.master",string="Course",tracking=True)
    state_id = fields.Many2one("res.country.state","State",domain=[('country_id.code','=','IN')],tracking=True)
    examiners = fields.Many2many('bes.examiner', string="Examiners",tracking=True)
    candidate_count = fields.Integer(string="Candidate Count",tracking=True)
    
    
    def assign_examiner(self):
        schedule_id = self.env.context.get('schedule_id')
        exam_schedule = self.env["bes.exam.schedule"].search([('id','=',schedule_id)])
        exam_schedule.write({'examiners':self.examiners,'state':'3-examiner_assigned'})

class ExamOnline(models.Model):
    _name = 'exam.type.online'
    _rec_name = "examiners"
    _inherit = ['mail.thread','mail.activity.mixin']
    exam_schedule_id = fields.Many2one("bes.exam.schedule",string="Exam Schedule ID",tracking=True)
    examiners = fields.Many2one('bes.examiner', string="Examiner",tracking=True)
    subject = fields.Many2one("course.master.subject","Subject",tracking=True)
    start_time_online = fields.Datetime("Start Time",tracking=True)
    end_time_online = fields.Datetime("End Time",tracking=True)
    candidate_count = fields.Integer(string="Candidate Count",compute="compute_candidate_count",tracking=True)
    candidates = fields.Many2many("exam.schedule.bes.candidate","exam_type_online_candidate_rel","exam_type_online_id","exam_candidate_id",string="Candidate",tracking=True)
    
    @api.onchange('exam_schedule_id')
    def onchange_exam_schedule_id(self):
        for rec in self:
            return {'domain':{'examiners':[('id','in',rec.exam_schedule_id.examiners.ids)],'subject':[('id','in',rec.exam_schedule_id.course.subjects.ids)]}}

    def compute_candidate_count(self):
        for rec in self:
            count = len(rec.candidates)
            rec.candidate_count = count

class CCMCExaminerAssignmentWizard(models.TransientModel):
    _name = 'ccmc.examiner.assignment.wizard'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Examiner Assignment Wizard'
    
    exam_duty = fields.Many2one("exam.type.oral.practical",string="Exam Duty",tracking=True)
    institute_id = fields.Many2one("bes.institute",string="Institute",tracking=True)
    course = fields.Many2one("course.master",related='exam_duty.course',string="Course",tracking=True)
    exam_region = fields.Many2one('exam.center', 'Exam Region',tracking=True)
    
    ccmc_prac_oral_candidates = fields.Integer('No. of Candidates In CCMC Oral/Practical', compute="_compute_ccmc_prac_oral_candidates",tracking=True)
    ccmc_gsk_oral_candidates = fields.Integer('No. of Candidates In CCMC GSK Oral', compute="_compute_ccmc_gsk_oral_candidates",tracking=True)
    ccmc_online_candidates = fields.Integer('No. of Candidates In CCMC GSK Online', compute="_compute_ccmc_online_candidates",tracking=True)
    
    
    no_of_days =  fields.Integer('No. of Days For Exam ',tracking=True)
    examiner_required_ccmc_prac_oral = fields.Integer("Examiner Required For CCMC Prac/Oral Per Day",compute="_compute_examiners_ccmc_prac_oral",tracking=True)
    examiner_required_ccmc_gsk_oral = fields.Integer("Examiner Required For CCMC GSK Oral Per Day",compute="_compute_examiners_ccmc_gsk_prac_oral",tracking=True)
    
    examiner_lines_ids = fields.One2many('ccmc.examiner.assignment.wizard.line', 'parent_id', string='Examiners',tracking=True)
    
    
    def update_marksheet(self):
            records = self.examiner_lines_ids
            
            candidate_with_ccmc_oral_prac = self.env['ccmc.exam.schedule'].sudo().search([('dgs_batch','=',self.exam_duty.dgs_batch.id),('registered_institute','=',self.institute_id.id),('state','=','1-in_process'),('oral_prac_status','in',('pending','failed')),('ccmc_oral_prac_assignment','=',False)]).ids
            candidate_with_ccmc_gsk_oral = self.env['ccmc.exam.schedule'].sudo().search([('dgs_batch','=',self.exam_duty.dgs_batch.id),('registered_institute','=',self.institute_id.id),('state','=','1-in_process'),('oral_prac_status','in',('pending','failed')),('ccmc_gsk_oral_assignment','=',False)]).ids


            candidate_with_ccmc_online = self.env['ccmc.exam.schedule'].sudo().search([('dgs_batch','=',self.exam_duty.dgs_batch.id),('registered_institute','=',self.institute_id.id),('state','=','1-in_process'),('ccmc_online_status','in',('pending','failed')),('ccmc_online_assignment','=',False)]).ids

        
            examiners_ccmc_prac_oral = records.filtered(lambda r: r.subject.name == 'CCMC' and r.exam_type == 'practical_oral').ids
            ccmc_prac_oral_assignments = {examiner: [] for examiner in examiners_ccmc_prac_oral}
            num_examiners_ccmc_prac_oral = len(examiners_ccmc_prac_oral)
            
            
            examiners_ccmc_gsk_oral = records.filtered(lambda r: r.subject.name == 'CCMC GSK Oral' and r.exam_type == 'practical_oral').ids
            ccmc_gsk_oral_assignments = {examiner: [] for examiner in examiners_ccmc_gsk_oral}
            num_examiners_ccmc_gsk_oral = len(examiners_ccmc_gsk_oral)
            
            
            examiners_ccmc_online = records.filtered(lambda r: r.subject.name == 'CCMC' and r.exam_type == 'online').ids
            ccmc_online_assignments = {examiner: [] for examiner in examiners_ccmc_online}
            num_examiners_ccmc_online = len(examiners_ccmc_online)
            
            
            #Distribute candidates with both CCMC Oral Prac
            for idx, candidate in enumerate(candidate_with_ccmc_oral_prac):
                try:
                    ccmc_prac_oral_examiner_index = idx % num_examiners_ccmc_prac_oral
                    examiner_ccmc_prac_oral = examiners_ccmc_prac_oral[ccmc_prac_oral_examiner_index]
                    ccmc_prac_oral_assignments[examiner_ccmc_prac_oral].append(candidate)
                except ZeroDivisionError:
                    if self.exam_duty.dgs_batch.repeater_batch:
                        pass
                    else:
                        raise ValidationError("Please Add Atleast One CCMC Prac/Oral Examiner")
            
            
            #Distribute candidates with both CCMC GSK Oral
            for idx, candidate in enumerate(candidate_with_ccmc_gsk_oral):
                try:
                    ccmc_gsk_oral_examiner_index = idx % num_examiners_ccmc_gsk_oral
                    examiner_ccmc_gsk_oral = examiners_ccmc_gsk_oral[ccmc_gsk_oral_examiner_index]
                    ccmc_gsk_oral_assignments[examiner_ccmc_gsk_oral].append(candidate)
                except ZeroDivisionError:
                    if self.exam_duty.dgs_batch.repeater_batch:
                        pass
                    else:
                        raise ValidationError("Please Add Atleast One CCMC GSK Oral Examiner")
            
            
            #Distribute candidates with both CCMC Online
            for idx, candidate in enumerate(candidate_with_ccmc_online):
                try:
                    ccmc_online_examiner_index = idx % num_examiners_ccmc_online
                    examiner_ccmc_online = examiners_ccmc_online[ccmc_online_examiner_index]
                    ccmc_online_assignments[examiner_ccmc_online].append(candidate)
                except ZeroDivisionError:
                    if self.exam_duty.dgs_batch.repeater_batch:
                        pass
                    else:
                        raise ValidationError("Please Add Atleast One CCMC Online Examiner")
                

            
            ### CCMC Oral Prac ASSIGNMENTS    
            for examiner, assigned_candidates in ccmc_prac_oral_assignments.items():
                examiner_id = examiner
                assignment = records.filtered(lambda r: r.id == examiner_id)
                assignment.ccmc_marksheet_ids = assigned_candidates
                
                
            ### CCMC GSK Oral ASSIGNMENTS    
            for examiner, assigned_candidates in ccmc_gsk_oral_assignments.items():
                examiner_id = examiner
                assignment = records.filtered(lambda r: r.id == examiner_id)
                assignment.ccmc_marksheet_ids = assigned_candidates
            
            ### CCMC Online ASSIGNMENTS    
            for examiner, assigned_candidates in ccmc_online_assignments.items():
                examiner_id = examiner
                assignment = records.filtered(lambda r: r.id == examiner_id)
                assignment.ccmc_marksheet_ids = assigned_candidates
            
            
            return {
                        'context': self.env.context,
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'ccmc.examiner.assignment.wizard',
                        'res_id': self.id,
                        'view_id': False,
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                    }
                
                
    def confirm(self):
        
        records = self.examiner_lines_ids
        
        for record in records:
            if record.subject.name == 'CCMC':
                if record.exam_type == 'practical_oral':
                    
                    if record.no_candidates > 25:
                        raise ValidationError("Number of candidates cannot exceed 25 for this assignment.")
                    elif record.no_candidates == 0:
                        raise ValidationError("Please Assigned Candidate By Clicking On Update Button")

                    prac_oral_id = self.exam_duty.id
                    institute_id = self.institute_id.id
                    subject = record.subject.id
                    examiner = record.examiner.id
                    exam_date = record.exam_date
                    exam_type = record.exam_type
                    
                    assignment = self.env["exam.type.oral.practical.examiners"].create({
                                                                                        'prac_oral_id':prac_oral_id,
                                                                                        'institute_id':institute_id,
                                                                                        'subject':subject,
                                                                                        'examiner':examiner,
                                                                                        'exam_date':exam_date,
                                                                                        'exam_type':exam_type      
                                                                                        })
                    
                    for marksheet in record.ccmc_marksheet_ids:
                        # import wdb;wdb.set_trace()
                        marksheet.write({ 'ccmc_oral_prac_assignment': True })
                        ccmc_marksheet = marksheet
                        cookery_bakery = marksheet.cookery_bakery
                        ccmc_oral = marksheet.ccmc_oral
                        candidate = marksheet.ccmc_candidate.id
                        self.env['exam.type.oral.practical.examiners.marksheet'].sudo().create({ 'examiners_id':assignment.id ,
                                                                                                    'ccmc_marksheet':ccmc_marksheet.id ,
                                                                                                    'ccmc_candidate':candidate , 
                                                                                                    'cookery_bakery':cookery_bakery.id , 
                                                                                                    'ccmc_oral':ccmc_oral.id 
                                                                                                    })
            
            
                if record.exam_type == 'online':
                    prac_oral_id = self.exam_duty.id
                    institute_id = self.institute_id.id
                    subject = record.subject.id
                    examiner = record.examiner.id
                    exam_date = record.exam_date
                    exam_type = record.exam_type
                    
                    assignment = self.env["exam.type.oral.practical.examiners"].create({
                                                                                        'prac_oral_id':prac_oral_id,
                                                                                        'institute_id':institute_id,
                                                                                        'subject':subject,
                                                                                        'examiner':examiner,
                                                                                        'exam_date':exam_date,
                                                                                        'exam_type':exam_type      
                                                                                        })
                    
                    
                    for marksheet in record.ccmc_marksheet_ids:
                        marksheet.write({'ccmc_online_assignment':True})
                        ccmc_marksheet = marksheet
                        candidate = marksheet.ccmc_candidate.id
                        ccmc_online = marksheet.ccmc_online
                        
                        self.env['exam.type.oral.practical.examiners.marksheet'].sudo().create({ 'examiners_id':assignment.id ,
                                                                                                    'ccmc_marksheet':ccmc_marksheet.id ,
                                                                                                    'ccmc_candidate':candidate , 
                                                                                                    'ccmc_online': ccmc_online.id
                                                                                                    })    

            if record.subject.name == 'CCMC GSK Oral':
                if record.no_candidates > 40:
                        raise ValidationError("Number of candidates cannot exceed 40 for this assignment.")
                elif record.no_candidates == 0:
                        raise ValidationError("Please Assigned Candidate By Clicking On Update Button")
                
                prac_oral_id = self.exam_duty.id
                institute_id = self.institute_id.id
                subject = record.subject.id
                examiner = record.examiner.id
                exam_date = record.exam_date
                exam_type = record.exam_type
                
                assignment = self.env["exam.type.oral.practical.examiners"].create({
                                                                                        'prac_oral_id':prac_oral_id,
                                                                                        'institute_id':institute_id,
                                                                                        'subject':subject,
                                                                                        'examiner':examiner,
                                                                                        'exam_date':exam_date,
                                                                                        'exam_type':exam_type      
                                                                                        })
                    
                for marksheet in record.ccmc_marksheet_ids:
                        marksheet.write({'ccmc_gsk_oral_assignment':True})
                        ccmc_marksheet = marksheet
                        candidate = marksheet.ccmc_candidate.id
                        ccmc_gsk_oral = marksheet.ccmc_gsk_oral
                        
                        self.env['exam.type.oral.practical.examiners.marksheet'].sudo().create({ 'examiners_id':assignment.id ,
                                                                                                    'ccmc_marksheet':ccmc_marksheet.id ,
                                                                                                    'ccmc_candidate':candidate , 
                                                                                                    'ccmc_gsk_oral': ccmc_gsk_oral.id
                                                                                                    }) 

    
    def calculate_examiners(self,num_candidates, max_candidates_per_examiner, num_days):
        candidates_per_day = math.ceil(num_candidates / num_days)
        return math.ceil(candidates_per_day / max_candidates_per_examiner)
    
    @api.depends('no_of_days')
    def _compute_examiners_ccmc_prac_oral(self):
        for record in self:
            try:
                max_candidates_per_examiner = 25            
                total_candidates = record.ccmc_prac_oral_candidates
                num_days = record.no_of_days
                record.examiner_required_ccmc_prac_oral = self.calculate_examiners(total_candidates, max_candidates_per_examiner, num_days)
            except ZeroDivisionError:
                record.examiner_required_ccmc_prac_oral = 0
                
    @api.depends('no_of_days')
    def _compute_examiners_ccmc_gsk_prac_oral(self):
        for record in self:
            try:
                max_candidates_per_examiner = 25            
                total_candidates = record.ccmc_gsk_oral_candidates
                num_days = record.no_of_days
                record.examiner_required_ccmc_gsk_oral = self.calculate_examiners(total_candidates, max_candidates_per_examiner, num_days)
            except ZeroDivisionError:
                record.examiner_required_ccmc_gsk_oral = 0
    
    @api.depends('institute_id')
    def _compute_ccmc_prac_oral_candidates(self):
        for record in self:
            # import wdb;wdb.set_trace() ('mek_oral_prac_assignment','=',False),('gsk_oral_prac_assignment','=',False)
            # import wdb;wdb.set_trace() 
            record.ccmc_prac_oral_candidates = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',record.exam_duty.dgs_batch.id),('registered_institute','=',record.institute_id.id),('state','=','1-in_process'),('oral_prac_status','in',('pending','failed')),('ccmc_oral_prac_assignment','=',False)])
            
    
    @api.depends('institute_id')
    def _compute_ccmc_gsk_oral_candidates(self):
        for record in self:
            # import wdb;wdb.set_trace() ('mek_oral_prac_assignment','=',False),('gsk_oral_prac_assignment','=',False)
            record.ccmc_gsk_oral_candidates = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',record.exam_duty.dgs_batch.id),('registered_institute','=',record.institute_id.id),('state','=','1-in_process'),('oral_prac_status','in',('pending','failed')),('ccmc_gsk_oral_assignment','=',False)])
    
    @api.depends('institute_id')
    def _compute_ccmc_online_candidates(self):
        for record in self:
            # import wdb;wdb.set_trace() ('mek_oral_prac_assignment','=',False),('gsk_oral_prac_assignment','=',False)
            record.ccmc_online_candidates = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',record.exam_duty.dgs_batch.id),('registered_institute','=',record.institute_id.id),('state','=','1-in_process'),('ccmc_online_status','in',('pending','failed')),('ccmc_online_assignment','=',False)])


class CCMCExaminerAssignmentLineWizard(models.TransientModel):
    _name = 'ccmc.examiner.assignment.wizard.line'
    _inherit = ['mail.thread','mail.activity.mixin']
    
    parent_id = fields.Many2one("ccmc.examiner.assignment.wizard",string="Parent",tracking=True)
    exam_date = fields.Date('Exam Date',tracking=True)
    subject = fields.Many2one("course.master.subject",string="Subject",tracking=True)
    examiner = fields.Many2one('bes.examiner', string="Examiner",tracking=True)
    ccmc_marksheet_ids = fields.Many2many('ccmc.exam.schedule', string='Candidates',tracking=True)
    exam_type = fields.Selection([
        ('practical_oral', 'Practical/Oral'),
        ('online', 'Online')     
    ], string='Exam Type', default='practical_oral',tracking=True)
    
    # no_candidates = fields.Integer('No. Of Candidates')
    no_candidates = fields.Integer('No. Of Candidates',compute='_compute_candidate_no',tracking=True)
    
    
    @api.depends('ccmc_marksheet_ids')
    def _compute_candidate_no(self):
        for record in self:
            record.no_candidates = len(record.ccmc_marksheet_ids)    


class GPExaminerAssignmentWizard(models.TransientModel):
    _name = 'examiner.assignment.wizard'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Examiner Assignment Wizard'
    exam_duty = fields.Many2one("exam.type.oral.practical",string="Exam Duty",tracking=True)
    institute_id = fields.Many2one("bes.institute",string="Institute",tracking=True)
    course = fields.Many2one("course.master",related='exam_duty.course',string="Course",tracking=True)

    
    #GP Course
    gsk_prac_oral_candidates = fields.Integer('No. of Candidates In GSK Oral/Practical', compute="_compute_gsk_prac_oral_candidates",tracking=True)
    mek_prac_oral_candidates = fields.Integer('No. of Candidates In MEK Oral/Practical', compute="_compute_mek_prac_oral_candidates",tracking=True)
    gsk_online_candidates = fields.Integer('No. of Candidates In GSK Online',compute="_compute_gsk_online_candidates",tracking=True)
    mek_online_candidates = fields.Integer('No. of Candidates In MEK Online',compute="_compute_mek_online_candidates",tracking=True)
    no_of_days =  fields.Integer('No. of Days For Exam ',tracking=True)
    examiner_required_mek = fields.Integer("Examiner Required For MEK Prac/Oral Per Day",compute="_compute_examiners_mek",tracking=True)
    examiner_required_gsk = fields.Integer("Examiner Required For GSK Prac/Oral Per Day",compute="_compute_examiners_gsk",tracking=True)

    
    
    
    
    def update_marksheet(self):
        
        records = self.examiner_lines_ids
        unique_exam_dates = list(set(record.exam_date for record in records))
        
        candidate_with_gsk_mek = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',self.exam_duty.dgs_batch.id),('registered_institute','=',self.institute_id.id),('state','=','1-in_process'),('gsk_oral_prac_status','in',('pending','failed')),('mek_oral_prac_status','in',('pending','failed')),('mek_oral_prac_assignment','=',False),('gsk_oral_prac_assignment','=',False),('stcw_criterias','=','passed')]).ids
        candidate_with_gsk  = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',self.exam_duty.dgs_batch.id),('registered_institute','=',self.institute_id.id),('state','=','1-in_process'),('gsk_oral_prac_status','in',('pending','failed')),('mek_oral_prac_status','=','passed'),('gsk_oral_prac_assignment','=',False),('stcw_criterias','=','passed')]).ids
        candidate_with_mek = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',self.exam_duty.dgs_batch.id),('registered_institute','=',self.institute_id.id),('state','=','1-in_process'),('gsk_oral_prac_status','=','passed'),('mek_oral_prac_status','in',('pending','failed')),('mek_oral_prac_assignment','=',False),('stcw_criterias','=','passed')]).ids
        
        print(candidate_with_mek)
        
        candidate_with_gsk_mek_online = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',self.exam_duty.dgs_batch.id),('registered_institute','=',self.institute_id.id),('state','=','1-in_process'),('gsk_online_status','in',('pending','failed')),('mek_online_status','in',('pending','failed')),('mek_online_assignment','=',False),('gsk_online_assignment','=',False),('stcw_criterias','=','passed')]).ids
        candidate_with_gsk_online  = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',self.exam_duty.dgs_batch.id),('registered_institute','=',self.institute_id.id),('state','=','1-in_process'),('gsk_online_status','in',('pending','failed')),('mek_online_status','=','passed'),('gsk_online_assignment','=',False),('stcw_criterias','=','passed')]).ids
        candidate_with_mek_online = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',self.exam_duty.dgs_batch.id),('registered_institute','=',self.institute_id.id),('state','=','1-in_process'),('gsk_online_status','=','passed'),('mek_online_status','in',('pending','failed')),('mek_online_assignment','=',False),('stcw_criterias','=','passed')]).ids


        examiners_gsk = records.filtered(lambda r: r.subject.name == 'GSK' and r.exam_type == 'practical_oral').ids
        gsk_assignments = {examiner: [] for examiner in examiners_gsk}
        num_examiners_gsk = len(examiners_gsk)
        
        
        examiners_gsk_online = records.filtered(lambda r: r.subject.name == 'GSK' and r.exam_type == 'online').ids
        online_gsk_assignments = {examiner: [] for examiner in examiners_gsk_online}
        num_examiners_gsk_online = len(examiners_gsk_online)
        
        
        examiners_mek = records.filtered(lambda r: r.subject.name == 'MEK' and r.exam_type == 'practical_oral').ids
        mek_assignments = {examiner: [] for examiner in examiners_mek}
        num_examiners_mek = len(examiners_mek)
        

        examiners_mek_online = records.filtered(lambda r: r.subject.name == 'MEK' and r.exam_type == 'online').ids
        online_mek_assignments = {examiner: [] for examiner in examiners_mek_online}
        num_examiners_mek_online = len(examiners_mek_online)
        
        

        
        
        #Distribute candidates with both GSK and MEK     
        for idx, candidate in enumerate(candidate_with_gsk_mek):
            try:
                gsk_examiner_index = idx % num_examiners_gsk
                examiner_gsk = examiners_gsk[gsk_examiner_index]
                gsk_assignments[examiner_gsk].append(candidate)
            except ZeroDivisionError:
                if self.exam_duty.dgs_batch.repeater_batch:
                    pass
                else:
                    raise ValidationError("Please Add Atleast One GSK Examiner")
            
            try:    
                mek_examiner_index = idx % num_examiners_mek
                examiner_mek = examiners_mek[mek_examiner_index]          
                mek_assignments[examiner_mek].append(candidate)
            except ZeroDivisionError:
                if self.exam_duty.dgs_batch.repeater_batch:
                    pass
                else:
                    raise ValidationError("Please Add Atleast One MEK Examiner")
        
        # import wdb;wdb.set_trace();

        #Distribute candidates with both GSK and MEK Online     
        for idx, candidate in enumerate(candidate_with_gsk_mek_online):
            try:
                
                online_gsk_examiner_index = idx % num_examiners_gsk_online
                examiner_gsk_online = examiners_gsk_online[online_gsk_examiner_index]
                online_gsk_assignments[examiner_gsk_online].append(candidate)
            except ZeroDivisionError:
                if self.exam_duty.dgs_batch.repeater_batch:
                    pass
                else:
                    raise ValidationError("Please Add Atleast One GSK Online Examiner")
                
            
            try:    
                online_mek_examiner_index = idx % num_examiners_mek_online
                examiner_mek_online = examiners_mek_online[online_mek_examiner_index]          
                online_mek_assignments[examiner_mek_online].append(candidate)
            except ZeroDivisionError:
                if self.exam_duty.dgs_batch.repeater_batch:
                    pass
                else:
                    raise ValidationError("Please Add Atleast One MEK Online Examiner")
            
        # import wdb;wdb.set_trace();
        
        
        
            
        # Distribute candidates with only GSK
        for idx, candidate in enumerate(candidate_with_gsk):
            try:
                gsk_examiner_index = idx % num_examiners_gsk
                examiner_gsk = examiners_gsk[gsk_examiner_index]
                gsk_assignments[examiner_gsk].append(candidate)
            except ZeroDivisionError:
                if self.exam_duty.dgs_batch.repeater_batch:
                    pass
                else:
                    raise ValidationError("Please Add Atleast One GSK Examiner")
            
         # Distribute candidates with only GSK Online
        for idx, candidate in enumerate(candidate_with_gsk_online):
            try:
                
                online_gsk_examiner_index = idx % num_examiners_gsk_online
                examiner_gsk_online = examiners_gsk_online[online_gsk_examiner_index]
                online_gsk_assignments[examiner_gsk_online].append(candidate)
            except ZeroDivisionError:
                if self.exam_duty.dgs_batch.repeater_batch:
                    pass
                else:
                    raise ValidationError("Please Add Atleast One GSK Online Examiner")
        
        
        # Distribute candidates with only MEK
        for idx, candidate in enumerate(candidate_with_mek):
            try:
                mek_examiner_index = idx % num_examiners_mek
                examiner_mek = examiners_mek[mek_examiner_index]
                print("Examiners_mek",examiners_mek)
                print("Examiner_mek",examiner_mek)
                print("mek_assignments",mek_assignments)
                print("mek_assignment_examiners_mek",mek_assignments)
                mek_assignments[examiner_mek].append(candidate)

            except ZeroDivisionError:
                if self.exam_duty.dgs_batch.repeater_batch:
                    pass
                else:
                    raise ValidationError("Please Add Atleast One MEK Examiner")
        
        
        # Distribute candidates with only MEK Online
        for idx, candidate in enumerate(candidate_with_mek_online):
            try:    
                online_mek_examiner_index = idx % num_examiners_mek_online
                examiner_mek_online = examiners_mek_online[online_mek_examiner_index]          
                online_mek_assignments[examiner_mek_online].append(candidate)
            except ZeroDivisionError:
                if self.exam_duty.dgs_batch.repeater_batch:
                    pass
                else:
                    raise ValidationError("Please Add Atleast One MEK Online Examiner")

            
        ### GSK ASSIGNMENTS    
        for examiner, assigned_candidates in gsk_assignments.items():
            examiner_id = examiner
            assignment = records.filtered(lambda r: r.id == examiner_id)
            assignment.gp_marksheet_ids = assigned_candidates
            
        
         ### GSK Online ASSIGNMENTS    
        for examiner, assigned_candidates in online_gsk_assignments.items():
            examiner_id = examiner
            assignment = records.filtered(lambda r: r.id == examiner_id)
            assignment.gp_marksheet_ids = assigned_candidates

        
        ### MEK ASSIGNMENTS    
        for examiner, assigned_candidates in mek_assignments.items():
            examiner_id = examiner
            assignment = records.filtered(lambda r: r.id == examiner_id)
            assignment.gp_marksheet_ids = assigned_candidates
        
        ### MeK Online ASSIGNMENTS    
        for examiner, assigned_candidates in online_mek_assignments.items():
            examiner_id = examiner
            assignment = records.filtered(lambda r: r.id == examiner_id)
            assignment.gp_marksheet_ids = assigned_candidates
        

        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'examiner.assignment.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    
    def confirm(self):
        records = self.examiner_lines_ids
        
        for record in records:
            
            if record.subject.name == 'GSK':
                if record.exam_type == 'practical_oral':
                    
                    if record.no_candidates > 25:
                        raise ValidationError("Number of candidates cannot exceed 25 for this assignment.")
                    elif record.no_candidates == 0:
                        raise ValidationError("Please Assigned Candidate By Clicking On Update")
                    
                    prac_oral_id = self.exam_duty.id
                    institute_id = self.institute_id.id
                    subject = record.subject.id
                    examiner = record.examiner.id
                    exam_date = record.exam_date
                    exam_type = record.exam_type
                    assignment = self.env["exam.type.oral.practical.examiners"].create({
                                                                                        'prac_oral_id':prac_oral_id,
                                                                                        'institute_id':institute_id,
                                                                                        'subject':subject,
                                                                                        'examiner':examiner,
                                                                                        'exam_date':exam_date,
                                                                                        'exam_type':exam_type      
                                                                                        })
                    
                    for marksheet in record.gp_marksheet_ids:
                        marksheet.write({'gsk_oral_prac_assignment':True})
                        gp_marksheet = marksheet
                        gsk_oral = marksheet.gsk_oral.id
                        gsk_prac = marksheet.gsk_prac.id
                        candidate = marksheet.gp_candidate.id
                        
                        # import wdb;wdb.set_trace()

                        self.env['exam.type.oral.practical.examiners.marksheet'].sudo().create({ 'examiners_id':assignment.id ,
                                                                                                    'gp_marksheet':gp_marksheet.id ,
                                                                                                    'gp_candidate':candidate , 
                                                                                                    'gsk_oral':gsk_oral , 
                                                                                                    'gsk_prac':gsk_prac 
                                                                                                    })
                
                elif record.exam_type == 'online':
                    
                    prac_oral_id = self.exam_duty.id
                    institute_id = self.institute_id.id
                    subject = record.subject.id
                    examiner = record.examiner.id
                    exam_date = record.exam_date
                    exam_type = record.exam_type
                    
                    assignment = self.env["exam.type.oral.practical.examiners"].create({
                                                                                        'prac_oral_id':prac_oral_id,
                                                                                        'institute_id':institute_id,
                                                                                        'subject':subject,
                                                                                        'examiner':examiner,
                                                                                        'exam_date':exam_date,
                                                                                        'exam_type':exam_type      
                                                                                        })
                    
                    for marksheet in record.gp_marksheet_ids:
                        marksheet.write({'gsk_online_assignment':True})
                        gp_marksheet = marksheet
                        gsk_online_id = marksheet.gsk_online.id
                        candidate = marksheet.gp_candidate.id
                        
                        self.env['exam.type.oral.practical.examiners.marksheet'].sudo().create({ 'examiners_id':assignment.id ,
                                                                                                 'gp_marksheet':gp_marksheet.id ,
                                                                                                 'gp_candidate':candidate , 
                                                                                                 'gsk_online':gsk_online_id })

                    
                    
                
                        

                                    
                
                
            elif record.subject.name == 'MEK':
                if record.exam_type == 'practical_oral':
                    if record.no_candidates > 25:
                        raise ValidationError("Number of candidates cannot exceed 25 for this assignment.")
                    elif record.no_candidates == 0:
                        raise ValidationError("Please Assigned Candidate By Clicking On Update Button")
                    
                    prac_oral_id = self.exam_duty.id
                    institute_id = self.institute_id.id
                    subject = record.subject.id
                    exam_date = record.exam_date
                    examiner = record.examiner.id
                    exam_type = record.exam_type
                    assignment = self.env["exam.type.oral.practical.examiners"].create({
                                                                                        'prac_oral_id':prac_oral_id,
                                                                                        'institute_id':institute_id,
                                                                                        'subject':subject,
                                                                                        'examiner':examiner,
                                                                                        'exam_date':exam_date,
                                                                                        'exam_type':exam_type      
                                                                                        })
                    for marksheet in record.gp_marksheet_ids:
                        marksheet.write({'mek_oral_prac_assignment':True})
                        # import wdb;wdb.set_trace()
                        gp_marksheet = marksheet
                        mek_oral = marksheet.mek_oral.id
                        mek_prac = marksheet.mek_prac.id
                        candidate = marksheet.gp_candidate.id
                        
                        self.env['exam.type.oral.practical.examiners.marksheet'].sudo().create({ 'examiners_id':assignment.id ,
                                                                                                    'gp_marksheet':gp_marksheet.id ,
                                                                                                    'gp_candidate':candidate , 
                                                                                                    'mek_oral':mek_oral , 
                                                                                                    'mek_prac':mek_prac 
                                                                                                    })
                elif record.exam_type == 'online':
                    prac_oral_id = self.exam_duty.id
                    institute_id = self.institute_id.id
                    subject = record.subject.id
                    examiner = record.examiner.id
                    exam_date = record.exam_date
                    exam_type = record.exam_type
                    
                    assignment = self.env["exam.type.oral.practical.examiners"].create({
                                                                                        'prac_oral_id':prac_oral_id,
                                                                                        'institute_id':institute_id,
                                                                                        'subject':subject,
                                                                                        'examiner':examiner,
                                                                                        'exam_date':exam_date,
                                                                                        'exam_type':exam_type      
                                                                                        })

                    for marksheet in record.gp_marksheet_ids:
                        marksheet.write({'mek_online_assignment':True})
                        gp_marksheet = marksheet
                        mek_online_id = marksheet.mek_online.id
                        candidate = marksheet.gp_candidate.id
                        
                        self.env['exam.type.oral.practical.examiners.marksheet'].sudo().create({ 'examiners_id':assignment.id ,
                                                                                                 'gp_marksheet':gp_marksheet.id ,
                                                                                                 'gp_candidate':candidate , 
                                                                                                 'mek_online':mek_online_id })
                

        
        # import wdb;wdb.set_trace()
        
        
        # return {
        #     'context': self.env.context,
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'examiner.assignment.wizard',
        #     'res_id': self.id,
        #     'view_id': False,
        #     'type': 'ir.actions.act_window',
        #     'target': 'new',
        # }
        
    
    
    def calculate_examiners(self,num_candidates, max_candidates_per_examiner, num_days):
        candidates_per_day = math.ceil(num_candidates / num_days)
        return math.ceil(candidates_per_day / max_candidates_per_examiner)
    
    @api.depends('no_of_days')
    def _compute_examiners_gsk(self):
        for record in self:
            try:
                max_candidates_per_examiner = 25            
                total_candidates = record.gsk_prac_oral_candidates
                num_days = record.no_of_days
                record.examiner_required_gsk = self.calculate_examiners(total_candidates, max_candidates_per_examiner, num_days)
            except ZeroDivisionError:
                record.examiner_required_gsk = 0
                
    @api.depends('no_of_days')
    def _compute_examiners_mek(self):
        for record in self:
            try:
                max_candidates_per_examiner = 25            
                total_candidates = record.mek_prac_oral_candidates
                num_days = record.no_of_days
                record.examiner_required_mek = self.calculate_examiners(total_candidates, max_candidates_per_examiner, num_days)
            except ZeroDivisionError:
                record.examiner_required_mek = 0
                
    
    @api.depends('institute_id')
    def _compute_gsk_prac_oral_candidates(self):
        for record in self:
            # import wdb;wdb.set_trace() ('mek_oral_prac_assignment','=',False),('gsk_oral_prac_assignment','=',False)
            record.gsk_prac_oral_candidates = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',record.exam_duty.dgs_batch.id),('registered_institute','=',record.institute_id.id),('state','=','1-in_process'),('gsk_oral_prac_status','in',('pending','failed')),('gsk_oral_prac_assignment','=',False)])

    @api.depends('institute_id')
    def _compute_mek_prac_oral_candidates(self):
        for record in self:
            record.mek_prac_oral_candidates = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',record.exam_duty.dgs_batch.id),('registered_institute','=',record.institute_id.id),('state','=','1-in_process'),('mek_oral_prac_status','in',('pending','failed')),('mek_oral_prac_assignment','=',False)])


    @api.depends('institute_id')
    def _compute_gsk_online_candidates(self):
        for record in self:
            record.gsk_online_candidates = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',record.exam_duty.dgs_batch.id),('registered_institute','=',record.institute_id.id),('state','=','1-in_process'),('gsk_online_status','in',('pending','failed')),('mek_online_assignment','=',False)])
    
    @api.depends('institute_id')
    def _compute_mek_online_candidates(self):
        for record in self:
            record.mek_online_candidates = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',record.exam_duty.dgs_batch.id),('registered_institute','=',record.institute_id.id),('state','=','1-in_process'),('mek_online_status','in',('pending','failed')),('gsk_online_assignment','=',False)])
    
    #CCMC Course
    
    
    
    exam_region = fields.Many2one('exam.center', 'Exam Region')
    examiner_lines_ids = fields.One2many('examiner.assignment.wizard.line', 'parent_id', string='Examiners')
    
class ExaminerAssignmentLineWizard(models.TransientModel):
    _name = 'examiner.assignment.wizard.line'
    _inherit = ['mail.thread','mail.activity.mixin']
    
    parent_id = fields.Many2one("examiner.assignment.wizard",string="Parent",tracking=True)

    exam_date = fields.Date('Exam Date',tracking=True)
    subject = fields.Many2one("course.master.subject",string="Subject",tracking=True)
    examiner = fields.Many2one('bes.examiner', string="Examiner",tracking=True)
    gp_marksheet_ids = fields.Many2many('gp.exam.schedule', string='Candidates',tracking=True)
    exam_type = fields.Selection([
        ('practical_oral', 'Practical/Oral'),
        ('online', 'Online')     
    ], string='Exam Type', default='practical_oral',tracking=True)
    
    no_candidates = fields.Integer('No. Of Candidates',compute='_compute_candidate_no',tracking=True)
    
    
    @api.depends('gp_marksheet_ids')
    def _compute_candidate_no(self):
        for record in self:
            record.no_candidates = len(record.gp_marksheet_ids)
    
    
    



    

      
class ExamOralPractical(models.Model):
    _name = 'exam.type.oral.practical'
    _inherit = ['mail.thread','mail.activity.mixin']
    # exam_schedule_id = fields.Many2one("bes.exam.schedule",string="Exam Schedule ID")
    # examiners = fields.Many2one('bes.examiner', string="Examiner")
    # subject = fields.Many2one("course.master.subject","Subject")
    institute_code = fields.Char(string="Institute Code", related='institute_id.code', required=True,tracking=True)
    dgs_batch = fields.Many2one("dgs.batches",string="Batch",required=True,tracking=True)
    institute_id = fields.Many2one("bes.institute",string="Institute",tracking=True)
    exam_region = fields.Many2one('exam.center', 'Exam Region',default=lambda self: self.get_examiner_region(),tracking=True)
    
    
    def open_assignment_wizard(self):
        
        if self.course.course_code == 'GP':
        
            view_id = self.env.ref('bes.examiner_assignment_wizard_form').id
            
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'res_model': 'examiner.assignment.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {
                    'default_exam_duty': self.id,
                    'default_exam_region': self.exam_region.id,
                }
            }
            
        elif self.course.course_code == 'CCMC':
            
            view_id = self.env.ref('bes.ccmc_examiner_assignment_wizard_form').id

            return {
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'res_model': 'ccmc.examiner.assignment.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {
                    'default_exam_duty': self.id,
                    'default_exam_region': self.exam_region.id,
                }
            }
    
    
    def get_examiner_region(self):
        user_id = self.env.user.id
        region = self.env['exam.center'].sudo().search([('exam_co_ordinator','=',user_id)]).id
        return region


    # start_time = fields.Datetime("Start Time")
    # end_time = fields.Datetime("End Time")
    examiners = fields.One2many("exam.type.oral.practical.examiners","prac_oral_id",string="Assign Examiners",tracking=True)
   
    
    course = fields.Many2one("course.master",string="Course",tracking=True)
    
    subject = fields.Many2one("course.master.subject",string="Subject",tracking=True)

    exam_type = fields.Selection([
        ('practical_oral', 'Practical/Oral'),
        ('online', 'Online')     
    ], string='Exam Type', default='practical_oral',tracking=True)
    
    expense_sheet_status = fields.Selection([
        ('pending', 'Pending'),
        ('generated', 'Generated')     
    ], string='Expense Sheet Status', default='pending',tracking=True)

    state = fields.Selection([
        ('1-draft', 'Pending'),
        ('2-confirm', 'Confirmed')     
    ], string='State', default='1-draft',tracking=True)
    
    
    def get_institute_id(self):
        institute_ids = set()
        for examiner in self.examiners:
            institute_ids.add(examiner.institute_id.id)
        return list(institute_ids)
    
    
    def generate_expense_sheet(self):
        print(self)
        for assignment in self.examiners:
            assignment_id = assignment.id
            examiner_id = assignment.examiner.id
            subject_name = assignment.subject.name
            institute_id = assignment.institute_id.id
            user_id = assignment.examiner.user_id.id
            quantity = len(assignment.marksheets)
            employee = self.env['hr.employee'].search([('user_id','=',user_id)])
            
            designation = assignment.examiner
            
            if subject_name == 'GSK' and assignment.exam_type == 'practical_oral': 
            
                product =  self.env['product.product'].search([('default_code','=','gsk_exam')])
                child_records = self.env['hr.expense'].sudo().create([
                                        {'product_id': product.id, 'employee_id': employee.id,'name': subject_name+' Exam','unit_amount': product.standard_price ,'quantity': quantity }
                                    ])
                
                expense_sheet = self.env['hr.expense.sheet'].sudo().create({'name': subject_name+' Exam',
                                                                    'dgs_exam':True,
                                                                    'dgs_batch': self.dgs_batch.id,
                                                                    'institute_id':institute_id,
                                                                    'employee_id':employee.id,
                                                                    'expense_line_ids': [(6, 0, child_records.ids)]
                                                                    })
            
                assignment.write({'expense_sheet':expense_sheet})
            
            elif subject_name == 'MEK' and assignment.exam_type == 'practical_oral': 
                
                product =  self.env['product.product'].search([('default_code','=','mek_exam')])
                child_records = self.env['hr.expense'].sudo().create([
                                        {'product_id': product.id, 'employee_id': employee.id,'name': subject_name+' Exam','unit_amount': product.standard_price ,'quantity': quantity }
                                    ])
                
                expense_sheet = self.env['hr.expense.sheet'].sudo().create({'name': subject_name+' Exam',
                                                                    'dgs_exam':True,
                                                                    'dgs_batch': self.dgs_batch.id,
                                                                    'institute_id':institute_id,
                                                                    'employee_id':employee.id,
                                                                    'expense_line_ids': [(6, 0, child_records.ids)]
                                                                    })
            
                assignment.write({'expense_sheet':expense_sheet})
            
            elif subject_name == 'GSK' and assignment.exam_type == 'online': 
                
                
        
                    
                    
                
                product =  self.env['product.product'].search([('default_code','=','gsk_online_exam')])
                
                if designation == 'non-mariner':
                    price = 2000
                else:
                    price = product.standard_price
                
                child_records = self.env['hr.expense'].sudo().create([
                                        {'product_id': product.id, 'employee_id': employee.id,'name': subject_name+' Exam','unit_amount': price ,'quantity': 1 }
                                    ])
                
                expense_sheet = self.env['hr.expense.sheet'].sudo().create({'name': subject_name+' Exam',
                                                                    'dgs_exam':True,
                                                                    'dgs_batch': self.dgs_batch.id,
                                                                    'institute_id':institute_id,
                                                                    'employee_id':employee.id,
                                                                    'expense_line_ids': [(6, 0, child_records.ids)]
                                                                    })
            
                assignment.write({'expense_sheet':expense_sheet})
            
            elif subject_name == 'MEK' and assignment.exam_type == 'online': 
                
                product =  self.env['product.product'].search([('default_code','=','mek_online_exam')])
                
                if designation == 'non-mariner':
                    price = 2000
                else:
                    price = product.standard_price
                
                
                child_records = self.env['hr.expense'].sudo().create([
                                        {'product_id': product.id, 'employee_id': employee.id,'name': subject_name+' Exam','unit_amount': price ,'quantity': 1 }
                                    ])
                
                expense_sheet = self.env['hr.expense.sheet'].sudo().create({'name': subject_name+' Exam',
                                                                    'dgs_exam':True,
                                                                    'dgs_batch': self.dgs_batch.id,
                                                                    'institute_id':institute_id,
                                                                    'employee_id':employee.id,
                                                                    'expense_line_ids': [(6, 0, child_records.ids)]
                                                                    })
            
                assignment.write({'expense_sheet':expense_sheet})
            
            elif subject_name == 'CCMC' and assignment.exam_type == 'practical_oral': 
                
                product =  self.env['product.product'].search([('default_code','=','ccmc_exam')])
                child_records = self.env['hr.expense'].sudo().create([
                                        {'product_id': product.id, 'employee_id': employee.id,'name': subject_name+' Exam','unit_amount': product.standard_price ,'quantity': quantity }
                                    ])
                
                expense_sheet = self.env['hr.expense.sheet'].sudo().create({'name': subject_name+' Exam',
                                                                    'dgs_exam':True,
                                                                    'dgs_batch': self.dgs_batch.id,
                                                                    'institute_id':institute_id,
                                                                    'employee_id':employee.id,
                                                                    'expense_line_ids': [(6, 0, child_records.ids)]
                                                                    })
            
                assignment.write({'expense_sheet':expense_sheet})
                
            elif subject_name == 'CCMC' and assignment.exam_type == 'online': 
                
                product =  self.env['product.product'].search([('default_code','=','ccmc_online_exam')])
                
                if designation == 'non-mariner':
                    price = 2000
                else:
                    price = product.standard_price
                
                
                child_records = self.env['hr.expense'].sudo().create([
                                        {'product_id': product.id, 'employee_id': employee.id,'name': subject_name+' Exam','unit_amount': price ,'quantity': 1 }
                                    ])
                
                expense_sheet = self.env['hr.expense.sheet'].sudo().create({'name': subject_name+' Exam',
                                                                    'dgs_exam':True,
                                                                    'dgs_batch': self.dgs_batch.id,
                                                                    'institute_id':institute_id,
                                                                    'employee_id':employee.id,
                                                                    'expense_line_ids': [(6, 0, child_records.ids)]
                                                                    })
            
                assignment.write({'expense_sheet':expense_sheet})
            
            elif subject_name == 'CCMC GSK Oral' and assignment.exam_type == 'practical_oral': 
                
                product =  self.env['product.product'].search([('default_code','=','ccmc_gsk_exam')])
                
                
                child_records = self.env['hr.expense'].sudo().create([
                                        {'product_id': product.id, 'employee_id': employee.id,'name': subject_name+' Exam','unit_amount': price ,'quantity': 1 }
                                    ])
                
                expense_sheet = self.env['hr.expense.sheet'].sudo().create({'name': subject_name+' Exam',
                                                                    'dgs_exam':True,
                                                                    'dgs_batch': self.dgs_batch.id,
                                                                    'institute_id':institute_id,
                                                                    'employee_id':employee.id,
                                                                    'expense_line_ids': [(6, 0, child_records.ids)]
                                                                    })
            
                assignment.write({'expense_sheet':expense_sheet})
            
        self.write({'expense_sheet_status':'generated'})
            
    
    
    
    def confirm(self):
        
        
        institute_id = self.get_institute_id()
        
        
        # import wdb; wdb.set_trace(); 
        for i in institute_id:
   
            # institute_id = self.env['gp.exam.schedule'].search([('dgs_batch','=',self.dgs_batch.id),('registered_institute','=',i),('state','=','1-in_process'),('gsk_oral_prac_status','in',('pending','failed'))]).ids
            

        
            if self.course.course_code == 'GP':
                
                if self.subject.name == 'GSK':
                    
                    if self.exam_type == 'practical_oral':
                
                        gp_marksheets = self.env['gp.exam.schedule'].search([('dgs_batch','=',self.dgs_batch.id),('registered_institute','=',i),('state','=','1-in_process'),('gsk_oral_prac_status','in',('pending','failed'))]).ids
                        
                        examiners = self.examiners.filtered(lambda r: r.institute_id.id == i).ids

                        
                        assignments = {examiner: [] for examiner in examiners}  # Dictionary to store assignments

                    
                        for i, candidate in enumerate(gp_marksheets):
                            examiner_index = i % len(examiners)  # Calculate the index of the examiner using modulo
                            examiner = examiners[examiner_index]
                            assignments[examiner].append(candidate)   
                            
                        for examiner, assigned_candidates in assignments.items():
                            # import wdb; wdb.set_trace();
                            examiner_id = examiner
                            for c in assigned_candidates:
                                gp_marksheet = self.env['gp.exam.schedule'].browse(c).id
                                gsk_oral = self.env['gp.exam.schedule'].browse(c).gsk_oral.id
                                gsk_prac = self.env['gp.exam.schedule'].browse(c).gsk_prac.id
                                candidate = self.env['gp.exam.schedule'].browse(c).gp_candidate.id
                                self.env['exam.type.oral.practical.examiners.marksheet'].sudo().create({ 'examiners_id':examiner_id ,
                                                                                                 'gp_marksheet':gp_marksheet ,
                                                                                                 'gp_candidate':candidate , 
                                                                                                 'gsk_oral':gsk_oral , 
                                                                                                 'gsk_prac':gsk_prac })
                            
                            
                            examiner_assignment = self.env['exam.type.oral.practical.examiners'].browse(examiner)
                            # import wdb; wdb.set_trace();
                            quantity = len(examiner_assignment.marksheets)
                            user_id = examiner_assignment.examiner.user_id.id
                            employee = self.env['hr.employee'].search([('user_id','=',user_id)])
                            product =  self.env['product.product'].search([('default_code','=','gsk_exam')])
                            child_records = self.env['hr.expense'].sudo().create([
                                    {'product_id': product.id, 'employee_id': employee.id,'name':'GSK Exam','unit_amount': product.standard_price ,'quantity': quantity }
                                ])

                            expense_sheet = self.env['hr.expense.sheet'].sudo().create({'name':'GSK Exam',
                                                                'dgs_exam':True,
                                                                'dgs_batch': self.dgs_batch.id,
                                                                'institute_id':examiner_assignment.institute_id.id,
                                                                'employee_id':employee.id,
                                                                'expense_line_ids': [(6, 0, child_records.ids)]
                                                                })
                            examiner_assignment.write({'status':'confirmed','expense_sheet':expense_sheet})
                            
                        self.write({'state':'2-confirm'})
                    
                    elif self.exam_type == 'online':
                        
                        gp_marksheets = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',self.dgs_batch.id),('registered_institute','=',i),('state','=','1-in_process'),('gsk_online_status','in',('pending','failed'))])
                        
                        examiners = self.examiners.filtered(lambda r: r.institute_id.id == i).ids
                        
                        assignments = {examiner: [] for examiner in examiners}
                        
                        for i, candidate in enumerate(gp_marksheets):
                            examiner_index = i % len(examiners)  # Calculate the index of the examiner using modulo
                            examiner = examiners[examiner_index]
                            assignments[examiner].append(candidate)
                        
                        for examiner, assigned_candidates in assignments.items():
                            # import wdb; wdb.set_trace();
                            examiner_id = examiner
                            for marksheet in assigned_candidates:
                                marksheet_id = marksheet.id
                                marksheet.gsk_online.generate_token()
                                gsk_online_id = marksheet.gsk_online.id
                                gp_candidate_id = marksheet.gp_candidate.id
                                self.env['exam.type.oral.practical.examiners.marksheet'].sudo().create({ 'examiners_id':examiner_id ,
                                                                                                 'gp_marksheet':marksheet_id ,
                                                                                                 'gp_candidate':gp_candidate_id , 
                                                                                                 'gsk_online':gsk_online_id })
                            
                            examiner_assignment = self.env['exam.type.oral.practical.examiners'].browse(examiner)
                            # import wdb; wdb.set_trace();
                            quantity = examiner_assignment.no_days
                            user_id = examiner_assignment.examiner.user_id.id
                            employee = self.env['hr.employee'].search([('user_id','=',user_id)])
                            product =  self.env['product.product'].search([('default_code','=','gsk_online_exam')])
                            child_records = self.env['hr.expense'].sudo().create([
                                    {'product_id': product.id, 'employee_id': employee.id,'name':'GSK Exam','unit_amount': product.standard_price ,'quantity': quantity }
                                ])

                            expense_sheet = self.env['hr.expense.sheet'].sudo().create({'name':'GSK Online Exam',
                                                                'dgs_exam':True,
                                                                'dgs_batch': self.dgs_batch.id,
                                                                'institute_id':examiner_assignment.institute_id.id,
                                                                'employee_id':employee.id,
                                                                'expense_line_ids': [(6, 0, child_records.ids)]
                                                                })
                            examiner_assignment.write({'status':'confirmed','expense_sheet':expense_sheet})
                        
                        self.write({'state':'2-confirm'})
                
                elif self.subject.name == 'MEK':

                    if self.exam_type == 'practical_oral':
                    
                        gp_marksheets = self.env['gp.exam.schedule'].search([('dgs_batch','=',self.dgs_batch.id),('registered_institute','=',i),('state','=','1-in_process'),('mek_oral_prac_status','in',('pending','failed'))]).ids
                        
                        # import wdb;wdb.set_trace()
                        
                        
                        examiners = self.examiners.filtered(lambda r: r.institute_id.id == i).ids
                        
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
                            
                            examiner_assignment = self.env['exam.type.oral.practical.examiners'].browse(examiner)
                            # import wdb; wdb.set_trace();
                            quantity = len(examiner_assignment.marksheets)
                            user_id = examiner_assignment.examiner.user_id.id
                            employee = self.env['hr.employee'].search([('user_id','=',user_id)])
                            product =  self.env['product.product'].search([('default_code','=','mek_exam')])
                            child_records = self.env['hr.expense'].create([
                                    {'product_id': product.id, 'employee_id': employee.id,'name':'MEK Exam','unit_amount': product.standard_price ,'quantity': quantity }
                                ])

                            expense_sheet = self.env['hr.expense.sheet'].create({'name':'MEK Exam',
                                                                'dgs_exam':True,
                                                                'dgs_batch': self.dgs_batch.id,
                                                                'institute_id':examiner_assignment.institute_id.id,
                                                                'employee_id':employee.id,
                                                                'expense_line_ids': [(6, 0, child_records.ids)]
                                                                })
                            examiner_assignment.write({'status':'confirmed','expense_sheet':expense_sheet})
                                                    
                        self.write({'state':'2-confirm'})
                    
                    elif self.exam_type == 'online':
                        gp_marksheets = self.env['gp.exam.schedule'].search([('dgs_batch','=',self.dgs_batch.id),('registered_institute','=',i),('state','=','1-in_process'),('mek_oral_prac_status','in',('pending','failed'))]).ids
                        
                        # import wdb;wdb.set_trace()
                        
                        
                        examiners = self.examiners.filtered(lambda r: r.institute_id.id == i).ids
                        
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
                            
                            examiner_assignment = self.env['exam.type.oral.practical.examiners'].browse(examiner)
                            # import wdb; wdb.set_trace();
                            quantity = len(examiner_assignment.marksheets)
                            user_id = examiner_assignment.examiner.user_id.id
                            employee = self.env['hr.employee'].search([('user_id','=',user_id)])
                            product =  self.env['product.product'].search([('default_code','=','mek_exam')])
                            child_records = self.env['hr.expense'].create([
                                    {'product_id': product.id, 'employee_id': employee.id,'name':'MEK Exam','unit_amount': product.standard_price ,'quantity': quantity }
                                ])

                            expense_sheet = self.env['hr.expense.sheet'].create({'name':'MEK Exam',
                                                                'dgs_exam':True,
                                                                'dgs_batch': self.dgs_batch.id,
                                                                'institute_id':examiner_assignment.institute_id.id,
                                                                'employee_id':employee.id,
                                                                'expense_line_ids': [(6, 0, child_records.ids)]
                                                                })
                            examiner_assignment.write({'status':'confirmed','expense_sheet':expense_sheet})
                                                    
                        self.write({'state':'2-confirm'})
                    
                
            elif self.course.course_code == 'CCMC':
                
                
                if self.subject.name == 'CCMC Oral and Practical':
                
                    # import wdb;wdb.set_trace()
                    if self.exam_type == 'practical_oral':
                    
                        ccmc_marksheets = self.env['ccmc.exam.schedule'].search([('dgs_batch','=',self.dgs_batch.id),('registered_institute','=',i),('state','=','1-in_process'),('oral_prac_status','=','failed')]).ids
                        
                        examiners = self.examiners.filtered(lambda r: r.institute_id.id == i).ids
                        
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
                                self.env['exam.type.oral.practical.examiners.marksheet'].create({ 'examiners_id': examiner_id ,'ccmc_marksheet':ccmc_marksheet,'ccmc_candidate':candidate , 'cookery_bakery':cookery_bakery })
                        
                            examiner_assignment = self.env['exam.type.oral.practical.examiners'].browse(examiner)
                            # import wdb; wdb.set_trace();
                            quantity = len(examiner_assignment.marksheets)
                            user_id = examiner_assignment.examiner.user_id.id
                            employee = self.env['hr.employee'].search([('user_id','=',user_id)])
                            product =  self.env['product.product'].search([('default_code','=','ccmc_exam_oral')])
                            child_records = self.env['hr.expense'].create([
                                    {'product_id': product.id, 'employee_id': employee.id,'name':'CCMC Oral Exam','unit_amount': product.standard_price ,'quantity': quantity }
                                ])

                            expense_sheet = self.env['hr.expense.sheet'].create({'name':'CCMC Oral Exam',
                                                                'dgs_exam':True,
                                                                'dgs_batch': self.dgs_batch.id,
                                                                'institute_id':examiner_assignment.institute_id.id,
                                                                'employee_id':employee.id,
                                                                'expense_line_ids': [(6, 0, child_records.ids)]
                                                                })
                            examiner_assignment.write({'status':'confirmed','expense_sheet':expense_sheet})

                        self.write({'state':'2-confirm'})
                    
                    elif self.exam_type == 'online':
                       
                        ccmc_marksheets = self.env['ccmc.exam.schedule'].search([('dgs_batch','=',self.dgs_batch.id),('registered_institute','=',i),('state','=','1-in_process'),('oral_prac_status','=','failed')]).ids
                        
                        examiners = self.examiners.filtered(lambda r: r.institute_id.id == i).ids
                        
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
                                self.env['exam.type.oral.practical.examiners.marksheet'].create({ 'examiners_id': examiner_id ,'ccmc_marksheet':ccmc_marksheet,'ccmc_candidate':candidate , 'cookery_bakery':cookery_bakery })
                        
                            examiner_assignment = self.env['exam.type.oral.practical.examiners'].browse(examiner)
                            # import wdb; wdb.set_trace();
                            quantity = len(examiner_assignment.marksheets)
                            user_id = examiner_assignment.examiner.user_id.id
                            employee = self.env['hr.employee'].search([('user_id','=',user_id)])
                            product =  self.env['product.product'].search([('default_code','=','ccmc_exam_oral')])
                            child_records = self.env['hr.expense'].create([
                                    {'product_id': product.id, 'employee_id': employee.id,'name':'CCMC Oral Exam','unit_amount': product.standard_price ,'quantity': quantity }
                                ])

                            expense_sheet = self.env['hr.expense.sheet'].create({'name':'CCMC Oral Exam',
                                                                'dgs_exam':True,
                                                                'dgs_batch': self.dgs_batch.id,
                                                                'institute_id':examiner_assignment.institute_id.id,
                                                                'employee_id':employee.id,
                                                                'expense_line_ids': [(6, 0, child_records.ids)]
                                                                })
                            examiner_assignment.write({'status':'confirmed','expense_sheet':expense_sheet})

                        self.write({'state':'2-confirm'})
                
                elif self.subject.name == 'CCMC GSK Oral':

                    if self.exam_type == 'practical_oral':
                    
                        ccmc_marksheets = self.env['ccmc.exam.schedule'].search([('dgs_batch','=',self.dgs_batch.id),('registered_institute','=',i),('state','=','1-in_process'),('oral_prac_status','=','failed')]).ids
                        
                        examiners = self.examiners.filtered(lambda r: r.institute_id.id == i).ids
                        
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
                                self.env['exam.type.oral.practical.examiners.marksheet'].create({ 'examiners_id': examiner_id ,'ccmc_oral':ccmc_oral,'ccmc_marksheet':ccmc_marksheet,'ccmc_candidate':candidate  })

                            examiner_assignment = self.env['exam.type.oral.practical.examiners'].browse(examiner)
                            # import wdb; wdb.set_trace();
                            quantity = len(examiner_assignment.marksheets)
                            user_id = examiner_assignment.examiner.user_id.id
                            employee = self.env['hr.employee'].search([('user_id','=',user_id)])
                            product =  self.env['product.product'].search([('default_code','=','ccmc_gsk_oral_exam')])
                            child_records = self.env['hr.expense'].create([
                                    {'product_id': product.id, 'employee_id': employee.id,'name':'CCMC Oral Exam','unit_amount': product.standard_price ,'quantity': quantity }
                                ])

                            expense_sheet = self.env['hr.expense.sheet'].create({'name':'CCMC Oral Exam',
                                                                'dgs_exam':True,
                                                                'dgs_batch': self.dgs_batch.id,
                                                                'institute_id':examiner_assignment.institute_id.id,
                                                                'employee_id':employee.id,
                                                                'expense_line_ids': [(6, 0, child_records.ids)]
                                                                })
                            examiner_assignment.write({'status':'confirmed','expense_sheet':expense_sheet})
                            
                        self.write({'state':'2-confirm'})
                   
                    elif self.exam_type == 'online':

                        ccmc_marksheets = self.env['ccmc.exam.schedule'].search([('dgs_batch','=',self.dgs_batch.id),('registered_institute','=',i),('state','=','1-in_process'),('oral_prac_status','=','failed')]).ids
                        
                        examiners = self.examiners.filtered(lambda r: r.institute_id.id == i).ids
                        
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
                                self.env['exam.type.oral.practical.examiners.marksheet'].create({ 'examiners_id': examiner_id ,'ccmc_oral':ccmc_oral,'ccmc_marksheet':ccmc_marksheet,'ccmc_candidate':candidate  })

                            examiner_assignment = self.env['exam.type.oral.practical.examiners'].browse(examiner)
                            # import wdb; wdb.set_trace();
                            quantity = len(examiner_assignment.marksheets)
                            user_id = examiner_assignment.examiner.user_id.id
                            employee = self.env['hr.employee'].search([('user_id','=',user_id)])
                            product =  self.env['product.product'].search([('default_code','=','ccmc_gsk_oral_exam')])
                            child_records = self.env['hr.expense'].create([
                                    {'product_id': product.id, 'employee_id': employee.id,'name':'CCMC Oral Exam','unit_amount': product.standard_price ,'quantity': quantity }
                                ])

                            expense_sheet = self.env['hr.expense.sheet'].create({'name':'CCMC Oral Exam',
                                                                'dgs_exam':True,
                                                                'dgs_batch': self.dgs_batch.id,
                                                                'institute_id':examiner_assignment.institute_id.id,
                                                                'employee_id':employee.id,
                                                                'expense_line_ids': [(6, 0, child_records.ids)]
                                                                })
                            examiner_assignment.write({'status':'confirmed','expense_sheet':expense_sheet})
                            
                        self.write({'state':'2-confirm'})

    

class ExamOralPracticalExaminers(models.Model):
    _name = 'exam.type.oral.practical.examiners'
    _inherit = ['mail.thread','mail.activity.mixin']
    dgs_batch = fields.Many2one("dgs.batches",related='prac_oral_id.dgs_batch',string="DGS Batch",store=True,required=False,tracking=True)
    exam_region = fields.Many2one('exam.center', 'Exam Center',related='prac_oral_id.exam_region',store=True,tracking=True)
    prac_oral_id = fields.Many2one("exam.type.oral.practical",string="Exam Practical/Oral ID",store=True,required=False,tracking=True)
    institute_id = fields.Many2one("bes.institute",string="Institute",required=True,tracking=True)
    course = fields.Many2one("course.master",related='prac_oral_id.course',string="Course",tracking=True)
    subject = fields.Many2one("course.master.subject",string="Subject",store=True,tracking=True)
    examiner = fields.Many2one('bes.examiner', string="Examiner",tracking=True)
    exam_date = fields.Date("Exam Date",tracking=True)
    marksheets = fields.One2many('exam.type.oral.practical.examiners.marksheet','examiners_id',string="Candidates",tracking=True)
    exam_type = fields.Selection([
        ('practical_oral', 'Practical/Oral'),
        ('online', 'Online')     
    ], string='Exam Type', default='practical_oral',tracking=True)
    
    online_from_date = fields.Date("From")
    online_to_date = fields.Date("To Date")
    team_lead = fields.Boolean("TL")
    no_days = fields.Integer("No. of Days" , compute='_compute_num_days' )
    
    expense_sheet = fields.Many2one('hr.expense.sheet', string="Expense Sheet")
    status = fields.Selection([
        ('draft', 'Draft'), 
        ('confirmed', 'Confirmed')
    ], string='Status',default="draft" )
    
    extended = fields.Boolean("Extended")
    
    marksheet_image = fields.Binary(string="Marksheet Image",tracking=True)
    marksheet_image_name = fields.Char(string="Marksheet Image name",tracking=True)
    marksheet_uploaded = fields.Boolean(string="Marksheet Uploaded",tracking=True)
    candidate_done = fields.Char("Candidate Done" , compute='compute_candidates_done',store=True)
    
    @api.depends('marksheets')
    def compute_candidates_done(self):
        for record in self:
            if record.subject.name == 'GSK':
                if record.exam_type == 'practical_oral':
                    count = 0
                    for sheet in record.marksheets:
                       if sheet.gsk_oral.gsk_oral_draft_confirm == 'confirm' and sheet.gsk_prac.gsk_practical_draft_confirm == 'confirm':
                           count += 1
                    record.candidate_done = count
                else:
                    record.candidate_done = 'NA'
                    
            elif record.subject.name == 'MEK':
                if record.exam_type == 'practical_oral':
                    count = 0
                    for sheet in record.marksheets:
                        if sheet.mek_oral.mek_oral_draft_confirm == 'confirm' and sheet.mek_prac.mek_practical_draft_confirm == 'confirm':
                            count += 1
                    record.candidate_done = count
                else:
                    record.candidate_done = 'NA'
            
            elif record.subject.name == 'CCMC':
                if record.exam_type == 'practical_oral':
                    count = 0
                    for sheet in record.marksheets:
                        if sheet.cookery_bakery.cookery_draft_confirm == 'confirm' and sheet.ccmc_oral.ccmc_oral_draft_confirm == 'confirm':
                            count += 1
                    record.candidate_done = count
                else:
                    record.candidate_done = 'NA'
            
            elif record.subject.name == 'CCMC GSK Oral':
                if record.exam_type == 'practical_oral':
                    count = 0
                    for sheet in record.marksheets:
                        if sheet.ccmc_gsk_oral.ccmc_oral_draft_confirm == 'confirm':
                            count += 1
                    record.candidate_done = count
                else:
                    record.candidate_done = 'NA'
                    
            else:
                record.candidate_done = 'NA'
                
            

    
    
    def download_marksheet(self):
        
        if self.exam_type == 'practical_oral' and self.subject.name == 'GSK':
        
            url = '/open_candidate_form/download_gsk_marksheet/7/'+str(self.id)
            
            return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }
        
        elif self.exam_type == 'practical_oral' and self.subject.name == 'MEK':
        
            url = '/open_candidate_form/download_mek_marksheet/7/'+str(self.id)
            
            return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }
            
        elif self.exam_type == 'practical_oral' and self.subject.name == 'CCMC':
        
            url = '/open_ccmc_candidate_form/download_ccmc_practical_marksheet/7/'+str(self.id)
            
            return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }
        
        elif self.exam_type == 'practical_oral' and self.subject.name == 'CCMC GSK Oral':
        
            url = '/open_ccmc_candidate_form/download_ccmc_gsk_oral_marksheet/7/'+str(self.id)
            
            return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }



        # examiner = self.examiner
        # # batch_info = request.env['exam.type.oral.practical'].sudo().search([('dgs_batch.id','=',batch_id)])
        # # examiner_assignments = request.env['exam.type.oral.practical.examiners'].sudo().search([('dgs_batch.id','=',batch_id),('id','=',assignment_id)])
        # examiner_assignments = self

        # marksheets = request.env['exam.type.oral.practical.examiners.marksheet'].sudo().search([('examiners_id','=',self.id)])

        # # import wdb;wdb.set_trace();
        
        # for exam in examiner_assignments:
        #     if examiner.subject_id.name == 'GSK':
        #         assignment = exam.id
                
        # # for candidate in assignment.gp_oral_prac

        # excel_buffer = io.BytesIO()

        # # Create a new Excel workbook and add a worksheet
        # workbook = xlsxwriter.Workbook(excel_buffer)
        # # workbook   = xlsxwriter.Workbook('filename.xlsx')

        # gsk_oral_sheet = workbook.add_worksheet('GSK Oral')
        # gsk_practical_sheet = workbook.add_worksheet('GSK Practical')
        
        # locked = workbook.add_format({'locked':True,'border':1,'font_size': 18})
        # unlocked = workbook.add_format({'locked':False, 'border':1 })
        # # Set the wrap text format
        # wrap_format = workbook.add_format({'text_wrap': True})
        
        # #For GSK Oral Marksheet
        # # gsk_oral_sheet.set_column('A:XDF',None, unlocked)
        # gsk_oral_sheet.set_column('A2:A2',50, unlocked)
        # gsk_oral_sheet.set_column('B2:B2',20, unlocked)
        # gsk_oral_sheet.set_column('C2:C2',30, unlocked)
        # gsk_oral_sheet.set_column('D2:E2',40, unlocked)
        # gsk_oral_sheet.set_column('F2:F2',30, unlocked)
        # gsk_oral_sheet.set_column('G:G',15, unlocked)
            
        # gsk_oral_sheet.protect()
        # date_format = workbook.add_format({'num_format': 'dd-mmm-yy','locked':False})

        # header_format = workbook.add_format({   
        #                                         'border':1,
        #                                         'bold': True,
        #                                         'align': 'center',
        #                                         'valign': 'vcenter',
        #                                         'font_color': 'black',
        #                                         'locked':True,
        #                                         'font_size': 15,
        #                                         'text_wrap': True,
        #                                     })
        
        # merge_format = workbook.add_format({    
        #                                         'border':1,
        #                                         'bold':     True,
        #                                         'align':    'center',
        #                                         'valign':   'vcenter',
        #                                         'font_size': 20,
        #                                         'font_color': 'black',
        #                                         'text_wrap': True,
        #                                     })
        
        # instruction = workbook.add_format({
        #                                         'bold':     True,
        #                                         'align':    'center',
        #                                         'valign':   'vcenter',
        #                                         'font_size': 12,
        #                                         'font_color': 'red',
        #                                         'text_wrap': True,
        #                                     })

        # gsk_oral_sheet.merge_range("A1:D1", examiner_assignments.institute_id.name, merge_format)
        # gsk_oral_sheet.write("E1:F1", "After filling the marks please save the file. \n Go back to the page where you download this excel and upload it.",instruction)
        # header_oral = ['Name of the Candidate','Roll No', 'Candidate Code No',
        #   'Subject area 1 and 2 and 3 \n Minimum 8 question \n 25 marks',
        #   'Subject area 4 and 5 and 6 \n Minimum 9 question \n 25 marks',
        #   'Practical Record Book and Journal \n 25 Marks', 'Remarks']
        # for col, value in enumerate(header_oral):
        #     gsk_oral_sheet.write(1, col, value, header_format)
        
          
        # candidate_list = [] #List of Candidates
        # roll_no = []
        # candidate_code = [] #Candidates Code No.
        # marks_values_5 = [1,2,3,4,5]
        # marks_values_6 = [1,2,3,4,5,6]
        # marks_values_8 = [1,2,3,4,5,6,7,8]
        # marks_values_10 = [1,2,3,4,5,6,7,8,9,10]
        # marks_values_12 = [1,2,3,4,5,6,7,8,9,10,11,12]
        # marks_values_18 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]
        # marks_values_25 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]
        # marks_values_30 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
        # remarks = ['Absent','Good','Average','Weak']

        # for candidate in marksheets:
        #     candidate_list.append(candidate.gp_candidate.name)
        #     roll_no.append(candidate.gp_marksheet.exam_id)
        #     candidate_code.append(candidate.gp_candidate.candidate_code)
        
        # # import wdb;wdb.set_trace();
        
        # for i, candidate in enumerate(candidate_list):
        #     gsk_oral_sheet.write('A{}'.format(i+3), candidate, locked)

        # for i, code in enumerate(roll_no):
        #     gsk_oral_sheet.write('B{}'.format(i+3), code, locked)

        # for i, code in enumerate(candidate_code):
        #     gsk_oral_sheet.write('C{}'.format(i+3), code, locked)
        #     gsk_oral_sheet.data_validation('D{}'.format(i+3), {'validate': 'list', 'source': marks_values_25 })
        #     gsk_oral_sheet.data_validation('E{}'.format(i+3), {'validate': 'list', 'source': marks_values_25 })
        #     gsk_oral_sheet.data_validation('F{}'.format(i+3), {'validate': 'list', 'source': marks_values_25 })
        #     gsk_oral_sheet.data_validation('G{}'.format(i+3), {'validate': 'list', 'source': remarks })

       
        # #For GSK Practical Marksheet
        # # gsk_practical_sheet.set_column('A:XDF',None, unlocked)
        # gsk_practical_sheet.set_column('A2:A2',50, unlocked)
        # gsk_practical_sheet.set_column('B2:B2',20, unlocked)
        # gsk_practical_sheet.set_column('C2:C2',30, unlocked)
        # gsk_practical_sheet.set_column('D2:G2',35, unlocked)
        # gsk_practical_sheet.set_column('F2:F2',50, unlocked)
        # gsk_practical_sheet.set_column('H2:H2',15, unlocked)
            
        # gsk_practical_sheet.protect()
        
        
        # # Merge 3 cells over two rows.
        # gsk_practical_sheet.merge_range("A1:D1", examiner_assignments.institute_id.name, merge_format)
        
        # header_prac = ['Name of the Candidate','Roll No', 'Candidate Code No',
        #   '-Climb the mast with safe practices \n -Prepare and throw Heaving Line \n Rigging Bosun\'s Chair and self lower and hoist \n 30 Marks', #D
        #   '-Rig a stage for painting shipside \n -Rig a Pilot Ladder \n -Rig scaffolding to work at a height  \n 30 marks',#E
        #   '-Making fast Ropes and Wires \n -Use Rope-Stopper / Chain Stopper \n -Knots, Bends, Hitches \n -Whippings/Seizing/Splicing Ropes/Wires \n ·Taking Soundings with sounding rod / sounding taps \n ·Reading of Draft \n .Mannual lifting of weight (30 Marks)',#G
        #   '-Recognise buyos and flags \n -Hoisting a Flag correctly \n -Steering and Helm Orders \n 10 Marks',#G
        # #   '-Rigging Bosuns Chair and self lower and hoist \n 8 marks',
        #     'Remarks']
        # for col, value in enumerate(header_prac):
        #     gsk_practical_sheet.write(1, col, value, header_format)
        
        # # # import wdb;wdb.set_trace();
        
        # for i, candidate in enumerate(candidate_list):
        #     gsk_practical_sheet.write('A{}'.format(i+3), candidate, locked)
            
        # for i, code in enumerate(roll_no):
        #     gsk_practical_sheet.write('B{}'.format(i+3), code, locked)

        # for i, code in enumerate(candidate_code):
        #     gsk_practical_sheet.write('C{}'.format(i+3), code, locked)
        #     gsk_practical_sheet.data_validation('D{}'.format(i+3), {'validate': 'list', 'source': marks_values_30 })
        #     gsk_practical_sheet.data_validation('E{}'.format(i+3), {'validate': 'list', 'source': marks_values_30 })
        #     gsk_practical_sheet.data_validation('F{}'.format(i+3), {'validate': 'list', 'source': marks_values_30 })
        #     gsk_practical_sheet.data_validation('G{}'.format(i+3), {'validate': 'list', 'source': marks_values_10 })
        #     gsk_practical_sheet.data_validation('H{}'.format(i+3), {'validate': 'list', 'source': remarks })
        
        # workbook.close()

        # # Set the buffer position to the beginning
        # excel_buffer.seek(0)

        # date = examiner_assignments[0].exam_date
        
        # file_name = examiner.name+"-GSK-"+str(date)+".xlsx"
        
        # # Generate a response with the Excel file
        # # response = request.make_response(
        # #     excel_buffer.getvalue(),
        # #     headers=[
        # #         ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
        # #         ('Content-Disposition', 'attachment; filename='+file_name)
        # #     ]
        # # )

        # # Clean up the buffer
        # excel_buffer.close()

        # return excel_buffer
        
        
    
    @api.constrains('examiner', 'exam_date')
    def _check_duplicate_examiner_on_date(self):
        for record in self:
            if record.examiner and record.exam_date and record.exam_type != 'online' and record.subject.name != 'CCMC GSK Oral' and record.dgs_batch.repeater_batch != True:
                # Check if there are any other records with the same examiner and exam date
                duplicate_records = self.search([
                    ('examiner', '=', record.examiner.id),
                    ('exam_date', '=', record.exam_date),
                    ('id', '!=', record.id)  # Exclude the current record
                ])
                if duplicate_records.exam_type == 'online':
                     # Get the name of the examiner
                    pass
                elif duplicate_records.exam_type == 'practical_oral':
                    examiner_name = record.examiner.name
                    # Format the validation error message to include the examiner's name and exam date
                    error_msg = _("Examiner '%s' is already assigned on %s! for '%s' ") % (examiner_name, record.exam_date,duplicate_records.institute_id.name)
                    raise ValidationError(error_msg)
                else:
                    pass
                    

    
    def download_attendance_sheet(self):
        if self.subject.name == "CCMC" and self.exam_type == "online":
            return self.env.ref('bes.action_attendance_sheet_online_ccmc').report_action(self)
        elif self.subject.name == "GSK" and self.exam_type == "online":
            return self.env.ref('bes.action_attendance_sheet_online_gp').report_action(self)
        elif self.subject.name == "MEK" and self.exam_type == "online":
            return self.env.ref('bes.action_attendance_sheet_online_gp').report_action(self)
            

    
    @api.depends('online_from_date', 'online_to_date')
    def _compute_num_days(self):
        for record in self:
            if record.online_from_date and record.online_to_date:
                delta = record.online_to_date - record.online_from_date
                record.no_days = delta.days + 1
            else:
                record.no_days = 0
    

    
    def open_marksheet_list(self):
        
        if self.subject.name == 'GSK':
            if self.exam_type == 'practical_oral':
                views = [(self.env.ref("bes.view_marksheet_gp_tree_gsk").id, 'tree'),  # Define tree view
                        (self.env.ref("bes.view_marksheet_gp_form_gsk").id, 'form')]
            elif self.exam_type == 'online':
                views = [(self.env.ref("bes.view_marksheet_gsk_tree_online").id, 'tree'),  # Define tree view
                        (self.env.ref("bes.view_marksheet_gp_form_gsk_online").id, 'form')]
                
        elif self.subject.name == 'MEK':
            if self.exam_type == 'practical_oral':
             views = [(self.env.ref("bes.view_marksheet_gp_tree_mek").id, 'tree'),  # Define tree view
                    (self.env.ref("bes.view_marksheet_gp_form_mek").id, 'form')]
            elif self.exam_type == 'online':
                views = [(self.env.ref("bes.view_marksheet_mek_tree_online").id, 'tree'),  # Define tree view
                      (self.env.ref("bes.view_marksheet_gp_form_mek_online").id, 'form')]
        
        elif self.subject.name == 'CCMC':
            if self.exam_type == 'practical_oral':
                views = [(self.env.ref("bes.view_marksheet_ccmc_tree_oral").id, 'tree'),  # Define tree view
                        (self.env.ref("bes.view_marksheet_ccmc_form_oral").id, 'form')]
            elif self.exam_type == 'online':
                views = [(self.env.ref("bes.view_marksheet_ccmc_tree_gsk_online").id, 'tree'),  # Define tree view
                        (self.env.ref("bes.view_marksheet_ccmc_form_gsk_online").id, 'form')]

        
        elif self.subject.name == 'CCMC GSK Oral':
            if self.exam_type == 'practical_oral':

                 views = [(self.env.ref("bes.view_marksheet_ccmc_tree_gsk_oral_new").id, 'tree'),  # Define tree view
                        (self.env.ref("bes.view_marksheet_ccmc_form_gsk_oral_new").id, 'form')]
            
        
        
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
    _inherit = ['mail.thread','mail.activity.mixin']
    examiners_id = fields.Many2one("exam.type.oral.practical.examiners",string="Examiners ID",tracking=True)
    gp_candidate = fields.Many2one("gp.candidate",string="GP Candidate",tracking=True)
    gp_marksheet = fields.Many2one("gp.exam.schedule",string="GP Marksheet",tracking=True)
    ccmc_marksheet = fields.Many2one("ccmc.exam.schedule",string="CCMC Marksheet",tracking=True)
    ccmc_candidate = fields.Many2one("ccmc.candidate",string="CCMC Candidate",tracking=True)
    mek_oral = fields.Many2one("gp.mek.oral.line","MEK Oral",tracking=True)
    mek_prac = fields.Many2one("gp.mek.practical.line","MEK Practical",tracking=True)
    gsk_oral = fields.Many2one("gp.gsk.oral.line","GSK Oral",tracking=True)
    gsk_prac = fields.Many2one("gp.gsk.practical.line","GSK Practical",tracking=True)
    
    cookery_bakery = fields.Many2one("ccmc.cookery.bakery.line","Cookery And Bakery",tracking=True)
    ccmc_oral = fields.Many2one("ccmc.oral.line","CCMC Oral",tracking=True)
    ccmc_gsk_oral = fields.Many2one("ccmc.gsk.oral.line","CCMC GSK Oral",tracking=True)
    ccmc_online = fields.Many2one("survey.user_input",string="CCMC Online",tracking=True)


    
    gsk_online = fields.Many2one("survey.user_input","GSK Online",tracking=True)
    mek_online = fields.Many2one("survey.user_input","MEK Online",tracking=True)
    

    
    
    
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
   

class ReissueApprovalWizard(models.TransientModel):
    _name = "certificate.reissue.approval.wizard"
    _inherit = ['mail.thread','mail.activity.mixin']
    
    
    
    marksheet_type = fields.Selection([
        ('gp', 'GP'),
        ('ccmc', 'CCMC')
    ], string='Marksheet Type',tracking=True)
    
    candidate_image_name = fields.Char("Candidate Image Name",tracking=True)
    candidate_image = fields.Binary(string='Candidate Image', attachment=True, help='Select an image',tracking=True)
    
    candidate_signature_name = fields.Char("Candidate Signature",tracking=True)
    candidate_signature = fields.Binary(string='Candidate Signature', attachment=True, help='Select an image',tracking=True)
    
    name = fields.Char("Full Name of Candidate as in INDOS",tracking=True)
    
    dob = fields.Date("DOB",help="Date of Birth", 
                      widget="date", 
                      date_format="%d-%b-%y",tracking=True)
    
    def edit_info(self):
        marksheet_id = self.env.context.get('marksheet_id')
        if self.marksheet_type == 'gp':
            marksheet = self.env['gp.exam.schedule'].search([('id','=',marksheet_id)])
            current_date = datetime.now().date()
            marksheet.gp_candidate.write({'candidate_image': self.candidate_image , 'candidate_signature': self.candidate_signature , 'name': self.name , 'dob' : self.dob  })
            marksheet.write({'reissued':True , 'reissued_date' : current_date , 'state': '3-certified'})  
        else:
            marksheet = self.env['ccmc.exam.schedule'].search([('id','=',marksheet_id)])
            current_date = datetime.now().date()
            marksheet.ccmc_candidate.write({'candidate_image': self.candidate_image , 'candidate_signature': self.candidate_signature , 'name': self.name , 'dob' : self.dob  })
            marksheet.write({'reissued':True , 'reissued_date' : current_date , 'state': '3-certified'}) 
                     

            


    
    
    
class GPExam(models.Model):
    _name = "gp.exam.schedule"
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = "exam_id"
    _description= 'Schedule'
    
    exam_id = fields.Char("Roll No",required=True, copy=False, readonly=True,tracking=True)

    registered_institute = fields.Many2one("bes.institute",string="Examination Center",tracking=True)
    
    dgs_batch = fields.Many2one("dgs.batches",string="DGS Batch",required=True,tracking=True)
    certificate_id = fields.Char(string="Certificate ID",tracking=True)
    gp_candidate = fields.Many2one("gp.candidate","GP Candidate",tracking=True)
    # roll_no = fields.Char(string="Roll No",required=True, copy=False, readonly=True,
    #                             default=lambda self: _('New')) 
    exam_region = fields.Many2one('exam.center',related='registered_institute.exam_center',string='Exam Region',store=True)

    
    institute_name = fields.Many2one("bes.institute","Institute Name",tracking=True)
    mek_oral = fields.Many2one("gp.mek.oral.line","MEK Oral",tracking=True)
    mek_prac = fields.Many2one("gp.mek.practical.line","MEK Practical",tracking=True)
    gsk_oral = fields.Many2one("gp.gsk.oral.line","GSK Oral",tracking=True)
    gsk_prac = fields.Many2one("gp.gsk.practical.line","GSK Practical",tracking=True)
    gsk_online = fields.Many2one("survey.user_input","GSK Online",tracking=True)
    mek_online = fields.Many2one("survey.user_input","MEK Online",tracking=True)
    attempt_number = fields.Integer("Attempt Number", default=1, copy=False,readonly=True,tracking=True)
    
    
    gsk_oral_marks = fields.Float("GSK Oral/Journal",readonly=True,tracking=True)
    mek_oral_marks = fields.Float("MEK Oral/Journal",readonly=True,tracking=True)
    gsk_practical_marks = fields.Float("GSK Practical",readonly=True,tracking=True)
    mek_practical_marks = fields.Float("MEK Practical",readonly=True,tracking=True)
    gsk_total = fields.Float("GSK Oral/Practical",readonly=True,tracking=True)
    gsk_percentage = fields.Float("GSK Oral/Practical Precentage",readonly=True,tracking=True)
    
    # mek_total = fields.Float("MEK Total",readonly=True,tracking=True)
    # mek_percentage = fields.Float("MEK Percentage",readonly=True,tracking=True)
    mek_online_marks = fields.Float("MEK Online",readonly=True, digits=(16,2),tracking=True)
    gsk_online_marks = fields.Float("GSK Online",readonly=True,digits=(16,2),tracking=True)
    mek_online_percentage = fields.Float("MEK Online (%)",readonly=True,digits=(16,2),tracking=True)
    gsk_online_percentage = fields.Float("GSK Online (%)",readonly=True,digits=(16,2),tracking=True)    
    mek_total = fields.Float("MEK Oral/Practical",readonly=True,tracking=True)
    mek_percentage = fields.Float("MEK Oral/Practical Percentage",readonly=True,tracking=True)
    overall_marks = fields.Float("Overall Marks",readonly=True,tracking=True)
    overall_percentage = fields.Float("Overall (%)",readonly=True,tracking=True)
    gsk_oral_prac_status = fields.Selection([
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='GSK Oral/Practical Status', default='pending',tracking=True)
    
    gsk_oral_prac_assignment = fields.Boolean('gsk_oral_prac_assignment')
    
    mek_oral_prac_status = fields.Selection([
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='MEK Oral/Practical Status', default='pending',tracking=True)
    
    mek_oral_prac_assignment = fields.Boolean('mek_oral_prac_assignment')
    
    mek_online_status = fields.Selection([
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='MEK Online Status', default='pending',tracking=True)
    
    mek_online_assignment = fields.Boolean('mek_online_assignment')
    
    gsk_online_status = fields.Selection([
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='GSK Online Status', default='pending',tracking=True)
    
    gsk_online_assignment = fields.Boolean('gsk_online_assignment')
    
    exam_criteria = fields.Selection([
        ('', ''),
        ('pending', 'Pending'),
        ('passed', 'Complied'),
    ], string='Exam Status' , compute="compute_certificate_criteria",tracking=True)
    
    certificate_criteria = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Complied'),
    ], string='Certificate Criteria',compute="compute_pending_certificate_criteria",tracking=True)

    
    # stcw_criteria = fields.Selection([
    #     ('', ''),
    #     ('pending', 'Pending'),
    #     ('passed', 'Complied'),
    # ], string='STCW Criteria' , compute="compute_certificate_criteria",tracking=True)
    
    # ship_visit_criteria = fields.Selection([
    #     ('', ''),
    #     ('pending', 'Pending'),
    #     ('passed', 'Complied'),
    # ], string='Ship Visit Criteria' , compute="compute_certificate_criteria",tracking=True)
    
    
    # attendance_criteria = fields.Selection([
    #     ('', ''),
    #     ('pending', 'Pending'),
    #     ('passed', 'Complied'),
    # ], string='Attendance Criteria' , compute="compute_certificate_criteria",tracking=True)

    stcw_criterias = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Complied'),
    ], string='STCW Criteria',store=True,related='gp_candidate.stcw_criteria')

    ship_visit_criteria = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Complied'),
    ], string='Ship Visit Criteria',store=True ,compute='_check_ship_visit_criteria')

    attendance_criteria = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Complied'),
    ], string='Attendance Criteria',store=True,compute="_check_attendance_criteria")
    
    state = fields.Selection([
        ('1-in_process', 'In Process'),
        ('2-done', 'Done'),
        ('3-certified', 'Certified'),
        ('4-pending', 'Pending'),
        ('5-pending_reissue_approval','Reissue Approval'),
        ('6-pending_reissue_approved','Approved')
        
    ], string='State', default='1-in_process',tracking=True)
    
    reissued = fields.Boolean("Reissued",tracking=True)
    reissued_date = fields.Date("Reissued Date",tracking=True)

    url = fields.Char("URL",compute="_compute_url",store=True,tracking=True)
    qr_code = fields.Binary(string="Admit Card QR Code", compute="_compute_url", store=True,tracking=True)
    certificate_qr_code = fields.Binary(string=" Certificate QR Code", compute="_compute_certificate_url",tracking=True)
    
    dgs_visible = fields.Boolean("DGS Visible",compute="compute_dgs_visible",tracking=True)
    
    gsk_oral_prac_carry_forward = fields.Boolean("GSK Oral/Prac Carry Forward",tracking=True)
    mek_oral_prac_carry_forward = fields.Boolean("MEK Oral/Prac Carry Forward",tracking=True)
    mek_online_carry_forward = fields.Boolean("MEK Online Carry Forward",tracking=True)
    gsk_online_carry_forward = fields.Boolean("GSK Online Carry Forward",tracking=True)

    exam_pass_date = fields.Date(string="Date of Examination Passed:",tracking=True)
    certificate_issue_date = fields.Date(string="Date of Issue of Certificate:",tracking=True)
    rank = fields.Char("Rank",compute='_compute_rank',tracking=True)
    
    institute_code = fields.Char(string="Institute Code", related='gp_candidate.institute_id.code', required=True,tracking=True)
    candidate_code = fields.Char(string="Candidate Code", related='gp_candidate.candidate_code', required=True,tracking=True)
    indos_no = fields.Char(string="INDoS No", related='gp_candidate.indos_no', required=True,tracking=True)
    user_state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], string='User Status', related='gp_candidate.user_state', required=True,tracking=True)

    institute_id = fields.Many2one("bes.institute",related='gp_candidate.institute_id',string="Institute",required=True,tracking=True)
    
    result_status = fields.Selection([
        ('absent','Absent'),
        ('pending','Pending'),
        ('failed','Failed'),
        ('passed','Passed'),
    ],string='Result',tracking=True,compute='_compute_result_status')

    gsk_oral_prac_attendance = fields.Selection([
        ('',''),
        ('absent','Absent'),
        ('present','Present'),
    ],string="GSK P&O",compute="_compute_attendance")

    gsk_online_attendance = fields.Selection([
        ('absent','Absent'),
        ('present','Present'),
    ],string="GSK Online")
    
    mek_oral_prac_attendance = fields.Selection([
        ('',''),
        ('absent','Absent'),
        ('present','Present'),
    ],string="MEK P&O",compute="_compute_attendance")
    
    mek_online_attendance = fields.Selection([
        ('absent','Absent'),
        ('present','Present'),
    ],string="MEK Online")

    candidate_image_status = fields.Selection([
        ('pending', 'Pending'),
        ('done', 'Done'),
    ],string="Candidate-Image",compute="_check_image",default="pending",store=True)
   
    candidate_signature_status = fields.Selection([
        ('pending', 'Pending'),
        ('done', 'Done'),
    ],string="Candidate-Sign",compute="_check_sign",default="pending",store=True)

    hold_admit_card = fields.Boolean("Hold Admit Card", default=False)
    hold_certificate = fields.Boolean("Hold Certificate", default=False)
    show_hold_admit_card = fields.Boolean("Hide Hold Admit Card button",compute='_compute_hide_button')

    @api.depends('gp_candidate.candidate_image')
    def _check_image(self):
        for record in self:
            
            
            # candidate_image
            if record.gp_candidate.candidate_image:
                
                
                record.candidate_image_status = 'done'
            else:
                record.candidate_image_status = 'pending'

    @api.depends('gp_candidate.candidate_signature')
    def _check_sign(self):
        for record in self:
            # candidate-sign
            if record.gp_candidate.candidate_signature:
                record.candidate_signature_status = 'done'
            else:
                record.candidate_signature_status = 'pending'

    # @api.depends('gp_candidate.stcw_certificate')
    # def _check_stcw_certificate(self):
    #      for record in self:
    #         # Retrieve all the STCW certificate records
    #         stcw_certificates = record.gp_candidate.stcw_certificate

    #         course_type_already  = [course.course_name for course in record.gp_candidate.stcw_certificate]

    #         # all_types_exist = all(course_type in course_type_already for course_type in all_course_types)
    #         all_types_exist = record.check_combination_exists(course_type_already)
            
    #         # Check if the candidate_cert_no is present for all the STCW certificates
    #         all_cert_nos_present = all(cert.candidate_cert_no for cert in stcw_certificates)

    #         # if all_types_exist and all_cert_nos_present:
            
    #         if all_types_exist:
    #             # import wdb; wdb.set_trace();
    #             record.stcw_criteria = 'passed'
    #         else:
    #             record.stcw_criteria = 'pending'
        
    
    @api.depends('gp_candidate.ship_visits')
    def _check_ship_visit_criteria(self):
        for record in self:
            # import wdb; wdb.set_trace();
            if len(record.gp_candidate.ship_visits) > 0:
                record.ship_visit_criteria = 'passed'
            else:
                record.ship_visit_criteria = 'pending'
    
    
    @api.depends('gp_candidate.attendance_compliance_1','gp_candidate.attendance_compliance_2')
    def _check_attendance_criteria(self):
       for record in self:
            if record.gp_candidate.attendance_compliance_1 == 'yes' or record.gp_candidate.attendance_compliance_2 == 'yes':
                record.attendance_criteria = 'passed'
            else:
                record.attendance_criteria = 'pending'

    @api.depends('mek_oral','mek_prac','gsk_oral','gsk_prac')
    def _compute_attendance(self):
        for record in self:
            # import wdb; wdb.set_trace();
            if record.gsk_oral.gsk_oral_remarks and record.gsk_prac.gsk_practical_remarks:
                if record.gsk_oral.gsk_oral_remarks.lower() == 'absent' and record.gsk_prac.gsk_practical_remarks.lower()  == 'absent':
                    record.gsk_oral_prac_attendance = 'absent'
                else:
                    record.gsk_oral_prac_attendance = 'present'
            else:
                record.gsk_oral_prac_attendance = ''
            
            if record.mek_oral.mek_oral_remarks and record.mek_prac.mek_practical_remarks:
                if record.mek_oral.mek_oral_remarks.lower() == 'absent' and record.mek_prac.mek_practical_remarks.lower()  == 'absent':
                    record.mek_oral_prac_attendance = 'absent'
                else:
                    record.mek_oral_prac_attendance = 'present'
            else:
                record.mek_oral_prac_attendance = ''
            


            



    @api.depends('certificate_criteria')
    def _compute_result_status(self):
        for record in self:
            print(record.state)
            if record.state == '3-certified':
                record.result_status = 'passed'
            elif record.state in ['1-in_process','2-done']:
                record.result_status = 'pending'
            elif record.state == '4-pending':
                 record.result_status = 'failed'
            elif record.state == '5-pending_reissue_approval':
                record.result_status = 'pending'
            elif record.state == '6-pending_reissue_approved':
                record.result_status = 'pending'
                



    def reissue_approval(self):
        self.state = '5-pending_reissue_approval'
    
    def HoldAdmitCard(self):
        self.sudo().write({
            'hold_admit_card':True,
        })

    def ReleaseAdmitCard(self):
        self.sudo().write({
            'hold_admit_card':False,
        })


    def _compute_hide_button(self):
        if self.state != '1-in_process':
            self.sudo().write({
            'show_hold_admit_card':True
        })
        else:
            self.sudo().write({
            'show_hold_admit_card':False
        })

    def HoldCertificate(self):
        self.sudo().write({
            'hold_certificate':True
        })

    def ReleaseCertificate(self):
        self.sudo().write({
            'hold_certificate':False
        })
    
    
    def reissue_approved(self):
        self.state = '6-pending_reissue_approved'
        
    
    
    
    def open_reissue_wizard(self):
        view_id = self.env.ref('bes.certificate_reissue_approval_wizard_form').id
        
        gp_candidate = self.gp_candidate
        
        
        return {
            'name': 'Reissue Approval',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'certificate.reissue.approval.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_marksheet_type' : 'gp',
                'marksheet_id': self.id ,
                'default_candidate_image': gp_candidate.candidate_image,
                'default_candidate_signature': gp_candidate.candidate_signature,
                'default_dob':gp_candidate.dob,
                'default_name':gp_candidate.name
                
            }
            
        }
        
        
    
    # def open_reissue_wizard(self):
    #     view_id = self.env.ref('bes.certificate_reissue_approval_wizard_form').id
        
    #     return {
    #         'name': 'Reissue Approval',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'view_id': view_id,
    #         'res_model': 'certificate.reissue.approval.wizard',
    #         'type': 'ir.actions.act_window',
    #         'target': 'new'
    #     }


    
    

    
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
    
    



    
    @api.depends('state')
    def compute_dgs_visible(self):
        for record in self:
            if record.state == '2-done':
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
        

    @api.depends('url')
    def _compute_url(self):
        for record in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            current_url = base_url + "verification/gpadmitcard/" + str(record.id)
            record.url = current_url
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
            record.qr_code = qr_image_base64
        
    
    def check_combination_exists(self,array):
        
        target_combinations = [['pst', 'efa', 'fpff', 'pssr', 'stsdsd'], ['bst', 'stsdsd']]
        
        for combination in target_combinations:
            if all(item in array for item in combination):
                return True
        
        return False
    
    
    
    @api.depends('gsk_online_status','mek_online_status','mek_oral_prac_status','gsk_oral_prac_status')
    def compute_certificate_criteria(self):
        for record in self:
            all_passed = all(field == 'passed' for field in [record.gsk_online_status, record.mek_online_status, record.mek_oral_prac_status , record.gsk_oral_prac_status])
            # all_course_types = ['pst', 'efa', 'fpff', 'pssr', 'stsdsd']
            course_type_already  = [course.course_name for course in record.gp_candidate.stcw_certificate]
            

            # all_types_exist = all(course_type in course_type_already for course_type in all_course_types)
            all_types_exist = self.check_combination_exists(course_type_already)
            print("Course Type already" + str(all_types_exist))

            
            if all_passed:
                # import wdb; wdb.set_trace();
                record.exam_criteria = 'passed'
            else:
                record.exam_criteria = 'pending'
                
            # if all_types_exist:
            #     # import wdb; wdb.set_trace();
            #     record.stcw_criterias = 'passed'
            # else:
            #     record.stcw_criterias = 'pending'
                
            if record.gp_candidate.attendance_compliance_1 == 'yes' or record.gp_candidate.attendance_compliance_2 == 'yes':
                record.attendance_criteria = 'passed'
            else:
                record.attendance_criteria = 'pending'
            
            if len(record.gp_candidate.ship_visits) > 0:
                
                record.ship_visit_criteria = 'passed'
                
            else:

                record.ship_visit_criteria = 'pending'
    
    @api.depends('exam_criteria','stcw_criterias','attendance_criteria','ship_visit_criteria')
    def compute_pending_certificate_criteria(self):
        for record in self:
            if record.exam_criteria == record.stcw_criterias == record.attendance_criteria == record.ship_visit_criteria == 'passed':
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
    
        
    def process_marks(self):
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
                    print("Exam_ID" + self.exam_id)
                    error_msg = _("MEK Oral Or Practical Not Confirmed for'%s'") % (self.gp_candidate.name)
                    raise ValidationError(error_msg)

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
                    error_msg = _("GSK Oral Or Practical Not Confirmed for'%s'") % (self.gp_candidate.name)
                    raise ValidationError(error_msg)
            
            if not (len(self.gsk_online) == 0):
                
                if gsk_online_done:
                
                    self.gsk_online_marks = self.gsk_online.scoring_total
                    self.gsk_online_percentage = (self.gsk_online_marks/75)*100
                    
                    if self.gsk_online_percentage >= 60 :
                        self.gsk_online_status = 'passed'
                    else:
                        self.gsk_online_status = 'failed'
                else:
                    error_msg = _("GSK Online Exam Not Done or Confirmed for'%s'") % (self.gp_candidate.name)
                    raise ValidationError(error_msg)
            
            else:
                # self.gsk_online_marks = self.gsk_online.scoring_total
                self.gsk_online_percentage = (self.gsk_online_marks/75)*100
                if self.gsk_online_percentage >= 60 :
                    self.gsk_online_status = 'passed'
                else:
                    self.gsk_online_status = 'failed'
            
            
            print("MEK ONline")
            print(not (len(self.mek_online) == 0))
            
            if not (len(self.mek_online) == 0):
                if mek_online_done:
                    
                    print("In MEK ONline done")
                    print(self.mek_online)
                     
                    self.mek_online_marks = self.mek_online.scoring_total
                    self.mek_online_percentage = (self.mek_online_marks/75)*100
                    
                    if self.mek_online_percentage >= 60 :
                        self.mek_online_status = 'passed'
                    else:
                        self.mek_online_status = 'failed'
                else:
                    error_msg = _("MEK Online Exam Not Done or Confirmed for'%s'") % (self.gp_candidate.name)
                    raise ValidationError(error_msg)
            else:
                self.mek_online_percentage = (self.mek_online_marks/75)*100
                if self.mek_online_percentage >= 60 :
                    self.mek_online_status = 'passed'
                else:
                    self.mek_online_status = 'failed'

          
                
                
                
            
            # print("Doing Nothing")
            overall_marks = self.gsk_total + self.mek_total + self.mek_online_marks + self.gsk_online_marks
            self.overall_marks = overall_marks
            self.overall_percentage = (overall_marks/500) * 100
            
        else:
            
        
        
            # if not (len(self.mek_oral) == 0 and len(self.mek_prac) == 0) or not (len(self.gsk_oral) == 0 and len(self.gsk_prac) == 0) or not (len(self.gsk_online) == 0) or not (len(self.mek_online) == 0)  :
            if mek_oral_draft_confirm and mek_practical_draft_confirm and gsk_oral_draft_confirm and gsk_practical_draft_confirm and gsk_online_done and mek_online_done:

            # if True:

            
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

                if self.gsk_online_percentage >= 60 :
                    self.gsk_online_status = 'passed'
                else:
                    self.gsk_online_status = 'failed'
                    
                
                if self.mek_online_percentage >= 60 :
                    self.mek_online_status = 'passed'
                else:
                    self.mek_online_status = 'failed'
                

                all_passed = all(field == 'passed' for field in [self.mek_oral_prac_status,
                                                                  self.gsk_oral_prac_status, self.gsk_online_status , self.mek_online_status , self.exam_criteria , self.stcw_criterias , self.ship_visit_criteria , self.attendance_criteria ])
                    
                    
            
            else:
                print("Exam_ID" + self.exam_id)
                raise ValidationError("Exam ID "+str(self.exam_id)+" Not All exam are Confirmed")




        
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
                    print("Exam_ID" + self.exam_id)
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
            
            else:
                # self.gsk_online_marks = self.gsk_online.scoring_total
                self.gsk_online_percentage = (self.gsk_online_marks/75)*100
                if self.gsk_online_percentage >= 60 :
                    self.gsk_online_status = 'passed'
                else:
                    self.gsk_online_status = 'failed'
            
            
            print("MEK ONline")
            print(not (len(self.mek_online) == 0))
            
            if not (len(self.mek_online) == 0):
                if mek_online_done:
                    
                    print("In MEK ONline done")
                    print(self.mek_online)
                     
                    self.mek_online_marks = self.mek_online.scoring_total
                    self.mek_online_percentage = (self.mek_online_marks/75)*100
                    
                    if self.mek_online_percentage >= 60 :
                        self.mek_online_status = 'passed'
                    else:
                        self.mek_online_status = 'failed'
                else:
                    raise ValidationError("MEK Online Exam Not Done or Confirmed")
            else:
                self.mek_online_percentage = (self.mek_online_marks/75)*100
                if self.mek_online_percentage >= 60 :
                    self.mek_online_status = 'passed'
                else:
                    self.mek_online_status = 'failed'

          
                
                
                
            
            # print("Doing Nothing")
            overall_marks = self.gsk_total + self.mek_total + self.mek_online_marks + self.gsk_online_marks
            self.overall_marks = overall_marks
            self.overall_percentage = (overall_marks/500) * 100
            
            self.state = '2-done'
        else:
            
        
        
            # if not (len(self.mek_oral) == 0 and len(self.mek_prac) == 0) or not (len(self.gsk_oral) == 0 and len(self.gsk_prac) == 0) or not (len(self.gsk_online) == 0) or not (len(self.mek_online) == 0)  :
            if mek_oral_draft_confirm and mek_practical_draft_confirm and gsk_oral_draft_confirm and gsk_practical_draft_confirm and gsk_online_done and mek_online_done:

            # if True:

            
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
                
                
                
                
                all_passed = all(field == 'passed' for field in [self.mek_oral_prac_status, self.gsk_oral_prac_status, self.gsk_online_status , self.mek_online_status , self.exam_criteria , self.stcw_criterias , self.ship_visit_criteria , self.attendance_criteria ])

                
                self.state = '2-done'
                    
                    
            
            else:
                print("Exam_ID" + self.exam_id)
                raise ValidationError("Exam ID "+str(self.exam_id)+" Not All exam are Confirmed")

    attempting_exam_list = fields.One2many("gp.exam.appear",'gp_exam_schedule_id',string="Attempting Exams Lists")
    


    def send_certificate_email(self):
        # Replace 'bes.report_gp_certificate' with the correct XML ID of the report template
        report_template = self.env.ref('bes.report_gp_certificate')
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
            'res_model': 'gp.exam.schedule',
        }

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
    _inherit = ['mail.thread','mail.activity.mixin']
    gp_exam_schedule_id = fields.Many2one('gp.exam.schedule',string="GP Exam ID",tracking=True)
    subject_name = fields.Char(string="Appearing Exam Lists",tracking=True)
    
    
    
    
    

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
    _inherit = ['mail.thread','mail.activity.mixin']
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
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'CCMC Schedule'
    
    dgs_batch = fields.Many2one("dgs.batches",string="DGS Batch",required=True,tracking=True)
    certificate_id = fields.Char(string="Certificate ID",tracking=True)
    institute_name = fields.Many2one("bes.institute","Institute Name",tracking=True)
    
    exam_region = fields.Many2one('exam.center',related='registered_institute.exam_center',string='Exam Center',store=True)

    exam_id = fields.Char(string="Roll No",required=True, copy=False, readonly=True,tracking=True)
    registered_institute = fields.Many2one("bes.institute",string="Examination Center",tracking=True)
    
    ccmc_candidate = fields.Many2one("ccmc.candidate","CCMC Candidate",tracking=True)
    candidate_code = fields.Char(string="Candidate Code", related='ccmc_candidate.candidate_code', required=True,tracking=True)
    institute_id = fields.Many2one("bes.institute",related='ccmc_candidate.institute_id',string="Institute",required=True,tracking=True)


    cookery_bakery = fields.Many2one("ccmc.cookery.bakery.line","Cookery And Bakery",tracking=True)
    ccmc_oral = fields.Many2one("ccmc.oral.line","CCMC Oral",tracking=True)
    
    ccmc_oral_prac_assignment = fields.Boolean('ccmc_oral_prac_assignment')
    
    
    ccmc_gsk_oral = fields.Many2one("ccmc.gsk.oral.line","CCMC GSK Oral",tracking=True)
    
    ccmc_gsk_oral_assignment = fields.Boolean('ccmc_gsk_oral_assignment')
    
    ccmc_online = fields.Many2one("survey.user_input",string="CCMC Online",tracking=True)
    
    ccmc_online_assignment = fields.Boolean('ccmc_online_assignment')

    attempt_number = fields.Integer("Attempt Number", default=1, copy=False,readonly=True,tracking=True)
    
    reissued = fields.Boolean("Reissued",tracking=True)
    reissued_date = fields.Date("Reissued Date",tracking=True)
    
    cookery_practical = fields.Float("Cookery Practical",readonly=True,tracking=True)
    cookery_bakery_percentage = fields.Float("Cookery And Bakery Precentage",readonly=True,tracking=True)
    cookery_gsk_online = fields.Float("Cookery/GSK Online",readonly=True,digits=(16,2),tracking=True)
    overall_marks = fields.Float("Overall Marks",readonly=True,tracking=True)
    overall_percentage = fields.Float("Overall Percentage",readonly=True,tracking=True)
    cookery_gsk_online_percentage = fields.Float("Cookery/GSK Online Percentage",readonly=True,tracking=True)
    cookery_bakery_prac_status = fields.Selection([
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='Cookery And Bakery',default="pending",tracking=True)
    
    
    cookery_bakery_prac_oral_status = fields.Selection([
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='Cookery And Bakery',tracking=True)
    
    
    cookery_oral = fields.Float("CCMC Oral/GSK",readonly=True,tracking=True)
    ccmc_oral_percentage = fields.Float("Cookery Oral Percentage",readonly=True,tracking=True)
    ccmc_gsk_oral_percentage = fields.Float("CCMC GSK Oral Percentage",readonly=True,tracking=True)
    ccmc_oral_prac_status = fields.Selection([
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='CCMC Oral Status',default="pending",tracking=True)
    
    oral_prac_status = fields.Selection([
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='Oral/Prac Status',store=True,compute="compute_oral_prac_status",tracking=True)
    
    attendance_criteria = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Passed'),
    ], string='Attendance Criteria' , compute="compute_certificate_criteria",tracking=True)

    
    
    exam_criteria = fields.Selection([
        ('', ''),
        ('pending', 'Pending'),
        ('passed', 'Passed'),
    ], string='Exam Status' , compute="compute_certificate_criteria",tracking=True)
    
    ccmc_online_status = fields.Selection([
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='CCMC Online Status',default="pending",tracking=True)
    
    
    
    stcw_criteria = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Passed'),
    ], string='STCW Criteria',compute="compute_certificate_criteria",tracking=True)

    ship_visit_criteria = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Passed'),
    ], string='Ship Visit Criteria',compute="compute_certificate_criteria",tracking=True)
    
    
    
    
    state = fields.Selection([
        ('1-in_process', 'In Process'),
        ('2-done', 'Done'),
        ('3-certified', 'Certified'),
        ('4-pending', 'Pending'),
        ('5-pending_reissue_approval','Reissue Approval'),
        ('6-pending_reissue_approved','Approved')
    ], string='State', default='1-in_process',tracking=True)
    
    certificate_criteria = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Complied'),
    ], string='Certificate Criteria',compute="compute_pending_certificate_criteria",tracking=True)
    
    user_state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], string='User Status', related='ccmc_candidate.ccmc_user_state', required=True,tracking=True)

    result_status = fields.Selection([
        ('absent','Absent'),
        ('pending','Pending'),
        ('failed','Failed'),
        ('passed','Passed'),
    ],string='Result',tracking=True,compute='_compute_result_status')

    
    url = fields.Char("URL",compute="_compute_url",tracking=True)
    qr_code = fields.Binary(string="QR Code", compute="_compute_url", store=True,tracking=True)
    certificate_qr_code = fields.Binary(string=" Certificate QR Code", compute="_compute_certificate_url",tracking=True)

    dgs_visible = fields.Boolean("DGS Visible",compute="compute_dgs_visible",tracking=True)
    
    exam_pass_date = fields.Date(string="Date of Examination Passed:",tracking=True)
    certificate_issue_date = fields.Date(string="Date of Issue of Certificate:",tracking=True)
    ccmc_rank = fields.Char("Rank",compute='_compute_rank',tracking=True)
   
    institute_code = fields.Char("Institute code",related='ccmc_candidate.institute_id.code',tracking=True)
    indos_no = fields.Char(string="INDoS No", related='ccmc_candidate.indos_no', required=True,tracking=True)
    
    cookery_prac_carry_forward = fields.Boolean("Cookery Practical Carry Forward",tracking=True)
    cookery_oral_carry_forward = fields.Boolean("Cookery Oral Carry Forward",tracking=True)
    cookery_gsk_online_carry_forward = fields.Boolean("Cookery/GSK Online Carry Forward",tracking=True)

    candidate_image_status = fields.Selection([
        ('pending', 'Pending'),
        ('done', 'Done'),
    ],string="Candidate-Image",compute="_check_image",default="pending",store=True)
   
    candidate_signature_status = fields.Selection([
        ('pending', 'Pending'),
        ('done', 'Done'),
    ],string="Candidate-Sign",compute="_check_sign",default="pending",store=True)

    @api.depends('ccmc_candidate.candidate_image')
    def _check_image(self):
        for record in self:
            
            
            # candidate_image
            if record.ccmc_candidate.candidate_image:
                
                
                record.candidate_image_status = 'done'
            else:
                record.candidate_image_status = 'pending'

    @api.depends('ccmc_candidate.candidate_signature')
    def _check_sign(self):
        for record in self:
            # candidate-sign
            if record.ccmc_candidate.candidate_signature:
                record.candidate_signature_status = 'done'
            else:
                record.candidate_signature_status = 'pending'
    
    def reissue_approval(self):
        self.state = '5-pending_reissue_approval'
    
    def reissue_approved(self):
        self.state = '6-pending_reissue_approved'
        
    @api.depends('certificate_criteria')
    def _compute_result_status(self):
        for record in self:
            if record.state == '3-certified':
                record.result_status = 'passed'
            elif record.state in ['1-in_process','2-done']:
                record.result_status = 'pending'
            elif record.state == '4-pending':
                 record.result_status = 'failed'
    
    
    def open_reissue_wizard(self):
        view_id = self.env.ref('bes.certificate_reissue_approval_wizard_form').id
        
        ccmc_candidate = self.ccmc_candidate
        
        
        return {
            'name': 'Reissue Approval',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'certificate.reissue.approval.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_marksheet_type' : 'ccmc',
                'marksheet_id': self.id ,
                'default_candidate_image': ccmc_candidate.candidate_image,
                'default_candidate_signature': ccmc_candidate.candidate_signature,
                'default_dob':ccmc_candidate.dob,
                'default_name':ccmc_candidate.name
                
            }
            
        }
    
    
    
    
    @api.depends('ccmc_oral_prac_status','cookery_bakery_prac_status')
    def compute_oral_prac_status(self):
        for record in self:
            # import wdb; wdb.set_trace()
            if record.cookery_bakery_prac_status == 'pending' and record.ccmc_oral_prac_status == 'pending':
                record.oral_prac_status = 'pending'
            elif record.cookery_bakery_prac_status == 'failed' or record.ccmc_oral_prac_status == 'failed':
                record.oral_prac_status = 'failed'
            else:
                record.oral_prac_status = 'passed'
                
            
            
        
    
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
        # import wdb;wdb.set_trace()
        for record in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            print("Base URL:", base_url)
            current_url = base_url + "verification/ccmcadmitcard/" + str(record.id)
            record.url = current_url
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
            record.qr_code = qr_image_base64

    
    @api.depends('stcw_criteria','ship_visit_criteria','cookery_bakery_prac_status','ccmc_online_status')
    def compute_certificate_criteria(self):
        for record in self:
            
            all_passed = all(field == 'passed' for field in [record.cookery_bakery_prac_status , record.ccmc_online_status, record.ccmc_oral_prac_status])
            # all_course_types = ['pst', 'efa', 'fpff', 'pssr', 'stsdsd']
            course_type_already  = [course.course_name for course in record.ccmc_candidate.stcw_certificate]
            # all_types_exist = all(course_type in course_type_already for course_type in all_course_types)
            all_types_exist = self.env['gp.exam.schedule'].check_combination_exists(course_type_already)
            print("CCMC "+str(all_types_exist))
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

        
    def processMarks(self):
         # import wdb; wdb.set_trace(); 
        cookery_draft_confirm = self.cookery_bakery.cookery_draft_confirm == 'confirm'
        ccmc_oral_state = self.ccmc_oral.ccmc_oral_draft_confirm == 'confirm'
        ccmc_gsk_oral_state = self.ccmc_gsk_oral.ccmc_oral_draft_confirm == 'confirm'
        ccmc_online_state = self.ccmc_online.state == 'done'
        ccmc_gsk_marks =  self.ccmc_gsk_oral.toal_ccmc_oral_rating
        
        
        if not (len(self.cookery_bakery)==0 and len(self.ccmc_oral)==0 and len(self.ccmc_gsk_oral) == 0) or not (len(self.ccmc_online)==0):
            
             if not (len(self.cookery_bakery)==0 and len(self.ccmc_oral)==0 and len(self.ccmc_gsk_oral) == 0 ):
                 
                 if cookery_draft_confirm and ccmc_oral_state and ccmc_gsk_oral_state:
                     cookery_bakery_marks = self.cookery_bakery.total_mrks
                     ccmc_oral_marks = self.ccmc_oral.toal_ccmc_rating 
                     self.cookery_oral = ccmc_oral_marks
                     self.cookery_practical = cookery_bakery_marks
                 else:
                    error_msg = _("CCMC Oral Or Practical Not Confirmed for'%s'") % (self.ccmc_candidate.name)
                    raise ValidationError(error_msg)
                
             if not (len(self.ccmc_online)==0):
                 if ccmc_online_state:
                    cookery_gsk_online = self.ccmc_online.scoring_total
                    self.cookery_gsk_online = cookery_gsk_online
                 else:
                    error_msg = _("CCMC Online Not Confirmed for'%s'") % (self.ccmc_candidate.name)
                    raise ValidationError(error_msg)
            
             self.overall_marks = self.cookery_practical + self.cookery_oral + self.cookery_gsk_online
            
             #Percentage Calculation
            #  import wdb; wdb.set_trace(); 
             self.cookery_bakery_percentage = (self.cookery_practical/100) * 100
             self.ccmc_oral_percentage = (self.cookery_oral/100) * 100
             self.ccmc_gsk_oral_percentage = (ccmc_gsk_marks/20) * 100
             
             self.cookery_gsk_online_percentage = (self.cookery_gsk_online/100) * 100
             self.overall_percentage = (self.overall_marks/300)*100
             
             
             if self.cookery_bakery_percentage >= 60:
                    self.cookery_bakery_prac_status = 'passed'
             else:
                    self.cookery_bakery_prac_status = 'failed'
                    
             if self.ccmc_oral_percentage >= 60 and self.ccmc_gsk_oral_percentage >= 60:
                self.ccmc_oral_prac_status = 'passed'
             else:
                self.ccmc_oral_prac_status = 'failed'
                
                
             if self.cookery_gsk_online_percentage  >= 60:
                self.ccmc_online_status = 'passed'
             else:
                self.ccmc_online_status = 'failed'
                    
             all_passed = all(field == 'passed' for field in [self.ccmc_oral_prac_status,self.cookery_bakery_prac_status,self.ccmc_online_status, self.exam_criteria , self.stcw_criteria , self.ship_visit_criteria , self.attendance_criteria ])

             if all_passed:
                self.write({'certificate_criteria':'passed'})
             else:
                self.write({'certificate_criteria':'pending'})

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
                    
                
            else:
                raise ValidationError("Not All exam are Confirmed")
    
    
    def move_done(self):
        
        # import wdb; wdb.set_trace(); 
        cookery_draft_confirm = self.cookery_bakery.cookery_draft_confirm == 'confirm'
        ccmc_oral_state = self.ccmc_oral.ccmc_oral_draft_confirm == 'confirm'
        ccmc_online_state = self.ccmc_online.state == 'done'
        
        
        if not (len(self.cookery_bakery)==0 and len(self.ccmc_oral)==0 and len(self.ccmc_gsk_oral) == 0) or not (len(self.ccmc_online)==0):
            
             if not (len(self.cookery_bakery)==0 and len(self.ccmc_oral)==0 and len(self.ccmc_gsk_oral) == 0 ):
                 
                 if cookery_draft_confirm and ccmc_oral_state:
                     cookery_bakery_marks = self.cookery_bakery.total_mrks
                     ccmc_oral_marks = self.ccmc_oral.toal_ccmc_rating
                     self.cookery_oral = ccmc_oral_marks
                     self.cookery_practical = cookery_bakery_marks
                 else:
                    raise ValidationError("CCMC Oral Or Practical Not Confirmed")
                
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
             
             
             if self.cookery_bakery_percentage >= 60:
                    self.cookery_bakery_prac_status = 'passed'
             else:
                    self.cookery_bakery_prac_status = 'failed'
                    
             if self.ccmc_oral_percentage >= 60:
                self.ccmc_oral_prac_status = 'passed'
             else:
                self.ccmc_oral_prac_status = 'failed'
                
                
             if self.cookery_gsk_online_percentage  >= 60:
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
    _inherit = ['mail.thread','mail.activity.mixin']
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

    
        
        
        