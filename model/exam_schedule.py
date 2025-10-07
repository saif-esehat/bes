
from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
import random
import logging
import qrcode
import io
import base64
from datetime import datetime , date, timedelta
import math
from odoo.http import content_disposition, request , Response
from odoo.tools import date_utils
import xlsxwriter
import random
from pytz import timezone, UTC
import requests





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
    institute_id = fields.Many2one("bes.institute",string="Institute",related='exam_duty.institute_id',tracking=True)
    course = fields.Many2one("course.master",related='exam_duty.course',string="Course",tracking=True)
    exam_region = fields.Many2one('exam.center', 'Exam Region',tracking=True)
    
    ccmc_prac_oral_candidates = fields.Integer('No. of Candidates In CCMC Cookery Bakery', compute="_compute_ccmc_prac_oral_candidates",tracking=True)
    ccmc_gsk_oral_candidates = fields.Integer('No. of Candidates In CCMC Oral / GSK Oral', compute="_compute_ccmc_gsk_oral_candidates",tracking=True)
    ccmc_online_candidates = fields.Integer('No. of Candidates In CCMC GSK Online', compute="_compute_ccmc_online_candidates",tracking=True)
    
    
    no_of_days =  fields.Integer('No. of Days For Exam ',tracking=True)
    examiner_required_ccmc_prac_oral = fields.Integer("Examiner Required For CCMC Prac/Oral Per Day",compute="_compute_examiners_ccmc_prac_oral",tracking=True)
    examiner_required_ccmc_gsk_oral = fields.Integer("Examiner Required For CCMC GSK Oral Per Day",compute="_compute_examiners_ccmc_gsk_prac_oral",tracking=True)
    
    examiner_lines_ids = fields.One2many('ccmc.examiner.assignment.wizard.line', 'parent_id', string='Examiners',tracking=True)
    
    
    def update_marksheet(self):
            records = self.examiner_lines_ids
            
            candidate_with_ccmc_oral_prac = self.env['ccmc.exam.schedule'].sudo().search([
                ('dgs_batch','=',self.exam_duty.dgs_batch.id),
                ('registered_institute','=',self.institute_id.id),
                ('state','=','1-in_process'),
                ('attempting_cookery','=',True),
                ('hold_admit_card','=',False),
                ('ccmc_oral_prac_assignment','=',False),
                    '|',
                ('ceo_override', '=', True),
                '&', '&',  # Explicitly combine three criteria with nested AND
                ('stcw_criteria', '=', 'passed'),
                ('ship_visit_criteria', '=', 'passed'),
                ('attendance_criteria', '=', 'passed'),
                ]).ids
            
            candidate_with_ccmc_gsk_oral = self.env['ccmc.exam.schedule'].sudo().search([
                ('dgs_batch','=',self.exam_duty.dgs_batch.id),
                ('registered_institute','=',self.institute_id.id),
                ('state','=','1-in_process'),
                ('attempting_oral','=',True),
                ('hold_admit_card','=',False),
                ('ccmc_gsk_oral_assignment','=',False),
                    '|',
                ('ceo_override', '=', True),
                '&', '&',  # Explicitly combine three criteria with nested AND
                ('stcw_criteria', '=', 'passed'),
                ('ship_visit_criteria', '=', 'passed'),
                ('attendance_criteria', '=', 'passed')
                ]).ids
            
            candidate_with_ccmc_online = self.env['ccmc.exam.schedule'].sudo().search([
                ('dgs_batch','=',self.exam_duty.dgs_batch.id),
                ('registered_institute','=',self.institute_id.id),
                ('state','=','1-in_process'),
                ('attempting_online','=',True),
                ('hold_admit_card','=',False),
                ('ccmc_online_assignment','=',False),
                    '|',
                ('ceo_override', '=', True),
                '&', '&',  # Explicitly combine three criteria with nested AND
                ('stcw_criteria', '=', 'passed'),
                ('ship_visit_criteria', '=', 'passed'),
                ('attendance_criteria', '=', 'passed')
                ]).ids

        
            examiners_ccmc_prac_oral = records.filtered(lambda r: r.subject.name == 'CCMC' and r.exam_type == 'practical_oral_cookery_bakery').ids
            ccmc_prac_oral_assignments = {examiner: [] for examiner in examiners_ccmc_prac_oral}
            num_examiners_ccmc_prac_oral = len(examiners_ccmc_prac_oral)
            
            
            
            ###  CCMC Oral 80 Marks
            
            examiners_ccmc_gsk_oral = records.filtered(lambda r: r.subject.name == 'CCMC GSK Oral' or r.subject.name == 'CCMC'  and r.exam_type == 'ccmc_oral').ids
            if len(examiners_ccmc_gsk_oral) > 0:
                if len(records.filtered(lambda r: r.subject.name == 'CCMC GSK Oral' or r.subject.name == 'CCMC'  and r.exam_type == 'gsk_oral').ids) == 0:
                    raise ValidationError("CCMC GSK Oral Assignment Must Be Defined In Table")
                    
            ccmc_gsk_oral_assignments = {examiner: [] for examiner in examiners_ccmc_gsk_oral}
            num_examiners_ccmc_gsk_oral = len(examiners_ccmc_gsk_oral)
            
            
            ###  CCMC Oral 20 Marks
            
            examiners_ccmc_gsk_oral_new = records.filtered(lambda r: r.subject.name == 'CCMC GSK Oral' or r.subject.name == 'CCMC'  and r.exam_type == 'gsk_oral').ids
            ccmc_gsk_oral_new_assignments = {examiner: [] for examiner in examiners_ccmc_gsk_oral_new}
            num_examiners_ccmc_gsk_oral_new = len(examiners_ccmc_gsk_oral_new)

            
            
            
            
            
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
            
            
            #Distribute candidates with both CCMC  Oral
            for idx, candidate in enumerate(candidate_with_ccmc_gsk_oral):
                
                    try:
                        
                        #CCMC Oral 80 marks
                        ccmc_gsk_oral_examiner_index = idx % num_examiners_ccmc_gsk_oral
                        examiner_ccmc_gsk_oral = examiners_ccmc_gsk_oral[ccmc_gsk_oral_examiner_index]
                        ccmc_gsk_oral_assignments[examiner_ccmc_gsk_oral].append(candidate)
                        
                        #CCMC Oral 20 marks
                        ccmc_gsk_oral_new_examiner_index = idx % num_examiners_ccmc_gsk_oral_new
                        examiner_ccmc_gsk_oral_new = examiners_ccmc_gsk_oral_new[ccmc_gsk_oral_new_examiner_index]
                        ccmc_gsk_oral_new_assignments[examiner_ccmc_gsk_oral_new].append(candidate)
                        
                        
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
                
            print('ccmc_prac_oral_assignments')
            print(ccmc_prac_oral_assignments)
            print(ccmc_gsk_oral_assignments)

            ### CCMC Oral Prac ASSIGNMENTS    
            for examiner, assigned_candidates in ccmc_prac_oral_assignments.items():
                examiner_id = examiner
                assignment = records.filtered(lambda r: r.id == examiner_id)
                assignment.ccmc_marksheet_ids = assigned_candidates
                
                
            ### CCMC Oral ASSIGNMENTS    
            for examiner, assigned_candidates in ccmc_gsk_oral_assignments.items():
                examiner_id = examiner
                assignment = records.filtered(lambda r: r.id == examiner_id)
                assignment.ccmc_marksheet_ids = assigned_candidates
                
            ### CCMC GSK Oral ASSIGNMENTS    
            for examiner, assigned_candidates in ccmc_gsk_oral_new_assignments.items():
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
        
        if self.ccmc_prac_oral_candidates == 0 and self.ccmc_gsk_oral_candidates == 0 and self.ccmc_online_candidates == 0:
            raise ValidationError("No Candidates Available for Assignment")

        
        for record in records:
            if record.subject.name == 'CCMC':
                if record.exam_type == 'practical_oral_cookery_bakery': #Means Cookery Bakery
                    
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
                    confirm_context = True
                    assignment = self.env["exam.type.oral.practical.examiners"].with_context({"marksheet_ids":record.ccmc_marksheet_ids ,'confirm_context':confirm_context}).create({
                                                                                        'prac_oral_id':prac_oral_id,
                                                                                        'institute_id':institute_id,
                                                                                        'subject':subject,
                                                                                        'examiner':examiner,
                                                                                        'exam_date':exam_date,
                                                                                        'exam_type':exam_type      
                                                                                        })
                    
                    for marksheet in record.ccmc_marksheet_ids:
                        # import wdb;wdb.set_trace()
                        marksheet.write({ 'ccmc_oral_prac_assignment': True ,'ccmc_practical_assignment_id':assignment.id })
                        ccmc_marksheet = marksheet
                        cookery_bakery = marksheet.cookery_bakery
                        # ccmc_oral = marksheet.ccmc_oral
                        candidate = marksheet.ccmc_candidate.id
                        self.env['exam.type.oral.practical.examiners.marksheet'].sudo().create({ 'examiners_id':assignment.id ,
                                                                                                    'ccmc_marksheet':ccmc_marksheet.id ,
                                                                                                    'ccmc_candidate':candidate , 
                                                                                                    'cookery_bakery':cookery_bakery.id , 
                                                                                                    # 'ccmc_oral':ccmc_oral.id 
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
                        marksheet.write({'ccmc_online_assignment':True,'ccmc_online_assignment_id':assignment.id})
                        ccmc_marksheet = marksheet
                        candidate = marksheet.ccmc_candidate.id
                        ccmc_online = marksheet.ccmc_online
                        
                        self.env['exam.type.oral.practical.examiners.marksheet'].sudo().create({ 'examiners_id':assignment.id ,
                                                                                                    'ccmc_marksheet':ccmc_marksheet.id ,
                                                                                                    'ccmc_candidate':candidate , 
                                                                                                    'ccmc_online': ccmc_online.id})
                        
                        
            #CCMC ORAL 80 Marks                
            
            
            if record.subject.name == 'CCMC GSK Oral' or record.subject.name == 'CCMC':
                if record.exam_type == 'ccmc_oral':
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
                    confirm_context = True
                    assignment = self.env["exam.type.oral.practical.examiners"].with_context({"marksheet_ids":record.ccmc_marksheet_ids ,'confirm_context':confirm_context}).create({
                                                                                            'prac_oral_id':prac_oral_id,
                                                                                            'institute_id':institute_id,
                                                                                            'subject':subject,
                                                                                            'examiner':examiner,
                                                                                            'exam_date':exam_date,
                                                                                            'exam_type':exam_type      
                                                                                            })
                        
                    for marksheet in record.ccmc_marksheet_ids:
                            marksheet.write({'ccmc_gsk_oral_assignment':True ,'ccmc_oral_assignment_id':assignment.id })
                            ccmc_marksheet = marksheet
                            candidate = marksheet.ccmc_candidate.id
                            ccmc_oral = marksheet.ccmc_oral                            
                            self.env['exam.type.oral.practical.examiners.marksheet'].sudo().create({ 'examiners_id':assignment.id ,
                                                                                                        'ccmc_marksheet':ccmc_marksheet.id ,
                                                                                                        'ccmc_candidate':candidate , 
                                                                                                        'ccmc_oral': ccmc_oral.id 
                                                                                                        }) 
            
            #CCMC GSK ORAL 20 Marks                         
                            
            if record.subject.name == 'CCMC GSK Oral' or record.subject.name == 'CCMC':
                if record.exam_type == 'gsk_oral':
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
                    
                    assignment = self.env["exam.type.oral.practical.examiners"].with_context({"marksheet_ids":record.ccmc_marksheet_ids ,'confirm_context':confirm_context}).create({
                                                                                            'prac_oral_id':prac_oral_id,
                                                                                            'institute_id':institute_id,
                                                                                            'subject':subject,
                                                                                            'examiner':examiner,
                                                                                            'exam_date':exam_date,
                                                                                            'exam_type':exam_type      
                                                                                            })
                        
                    for marksheet in record.ccmc_marksheet_ids:
                            marksheet.write({'ccmc_gsk_oral_assignment':True,'ccmc_gsk_oral_assignment_id':assignment.id })
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
            record.ccmc_prac_oral_candidates = self.env['ccmc.exam.schedule'].sudo().search_count([
                ('dgs_batch','=',self.exam_duty.dgs_batch.id),
                ('registered_institute','=',self.institute_id.id),
                ('state','=','1-in_process'),
                ('attempting_cookery','=',True),
                ('hold_admit_card','=',False),
                ('ccmc_oral_prac_assignment','=',False),
                    '|',
                ('ceo_override', '=', True),
                '&', '&',  # Explicitly combine three criteria with nested AND
                ('stcw_criteria', '=', 'passed'),
                ('ship_visit_criteria', '=', 'passed'),
                ('attendance_criteria', '=', 'passed')
                ])
            
    
    @api.depends('institute_id')
    def _compute_ccmc_gsk_oral_candidates(self):
        for record in self:
            # import wdb;wdb.set_trace() ('mek_oral_prac_assignment','=',False),('gsk_oral_prac_assignment','=',False)
            record.ccmc_gsk_oral_candidates = self.env['ccmc.exam.schedule'].sudo().search_count([
                ('dgs_batch','=',self.exam_duty.dgs_batch.id),
                ('registered_institute','=',self.institute_id.id),
                ('state','=','1-in_process'),
                ('attempting_oral','=',True),
                ('hold_admit_card','=',False),
                ('ccmc_gsk_oral_assignment','=',False),
                    '|',
                ('ceo_override', '=', True),
                '&', '&',  # Explicitly combine three criteria with nested AND
                ('stcw_criteria', '=', 'passed'),
                ('ship_visit_criteria', '=', 'passed'),
                ('attendance_criteria', '=', 'passed')
                ])
    
    @api.depends('institute_id')
    def _compute_ccmc_online_candidates(self):
        for record in self:
            # import wdb;wdb.set_trace() ('mek_oral_prac_assignment','=',False),('gsk_oral_prac_assignment','=',False)
            record.ccmc_online_candidates = self.env['ccmc.exam.schedule'].sudo().search_count([
                ('dgs_batch','=',self.exam_duty.dgs_batch.id),
                ('registered_institute','=',self.institute_id.id),
                ('state','=','1-in_process'),
                ('attempting_online','=',True),
                ('hold_admit_card','=',False),
                ('ccmc_online_assignment','=',False),
                    '|',
                ('ceo_override', '=', True),
                '&', '&',  # Explicitly combine three criteria with nested AND
                ('stcw_criteria', '=', 'passed'),
                ('ship_visit_criteria', '=', 'passed'),
                ('attendance_criteria', '=', 'passed')
                ])


class CCMCExaminerAssignmentLineWizard(models.TransientModel):
    _name = 'ccmc.examiner.assignment.wizard.line'
    _inherit = ['mail.thread','mail.activity.mixin']
    
    parent_id = fields.Many2one("ccmc.examiner.assignment.wizard",string="Parent",tracking=True)
    
    exam_date = fields.Date('Exam Date',tracking=True)
    outstation =  fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')  
    ], string='OutStation')
    subject = fields.Many2one("course.master.subject",string="Subject",tracking=True)
    examiner = fields.Many2one('bes.examiner', string="Examiner",tracking=True)
    ccmc_marksheet_ids = fields.Many2many('ccmc.exam.schedule', string='Candidates',tracking=True)
    exam_type = fields.Selection([
        ('practical_oral_cookery_bakery', 'Practical (Cookery Bakery)'),
        ('ccmc_oral', 'CCMC Oral'),
        ('gsk_oral', 'CCMC(GSK Oral)'),
        ('online', 'Online')     
    ], string='Exam Type', default='practical_oral',tracking=True)
    
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
    institute_id = fields.Many2one("bes.institute",string="Institute",related='exam_duty.institute_id',required=True,tracking=True)
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
        

        candidate_with_gsk_mek = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',self.exam_duty.dgs_batch.id),('state','=','1-in_process'),('registered_institute','=',self.institute_id.id),('attempting_gsk_oral_prac','=',True),('hold_admit_card','=',False),('attempting_mek_oral_prac','=',True),('mek_oral_prac_assignment','=',False),('gsk_oral_prac_assignment','=',False),
                 '|',
                    ('ceo_override', '=', True),
                    '&', '&',  # Explicitly combine three criteria with nested AND
                    ('stcw_criterias', '=', 'passed'),
                    ('ship_visit_criteria', '=', 'passed'),
                    ('attendance_criteria', '=', 'passed')
            ]).ids
        candidate_with_gsk  = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',self.exam_duty.dgs_batch.id),('state','=','1-in_process'),('registered_institute','=',self.institute_id.id),('attempting_gsk_oral_prac','=',True),('hold_admit_card','=',False),('attempting_mek_oral_prac','=',False),('gsk_oral_prac_assignment','=',False),
                 '|',
                    ('ceo_override', '=', True),
                    '&', '&',  # Explicitly combine three criteria with nested AND
                    ('stcw_criterias', '=', 'passed'),
                    ('ship_visit_criteria', '=', 'passed'),
                    ('attendance_criteria', '=', 'passed')
            ]).ids
        candidate_with_mek = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',self.exam_duty.dgs_batch.id),('state','=','1-in_process'),('registered_institute','=',self.institute_id.id),('attempting_gsk_oral_prac','=',False),('hold_admit_card','=',False),('attempting_mek_oral_prac','=',True),('mek_oral_prac_assignment','=',False),
                '|',
                    ('ceo_override', '=', True),
                    '&', '&',  # Explicitly combine three criteria with nested AND
                    ('stcw_criterias', '=', 'passed'),
                    ('ship_visit_criteria', '=', 'passed'),
                    ('attendance_criteria', '=', 'passed')
            ]).ids
        candidate_with_gsk_mek_online = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',self.exam_duty.dgs_batch.id),('state','=','1-in_process'),('registered_institute','=',self.institute_id.id),('attempting_gsk_online','=',True),('attempting_mek_online','=',True),('hold_admit_card','=',False),('mek_online_assignment','=',False),('gsk_online_assignment','=',False),
                '|',
                    ('ceo_override', '=', True),
                    '&', '&',  # Explicitly combine three criteria with nested AND
                    ('stcw_criterias', '=', 'passed'),
                    ('ship_visit_criteria', '=', 'passed'),
                    ('attendance_criteria', '=', 'passed')
            ]).ids
        
        
        candidate_with_gsk_online  = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',self.exam_duty.dgs_batch.id),('state','=','1-in_process'),('registered_institute','=',self.institute_id.id),('attempting_gsk_online','=',True),('attempting_mek_online','=',False),('hold_admit_card','=',False),('gsk_online_assignment','=',False),
                    '|',
                    ('ceo_override', '=', True),
                    '&', '&',  # Explicitly combine three criteria with nested AND
                    ('stcw_criterias', '=', 'passed'),
                    ('ship_visit_criteria', '=', 'passed'),
                    ('attendance_criteria', '=', 'passed')
            ]).ids
        candidate_with_mek_online = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',self.exam_duty.dgs_batch.id),('state','=','1-in_process'),('registered_institute','=',self.institute_id.id),('attempting_gsk_online','=',False),('attempting_mek_online','=',True),('hold_admit_card','=',False),('mek_online_assignment','=',False),
                    '|',
                    ('ceo_override', '=', True),
                    '&', '&',  # Explicitly combine three criteria with nested AND
                    ('stcw_criterias', '=', 'passed'),
                    ('ship_visit_criteria', '=', 'passed'),
                    ('attendance_criteria', '=', 'passed')
            ]).ids


        
        
        
        print("candidate_with_gsk_mek")
        print(candidate_with_gsk_mek)
        print(candidate_with_mek)
        print("candidate_with_gsk_mek_online")
        print(candidate_with_gsk_mek_online)

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
        if candidate_with_gsk_mek:
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
        
                print("gsk_assignments")
                print(gsk_assignments)
                print("mek_assignments")
                print(gsk_assignments)
        
        # import wdb;wdb.set_trace();

        #Distribute candidates with both GSK and MEK Online
        if candidate_with_gsk_mek_online:
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
        if candidate_with_gsk:
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
        if candidate_with_gsk_online:
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
        if candidate_with_mek:
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
        if candidate_with_mek_online:
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
            print("examiner, gsk assigned_candidates")
            print(examiner, assigned_candidates)
            examiner_id = examiner
            assignment = records.filtered(lambda r: r.id == examiner_id)
            print("assignment")
            print(assignment)
            assignment.gp_marksheet_ids = assigned_candidates
            
        
         ### GSK Online ASSIGNMENTS    
        for examiner, assigned_candidates in online_gsk_assignments.items():
            print("examiner, online_gsk_assignments assigned_candidates")
            print(examiner, assigned_candidates)
            examiner_id = examiner
            assignment = records.filtered(lambda r: r.id == examiner_id)
            print("assignment")
            print(assignment)
            assignment.gp_marksheet_ids = assigned_candidates

        
        ### MEK ASSIGNMENTS    
        for examiner, assigned_candidates in mek_assignments.items():
            print("examiner, mek_assignments assigned_candidates")
            print(examiner, assigned_candidates)
            examiner_id = examiner
            assignment = records.filtered(lambda r: r.id == examiner_id)
            print("assignment")
            print(assignment)
            assignment.gp_marksheet_ids = assigned_candidates
            # assignment.gp_marksheet_ids = [16787, 16788]
            # assignment.write({'gp_marksheet_ids':[(4,16787)]})
        
        ### MeK Online ASSIGNMENTS    
        for examiner, assigned_candidates in online_mek_assignments.items():
            print("examiner, online_mek_assignments assigned_candidates")
            print(examiner, assigned_candidates)
            examiner_id = examiner
            assignment = records.filtered(lambda r: r.id == examiner_id)
            print("assignment")
            print(assignment)
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
        
        if (self.gsk_prac_oral_candidates == 0 and
            self.mek_prac_oral_candidates == 0 and
            self.gsk_online_candidates == 0 and
            self.mek_online_candidates == 0):
            raise ValidationError("No Candidates Available for Assignment")

        
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
                    confirm_context = True
                    assignment = self.env["exam.type.oral.practical.examiners"].with_context({"marksheet_ids":record.gp_marksheet_ids ,'confirm_context':confirm_context}).create({
                                                                                        'prac_oral_id':prac_oral_id,
                                                                                        'institute_id':institute_id,
                                                                                        'subject':subject,
                                                                                        'examiner':examiner,
                                                                                        'exam_date':exam_date,
                                                                                        'exam_type':exam_type      
                                                                                        })
                    
                    for marksheet in record.gp_marksheet_ids:
                        marksheet.write({'gsk_oral_prac_assignment':True,'gsk_oral_prac_assignment_id':assignment.id})
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
                    
                    assignment = self.env["exam.type.oral.practical.examiners"].with_context({"marksheet_ids":record.gp_marksheet_ids}).create({
                                                                                        'prac_oral_id':prac_oral_id,
                                                                                        'institute_id':institute_id,
                                                                                        'subject':subject,
                                                                                        'examiner':examiner,
                                                                                        'exam_date':exam_date,
                                                                                        'exam_type':exam_type      
                                                                                        })
                    
                    for marksheet in record.gp_marksheet_ids:
                        marksheet.write({'gsk_online_assignment':True, 'gsk_online_assignment_id':assignment.id})
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
                    confirm_context = True
                    assignment = self.env["exam.type.oral.practical.examiners"].with_context({"marksheet_ids":record.gp_marksheet_ids,'confirm_context':confirm_context}).create({
                                                                                        'prac_oral_id':prac_oral_id,
                                                                                        'institute_id':institute_id,
                                                                                        'subject':subject,
                                                                                        'examiner':examiner,
                                                                                        'exam_date':exam_date,
                                                                                        'exam_type':exam_type      
                                                                                        })
                    for marksheet in record.gp_marksheet_ids:
                        marksheet.write({'mek_oral_prac_assignment':True,'mek_oral_prac_assignment_id':assignment.id})
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
                    
                    assignment = self.env["exam.type.oral.practical.examiners"].with_context({"marksheet_ids":record.gp_marksheet_ids}).create({
                                                                                        'prac_oral_id':prac_oral_id,
                                                                                        'institute_id':institute_id,
                                                                                        'subject':subject,
                                                                                        'examiner':examiner,
                                                                                        'exam_date':exam_date,
                                                                                        'exam_type':exam_type      
                                                                                        })

                    for marksheet in record.gp_marksheet_ids:
                        marksheet.write({'mek_online_assignment':True, 'mek_online_assignment_id':assignment.id})
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
            # import wdb;wdb.set_trace() 
            # ('mek_oral_prac_assignment','=',False),('gsk_oral_prac_assignment','=',False)
            
            # record.gsk_prac_oral_candidates = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',record.exam_duty.dgs_batch.id),('registered_institute','=',record.institute_id.id),('state','=','1-in_process'),('attempting_gsk_oral_prac','=',True),('hold_admit_card','=',False),('gsk_oral_prac_assignment','=',False)                
            #     ,'|',
            #     ('ceo_override', '=', True),
            #     '&',
            #     ('stcw_criterias', '=', 'passed'),
            #     ('ship_visit_criteria', '=', 'passed'),
            #     ('attendance_criteria', '=', 'passed')])
            
            record.gsk_prac_oral_candidates = self.env['gp.exam.schedule'].sudo().search_count([
                    ('dgs_batch', '=', record.exam_duty.dgs_batch.id),
                    ('registered_institute', '=', record.institute_id.id),
                    ('state', '=', '1-in_process'),
                    ('attempting_gsk_oral_prac', '=', True),
                    ('hold_admit_card', '=', False),
                    ('gsk_oral_prac_assignment', '=', False),
                    '|',
                    ('ceo_override', '=', True),
                    '&', '&',  # Explicitly combine three criteria with nested AND
                    ('stcw_criterias', '=', 'passed'),
                    ('ship_visit_criteria', '=', 'passed'),
                    ('attendance_criteria', '=', 'passed'),
            ])

    @api.depends('institute_id')
    def _compute_mek_prac_oral_candidates(self):
        for record in self:
            # record.mek_prac_oral_candidates = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',record.exam_duty.dgs_batch.id),('registered_institute','=',record.institute_id.id),('state','=','1-in_process'),('attempting_mek_oral_prac','=',True),('hold_admit_card','=',False),('mek_oral_prac_assignment','=',False)                
            #     ,'|',
            #     ('ceo_override', '=', True),
            #     '&',
            #     ('stcw_criterias', '=', 'passed'),
            #     ('ship_visit_criteria', '=', 'passed'),
            #     ('attendance_criteria', '=', 'passed')])
            record.mek_prac_oral_candidates = self.env['gp.exam.schedule'].sudo().search_count([
                    ('dgs_batch', '=', record.exam_duty.dgs_batch.id),
                    ('registered_institute', '=', record.institute_id.id),
                    ('state', '=', '1-in_process'),
                    ('attempting_mek_oral_prac', '=', True),
                    ('hold_admit_card', '=', False),
                    ('mek_oral_prac_assignment', '=', False),
                    '|',
                    ('ceo_override', '=', True),
                    '&', '&',  # Explicitly combine three criteria with nested AND
                    ('stcw_criterias', '=', 'passed'),
                    ('ship_visit_criteria', '=', 'passed'),
                    ('attendance_criteria', '=', 'passed'),
            ])
    
    @api.depends('institute_id')
    def _compute_gsk_online_candidates(self):
        for record in self:
            # record.gsk_online_candidates = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',self.exam_duty.dgs_batch.id),('state','=','1-in_process'),('registered_institute','=',self.institute_id.id),('attempting_gsk_online','=',True),('hold_admit_card','=',False),('gsk_online_assignment','=',False)                
            #     ,'|',
            #     ('ceo_override', '=', True),
            #     '&',
            #     ('stcw_criterias', '=', 'passed'),
            #     ('ship_visit_criteria', '=', 'passed'),
            #     ('attendance_criteria', '=', 'passed')])
            
            record.gsk_online_candidates = self.env['gp.exam.schedule'].sudo().search_count([
                    ('dgs_batch', '=', record.exam_duty.dgs_batch.id),
                    ('registered_institute', '=', record.institute_id.id),
                    ('state', '=', '1-in_process'),
                    ('attempting_gsk_online', '=', True),
                    ('hold_admit_card', '=', False),
                    ('gsk_online_assignment', '=', False),
                    '|',
                    ('ceo_override', '=', True),
                    '&', '&',  # Explicitly combine three criteria with nested AND
                    ('stcw_criterias', '=', 'passed'),
                    ('ship_visit_criteria', '=', 'passed'),
                    ('attendance_criteria', '=', 'passed'),
            ])
    
    @api.depends('institute_id')
    def _compute_mek_online_candidates(self):
        for record in self:
            # record.mek_online_candidates = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',self.exam_duty.dgs_batch.id),('state','=','1-in_process'),('registered_institute','=',self.institute_id.id),('attempting_mek_online','=',True),('hold_admit_card','=',False),('mek_online_assignment','=',False)                
            #     ,'|',
            #     ('ceo_override', '=', True),
            #     '&',
            #     ('stcw_criterias', '=', 'passed'),
            #     ('ship_visit_criteria', '=', 'passed'),
            #     ('attendance_criteria', '=', 'passed')])
            
            record.mek_online_candidates = self.env['gp.exam.schedule'].sudo().search_count([
                    ('dgs_batch', '=', record.exam_duty.dgs_batch.id),
                    ('registered_institute', '=', record.institute_id.id),
                    ('state', '=', '1-in_process'),
                    ('attempting_mek_online', '=', True),
                    ('hold_admit_card', '=', False),
                    ('mek_online_assignment', '=', False),
                    '|',
                    ('ceo_override', '=', True),
                    '&', '&',  # Explicitly combine three criteria with nested AND
                    ('stcw_criterias', '=', 'passed'),
                    ('ship_visit_criteria', '=', 'passed'),
                    ('attendance_criteria', '=', 'passed'),
            ])
    
    #CCMC Course
    
    
    
    exam_region = fields.Many2one('exam.center', 'Exam Region')
    examiner_lines_ids = fields.One2many('examiner.assignment.wizard.line', 'parent_id', string='Examiners')
    
class ExaminerAssignmentLineWizard(models.TransientModel):
    _name = 'examiner.assignment.wizard.line'
    _inherit = ['mail.thread','mail.activity.mixin']
    
    parent_id = fields.Many2one("examiner.assignment.wizard",string="Parent",tracking=True)
    outstation =  fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')  
    ], string='OutStation')
    examiner_domain = fields.Char(compute='_compute_examiner_domain')
    
    @api.depends('subject','exam_type')
    def _compute_examiner_domain(self):
        for record in self:
            if record.subject and record.subject.name == 'GSK' and record.exam_type and record.exam_type == 'practical_oral':
                record.examiner_domain = [('designation', '=', 'master')]
            elif record.subject and record.subject.name == 'MEK' and record.exam_type and record.exam_type == 'practical_oral':
                record.examiner_domain = [('designation', '=', 'chief')]
            elif record.subject and record.subject.name == 'GSK' and record.exam_type and record.exam_type == 'online':
                record.examiner_domain = [('designation', 'in', ('chief', 'master','non_mariner','catering'))]
            elif record.subject and record.subject.name == 'MEK' and record.exam_type and record.exam_type == 'online':
                record.examiner_domain = [('designation', 'in', ('chief', 'master','non_mariner','catering'))]
            else:
                record.examiner_domain = []
    
    @api.onchange('subject','exam_type')
    def _onchange_subject(self):
        return {'domain': {'examiner': self.examiner_domain}}

    
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
    
    
    
class ExamOralPracticalNonMariner(models.Model):
    _name = 'exam.type.non.mariner'
    _inherit = ['mail.thread','mail.activity.mixin']

    
    prac_oral_id = fields.Many2one("exam.type.oral.practical",string="Exam Practical/Oral ID",store=True,required=False,tracking=True)
    institute = fields.Many2one("bes.institute",string="Institute",related='prac_oral_id.institute_id',store=True)
    non_mariner = fields.Many2one("bes.examiner",string="Non Mariner")
    account_details = fields.Char("Account Details")
    date = fields.Date("Exam Date")    

    

      
class ExamOralPractical(models.Model):
    _name = 'exam.type.oral.practical'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'institute_id'
    _description= 'Practical&Oral'

    # exam_schedule_id = fields.Many2one("bes.exam.schedule",string="Exam Schedule ID")
    # examiners = fields.Many2one('bes.examiner', string="Examiner")
    # subject = fields.Many2one("course.master.subject","Subject")
    
    institute_code = fields.Char(string="Institute Code", related='institute_id.code', required=True,tracking=True)
    dgs_batch = fields.Many2one("dgs.batches",string="Batch",required=True,tracking=True)
    team_lead = fields.Many2one("bes.examiner",string="Team Lead")
    institute_id = fields.Many2one("bes.institute",string="Institute",tracking=True)
    exam_region = fields.Many2one('exam.center', 'Exam Region',default=lambda self: self.get_examiner_region(),tracking=True)
    active = fields.Boolean(string="Active",default=True)

    def unlink(self):
        
        if len(self.examiners) > 0:
            raise ValidationError("Please Delete Examiner Assignment First")

        result = super(ExamOralPractical, self).unlink()
        return result


    
    
    def open_online_attendance(self):
        # Search for examiners who are assigned to the specific course, batch, and exam type
        examiners = self.env['exam.type.oral.practical.examiners'].search([
            ('institute_id', '=', self.institute_id.id),
            ('dgs_batch', '=', self.dgs_batch.id),
            ('exam_type', '=', 'online'),
            ('course', '=', self.course.id)
        ])

        # Create a list of examiner IDs to be used in the context
        examiner_ids = examiners.ids  # Get the IDs of the filtered examiners
        # import wdb;wdb.set_trace()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Online Attendance Sheet',
            'view_mode': 'form',
            'res_model': 'examiner.attendance.wizard',
            'target': 'new',
            'context': {
                'default_duty_id': self.id,  # Allow the user to select an examiner
                'default_examiner_assignment': examiner_ids,  # Pass the filtered examiner IDs to the context
                'default_course': self.course.id
            }
        }
    
    def open_assignment_wizard(self):
        
        if self.course.course_code == 'GP':
        
            view_id = self.env.ref('bes.examiner_assignment_wizard_form').id
            
            return {
                'name': 'Examiner Assignment',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'res_model': 'examiner.assignment.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {
                    'default_exam_duty': self.id,
                    'default_exam_region': self.exam_region.id,
                    'deafault_institute': self.institute_id.id,
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
                    'deafault_institute': self.institute_id.id,
                }
            }
    
    
    def get_examiner_region(self):
        user_id = self.env.user.id
        region = self.env['exam.center'].sudo().search([('exam_co_ordinator','=',user_id)]).id
        return region


    # start_time = fields.Datetime("Start Time")
    # end_time = fields.Datetime("End Time")
    examiners = fields.One2many("exam.type.oral.practical.examiners","prac_oral_id",string="Assign Examiners",tracking=True)

    non_mariners = fields.One2many("exam.type.non.mariner","prac_oral_id",string="Non Mariners",tracking=True)
    
    unique_examiners = fields.Many2many("bes.examiner",compute='compute_examiners') 
    
    @api.depends('examiners')
    def compute_examiners(self):
        for record in self:
            record.unique_examiners = self.examiners.examiner
    
    
    
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
    
    # def generate_overall_expense(self):
        
    def generate_timesheet(self):
        for assignment in self.examiners:
            self.assignment.time_sheet = timesheet.id 
            for examiner in assignment.examiner:
                timesheet = self.env["time.sheet.report"].sudo().create({
                    "dgs_batch": self.dgs_batch.id,
                    "examiner":examiner.id,
                    "institutes_id":self.institute_id.id
                })
        
        
    
    def generate_expense_sheet(self):
        # import wdb;wdb.set_trace()
        
        for examiner in self.examiners.examiner:
            
            
            
            
            expense = self.env["examiner.expenses"].sudo().search([('examiner_id','=',examiner.id),('dgs_batch','=',self.dgs_batch.id)])
            
            expense_batch = self.env["exam.batch.expenses"].sudo().search([('dgs_batch','=',self.dgs_batch.id)])
            
            # timesheet = self.env["time.sheet.report"].sudo().create({
            #     "dgs_batch": self.dgs_batch.id,
            #     "examiner":examiner.id,
            #     "institutes_id":self.institute_id.id
            # })
            
            if not expense_batch:
                expense_batch = self.env["exam.batch.expenses"].sudo().create({
                    "dgs_batch": self.dgs_batch.id
                })
                
            if not expense:
                expense = self.env["examiner.expenses"].sudo().create({
                    "expense_batch":expense_batch.id,
                    "examiner_id":examiner.id,
                    "dgs_batch": self.dgs_batch.id
                })
                        
            
            practical_assignments = self.examiners.filtered(lambda e: e.examiner.id == examiner.id and e.exam_type != 'online')
            for assignment in practical_assignments:
                # self.env["exam.assignment.expense"].sudo().search([('examiner_expenses_id','=',expense.id)]).unlink()
                # if assignment.candidates_count != assignment.candidate_done:
                #     examiner_name = assignment.examiner.name
                #     raise ValidationError(str(assignment.candidate_done) +"/"+str(assignment.candidates_count)+" Candidate Confirmed for "+examiner_name+" Exam Date : "+ str(assignment.exam_date)  )
                
                if examiner.designation in ['non-mariner','catering']:
                    price =  self.env['product.product'].search([('default_code','=','practical_oral_non_mariner')]).standard_price
                elif examiner.designation in ['master','chief']:
                    price =  self.env['product.product'].search([('default_code','=','practical_oral_mariner')]).standard_price
                
                self.env["exam.assignment.expense"].sudo().create({
                    "examiner_expenses_id":expense.id,
                    "price_per_unit":price,
                    "assignment": assignment.id
                 })
                
            time_sheets = self.examiners.filtered(lambda e: e.examiner.id == examiner.id and e.time_sheet)

            if time_sheets:
                for time_sheet in time_sheets:
                    timeshee = time_sheet.time_sheet
                    self.env["exam.misc.expense"].sudo().create({
                    "examiner_expenses_id":expense.id,
                    "assignment":time_sheet.id
                 })
                    

            
            outstations = self.examiners.filtered(lambda e: e.examiner.id == examiner.id and e.outstation == 'yes')
            
            
            if outstations:
                for outstation in outstations:
                    
                     if outstation.examiner.designation in ['non-mariner','catering']:
                        price =  self.env['product.product'].search([('default_code','=','outstation_non_mariner')]).standard_price
                     elif outstation.examiner.designation in ['master','chief']:
                        price =  self.env['product.product'].search([('default_code','=','outstation_mariner')]).standard_price
                        
                    
                     self.env['examiner.outstation.expense'].sudo().create({
                         "examiner_expenses_id":expense.id,
                         "dgs_batch" : self.dgs_batch.id,
                         "assignment": assignment.id,
                         "exam_date": outstation.exam_date,
                         "price": price
                     })
                    
                    
            
                
            online_assignments = self.examiners.filtered(lambda e: e.examiner.id == examiner.id and e.exam_type == 'online')
            
            
            if online_assignments:
                # self.env["exam.assignment.online.expense"].sudo().search([('examiner_expenses_id','=',expense.id)]).unlink()
                # GET Unique Exam Date
                exam_dates = sorted(set(online_assignments.mapped('exam_date')))
                
                if examiner.designation in ['non-mariner','catering']:
                    price =  self.env['product.product'].search([('default_code','=','online_non_mariner')]).standard_price
                elif examiner.designation in ['master','chief']:
                    price =  self.env['product.product'].search([('default_code','=','online_mariner')]).standard_price
                
                
                
                for date in exam_dates:
                    online_exams = self.examiners.filtered(lambda e: e.examiner.id == examiner.id and e.exam_type == 'online' and e.exam_date == date)
                    online_candidate_count = sum(online_exams.mapped('candidates_count'))
                    self.env["exam.assignment.online.expense"].sudo().create({
                            "examiner_expenses_id":expense.id,
                            "exam_date":date,
                            "assignments_onlines": online_exams.ids,
                            "candidate_count":online_candidate_count,
                            "price" : price
                        })
                            
            
                # examiners_team_lead = self.examiners.mapped('examiner')
                
            ## Team Lead Expense    
            if examiner.id == self.team_lead.id:
                price =  self.env['product.product'].search([('default_code','=','team_lead')]).standard_price
                self.env["institute.team.lead"].sudo().create({
                    "examiner_expenses_id":expense.id,
                    "examiner_duty":self.id,
                    "price": price,
                })
                
                
            
            
            # if expense.assignment_expense_ids:
            # Check if a record with the same expenses_type already exists
            practical_oral_found = self.env["examiner.overall.expenses"].sudo().search([
                ("examiner_expenses_id", "=", expense.id),
                ("expenses_type", "=", "practical_oral")
            ])

            # If no existing record is found, create a new one
            if not practical_oral_found:
                self.env["examiner.overall.expenses"].sudo().create({
                    "examiner_expenses_id": expense.id,
                    "expenses_type": "practical_oral"
                })
            

            # Check for 'online' expenses_type
            existing_online_record = self.env["examiner.overall.expenses"].sudo().search([
                ("examiner_expenses_id", "=", expense.id),
                ("expenses_type", "=", "online")
            ])

            if not existing_online_record:
                self.env["examiner.overall.expenses"].sudo().create({
                    "examiner_expenses_id": expense.id,
                    "expenses_type": "online"
                })

            # Check for 'team_lead' expenses_type
            existing_team_lead_record = self.env["examiner.overall.expenses"].sudo().search([
                ("examiner_expenses_id", "=", expense.id),
                ("expenses_type", "=", "team_lead")
            ])

            if not existing_team_lead_record:
                self.env["examiner.overall.expenses"].sudo().create({
                    "examiner_expenses_id": expense.id,
                    "expenses_type": "team_lead"
                })

            # Check for 'misc' expenses_type
            existing_outstation_record = self.env["examiner.overall.expenses"].sudo().search([
                ("examiner_expenses_id", "=", expense.id),
                ("expenses_type", "=", "outstation")
            ])

            if not existing_outstation_record:
                self.env["examiner.overall.expenses"].sudo().create({
                    "examiner_expenses_id": expense.id,
                    "expenses_type": "outstation"
                })

            existing_local_travel_record = self.env["examiner.overall.expenses"].sudo().search([
                ("examiner_expenses_id", "=", expense.id),
                ("expenses_type", "=", "local_travel")
            ])

            if not existing_local_travel_record:
                self.env["examiner.overall.expenses"].sudo().create({
                    "examiner_expenses_id": expense.id,
                    "expenses_type": "local_travel"
                })

            
                # total_online = sum(expense.online_assignment_expense.mapped('price'))

            # if expense.team_lead_expense:
            #     total_team_lead = sum(expense.team_lead_expense.mapped('price'))
            # total_misc = sum(expense.misc_expense_ids.mapped('price'))        

            
            # import wdb; wdb.set_trace(); 
            
            
                

            
            
            self.expense_sheet_status = "generated"    
            print("working")
        
        
        for nm in self.non_mariners:
            
            expense = self.env["examiner.expenses"].sudo().search([('examiner_id','=',nm.non_mariner.id),('dgs_batch','=',self.dgs_batch.id)])
            
            expense_batch = self.env["exam.batch.expenses"].sudo().search([('dgs_batch','=',self.dgs_batch.id)])
            
            if not expense_batch:
                expense_batch = self.env["exam.batch.expenses"].sudo().create({
                    "dgs_batch": self.dgs_batch.id
                })
                

            if not expense:
                expense = self.env["examiner.expenses"].sudo().create({
                    "expense_batch":expense_batch.id,
                    "examiner_id":nm.non_mariner.id,
                    "dgs_batch": self.dgs_batch.id
                })
            
            price =  self.env['product.product'].search([('default_code','=','online_non_mariner')]).standard_price
            
            self.env["examiner.expense.non.mariner"].sudo().create({
                    "examiner_expenses_id":expense.id,
                    "non_mariner_assignment":nm.id,
                    "exam_date":nm.date,
                    "dgs_batch": self.dgs_batch.id,
                    "price":price
                })
            
            
        # import wdb;wdb.set_trace();
        institute_expense = self.env["institute.exam.expenses"].search([('dgs_batch','=',self.dgs_batch.id),('institute','=',self.institute_id.id)])

        

        if not institute_expense:
            self.env["institute.exam.expenses"].sudo().create({
                'expense_batch': expense_batch.id,
                'dgs_batch':self.dgs_batch.id,
                'institute':self.institute_id.id    
                })
                
        
        
        
                
    
    # def generate_expense_sheet(self):
        # for assignment in self.examiners:
        #     assignment_id = assignment.id
        #     examiner_id = assignment.examiner.id
        #     subject_name = assignment.subject.name
        #     institute_id = assignment.institute_id.id
        #     user_id = assignment.examiner.user_id.id
        #     quantity = len(assignment.marksheets)
        #     employee = self.env['hr.employee'].search([('user_id','=',user_id)])
            
        #     designation = assignment.examiner
        #     exam_date = assignment.exam_date
        #     # import wdb; wdb.set_trace(); 
            
        #     if subject_name == 'GSK' and assignment.exam_type == 'practical_oral': 
            
        #         product =  self.env['product.product'].search([('default_code','=','gsk_exam')])
        #         child_records = self.env['hr.expense'].sudo().create([
        #                                 {'product_id': product.id, 'employee_id': employee.id,'name': subject_name+' Exam','unit_amount': product.standard_price ,'quantity': quantity }
        #                             ])
                
        #         expense_sheet = self.env['hr.expense.sheet'].sudo().create({'name': subject_name+' Exam',
        #                                                             'dgs_exam':True,
        #                                                             'dgs_batch': self.dgs_batch.id,
        #                                                             'institute_id':institute_id,
        #                                                             'employee_id':employee.id,
        #                                                             'expense_line_ids': [(6, 0, child_records.ids)]
        #                                                             })
                
        #         time_sheet = self.env['time.sheet.report'].sudo().create({
        #                                                                 'institutes_id':institute_id,
        #                                                                 'examiner':examiner_id,
        #                                                                 'expense_sheet':expense_sheet.id,
        #                                                                 'exam_date':exam_date
        #         })
        #         expense_sheet.write({'time_sheet': time_sheet.id})
            
        #         assignment.write({'expense_sheet':expense_sheet,'time_sheet':time_sheet})
            
        #     elif subject_name == 'MEK' and assignment.exam_type == 'practical_oral': 
                
        #         product =  self.env['product.product'].search([('default_code','=','mek_exam')])
        #         child_records = self.env['hr.expense'].sudo().create([
        #                                 {'product_id': product.id, 'employee_id': employee.id,'name': subject_name+' Exam','unit_amount': product.standard_price ,'quantity': quantity }
        #                             ])
                
        #         expense_sheet = self.env['hr.expense.sheet'].sudo().create({'name': subject_name+' Exam',
        #                                                             'dgs_exam':True,
        #                                                             'dgs_batch': self.dgs_batch.id,
        #                                                             'institute_id':institute_id,
        #                                                             'employee_id':employee.id,
        #                                                             'expense_line_ids': [(6, 0, child_records.ids)]
        #                                                             })
        #         time_sheet = self.env['time.sheet.report'].sudo().create({
        #                                                                 'institutes_id':institute_id,
        #                                                                 'examiner':examiner_id,
        #                                                                 'expense_sheet':expense_sheet.id,
        #                                                                 'exam_date':exam_date
        #         })

        #         expense_sheet.write({'time_sheet': time_sheet.id})
        #         assignment.write({'expense_sheet':expense_sheet,'time_sheet':time_sheet})
            
        #     elif subject_name == 'GSK' and assignment.exam_type == 'online': 
                
                
        
                    
                    
                
        #         product =  self.env['product.product'].search([('default_code','=','gsk_online_exam')])
                
        #         if designation == 'non-mariner':
        #             price = 2000
        #         else:
        #             price = product.standard_price
                
        #         child_records = self.env['hr.expense'].sudo().create([
        #                                 {'product_id': product.id, 'employee_id': employee.id,'name': subject_name+' Exam','unit_amount': price ,'quantity': 1 }
        #                             ])
                
        #         expense_sheet = self.env['hr.expense.sheet'].sudo().create({'name': subject_name+' Exam',
        #                                                             'dgs_exam':True,
        #                                                             'dgs_batch': self.dgs_batch.id,
        #                                                             'institute_id':institute_id,
        #                                                             'employee_id':employee.id,
        #                                                             'expense_line_ids': [(6, 0, child_records.ids)]
        #                                                             })
        #         time_sheet = self.env['time.sheet.report'].sudo().create({
        #                                                                 'institutes_id':institute_id,
        #                                                                 'examiner':examiner_id,
        #                                                                 'expense_sheet':expense_sheet.id,
        #                                                                 'exam_date':exam_date
        #         })

        #         expense_sheet.write({'time_sheet': time_sheet.id})
        #         assignment.write({'expense_sheet':expense_sheet,'time_sheet':time_sheet})
            
        #     elif subject_name == 'MEK' and assignment.exam_type == 'online': 
                
        #         product =  self.env['product.product'].search([('default_code','=','mek_online_exam')])
                
        #         if designation == 'non-mariner':
        #             price = 2000
        #         else:
        #             price = product.standard_price
                
                
        #         child_records = self.env['hr.expense'].sudo().create([
        #                                 {'product_id': product.id, 'employee_id': employee.id,'name': subject_name+' Exam','unit_amount': price ,'quantity': 1 }
        #                             ])
                
        #         expense_sheet = self.env['hr.expense.sheet'].sudo().create({'name': subject_name+' Exam',
        #                                                             'dgs_exam':True,
        #                                                             'dgs_batch': self.dgs_batch.id,
        #                                                             'institute_id':institute_id,
        #                                                             'employee_id':employee.id,
        #                                                             'expense_line_ids': [(6, 0, child_records.ids)]
        #                                                             })
        #         time_sheet = self.env['time.sheet.report'].sudo().create({
        #                                                                     'institutes_id':institute_id,
        #                                                                     'examiner':examiner_id,
        #                                                                     'expense_sheet':expense_sheet.id,
        #                                                                     'exam_date':exam_date
        #             })

        #         expense_sheet.write({'time_sheet': time_sheet.id})
        #         assignment.write({'expense_sheet':expense_sheet,'time_sheet':time_sheet})
            
        #     elif subject_name == 'CCMC' and assignment.exam_type == 'practical_oral': 
                
        #         product =  self.env['product.product'].search([('default_code','=','ccmc_exam')])
        #         child_records = self.env['hr.expense'].sudo().create([
        #                                 {'product_id': product.id, 'employee_id': employee.id,'name': subject_name+' Exam','unit_amount': product.standard_price ,'quantity': quantity }
        #                             ])
                
        #         expense_sheet = self.env['hr.expense.sheet'].sudo().create({'name': subject_name+' Exam',
        #                                                             'dgs_exam':True,
        #                                                             'dgs_batch': self.dgs_batch.id,
        #                                                             'institute_id':institute_id,
        #                                                             'employee_id':employee.id,
        #                                                             'expense_line_ids': [(6, 0, child_records.ids)]
        #                                                             })
            
        #         time_sheet = self.env['time.sheet.report'].sudo().create({
        #                                                                 'institutes_id':institute_id,
        #                                                                 'examiner':examiner_id,
        #                                                                 'expense_sheet':expense_sheet.id,
        #                                                                 'exam_date':exam_date
        #         })

        #         expense_sheet.write({'time_sheet': time_sheet.id})
        #         assignment.write({'expense_sheet':expense_sheet,'time_sheet':time_sheet})
                
        #     elif subject_name == 'CCMC' and assignment.exam_type == 'online': 
                
        #         product =  self.env['product.product'].search([('default_code','=','ccmc_online_exam')])
                
        #         if designation == 'non-mariner':
        #             price = 2000
        #         else:
        #             price = product.standard_price
                
                
        #         child_records = self.env['hr.expense'].sudo().create([
        #                                 {'product_id': product.id, 'employee_id': employee.id,'name': subject_name+' Exam','unit_amount': price ,'quantity': 1 }
        #                             ])
                
        #         expense_sheet = self.env['hr.expense.sheet'].sudo().create({'name': subject_name+' Exam',
        #                                                             'dgs_exam':True,
        #                                                             'dgs_batch': self.dgs_batch.id,
        #                                                             'institute_id':institute_id,
        #                                                             'employee_id':employee.id,
        #                                                             'expense_line_ids': [(6, 0, child_records.ids)]
        #                                                             })
            
        #         time_sheet = self.env['time.sheet.report'].sudo().create({
        #                                                                 'institutes_id':institute_id,
        #                                                                 'examiner':examiner_id,
        #                                                                 'expense_sheet':expense_sheet.id,
        #                                                                 'exam_date':exam_date
        #         })

        #         expense_sheet.write({'time_sheet': time_sheet.id})
        #         assignment.write({'expense_sheet':expense_sheet,'time_sheet':time_sheet})
            
        #     elif subject_name == 'CCMC GSK Oral' and assignment.exam_type == 'practical_oral': 
                
        #         product =  self.env['product.product'].search([('default_code','=','ccmc_gsk_exam')])
                
                
        #         child_records = self.env['hr.expense'].sudo().create([
        #                                 {'product_id': product.id, 'employee_id': employee.id,'name': subject_name+' Exam','unit_amount': price ,'quantity': 1 }
        #                             ])
                
        #         expense_sheet = self.env['hr.expense.sheet'].sudo().create({'name': subject_name+' Exam',
        #                                                             'dgs_exam':True,
        #                                                             'dgs_batch': self.dgs_batch.id,
        #                                                             'institute_id':institute_id,
        #                                                             'employee_id':employee.id,
        #                                                             'expense_line_ids': [(6, 0, child_records.ids)]
        #                                                             })
            
        #         time_sheet = self.env['time.sheet.report'].sudo().create({
        #                                                                 'institutes_id':institute_id,
        #                                                                 'examiner':examiner_id,
        #                                                                 'expense_sheet':expense_sheet.id,
        #                                                                 'exam_date':exam_date
        #         })

        #         expense_sheet.write({'time_sheet': time_sheet.id})
        #         assignment.write({'expense_sheet':expense_sheet,'time_sheet':time_sheet})
            
        # self.write({'expense_sheet_status':'generated'})
            
    
    
    
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
    _rec_name = 'display_name'
    _description= 'Examiners'

    dgs_batch = fields.Many2one("dgs.batches",related='prac_oral_id.dgs_batch',string="Exam Batch",store=True,required=False,tracking=True)
    exam_region = fields.Many2one('exam.center', 'Exam Center',related='prac_oral_id.exam_region',store=True,tracking=True)
    outstation =  fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')  
    ], string='OutStation',compute='_compute_outstation')
    
    prac_oral_id = fields.Many2one("exam.type.oral.practical",string="Exam Practical/Oral ID",store=True,required=False,tracking=True)
    institute_id = fields.Many2one("bes.institute",string="Institute",tracking=True)
    course = fields.Many2one("course.master",related='prac_oral_id.course',string="Course",tracking=True)
    subject = fields.Many2one("course.master.subject",string="Subject",store=True,tracking=True)
    examiner = fields.Many2one('bes.examiner', string="Examiner",tracking=True)
    exam_date = fields.Date("Exam Date",tracking=True)
    marksheets = fields.One2many('exam.type.oral.practical.examiners.marksheet','examiners_id',string="Candidates",tracking=True)
    ipaddr = fields.Char("IP Address",tracking=True)    
    candidates_count = fields.Integer("Candidates Assigned",compute='compute_candidates_count')
    exam_type = fields.Selection([
        ('practical_oral', 'Practical/Oral'),
        ('online', 'Online'),
        ('practical_oral_cookery_bakery', 'Practical (Cookery Bakery)'),
        ('ccmc_oral', 'CCMC Oral'),
        ('gsk_oral', 'CCMC(GSK Oral)'),    
    ], string='Exam Type', default='practical_oral',tracking=True)
    
    
    
    all_marksheet_confirmed = fields.Selection([
                    ('na', 'Online'),
                    ('pending', 'Pending'),
                    ('done', 'Completed')
                ], string='Marksheet Remaining Status', default='pending',compute='compute_marksheet_done',store=True)
    
    display_name = fields.Char(string='Name', compute='_compute_display_name', store=True)
    active = fields.Boolean(string="Active",default=True)
    commence_exam = fields.Boolean(string="Commence Exam",default=False)

    online_from_date = fields.Date("From")
    online_to_date = fields.Date("To Date")
    team_lead = fields.Boolean("TL")
    no_days = fields.Integer("No. of Days" , compute='_compute_num_days' )
    
    expense_sheet = fields.Many2one('hr.expense.sheet', string="Renumeration")
    time_sheet = fields.Many2one("time.sheet.report",string="Time sheet")
    
    status = fields.Selection([
        ('draft', 'Draft'), 
        ('confirmed', 'Confirmed')
    ], string='Status',default="draft" )
    
    extended = fields.Boolean("Extended")
    
    marksheet_image = fields.Binary(string="Marksheet Image",tracking=True)
    marksheet_image_name = fields.Char(string="Marksheet Image name",tracking=True)
    marksheet_uploaded = fields.Boolean(string="Marksheet Uploaded",tracking=True)
    attendance_sheet_uploaded = fields.Boolean(string="Attendance Sheet Uploaded",tracking=True)
    # attendance_sheet_file = fields.Binary(string="Attendance Sheet File",tracking=True)
    attendance_sheet_files = fields.Many2many('ir.attachment',string='Attendance Sheets',help='Upload multiple attendance sheets')
    attendance_sheet_name = fields.Char(string="Attendance Sheet File name",tracking=True)

    absent_candidates = fields.Char(string="Absent Candidates",compute='check_absent',store=True,tracking=True)
    candidate_done = fields.Char("Marks Confirmed" , compute='compute_candidates_done',store=True,tracking=True)
    # Add One2many field
    assignment_expense_ids = fields.One2many('exam.assignment.expense', 'assignment', string="Assignment Expenses")
    
    online_start_time = fields.Datetime("Start Time",store=True)
    online_end_time = fields.Datetime("End Time",store=True)

    with_context_check = fields.Boolean("With Context Check",default=False)


    def _compute_outstation(self):
        if self.institute_id.outstation:
            self.outstation = 'yes'
        else:
            self.outstation = 'no'


    def commence_online_exam(self):
        record = self.search([], limit=1)  # Fetch the first available record

        if not record:
            raise UserError("No records found to commence the exam.")  # Show an error if no records exist

        return {
            'name': 'Commence Online Exam',
            'type': 'ir.actions.act_window',
            'res_model': 'online.exam.wizard',
            'view_mode': 'form',
            'views': [(False, 'form')],  # Explicitly add "views" to fix the issue
            'target': 'new',
            'context': {
                'default_examiners_id': record.id,  # Pass first found record ID
            },
        }


    
    def end_online_exam(self):
        online_assignment = self.env['exam.type.oral.practical.examiners'].sudo().search([('id','=',self.id)])

        config_param = self.env['ir.config_parameter'].sudo().get_param('bes.server_type')
        
        for examiner in online_assignment:
            if config_param == 'production':  
                api_url = "http://178.18.255.245:5000/api/ip/remove"
                ip_list = [ip.strip() for ip in examiner.ipaddr.split(',') if ip.strip()]
            
                for ip in ip_list:
                    data = {
                        "ip": ip,
                        "location": "survey"
                    }
                    response = requests.post(api_url, json=data, timeout=5)
            examiner.commence_exam = False
            if examiner.course.course_code == 'GP':
                if examiner.subject.name == "GSK":
                    examiner.marksheets.gsk_online.write({'commence_online_exam':False})
                if examiner.subject.name == "MEK":
                    examiner.marksheets.mek_online.write({'commence_online_exam':False})
            elif examiner.course.course_code == 'CCMC':
                examiner.marksheets.ccmc_online.write({'commence_online_exam':False})
        # return {'type': 'ir.actions.act_window_close'}
            # Close the wizard and refresh the page
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'reload',
        # }
        

    
    @api.depends('examiner.name', 'subject.name', 'exam_date', 'dgs_batch.batch_name', 'institute_id.name')
    def _compute_display_name(self):
        for record in self:

            if record.exam_date:
                date = record.exam_date.strftime('%d-%m-%Y')
            else:
                date = False
            record.display_name = f"{record.examiner.name} - {record.institute_id.name} - {record.subject.name} - {date} - {record.dgs_batch.batch_name}"

    @api.depends('candidates_count','candidate_done')
    def compute_marksheet_done(self):
        for record in self:
            if record.candidate_done == 'NA':
                record.all_marksheet_confirmed = 'na'
            elif record.candidates_count == int(record.candidate_done):
                record.all_marksheet_confirmed = 'done'
            else:
                record.all_marksheet_confirmed = 'pending'
             
    
    
    @api.depends('marksheets')
    def compute_candidates_count(self):
        for record in self:
            record.candidates_count = len(record.marksheets)
    
    @api.depends('marksheets')
    def check_absent(self):
        for record in self:
            if record.subject.name == 'GSK':
                if record.exam_type == 'practical_oral':
                    abs_count = 0
                    for sheet in record.marksheets:
                        if sheet.gp_marksheet.gsk_oral_prac_attendance == 'absent':
                                abs_count += 1
                    record.absent_candidates = abs_count
                elif record.exam_type == 'online':
                    abs_count = 0
                    for sheet in record.marksheets:
                        if sheet.gp_marksheet.gsk_online_attendance == 'absent':
                                abs_count += 1
                    record.absent_candidates = abs_count
                    
            elif record.subject.name == 'MEK':
                if record.exam_type == 'practical_oral':
                    abs_count = 0
                    for sheet in record.marksheets:
                        if sheet.gp_marksheet.mek_oral_prac_attendance == 'absent':
                                abs_count += 1
                    record.absent_candidates = abs_count
                elif record.exam_type == 'online':
                    abs_count = 0
                    for sheet in record.marksheets:
                        if sheet.gp_marksheet.mek_online_attendance == 'absent':
                                abs_count += 1
                    record.absent_candidates = abs_count
                    
            
            elif record.subject.name == 'CCMC':
                if record.exam_type == 'practical_oral_cookery_bakery' :
                    abs_count = 0
                    for sheet in record.marksheets:
                        if sheet.ccmc_marksheet.cookery_prac_attendance == 'absent':
                                abs_count += 1
                    record.absent_candidates = abs_count
            
                elif record.exam_type == 'ccmc_oral':
                    abs_count = 0
                    for sheet in record.marksheets:
                        if sheet.ccmc_marksheet.ccmc_oral_attendance == 'absent':
                                abs_count += 1
                    record.absent_candidates = abs_count

                elif record.exam_type == 'online':
                    abs_count = 0
                    for sheet in record.marksheets:
                        if sheet.ccmc_marksheet.ccmc_online_attendance == 'absent':
                                abs_count += 1
                    record.absent_candidates = abs_count

            elif record.subject.name == 'CCMC GSK Oral':
                if record.exam_type == 'gsk_oral':
                    abs_count = 0
                    for sheet in record.marksheets:
                        if sheet.ccmc_marksheet.ccmc_gsk_oral_attendance == 'absent':
                                abs_count += 1
                    record.absent_candidates = abs_count

            else:
                record.absent_candidates = 'NA'


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
                elif record.exam_type == 'online':
                    count = 0
                    for sheet in record.marksheets:
                        if sheet.gp_marksheet.gsk_online_attendance:
                            count += 1
                    record.candidate_done = count
                    
            elif record.subject.name == 'MEK':
                if record.exam_type == 'practical_oral':
                    count = 0
                    for sheet in record.marksheets:
                        if sheet.mek_oral.mek_oral_draft_confirm == 'confirm' and sheet.mek_prac.mek_practical_draft_confirm == 'confirm':
                            count += 1
                    record.candidate_done = count
                elif record.exam_type == 'online':
                    count = 0
                    for sheet in record.marksheets:
                        if sheet.gp_marksheet.mek_online_attendance:
                            count += 1
                    record.candidate_done = count
            
            elif record.subject.name == 'CCMC':
                if record.exam_type == 'practical_oral_cookery_bakery':
                    count = 0
                    for sheet in record.marksheets:
                        if sheet.cookery_bakery.cookery_draft_confirm == 'confirm':
                            count += 1
                    record.candidate_done = count
                elif record.exam_type == 'ccmc_oral':
                    count = 0
                    for sheet in record.marksheets:
                        if sheet.ccmc_oral.ccmc_oral_draft_confirm == 'confirm':
                            count += 1
                    record.candidate_done = count
                elif record.exam_type == 'gsk_oral':
                    count = 0
                    for sheet in record.marksheets:
                        if sheet.ccmc_gsk_oral.ccmc_oral_draft_confirm == 'confirm':
                            count += 1
                    record.candidate_done = count
                elif record.exam_type == 'online':
                    count = 0
                    for sheet in record.marksheets:
                        if sheet.ccmc_marksheet.ccmc_online_attendance:
                            count += 1
                    record.candidate_done = count
            
            elif record.subject.name == 'CCMC GSK Oral':
                if record.exam_type == 'practical_oral':
                    count = 0
                    for sheet in record.marksheets:
                        if sheet.ccmc_gsk_oral.ccmc_oral_draft_confirm == 'confirm':
                            count += 1
                    record.candidate_done = count
                elif record.exam_type == 'online':
                    count = 0
                    for sheet in record.marksheets:
                        if sheet.ccmc_marksheet.ccmc_online_attendance:
                            count += 1
                    record.candidate_done = count
                    
            else:
                record.candidate_done = 'NA'
                
            

            
            

    
    
    def download_marksheet(self):
        
        batch_id = self.dgs_batch.id
        
        if self.exam_type == 'practical_oral' and self.subject.name == 'GSK':
        
            url = '/open_candidate_form/download_gsk_marksheet/'+str(batch_id)+'/'+str(self.id)
            
            return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }
        
        elif self.exam_type == 'practical_oral' and self.subject.name == 'MEK':
        
            url = '/open_candidate_form/download_mek_marksheet/'+str(batch_id)+'/'+str(self.id)
            
            return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }
            
        elif self.exam_type == 'practical_oral_cookery_bakery' and self.subject.name == 'CCMC':
        
            url = '/open_ccmc_candidate_form/download_ccmc_practical_marksheet/'+str(batch_id)+'/'+str(self.id)
            
            return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }
        
        elif self.exam_type == 'ccmc_oral' and self.subject.name == 'CCMC':
        
            url = '/open_ccmc_candidate_form/download_ccmc_oral_marksheet/'+str(batch_id)+'/'+str(self.id)
            
            return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }
        
        elif self.exam_type == 'gsk_oral' and self.subject.name == 'CCMC' or self.subject.name == 'CCMC GSK Oral':
        
            url = '/open_ccmc_candidate_form/download_ccmc_gsk_oral_marksheet/'+str(batch_id)+'/'+str(self.id)
            
            return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }
     
    
    @api.constrains('examiner', 'exam_date')
    def _check_duplicate_examiner_on_date(self):
        for record in self:
            if record.examiner and record.exam_date and record.exam_type != 'online' and record.subject.name != 'CCMC GSK Oral':
                # import wdb;wdb.set_trace()
                examiner_name = record.examiner.name
                is_confirming = self.env.context.get("confirm_context")
                marksheet_ids = self.env.context.get("marksheet_ids") or []
                # All exam records for the same examiner & date (including current)
                all_records = self.search([
                    ('examiner', '=', record.examiner.id),
                    ('exam_date', '=', record.exam_date)
                ])
                base_count = sum(r.candidates_count for r in all_records)
                total_candidates = base_count + (len(marksheet_ids) if is_confirming else 0)

                if record.subject.name == 'CCMC':
                    if any(rec.exam_type != 'online' for rec in all_records):
                        if is_confirming:
                            marksheet_ids = self.env.context.get("marksheet_ids")               
                            if total_candidates > 50:
                                error_msg = _("Examiner '%s' is exceeding 25 candidates on %s! for '%s' ") % (
                                    examiner_name,record.exam_date,all_records[0].institute_id.name)
                                raise ValidationError(error_msg)
                        else:
                            if total_candidates > 50:
                                error_msg = _("Examiner '%s' is exceeding 25 candidates on %s! for '%s' ") % (
                                            examiner_name,record.exam_date,all_records[0].institute_id.name)
                                raise ValidationError(error_msg)
                else:
                    if any(rec.exam_type != 'online' for rec in all_records):
                        if is_confirming:
                            if total_candidates > 25:
                                error_msg = _("Examiner '%s' is exceeding 25 candidates on %s! for '%s' ") % (
                                    examiner_name,record.exam_date,all_records[0].institute_id.name)
                                raise ValidationError(error_msg)
                        else:
                            if total_candidates > 25:
                                error_msg = _("Examiner '%s' is exceeding 25 candidates on %s! for '%s' ") % (
                                            examiner_name,record.exam_date,all_records[0].institute_id.name)
                                raise ValidationError(error_msg)
                        
                duplicate_records = self.search([
                    ('examiner', '=', record.examiner.id),
                    ('exam_date', '=', record.exam_date),
                    ('id', '!=', record.id)  # Exclude the current record
                ])

                if record.exam_type != 'gsk_oral' and any(rec.exam_type == 'practical_oral' for rec in duplicate_records):
                    if total_candidates > 25:
                        error_msg = _("Examiner '%s' is already assigned on %s! for '%s' ") % (
                            examiner_name,record.exam_date,duplicate_records[0].institute_id.name)
                        raise ValidationError(error_msg)
                        
                    
    
    def download_attendance_sheet(self):
        # import wdb;wdb.set_trace()
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
        
        name = f"{self.examiner.name} - {self.dgs_batch.batch_name} - {self.subject.name}"
#  - {self.institute_id.name}
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
            if self.exam_type == 'practical_oral_cookery_bakery':
                views = [(self.env.ref("bes.view_marksheet_ccmc_tree_oral").id, 'tree'),  # Define tree view
                        (self.env.ref("bes.view_marksheet_ccmc_form_oral").id, 'form')]
            elif self.exam_type == 'online':
                views = [(self.env.ref("bes.view_marksheet_ccmc_tree_gsk_online").id, 'tree'),  # Define tree view
                        (self.env.ref("bes.view_marksheet_ccmc_form_gsk_online").id, 'form')]
            elif self.exam_type == 'gsk_oral':

                 views = [(self.env.ref("bes.view_marksheet_ccmc_tree_gsk_oral_new").id, 'tree'),  # Define tree view
                        (self.env.ref("bes.view_marksheet_ccmc_form_gsk_oral_new").id, 'form')]
            elif self.exam_type == 'ccmc_oral':
                 views = [(self.env.ref("bes.view_marksheet_ccmc_tree_oral_no_prac").id, 'tree'),  # Define tree view
                        (self.env.ref("bes.view_marksheet_ccmc_form_oral_no_prac").id, 'form')]         
        
            

        
        # elif self.subject.name == 'CCMC GSK Oral' or self.subject.name == 'CCMC' :
        #     if self.exam_type == 'gsk_oral':

        #          views = [(self.env.ref("bes.view_marksheet_ccmc_tree_gsk_oral_new").id, 'tree'),  # Define tree view
        #                 (self.env.ref("bes.view_marksheet_ccmc_form_gsk_oral_new").id, 'form')]
            
        
        return {
        # Breadcrum
            'name': name,
            'domain': [('examiners_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',  # Specify both tree and form views
            'res_model': 'exam.type.oral.practical.examiners.marksheet',
            'views': views,
            'target': 'current',
            'groups': 'bes.group_exam_coordinator',
        }
    

        
class OralPracticalExaminersMarksheet(models.Model):
    _name = 'exam.type.oral.practical.examiners.marksheet'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'display_name'
    _description= 'Marksheets'

    examiners_id = fields.Many2one("exam.type.oral.practical.examiners",string="Examiners ID",tracking=True)
    gp_candidate = fields.Many2one("gp.candidate",string="GP Candidate",tracking=True)
    gp_marksheet = fields.Many2one("gp.exam.schedule",string="GP Marksheet",tracking=True)
    ccmc_marksheet = fields.Many2one("ccmc.exam.schedule",string="CCMC Marksheet",tracking=True)
    ccmc_candidate = fields.Many2one("ccmc.candidate",string="CCMC Candidate",tracking=True)
   
    mek_oral = fields.Many2one("gp.mek.oral.line","MEK Oral",tracking=True)
    using_of_tools = fields.Integer("Uses of Hand/Plumbing/Carpentry Tools & Chipping Tools & Brushes & Paints",tracking=True,related='mek_oral.using_of_tools')
    welding_lathe_drill_grinder = fields.Integer("Welding & Lathe/Drill/Grinder",tracking=True,related='mek_oral.welding_lathe_drill_grinder')
    electrical = fields.Integer("Electrical",tracking=True,related='mek_oral.electrical')
    journal = fields.Integer("Journal",tracking=True,related='mek_oral.journal')
    mek_oral_total_marks = fields.Integer("Oral Total Marks", store=True,tracking=True,related='mek_oral.mek_oral_total_marks')
    mek_oral_remarks = fields.Text("Remarks",tracking=True,related='mek_oral.mek_oral_remarks')
    mek_oral_draft_confirm = fields.Selection([('draft','Draft'),('confirm','Confirm')],string="Status",related='mek_oral.mek_oral_draft_confirm',tracking=True)

    mek_prac = fields.Many2one("gp.mek.practical.line","MEK Practical",tracking=True)
    using_hand_plumbing_tools_task_3 = fields.Integer("Using Hand & Plumbing Tools (Task 3)",tracking=True,related='mek_prac.using_hand_plumbing_tools_task_3')
    use_of_chipping_tools_paint = fields.Integer("Use of Chipping Tools & paint Brushes",tracking=True,related='mek_prac.use_of_chipping_tools_paint')
    welding_lathe = fields.Integer("Welding (1 Task),Lathe Work (1 Task)",tracking=True,related='mek_prac.welding_lathe')
    prac_electrical = fields.Integer("Electrical (1 Task)",tracking=True,related='mek_prac.electrical')
    mek_practical_total_marks = fields.Integer("Practical Total Marks",store=True,tracking=True,related='mek_prac.mek_practical_total_marks')
    mek_practical_remarks = fields.Text(" Remarks",tracking=True,related='mek_prac.mek_practical_remarks')
    mek_practical_draft_confirm = fields.Selection([('draft','Draft'),('confirm','Confirm')],string="Status",default="draft",tracking=True,related='mek_prac.mek_practical_draft_confirm')

    gsk_oral = fields.Many2one("gp.gsk.oral.line","GSK Oral",tracking=True)
    subject_area_1_2_3 = fields.Integer("Subject Area 1, 2, 3 ",tracking=True,related='gsk_oral.subject_area_1_2_3')
    subject_area_4_5_6 = fields.Integer("Subject Area 4, 5, 6",tracking=True,related='gsk_oral.subject_area_4_5_6')
    practical_record_journals = fields.Integer("Practical Record Book and Journal",tracking=True,related='gsk_oral.practical_record_journals')
    gsk_oral_total_marks = fields.Integer("Oral Total Marks", store=True,tracking=True,related='gsk_oral.gsk_oral_total_marks')
    gsk_oral_remarks = fields.Text(" Remarks",tracking=True,related='gsk_oral.gsk_oral_remarks')
    gsk_oral_draft_confirm = fields.Selection([('draft','Draft'),('confirm','Confirm')],string="Status",default="draft",tracking=True,related='gsk_oral.gsk_oral_draft_confirm')


    gsk_prac = fields.Many2one("gp.gsk.practical.line","GSK Practical",tracking=True)
    climbing_mast_bosun_chair= fields.Integer("Climb the mast with safe practices , Prepare and throw Heaving Line,Rigging Bosun's Chair and self lower and hoist",tracking=True,related='gsk_prac.climbing_mast_bosun_chair')
    buoy_flags_recognition = fields.Integer("·Recognise buyos and flags .Hoisting a Flag correctly .Steering and Helm Orders",tracking=True,related='gsk_prac.buoy_flags_recognition')
    rig_stage_rig_pilot_rig_scaffolding = fields.Integer("Rig a stage for painting shipside,Rig a Pilot Ladder,Rig scaffolding to work at a height",tracking=True,related='gsk_prac.rig_stage_rig_pilot_rig_scaffolding')
    fast_ropes_knots_bend_sounding_rod = fields.Integer("·Making fast Ropes and Wires ·Use Rope-Stopper / Chain Stopper.Knots, Bends, Hitches .Whippings/Seizing/Splicing Ropes/Wires .Reeve 3- fold / 2 fold purchase·Taking Soundings with sounding rod / sounding taps ·Reading of Draft .Mannual lifting of weight",tracking=True,related='gsk_prac.fast_ropes_knots_bend_sounding_rod')
    gsk_practical_total_marks = fields.Integer("Practical Total Marks",store=True,tracking=True,related='gsk_prac.gsk_practical_total_marks')
    gsk_practical_remarks = fields.Text("Remarks",tracking=True,related='gsk_prac.gsk_practical_remarks')
    gsk_practical_draft_confirm = fields.Selection([('draft','Draft'),('confirm','Confirm')],string="Status",default="draft",tracking=True,related='gsk_prac.gsk_practical_draft_confirm')


    cookery_bakery = fields.Many2one("ccmc.cookery.bakery.line","Cookery And Bakery",tracking=True)
    hygien_grooming = fields.Integer("Hygiene & Grooming",tracking=True,related='cookery_bakery.hygien_grooming')
    appearance = fields.Integer("Appearance(Dish 1)",tracking=True,related='cookery_bakery.hygien_grooming')
    taste = fields.Integer("Taste(Dish 1)",tracking=True,related='cookery_bakery.taste')
    texture = fields.Integer("Texture(Dish 1)",tracking=True,related='cookery_bakery.texture')
    appearance_2 = fields.Integer("Appearance(Dish 2)",tracking=True,related='cookery_bakery.appearance_2')
    taste_2 = fields.Integer("Taste(Dish 2)",tracking=True,related='cookery_bakery.taste_2')
    texture_2 = fields.Integer("Texture(Dish 2)",tracking=True,related='cookery_bakery.texture_2')
    appearance_3 = fields.Integer("Appearance(Dish 3)",tracking=True,related='cookery_bakery.appearance_3')
    taste_3 = fields.Integer("Taste(Dish 3)",tracking=True,related='cookery_bakery.taste_3')
    texture_3 = fields.Integer("Texture(Dish 3)",tracking=True,related='cookery_bakery.texture_3')
    identification_ingredians = fields.Integer("identification of ingredients",tracking=True,related='cookery_bakery.identification_ingredians')
    knowledge_of_menu = fields.Integer("Knowledge of menu",tracking=True,related='cookery_bakery.knowledge_of_menu')
    total_mrks = fields.Integer("Total",store=True,tracking=True,related='cookery_bakery.total_mrks')
    cookery_practical_remarks = fields.Char("Remarks",tracking=True,related='cookery_bakery.cookery_practical_remarks')
    cookery_draft_confirm = fields.Selection([('draft','Draft'),('confirm','Confirm')],string="Status",default="draft",related='cookery_bakery.cookery_draft_confirm')

    ccmc_oral = fields.Many2one("ccmc.oral.line","CCMC Oral",tracking=True)
    house_keeping = fields.Integer("House Keeping",tracking=True,related='ccmc_oral.house_keeping')
    f_b = fields.Integer("F & B service Practical",tracking=True,related='ccmc_oral.f_b')
    orals_house_keeping = fields.Integer("Orals on Housekeeping and F& B Service",tracking=True,related='ccmc_oral.orals_house_keeping')
    attitude_proffessionalism = fields.Integer("Attitude & Proffesionalism",tracking=True,related='ccmc_oral.attitude_proffessionalism')
    equipment_identification = fields.Integer("Identification of Equipment",tracking=True,related='ccmc_oral.equipment_identification')
    gsk_ccmc = fields.Integer("GSK",related='ccmc_oral.gsk_ccmc',tracking=True)
    toal_ccmc_rating = fields.Integer("Total", store=True,tracking=True,related='ccmc_oral.toal_ccmc_rating')
    ccmc_oral_remarks = fields.Char(" Remarks",tracking=True,related='ccmc_oral.ccmc_oral_remarks')
    ccmc_oral_draft_confirm = fields.Selection([('draft','Draft'),('confirm','Confirm')],string="Status",default="draft",related='ccmc_oral.ccmc_oral_draft_confirm')
    

    ccmc_gsk_oral = fields.Many2one("ccmc.gsk.oral.line","CCMC GSK Oral",tracking=True)
    ccmc_gsk = fields.Integer("GSK",related='ccmc_gsk_oral.gsk_ccmc',tracking=True)
    safety_ccmc = fields.Integer("Safety",related='ccmc_gsk_oral.safety_ccmc',tracking=True)
    toal_ccmc_oral_rating = fields.Integer("Total", store=True,tracking=True,related='ccmc_gsk_oral.toal_ccmc_oral_rating')
    ccmc_gsk_oral_remarks = fields.Char(" Remarks",tracking=True,related='ccmc_gsk_oral.ccmc_gsk_oral_remarks')
    ccmc__gsk_oral_draft_confirm = fields.Selection([('draft','Draft'),('confirm','Confirm')],string="Status",default="draft",related='ccmc_gsk_oral.ccmc_oral_draft_confirm')
    
    ccmc_online = fields.Many2one("survey.user_input",string="CCMC Online",tracking=True,related="ccmc_marksheet.ccmc_online")


    
    gsk_online = fields.Many2one("survey.user_input","GSK Online",tracking=True,related="gp_marksheet.gsk_online")
    mek_online = fields.Many2one("survey.user_input","MEK Online",tracking=True,related="gp_marksheet.mek_online")
    
    display_name = fields.Char(string='Name', compute='_compute_display_name')
   
    @api.depends('gp_candidate', 'ccmc_candidate')
    def _compute_display_name(self):
        for cousre in self.examiners_id.course:
            for record in self:
                if cousre.id == 7:
                    record.display_name = f"{record.gp_candidate.name}"
                else:
                    record.display_name = f"{record.ccmc_candidate.name}"



    def open_reallocate_candidates(self):
        # import wdb;wdb.set_trace();
        assignment_id = request.env['exam.type.oral.practical'].sudo().search([('dgs_batch','=',self.examiners_id.dgs_batch.id),('institute_id','=',self.examiners_id.institute_id.id)])
        
        examiner_id = self.examiners_id.id
        
        # print(self.env.context.get("active_ids"))
        
        # examiner_id = request.env["exam.type.oral.practical.examiners"].sudo().search([('prac_oral_id','=',assignment_id.id)])
        
        return {
            'name': 'Reallocate Examiner Assignments',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'reallocate.candidates.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_candidate_ids': self.env.context.get("active_ids"),  # Pass a list of candidate IDs
                'default_exam_batch': assignment_id.dgs_batch.id,  
                'default_institute_id': assignment_id.institute_id.id,
                'default_examiner_id': examiner_id,
            }
        }
    
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
                     

            
class IntegrityViolationWizard(models.TransientModel):
    _name = 'candidate.integrity.violation.wizard'
    _description = 'Report Integrity Violation '

    incident_details = fields.Text(string='Incident Details')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    
    def action_log_note(self):
        self.ensure_one()
        active_id = self.env.context.get('active_id')
        if active_id:
            model = self.env.context.get('active_model')
            record = self.env[model].browse(active_id)
            
            # Log note
            attachments=[]
            for pdf in self.attachment_ids:
                attachments.append(pdf.id)
            
            
            record.message_post(body=self.incident_details,attachment_ids=attachments)
            
            record.exam_violation_state = 'pending_approval'
            

            
            # Add attachment
            # if self.attachment:
            #     self.env['ir.attachment'].create({
            #         'name': self.attachment_filename,
            #         'type': 'binary',
            #         'datas': self.attachment,
            #         'res_model': model,
            #         'res_id': record.id,
            #     })


class ResetOnlineExamWizard(models.TransientModel):
    _name = 'reset.online.exam.wizard'
    
    model = fields.Char("Model")
    gp_subject = fields.Selection([('gsk','GSK'), ('mek', 'MEK')], string="GP Subject")
    ccmc_subject = fields.Selection([('ccmc', 'CCMC')],default="ccmc", string="CCMC Subject")
    reset_reason = fields.Text(string='Reset Reason')
    def convert_to_ist(self, dt_utc):
        """Convert UTC datetime to IST."""
        if not dt_utc:
            return False  # Handle cases where the datetime is not provided
        ist_timezone = timezone('Asia/Kolkata')
        ist_time = dt_utc.replace(tzinfo=timezone('UTC')).astimezone(ist_timezone).replace(tzinfo=None)
        return ist_time
    
    
    def confirm_reset(self):
        self.ensure_one()

        record_id = self.env.context.get('active_id')
        active_model = self.env.context.get('active_model')
    
        parent_record = self.env[active_model].browse(record_id)
        message = f"Reason for Reset of Online Exam: {self.reset_reason}"

        # import wdb;wdb.set_trace()

        ist_timezone = timezone('Asia/Kolkata')
        if self.model == "gp.exam.schedule":
            if self.gp_subject == "gsk":
                
                active_id = self.env.context.get('active_id')
                gp_exam = self.env[self.model].browse(active_id)
                
                if not gp_exam.attempting_gsk_online:
                    raise ValidationError("Candidate is Not Appearing for GSK online")
                
                # Default values in case data is missing
                start_time = "00:00:00"
                end_time = "00:00:00"
                total_time = "00:00:00"
                question_count = 0

                if gp_exam.attempting_gsk_online:
                    if gp_exam.gsk_online.user_input_line_ids:
                        start_time_utc = gp_exam.gsk_online.user_input_line_ids[0].create_date
                        question_count = len(gp_exam.gsk_online.user_input_line_ids)
                        end_time_utc = gp_exam.gsk_online.user_input_line_ids[-1].create_date
                    else:
                        start_time_utc = None
                        end_time_utc = None
                        
                    if start_time_utc and end_time_utc:
                        # Convert UTC to IST
                        start_time_ist = start_time_utc.astimezone(ist_timezone)
                        end_time_ist = end_time_utc.astimezone(ist_timezone)

                        total_time_delta = end_time_ist - start_time_ist

                        # Format the times
                        start_time = start_time_ist.strftime('%H:%M:%S')
                        end_time = end_time_ist.strftime('%H:%M:%S')

                        # Calculate total time in HH:MM:SS
                        total_seconds = int(total_time_delta.total_seconds())
                        hours, remainder = divmod(total_seconds, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        total_time = f"{hours:02}:{minutes:02}:{seconds:02}"

                # Final message format
                message = f"""
                <b>Previous Exam LOG Before Reset</b><br/>
                <b>First Question Attempted</b>: {start_time}<br/>
                <b>Last Question No. Attempted</b>: {question_count}<br/>
                <b>Last Question Attempted</b>: {end_time}<br/>
                <b>Total Time Taken</b>: {total_time}<br/>
                <b>Reason for Reset of Online Exam</b>: {self.reset_reason}
                """


                    
                gp_exam.gsk_online.sudo().unlink()
                # gsk_survey_qb_input = self.env["survey.survey"].sudo().search([('title','=','GSK ONLINE EXIT EXAMINATION')])
                gsk_survey_qb_input = self.env["course.master.subject"].sudo().search([('name','=','GSK')]).qb_online
                gsk_predefined_questions = gsk_survey_qb_input._prepare_user_input_predefined_questions()

                # print(gsk_predefined_questions)
                start_time_ist =  self.convert_to_ist(gp_exam.gsk_online_assignment_id.online_start_time)
                end_time_ist =  self.convert_to_ist(gp_exam.gsk_online_assignment_id.online_end_time)

                # import wdb;wdb.set_trace()
                
                gsk_survey_qb_input = gsk_survey_qb_input.sudo()._create_answer(user=gp_exam.gp_candidate.user_id)
                gsk_survey_qb_input.sudo().write({"gp_candidate": gp_exam.gp_candidate.id,
                                           'gp_exam':gp_exam.id,
                                           'institute_id': gp_exam.gp_candidate.institute_id.id,
                                            "dgs_batch":gp_exam.dgs_batch.id,
                                            "ip_address":gp_exam.ip_address,
                                            'token_regenrated': True,
                                            'is_gp': True,
                                            'is_ccmc': False,
                                            'exam_date': gp_exam.exam_date,
                                            'commence_online_exam':True,
                                            "online_start_time": start_time_ist,
                                            "online_end_time": end_time_ist,
                                            })
                
                # if gp_exam.attempting_gsk_online and gp_exam.attempting_mek_online:
                #     gp_exam.sudo().write({
                #         "gsk_online": gsk_survey_qb_input,
                #         "gsk_online_token_used": False,
                #         "attempted_gsk_online": False,
                #         "gsk_online_attendance":'',
                #         "mek_online_attendance":'',
                #         "token":False
                #     })
                # elif gp_exam.attempting_gsk_online and not gp_exam.attempting_mek_online:
                gp_exam.sudo().write({
                    "gsk_online": gsk_survey_qb_input,
                    "gsk_online_token_used": False,
                    "attempted_gsk_online": False,
                    "gsk_online_attendance":'',
                    "token":False
                })


            elif self.gp_subject == "mek":
                active_id = self.env.context.get('active_id')
                gp_exam = self.env[self.model].browse(active_id)
                                # Default values in case data is missing
                if not gp_exam.attempting_mek_online:
                    raise ValidationError("Candidate is Not Appearing for MEK online")

                start_time = "00:00:00"
                end_time = "00:00:00"
                total_time = "00:00:00"
                question_count = 0

                if gp_exam.attempting_mek_online:
                    if gp_exam.mek_online.user_input_line_ids:
                        question_count = len(gp_exam.mek_online.user_input_line_ids)
                        start_time_utc = gp_exam.mek_online.user_input_line_ids[0].create_date
                        end_time_utc = gp_exam.mek_online.user_input_line_ids[-1].create_date
                    else:
                        start_time_utc = None
                        end_time_utc = None
                        
                    if start_time_utc and end_time_utc:
                        # Convert UTC to IST
                        start_time_ist = start_time_utc.astimezone(ist_timezone)
                        end_time_ist = end_time_utc.astimezone(ist_timezone)

                        total_time_delta = end_time_ist - start_time_ist

                        # Format the times
                        start_time = start_time_ist.strftime('%H:%M:%S')
                        end_time = end_time_ist.strftime('%H:%M:%S')

                        # Calculate total time in HH:MM:SS
                        total_seconds = int(total_time_delta.total_seconds())
                        hours, remainder = divmod(total_seconds, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        total_time = f"{hours:02}:{minutes:02}:{seconds:02}"

                # Final message format
                message = f"""
                <b>Previous Exam LOG Before Reset</b><br/>
                <b>First Question Attempted</b>: {start_time}<br/>
                <b>Last Question No. Attempted</b>: {question_count}<br/>
                <b>Last Question Attempted</b>: {end_time}<br/>
                <b>Total Time Taken</b>: {total_time}<br/>
                <b>Reason for Reset of Online Exam</b>: {self.reset_reason}
                """

                gp_exam.mek_online.sudo().unlink()
                # mek_survey_qb_input = self.env["survey.survey"].sudo().search([('title','=','MEK ONLINE EXIT EXAMINATION')])
                mek_survey_qb_input = self.env["course.master.subject"].sudo().search([('name','=','MEK')]).qb_online
                mek_survey_qb_input = mek_survey_qb_input.sudo()._create_answer(user=gp_exam.gp_candidate.user_id)

                # ✅ Use already stored IST values
                start_time_ist =  self.convert_to_ist(gp_exam.mek_online_assignment_id.online_start_time)
                end_time_ist =  self.convert_to_ist(gp_exam.mek_online_assignment_id.online_end_time)

                
                mek_survey_qb_input.sudo().write({"gp_candidate": gp_exam.gp_candidate.id,
                                           'gp_exam':gp_exam.id,
                                            'institute_id': gp_exam.gp_candidate.institute_id.id,
                                            "dgs_batch":gp_exam.dgs_batch.id,
                                            "ip_address":gp_exam.ip_address,
                                            'token_regenrated': True,
                                            'is_gp': True,
                                            'is_ccmc': False,
                                            'exam_date': gp_exam.exam_date,
                                            'commence_online_exam':True,
                                            "online_start_time": start_time_ist,
                                            "online_end_time": end_time_ist,
                                            })

                gp_exam.write({
                    "mek_online": mek_survey_qb_input,
                    "mek_online_token_used": False,
                    "attempted_mek_online": False,
                    "ip_address":gp_exam.ip_address,
                    "mek_online_attendance":'',
                    "token":False
                })
                

        elif self.model == "ccmc.exam.schedule":
            if self.ccmc_subject == "ccmc":
                active_id = self.env.context.get('active_id')
                ccmc_exam = self.env[self.model].browse(active_id)
                
                if not ccmc_exam.attempting_online:
                    raise ValidationError("Candidate is Not Appearing for CCMC online")
                
                # Default values in case data is missing
                start_time = "00:00:00"
                end_time = "00:00:00"
                total_time = "00:00:00"
                question_count = 0

                if ccmc_exam.attempting_online:
                    if ccmc_exam.ccmc_online.user_input_line_ids:
                        question_count = len(ccmc_exam.ccmc_online.user_input_line_ids)
                        start_time_utc = ccmc_exam.ccmc_online.user_input_line_ids[0].create_date
                        end_time_utc = ccmc_exam.ccmc_online.user_input_line_ids[-1].create_date
                    else:
                        start_time_utc = None
                        end_time_utc = None

                    if start_time_utc and end_time_utc:
                        # Convert UTC to IST
                        start_time_ist = start_time_utc.astimezone(ist_timezone)
                        end_time_ist = end_time_utc.astimezone(ist_timezone)

                        total_time_delta = end_time_ist - start_time_ist

                        # Format the times
                        start_time = start_time_ist.strftime('%H:%M:%S')
                        end_time = end_time_ist.strftime('%H:%M:%S')

                        # Calculate total time in HH:MM:SS
                        total_seconds = int(total_time_delta.total_seconds())
                        hours, remainder = divmod(total_seconds, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        total_time = f"{hours:02}:{minutes:02}:{seconds:02}"

                # Final message format
                message = f"""
                <b>Previous Exam LOG Before Reset</b><br/>
                <b>First Question Attempted</b>: {start_time}<br/>
                <b>Last Question No. Attempted</b>: {question_count}<br/>
                <b>Last Question Attempted</b>: {end_time}<br/>
                <b>Total Time Taken</b>: {total_time}<br/>
                <b>Reason for Reset of Online Exam</b>: {self.reset_reason}
                """
                ccmc_exam.ccmc_online.sudo().unlink()

                start_time_ist =  self.convert_to_ist(ccmc_exam.ccmc_online_assignment_id.online_start_time)
                end_time_ist =  self.convert_to_ist(ccmc_exam.ccmc_online_assignment_id.online_end_time)
                
                # ccmc_qb_input = self.env["survey.survey"].sudo().search([('title','=','CCMC ONLINE EXIT EXAMINATION')])
                ccmc_qb_input = self.env["course.master.subject"].sudo().search([('name','=','CCMC')]).qb_online
                ccmc_qb_input = ccmc_qb_input.sudo()._create_answer(user=ccmc_exam.ccmc_candidate.user_id)
                ccmc_qb_input.sudo().write({"ccmc_candidate": ccmc_exam.ccmc_candidate.id,
                                     'ccmc_exam':ccmc_exam.id,
                                    'institute_id': ccmc_exam.ccmc_candidate.institute_id.id,
                                    "dgs_batch":ccmc_exam.dgs_batch.id,
                                    "ip_address":ccmc_exam.ip_address,
                                    'token_regenrated': True,
                                    'is_gp': False,
                                    'is_ccmc': True,
                                    'exam_date': ccmc_exam.exam_date,
                                    'commence_online_exam':True,
                                    "online_start_time": start_time_ist,
                                    "online_end_time": end_time_ist,
                                    })

                ccmc_exam.write({
                    "ccmc_online": ccmc_qb_input,
                    "ccmc_online_token_used": False,
                    "attempted_ccmc_online": False,
                    "ip_address":ccmc_exam.ip_address,
                    "ccmc_online_attendance":'',
                    "token":False
                })
                

        
        parent_record.message_post(body=message)    

                
        
        # Reset Online Exam
    
    
    





class GpAdmitCardRelease(models.TransientModel):
    _name = 'gp.admit.card.release'
    _description = 'GP Admit Card Release'

    exam_ids = fields.Many2many('gp.exam.schedule', string='Exams')
    admit_card_type = fields.Selection([
        ('gp', 'GP'),
        ('ccmc', 'CCMC')
    ], string='Admit Card Type', default='gp')
    exam_region = fields.Many2one('exam.center', string='Region')
    candidates_count = fields.Integer(string='Candidates Processed', readonly=True)
    result_message = fields.Text(string='Result', readonly=True)

    exam_date_practical = fields.Date(string="Exam Date Practical & Oral From",tracking=True)
    exam_date_practical_to = fields.Date(string="Exam Date Practical & Oral To",tracking=True)
    exam_date_online = fields.Date(string="Exam Date Online From",tracking=True)
    exam_date_online_to = fields.Date(string="Exam Date Online To",tracking=True)
    dgs_batch = fields.Many2one('dgs.batches', string='DGS Batch', readonly=True)

    check_batch = fields.Selection([('invisible', 'Invisible'), ('required', 'Required')],compute='_compute_check_batch')

    @api.depends('dgs_batch')
    def _compute_check_batch(self):
        if self.dgs_batch.is_current_batch or not self.dgs_batch.is_march_september and not self.dgs_batch.repeater_batch:
            self.check_batch = 'invisible'
        elif self.dgs_batch.repeater_batch and not self.dgs_batch.is_march_september and not self.dgs_batch.is_current_batch:
            self.check_batch = 'required'
        else:
            self.check_batch = 'invisible'
            

    def release_gp_admit_card(self, *args, **kwargs):
        exam_ids = self.env.context.get('active_ids')
        candidates = self.env["gp.exam.schedule"].sudo().browse(exam_ids)
        
        # Count candidates who have already had their admit cards released
        already_released_count = len(candidates.filtered(lambda c: not c.hold_admit_card))
        
        count = 0
        for candidate in candidates:
            mumbai_region = candidate.dgs_batch.mumbai_region
            kolkata_region = candidate.dgs_batch.kolkatta_region
            chennai_region = candidate.dgs_batch.chennai_region
            delhi_region = candidate.dgs_batch.delhi_region
            kochi_region = candidate.dgs_batch.kochi_region
            goa_region = candidate.dgs_batch.goa_region
            is_march_september = candidate.dgs_batch.is_march_september

            # Check if the candidate meets the criteria for releasing the admit card
            if (candidate.stcw_criterias == 'passed' and candidate.attendance_criteria == 'passed' and candidate.ship_visit_criteria == 'passed') or candidate.ceo_override:
                # Determine the region-specific institute\
                if is_march_september:
                    # import wdb; wdb.set_trace()
                    registered_institute = None
                    if candidate.exam_region.name == 'MUMBAI' and mumbai_region:
                        registered_institute = mumbai_region.id
                    elif candidate.exam_region.name == 'KOLKATA' and kolkata_region:
                        registered_institute = kolkata_region.id
                    elif candidate.exam_region.name == 'CHENNAI' and chennai_region:
                        registered_institute = chennai_region.id
                    elif candidate.exam_region.name == 'DELHI' and delhi_region:
                        registered_institute = delhi_region.id
                    elif candidate.exam_region.name == 'KOCHI' and kochi_region:
                        registered_institute = kochi_region.id
                    elif candidate.exam_region.name == 'GOA' and goa_region:
                        registered_institute = goa_region.id
                else:
                    registered_institute = candidate.institute_id.id
                # Only update if hold_admit_card is being set to False
                if candidate.hold_admit_card:
                    candidate.write({
                        'hold_admit_card': False,
                        'registered_institute': registered_institute,
                    })
                    count += 1  # Increment count only when hold_admit_card is updated to False

                # Update exam dates if not March/September
                if not is_march_september:
                    candidate.write({
                        'exam_date_practical': self.exam_date_practical,
                        'exam_date_practical_to': self.exam_date_practical_to,
                        'exam_date_online': self.exam_date_online,
                        'exam_date_online_to': self.exam_date_online_to,
                    })
            else:
                # If criteria are not met, set hold_admit_card to True
                candidate.write({'hold_admit_card': True})

        # Calculate the total number of candidates
        total_candidates = len(exam_ids)

        # Final message
        message = f"GP Admit Card Released for {count} Candidates. Out of {total_candidates} selected candidates, {already_released_count} admit cards were already released."

        # Return a notification
        return {
            'name': 'Admit Card Released',
            'type': 'ir.actions.act_window',
            'res_model': 'batch.pop.up.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'default_message': message},
        }

    
    
class GPExam(models.Model):
    _name = "gp.exam.schedule"
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = "exam_id"
    _description= 'Schedule'
    

    
    exam_id = fields.Char("Roll No",required=True, copy=False, readonly=True,tracking=True)

    registered_institute = fields.Many2one("bes.institute",string="Examination Center",tracking=True)
    
    dgs_batch = fields.Many2one("dgs.batches",string="Exam Batch",required=True,tracking=True)
    certificate_id = fields.Char(string="Certificate No.",tracking=True)
    gp_candidate = fields.Many2one("gp.candidate","GP Candidate",store=True,tracking=True)
    # roll_no = fields.Char(string="Roll No",required=True, copy=False, readonly=True,
    #                             default=lambda self: _('New')) 
    
    
    ip_address = fields.Char("IP Address")
    
    exam_region = fields.Many2one('exam.center',string='Exam Region',store=True)
    
    exam_violation_state = fields.Selection([
        ('na', 'N/A'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
    ], string='Exam Violation', default='na',tracking=True)
    
    attempt_number = fields.Integer("Attempt Number",tracking=True)
    
    institute_name = fields.Many2one("bes.institute","Institute Name",tracking=True)
    mek_oral = fields.Many2one("gp.mek.oral.line","MEK Oral",tracking=True)
    mek_prac = fields.Many2one("gp.mek.practical.line","MEK Practical",tracking=True)
    gsk_oral = fields.Many2one("gp.gsk.oral.line","GSK Oral",tracking=True)
    gsk_prac = fields.Many2one("gp.gsk.practical.line","GSK Practical",tracking=True)
    gsk_online = fields.Many2one("survey.user_input","GSK Online",tracking=True)
    mek_online = fields.Many2one("survey.user_input","MEK Online",tracking=True)
    
    gsk_oral_marks = fields.Float("GSK Oral/Journal",readonly=True,tracking=True)
    mek_oral_marks = fields.Float("MEK Oral/Journal",readonly=True,tracking=True)
    gsk_practical_marks = fields.Float("GSK Practical",readonly=True,tracking=True)
    mek_practical_marks = fields.Float("MEK Practical",readonly=True,tracking=True)
    gsk_total = fields.Float("GSK Oral/Practical Marks",readonly=True,tracking=True)
    gsk_percentage = fields.Float("GSK Oral/Practical Precentage",readonly=True,tracking=True)
    

    mek_online_marks = fields.Float("MEK Online",readonly=True, digits=(16,2),tracking=True)
    gsk_online_marks = fields.Float("GSK Online",readonly=True,digits=(16,2),tracking=True)
    mek_online_percentage = fields.Float("MEK Online (%)",readonly=True,digits=(16,2),tracking=True)
    gsk_online_percentage = fields.Float("GSK Online (%)",readonly=True,digits=(16,2),tracking=True)    
    mek_total = fields.Float("MEK Oral/Practical Marks",readonly=True,tracking=True)
    mek_percentage = fields.Float("MEK Oral/Practical Percentage",readonly=True,tracking=True)
    overall_marks = fields.Float("Overall Marks",readonly=True,tracking=True)
    overall_percentage = fields.Float("Overall (%)",readonly=True,tracking=True)
    
    # Attempting Exams
    attempting_gsk_oral_prac = fields.Boolean('attempting_gsk_oral_prac',tracking=True)
    attempting_mek_oral_prac = fields.Boolean('attempting_mek_oral_prac',tracking=True)
    attempting_mek_online = fields.Boolean('attempting_mek_online',tracking=True)
    attempting_gsk_online = fields.Boolean('attempting_gsk_online',tracking=True)
    
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
    
    token = fields.Char(string='Online Token',tracking=True)
    
    def generate_token(self):
        return random.randint(100000, 999999)

    
    gsk_online_token_used = fields.Boolean('gsk_online_token_used')
    
    mek_online_token_used = fields.Boolean('mek_online_token_used')
    
    attempted_gsk_online = fields.Boolean('attempted_gsk_online')

    attempted_mek_online = fields.Boolean('attempted_mek_online')
    
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
    
    edit_marksheet_status = fields.Boolean('edit_marksheet_status',compute='_compute_is_in_group')

    @api.depends_context('uid')  # Depends on current user
    def _compute_is_in_group(self):
        for record in self:
            user = self.env.user
            group_xml_ids = ['bes.edit_marksheet_status']
            record.edit_marksheet_status = any(user.has_group(group) for group in group_xml_ids)
    
    exam_criteria = fields.Selection([
        ('', ''),
        ('pending', 'Failed'),
        ('passed', 'Passed'),
    ], string='Result Status',store=True, compute="compute_certificate_criteria")
    
    certificate_criteria = fields.Selection([
        ('pending', 'Not Complied'),
        ('passed', 'Complied'),
    ], string='Certificate Criteria',compute="compute_pending_certificate_criteria")
    
    fees_paid_candidate = fields.Char("Fees Paid by Candidate",tracking=True,compute="_fees_paid_by_candidate",store=True)
    
    online_start_time = fields.Datetime("Start Time")
    online_end_time = fields.Datetime("End Time")
    def _fees_paid_by_candidate(self):
        for rec in self:
            # last_exam = self.env['gp.exam.schedule'].search([('gp_candidate','=',rec.id)], order='attempt_number desc', limit=1)
            # last_exam_dgs_batch = last_exam.dgs_batch.id
            invoice = self.env['account.move'].sudo().search([('repeater_exam_batch','=',rec.dgs_batch.id),('gp_candidate','=',rec.gp_candidate.id)],order='date desc')
            if invoice:
                batch = invoice.repeater_exam_batch.to_date.strftime("%B %Y")
                if invoice.payment_state == 'paid':
                    rec.fees_paid_candidate = batch + ' - Paid'
                else:
                    rec.fees_paid_candidate = batch + ' - Not Paid'
            else:
                rec.fees_paid_candidate = 'No Fees Paid'
    
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
    ], string='Ship Visit Criteria',store=True ,related='gp_candidate.ship_visit_criteria')

    attendance_criteria = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Complied'),
    ], string='Attendance Criteria',store=True,related='gp_candidate.attendance_criteria')
    
    # admit_card_status = fields.Selection([
    #     ('pending', 'Pending'),
    #     ('issued', 'Issued')
    # ],default="pending", string='Admit Card Status',store=True,related='gp_candidate.institute_batch_id.admit_card_status')

    state = fields.Selection([
        ('1-in_process', 'In Process'),
        ('2-done', 'Done'),
        ('3-certified', 'Certified'),
        ('4-pending', 'Pending'),
        ('5-pending_reissue_approval','Reissue Approval'),
        ('6-pending_reissue_approved','Approved')
        
    ], string='State', default='1-in_process')
    
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

    exam_pass_date = fields.Date(string="Date of DGS Approval:",tracking=True)
    certificate_issue_date = fields.Date(string="Date of Issue of Certificate:",tracking=True)
    rank = fields.Char("Rank",compute='_compute_rank',tracking=True,store=True)
    
    institute_code = fields.Char(string="Institute Code", related='institute_id.code',store=True,tracking=True)
    candidate_code = fields.Char(string="Candidate Code", related='gp_candidate.candidate_code',store=True,tracking=True)
    indos_no = fields.Char(string="INDoS No", related='gp_candidate.indos_no',store=True,tracking=True)
    user_state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], string='User Status', related='gp_candidate.user_state', required=True,tracking=True)

    institute_id = fields.Many2one("bes.institute",related='gp_candidate.institute_id',store=True,string="Institute",tracking=True)
    
    result_status = fields.Selection([
        ('absent','Absent'),
        ('pending','Pending'),
        ('failed','Failed'),
        ('passed','Passed'),
    ],string='Result',compute='_compute_result_status')
    
    result = fields.Selection([
        ('failed','Failed'),
        ('passed','Passed'),
    ],string='Result Status',store=True,compute='_compute_result_status_2')
    
    @api.depends('certificate_criteria')
    def _compute_result_status_2(self):
        for record in self:
            
            if record.certificate_criteria == 'passed':
                record.result = 'passed'
            else:
                record.result = 'failed'

    gsk_oral_prac_attendance = fields.Selection([
        ('',''),
        ('absent','Absent'),
        ('present','Present'),
    ],string="GSK P&O Attendance",store=True,compute="_compute_attendance_gsk",tracking=True)

    gsk_online_attendance = fields.Selection([
        ('absent','Absent'),
        ('present','Present'),
    ],string="GSK Online Attendance",tracking=True)
    
    mek_oral_prac_attendance = fields.Selection([
        ('',''),
        ('absent','Absent'),
        ('present','Present'),
    ],string="MEK P&O Attendance",store=True,compute="_compute_attendance_mek",tracking=True)
    
    mek_online_attendance = fields.Selection([
        ('absent','Absent'),
        ('present','Present'),
    ],string="MEK Online Attendance",tracking=True)

    candidate_image_status = fields.Selection([
        ('pending', 'Pending'),
        ('done', 'Done'),
    ],string="Candidate-Image",compute="_check_image",default="pending",store=True)
   
    candidate_signature_status = fields.Selection([
        ('pending', 'Pending'),
        ('done', 'Done'),
    ],string="Candidate-Sign",compute="_check_sign",default="pending",store=True)
    
    absent_status = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
    ],string="Absent Status (Fresh)) ",compute="_compute_absent_status",store=True)
    
    absent_status_repeater = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
    ],string="Absent Status (Repeater) ",compute="_compute_absent_status_repeater",store=True)
    
    edit_register_institute = fields.Boolean(
        string="Can Edit Institute",
        compute="_compute_edit_register_institute",
        store=False  # Don't store as it's computed on the fly
    )

    @api.depends_context('uid')  # Depends on current user
    def _compute_edit_register_institute(self):
        can_edit = self.env.user.has_group('bes.group_bes_coo')
        for record in self:
            record.edit_register_institute = can_edit


    @api.depends('gsk_oral_prac_attendance','gsk_online_attendance','mek_oral_prac_attendance','mek_online_attendance')
    def _compute_absent_status_repeater(self):
        for record in self:
            index = 0
            row = [ ]
            
            if record.gsk_oral_prac_carry_forward and record.gsk_oral_prac_status == 'passed':
                gsk_status = "AP"
                row.append(gsk_status)
            elif record.gsk_oral_prac_status == 'passed':
                gsk_status = "P"
                row.append(gsk_status)
            elif record.gsk_oral_prac_attendance == 'absent':
                    gsk_status = "A"
                    row.append(gsk_status)
            else:
                gsk_status = "F"
                row.append(gsk_status)
                    
            if record.mek_oral_prac_carry_forward and record.mek_oral_prac_status == 'passed':
                mek_status = "AP"
                row.append(mek_status)
            elif record.mek_oral_prac_status == 'passed':
                mek_status = "P"
                row.append(mek_status)
            elif record.mek_oral_prac_attendance == 'absent':
                    mek_status = "A"
                    row.append(mek_status)
            else:
                mek_status = "F"
                row.append(mek_status)
            
            if record.mek_online_carry_forward and record.mek_online_status == 'passed':
                mek_online_status = "AP"
                row.append(mek_online_status)
            elif record.mek_online_status == 'passed':
                mek_online_status = "P"
                row.append(mek_online_status)
            elif record.mek_online_attendance == 'absent':
                    mek_online_status = "A"
                    row.append(mek_online_status)
            else:
                mek_online_status = "F"
                row.append(mek_online_status)
            
            if record.gsk_online_carry_forward and record.gsk_online_status == 'passed':
                gsk_online_status = "AP"
                row.append(gsk_online_status)
            elif record.gsk_online_status == 'passed':
                gsk_online_status = "P"
                row.append(gsk_online_status)
            elif record.gsk_online_attendance == 'absent':
                    gsk_online_status = "A"
                    row.append(gsk_online_status)
            else:
                gsk_online_status = "F"
                row.append(gsk_online_status)
            
            allowed_values = {'AP', 'A'}

            # Convert the record to a set to find unique values
            unique_values = set(row)
            # absent_status = False
            # Check if the unique values are a subset of allowed values
            if unique_values.issubset(allowed_values) and len(unique_values) <= len(allowed_values):
                record.absent_status_repeater = 'absent'
            else:
                record.absent_status_repeater = 'present'
                
                # absent = absent + 1
    
    @api.depends('gsk_oral_prac_attendance','gsk_online_attendance','mek_oral_prac_attendance','mek_online_attendance')
    def _compute_absent_status(self):
        for record in self:
            
            if record.gsk_oral_prac_attendance == 'absent' and record.gsk_online_attendance == 'absent' and record.mek_oral_prac_attendance == 'absent' and record.mek_online_attendance == 'absent':
                record.absent_status = "absent"
            elif record.gsk_oral_prac_attendance == 'absent' or record.gsk_online_attendance == 'absent' or record.mek_oral_prac_attendance == 'absent' or record.mek_online_attendance == 'absent':
                record.absent_status = "present"
            else:
                 record.absent_status = "present"

    hold_admit_card = fields.Boolean("Pending Admit Card", default=False,tracking=True)
    hold_certificate = fields.Boolean("Hold Certificate", default=False,tracking=True)

    exam_date = fields.Date(string="Exam Date",tracking=True)
    exam_date_practical = fields.Date(string="Exam Date Practical",tracking=True)
    exam_date_practical_to = fields.Date(string="Exam Date Practical",tracking=True)
    exam_date_online = fields.Date(string="Exam Date Online",tracking=True)
    exam_date_online_to = fields.Date(string="Exam Date Online",tracking=True)

    ceo_override = fields.Boolean("CEO Override", related='gp_candidate.ceo_override',store=True,tracking=True)

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ],string="Gender",related='gp_candidate.gender',store=True,tracking=True)

    gsk_online_assignment_id = fields.Many2one("exam.type.oral.practical.examiners",string="GSK Online Assignment",tracking=True)
    mek_online_assignment_id = fields.Many2one("exam.type.oral.practical.examiners",string="MEK Online Assignment",tracking=True)
    gsk_oral_prac_assignment_id = fields.Many2one("exam.type.oral.practical.examiners",string="GSK Practical & Oral Assignment",tracking=True)
    mek_oral_prac_assignment_id = fields.Many2one("exam.type.oral.practical.examiners",string="MEK Practical & Oral Assignment",tracking=True)

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
    @api.model
    def action_open_gp_admit_card_release_wizard(self, exam_ids=None):
        view_id = self.env.ref('bes.view_release_admit_card_form_gp').id
        # import wdb; wdb.set_trace();
        dgs_batch = self.env['gp.exam.schedule'].browse(exam_ids).dgs_batch.id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Release GP Admit Card',
            'res_model': 'gp.admit.card.release',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {
                'default_exam_ids': exam_ids,
                'default_dgs_batch': dgs_batch
            }
        }


    
    def format_name(self,name):
        words = name.split()
        capitalized_words = [word.capitalize() for word in words]
        formatted_name = ' '.join(capitalized_words)
        return formatted_name
    
    def approve_violation(self):
        
        self.exam_violation_state = 'approved'
        self.gp_candidate.user_id.sudo().write({'active':False})
        
        if self.attempting_gsk_oral_prac:
            self.gsk_oral_prac_status = 'failed'

        if self.attempting_mek_oral_prac:
            self.mek_oral_prac_status = 'failed'
        
        if self.attempting_gsk_online:
            self.gsk_online_status = 'failed'
        
        if self.attempting_mek_online:
            self.mek_online_status = 'failed'
        
        self.state = '4-pending'
        
    
    def report_integrity_violation(self):
        
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Report Integrity Violation',
            'res_model': 'candidate.integrity.violation.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('bes.candidate_integrity_violation_wizard_form').id,
            'target': 'new',
            'context': {
                },
        }
    
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

    @api.depends('gsk_oral.gsk_oral_remarks','gsk_prac.gsk_practical_remarks')
    def _compute_attendance_gsk(self):
        for record in self:
            # import wdb; wdb.set_trace();
            if record.gsk_oral.gsk_oral_remarks and record.gsk_prac.gsk_practical_remarks:
                if record.gsk_oral.gsk_oral_remarks.lower() == 'absent' and record.gsk_prac.gsk_practical_remarks.lower()  == 'absent':
                    record.gsk_oral_prac_attendance = 'absent'
                else:
                    record.gsk_oral_prac_attendance = 'present'
            else:
                record.gsk_oral_prac_attendance = ''
            
    
    @api.depends('mek_oral.mek_oral_remarks','mek_prac.mek_practical_remarks')
    def _compute_attendance_mek(self):
        for record in self:
            if record.mek_oral.mek_oral_remarks and record.mek_prac.mek_practical_remarks:
                if record.mek_oral.mek_oral_remarks.lower() == 'absent' and record.mek_prac.mek_practical_remarks.lower()  == 'absent':
                    record.mek_oral_prac_attendance = 'absent'
                else:
                    record.mek_oral_prac_attendance = 'present'
            else:
                record.mek_oral_prac_attendance = ''
            

    def open_reset_online_exam_wizard(self):
        view_id = self.env.ref('bes.reset_online_exam_wizard').id
        print(self.env.context)
        print("model")
        print(self.env.context.get("model"))
        
        
        return {
            'name': 'Reset Online Exam Wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'reset.online.exam.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                "default_model": "gp.exam.schedule"
                }
        }

            



    @api.depends('certificate_criteria')
    def _compute_result_status(self):
        for record in self:
            # print(record.state)
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


    
    

    
    @api.depends('overall_percentage','state')
    def _compute_rank(self):
           for record in self:
               if record.overall_percentage > 0:
                   sorted_records = self.env['gp.exam.schedule'].search([
                        ('dgs_batch','=',record.dgs_batch.id),
                        ('attempt_number','=',1),
                        ('state','=','3-certified')
                    ], order='overall_percentage desc, institute_code asc, gp_candidate asc')

                   
                   total_records = len(sorted_records)
                   top_25_percent = int(total_records * 0.25)
   
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
               else:
                   record.rank = "0th"
    
    



    
    @api.depends('state')
    def compute_dgs_visible(self):
        for record in self:
            if record.certificate_criteria == 'passed' and record.state == '2-done' or record.state == '4-pending' :
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
        
        if self.attempting_gsk_oral_prac and not self.gsk_oral_prac_assignment:
            self.gsk_oral_prac_attendance = 'absent'
        
        if self.attempting_mek_oral_prac and not self.mek_oral_prac_assignment:
            self.mek_oral_prac_attendance = 'absent'
        
        if self.exam_violation_state == 'na':
        
            
            mek_oral_draft_confirm = self.mek_oral.mek_oral_draft_confirm == 'confirm'
            mek_practical_draft_confirm = self.mek_prac.mek_practical_draft_confirm == 'confirm'
            gsk_oral_draft_confirm = self.gsk_oral.gsk_oral_draft_confirm == 'confirm'
            gsk_practical_draft_confirm = self.gsk_prac.gsk_practical_draft_confirm == 'confirm'
            
            gsk_online_done = self.gsk_online.state == 'done' 
            mek_online_done = self.mek_online.state == 'done'
            
            print((len(self.gsk_oral) == 0 and len(self.gsk_prac) == 0))
            
            if not (len(self.mek_oral) == 0 and len(self.mek_prac) == 0) or not (len(self.gsk_oral) == 0 and len(self.gsk_prac) == 0) or not (len(self.gsk_online) == 0) or not (len(self.mek_online) == 0)  :
                print("We reached")
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
                        error_msg = _("MEK Oral Or Practical Not Confirmed for'%s'") % (self.gp_candidate.candidate_code)
                        print(error_msg)

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
                        # raise ValidationError("GSK Oral Or Practical Not Confirmed :"+str(self.gp_candidate.candidate_code))
                        error_msg = _("GSK Oral Or Practical Not Confirmed : '%s'") % (self.gp_candidate.candidate_code)
                        print(error_msg)
                
                if not (len(self.gsk_online) == 0):
                # if False:
                    
                    if gsk_online_done:
                    
                        self.gsk_online_marks = self.gsk_online.scoring_total
                        self.gsk_online_percentage = (self.gsk_online_marks/75)*100
                        
                        if self.gsk_online_percentage >= 60 :
                            self.gsk_online_status = 'passed'
                        else:
                            self.gsk_online_status = 'failed'
                    else:
                        # raise ValidationError("GSK Online Exam Not Done or Confirmed :"+str(self.gp_candidate.candidate_code))
                        error_msg = _("GSK Online Exam Not Done or Confirmed : '%s'") % (self.gp_candidate.candidate_code)
                        print(error_msg)
                        self.gsk_online_status = 'failed'
                
                else:
                    # self.gsk_online_marks = self.gsk_online.scoring_total
                    self.gsk_online_percentage = (self.gsk_online_marks/75)*100
                    if self.gsk_online_percentage >= 60 :
                        self.gsk_online_status = 'passed'
                    else:
                        self.gsk_online_status = 'failed'

                # if False:
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
                        # raise ValidationError("MEK Online Exam Not Done or Confirmed :"+str(self.gp_candidate.candidate_code))
                        error_msg = _("MEK Online Exam Not Done or Confirmed : '%s'") % (self.gp_candidate.candidate_code)
                        print(error_msg)
                        self.mek_online_status = 'failed'
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
                # if mek_oral_draft_confirm and mek_practical_draft_confirm and gsk_oral_draft_confirm and gsk_practical_draft_confirm and gsk_online_done and mek_online_done:

                if True:

                
                    mek_oral_marks = self.mek_oral_marks
                    self.mek_oral_marks = mek_oral_marks
                    mek_practical_marks = self.mek_practical_marks
                    self.mek_practical_marks = mek_practical_marks
                    mek_total_marks = mek_oral_marks + mek_practical_marks
                    self.mek_total = mek_total_marks
                    self.mek_percentage = (mek_total_marks/175) * 100
                    self.mek_online_marks = self.mek_online_marks
                    self.mek_online_percentage = (self.mek_online_marks/75)*100
                    
                    
                    
                    if self.mek_percentage >= 60:
                        self.mek_oral_prac_status = 'passed'
                    else:
                        self.mek_oral_prac_status = 'failed'


                    gsk_oral_marks = self.gsk_oral_marks
                    self.gsk_oral_marks = gsk_oral_marks
                    gsk_practical_marks = self.gsk_practical_marks
                    self.gsk_practical_marks = gsk_practical_marks
                    gsk_total_marks = gsk_oral_marks + gsk_practical_marks
                    self.gsk_total = gsk_total_marks
                    self.gsk_percentage = (gsk_total_marks/175) * 100
                    self.gsk_online_marks = self.gsk_online_marks
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

                else:
                    print("Exam_ID" + self.exam_id)
                    raise ValidationError("Exam ID "+str(self.exam_id)+" Not All exam are Confirmed")
        else:
            pass




        
    def move_done(self):
                # import wdb; wdb.set_trace();
        
        
        if self.attempting_gsk_oral_prac and not self.gsk_oral_prac_assignment:
            self.gsk_oral_prac_attendance = 'absent'
            self.gsk_oral_prac_status = 'failed'
        
        if self.attempting_mek_oral_prac and not self.mek_oral_prac_assignment:
            self.mek_oral_prac_attendance = 'absent'
            self.mek_oral_prac_status = 'failed'
                
        if self.attempting_gsk_online and not self.gsk_online_assignment:
            self.gsk_online_attendance = 'absent'
            self.gsk_online_status = 'failed'
        
        if self.attempting_mek_online and not self.mek_online_assignment:
            self.mek_online_attendance = 'absent'
            self.mek_online_status = 'failed'

        if self.exam_violation_state == 'na':
        

            mek_oral_draft_confirm = self.mek_oral.mek_oral_draft_confirm == 'confirm'
            mek_practical_draft_confirm = self.mek_prac.mek_practical_draft_confirm == 'confirm'
            gsk_oral_draft_confirm = self.gsk_oral.gsk_oral_draft_confirm == 'confirm'
            gsk_practical_draft_confirm = self.gsk_prac.gsk_practical_draft_confirm == 'confirm'
            
            gsk_online_done = self.gsk_online.state == 'done' 
            mek_online_done = self.mek_online.state == 'done'
            
            print((len(self.gsk_oral) == 0 and len(self.gsk_prac) == 0))
            
            if not (len(self.mek_oral) == 0 and len(self.mek_prac) == 0) or not (len(self.gsk_oral) == 0 and len(self.gsk_prac) == 0) or not (len(self.gsk_online) == 0) or not (len(self.mek_online) == 0)  :
                print("We reached")
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
                        error_msg = _("MEK Oral Or Practical Not Confirmed for'%s'") % (self.gp_candidate.candidate_code)
                        print(error_msg)
                        # raise ValidationError("MEK Oral Or Practical Not Confirmed")

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
                        print("Exam_ID" + self.exam_id)
                        error_msg = _("GSK Oral Or Practical Not Confirmed : '%s'") % (self.gp_candidate.candidate_code)
                        print(error_msg)
                        # raise ValidationError("GSK Oral Or Practical Not Confirmed :"+str(self.exam_id))
                
                if not (len(self.gsk_online) == 0):
                # if False:
                    
                    if gsk_online_done:
                    
                        self.gsk_online_marks = self.gsk_online.scoring_total
                        self.gsk_online_percentage = (self.gsk_online_marks/75)*100
                        
                        if self.gsk_online_percentage >= 60 :
                            self.gsk_online_status = 'passed'
                        else:
                            self.gsk_online_status = 'failed'
                    else:
                        print("Exam_ID" + self.exam_id)
                        error_msg = _("GSK Online Exam Not Done or Confirmed : '%s'") % (self.gp_candidate.candidate_code)
                        print(error_msg)
                        self.gsk_online_status = 'failed'
                        # raise ValidationError("GSK Online Exam Not Done or Confirmed")
                
                else:
                    # self.gsk_online_marks = self.gsk_online.scoring_total
                    self.gsk_online_percentage = (self.gsk_online_marks/75)*100
                    if self.gsk_online_percentage >= 60 :
                        self.gsk_online_status = 'passed'
                    else:
                        self.gsk_online_status = 'failed'
                
                
                print("MEK ONline")
                print(not (len(self.mek_online) == 0))
                
                
                # if False:
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
                        print("Exam_ID" + self.exam_id)
                        error_msg = _("MEK Online Exam Not Done or Confirmed : '%s'") % (self.gp_candidate.candidate_code)
                        print(error_msg)
                        self.mek_online_status = 'failed'
                        # raise ValidationError("MEK Online Exam Not Done or Confirmed")
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
                # if mek_oral_draft_confirm and mek_practical_draft_confirm and gsk_oral_draft_confirm and gsk_practical_draft_confirm and gsk_online_done and mek_online_done:

                if True:

                
                    mek_oral_marks = self.mek_oral_marks
                    self.mek_oral_marks = mek_oral_marks
                    mek_practical_marks = self.mek_practical_marks
                    self.mek_practical_marks = mek_practical_marks
                    mek_total_marks = mek_oral_marks + mek_practical_marks
                    self.mek_total = mek_total_marks
                    self.mek_percentage = (mek_total_marks/175) * 100
                    self.mek_online_marks = self.mek_online_marks
                    self.mek_online_percentage = (self.mek_online_marks/75)*100
                    
                    
                    
                    if self.mek_percentage >= 60:
                        self.mek_oral_prac_status = 'passed'
                    else:
                        self.mek_oral_prac_status = 'failed'


                    gsk_oral_marks = self.gsk_oral_marks
                    self.gsk_oral_marks = gsk_oral_marks
                    gsk_practical_marks = self.gsk_practical_marks
                    self.gsk_practical_marks = gsk_practical_marks
                    gsk_total_marks = gsk_oral_marks + gsk_practical_marks
                    self.gsk_total = gsk_total_marks
                    self.gsk_percentage = (gsk_total_marks/175) * 100
                    self.gsk_online_marks = self.gsk_online_marks
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
                    # raise ValidationError("Exam ID "+str(self.exam_id)+" Not All exam are Confirmed")
        else:
            pass

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
        
        user_id = self.env.user
        # import wdb; wdb.set_trace()
        if user_id.has_group('bes.download_not_allowed'):
            # User is in the group
            raise ValidationError("Please Contact Administrator")

        
        if docs1.certificate_criteria == 'passed' and docs1.certificate_id:
            return {
                'docids': docids,
                'doc_model': 'gp.exam.schedule',
                'data': data,
                'docs': docs1
            }
        else:
            raise ValidationError("Certificate criteria not met. Report cannot be generated.")


class CcmcAdmitCardRelease(models.TransientModel):
    _name = 'ccmc.admit.card.release'
    _description = 'CCMC Admit Card Release'

    exam_ids = fields.Many2many('ccmc.exam.schedule', string='Exams')
    admit_card_type = fields.Selection([
        ('gp', 'GP'),
        ('ccmc', 'CCMC')
    ], string='Admit Card Type', default='ccmc')
    exam_region = fields.Many2one('exam.center', string='Region')
    candidates_count = fields.Integer(string='Candidates Processed', readonly=True)
    result_message = fields.Text(string='Result', readonly=True)

    exam_date_practical = fields.Date(string="Exam Date Practical/Oral From",tracking=True)
    exam_date_practical_to = fields.Date(string="Exam Date Practical/Oral To",tracking=True)
    exam_date_online = fields.Date(string="Exam Date Online From",tracking=True)
    exam_date_online_to = fields.Date(string="Exam Date Online To",trcking=True)
    dgs_batch = fields.Many2one('dgs.batches', string='DGS Batch', readonly=True)
    check_batch = fields.Selection([('invisible', 'Invisible'), ('required', 'Required')],compute='_compute_check_batch')

    @api.depends('dgs_batch')
    def _compute_check_batch(self):
        
        if self.dgs_batch.is_current_batch or not self.dgs_batch.is_march_september and not self.dgs_batch.repeater_batch:
            self.check_batch = 'invisible'
        elif self.dgs_batch.repeater_batch and not self.dgs_batch.is_march_september and not self.dgs_batch.is_current_batch:
            self.check_batch = 'required'
        else:
            self.check_batch = 'invisible'

    def release_ccmc_admit_card(self, *args, **kwargs):
        exam_ids = self.env.context.get('active_ids')
        candidates = self.env["ccmc.exam.schedule"].sudo().browse(exam_ids)
        
        # Count candidates who have already had their admit cards released
        already_released_count = len(candidates.filtered(lambda c: not c.hold_admit_card))

        count = 0
        for candidate in candidates:
            mumbai_region = candidate.dgs_batch.mumbai_region
            kolkata_region = candidate.dgs_batch.kolkatta_region
            chennai_region = candidate.dgs_batch.chennai_region
            delhi_region = candidate.dgs_batch.delhi_region
            kochi_region = candidate.dgs_batch.kochi_region
            goa_region = candidate.dgs_batch.goa_region
            is_march_september = candidate.dgs_batch.is_march_september

            # Check if the candidate meets the criteria for releasing the admit card
            if (candidate.stcw_criteria == 'passed' and candidate.attendance_criteria == 'passed' and candidate.ship_visit_criteria == 'passed') or candidate.ceo_override:
                # Determine the region-specific institute
                if is_march_september:
                    registered_institute = None
                    if candidate.exam_region.name == 'MUMBAI' and mumbai_region:
                        registered_institute = mumbai_region.id
                    elif candidate.exam_region.name == 'KOLKATA' and kolkata_region:
                        registered_institute = kolkata_region.id
                    elif candidate.exam_region.name == 'CHENNAI' and chennai_region:
                        registered_institute = chennai_region.id
                    elif candidate.exam_region.name == 'DELHI' and delhi_region:
                        registered_institute = delhi_region.id
                    elif candidate.exam_region.name == 'KOCHI' and kochi_region:
                        registered_institute = kochi_region.id
                    elif candidate.exam_region.name == 'GOA' and goa_region:
                        registered_institute = goa_region.id
                else:
                    registered_institute = candidate.institute_id.id
                # Only update if hold_admit_card is being set to False
                if candidate.hold_admit_card:
                    candidate.write({
                        'hold_admit_card': False,
                        'registered_institute': registered_institute,
                    })
                    count += 1  # Increment count only when hold_admit_card is updated to False

                # Update exam dates if not March/September
                if not is_march_september:
                    candidate.write({
                        'exam_date_practical': self.exam_date_practical,
                        'exam_date_practical_to': self.exam_date_practical_to,
                        'exam_date_online': self.exam_date_online,
                        'exam_date_online_to': self.exam_date_online_to,
                    })
            else:
                # If criteria are not met, set hold_admit_card to True
                candidate.write({'hold_admit_card': True})

            # Calculate the total number of candidates and those whose admit cards were already released
            total_candidates = len(exam_ids)
            message = f"CCMC Admit Card Released for {count} Candidates. Out of {total_candidates} selected candidates, {already_released_count} admit cards were already released."


        # Return a notification
        return {
                'name': 'Admit Card Released',
                'type': 'ir.actions.act_window',
                'res_model': 'batch.pop.up.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'context': {'default_message': message},
            }



class CCMCExam(models.Model):
    _name = "ccmc.exam.schedule"
    _rec_name = "exam_id"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'CCMC Schedule'
    
    dgs_batch = fields.Many2one("dgs.batches",string="Exam Batch",required=True,tracking=True)
    certificate_id = fields.Char(string="Certificate No.",tracking=True)
    institute_name = fields.Many2one("bes.institute","Institute Name",tracking=True)
    hold_admit_card = fields.Boolean("Pending Admit Card", default=False,tracking=True)
    hold_certificate = fields.Boolean("Hold Certificate", default=False,tracking=True)

    exam_region = fields.Many2one('exam.center',string='Exam Center',store=True)

    exam_id = fields.Char(string="Roll No", copy=False, readonly=True)
    registered_institute = fields.Many2one("bes.institute",string="Examination Center",tracking=True)
    
    ccmc_candidate = fields.Many2one("ccmc.candidate","CCMC Candidate",tracking=True)
    candidate_code = fields.Char(string="Candidate Code", related='ccmc_candidate.candidate_code',store=True,tracking=True)
    institute_id = fields.Many2one("bes.institute",related='ccmc_candidate.institute_id',string="Institute",store=True,tracking=True)

    ip_address = fields.Char(string='IP Address')    

    cookery_bakery = fields.Many2one("ccmc.cookery.bakery.line","Cookery And Bakery",tracking=True)
    ccmc_oral = fields.Many2one("ccmc.oral.line","CCMC Oral",tracking=True)
    ccmc_gsk_oral = fields.Many2one("ccmc.gsk.oral.line","CCMC GSK Oral",tracking=True)
    
    ccmc_oral_prac_assignment = fields.Boolean('ccmc_oral_prac_assignment',tracking=True)

    ccmc_gsk_oral_assignment = fields.Boolean('ccmc_gsk_oral_assignment',tracking=True)
    
    ccmc_online = fields.Many2one("survey.user_input",string="CCMC Online",tracking=True)
    
    ccmc_online_assignment = fields.Boolean('ccmc_online_assignment',tracking=True)

    attempt_number = fields.Integer("Attempt Number",tracking=True)
    
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
    
    attempted_ccmc_online = fields.Boolean("Attempted CCMC Online",tracking=True)
    
    cookery_oral = fields.Float("Catering",readonly=True,tracking=True)
    
    
    ccmc_gsk_oral_marks = fields.Float("GSK Oral",readonly=True,tracking=True)
    ccmc_oral_percentage = fields.Float("Catering Percentage",readonly=True,tracking=True)
    ccmc_gsk_oral_percentage = fields.Float("GSK Oral Percentage",readonly=True,tracking=True)
    
    # Attempting Exams
    attempting_cookery = fields.Boolean("Attempting Cookery Bakery",tracking=True)
    attempting_oral = fields.Boolean("Attempting CCMC Oral",tracking=True)
    attempting_online = fields.Boolean("Attempting CCMC Online",tracking=True)
    
    ccmc_oral_prac_status = fields.Selection([
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='CCMC Oral Status',default="pending",tracking=True)
    
    ccmc_catering_status = fields.Selection([
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='Catering Status',default="pending",tracking=True)
    
    ccmc_gsk_status = fields.Selection([
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='GSK Status',default="pending",tracking=True)
    
    
    token = fields.Char(string='Online Token',tracking=True)
    
    ccmc_online_token_used = fields.Boolean("CCMC Online Token Used",tracking=True)
    
    def generate_token(self):
        return random.randint(100000, 999999)
    
    ccmc_gsk_oral_prac_status = fields.Selection([
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='CCMC GSK Oral Status',default="pending",tracking=True)
    
    oral_prac_status = fields.Selection([
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='Oral/Prac Status',store=True,compute="compute_oral_prac_status",tracking=True)
    
    attendance_criteria = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Passed'),
    ], string='Attendance Criteria' ,related='ccmc_candidate.attendance_criteria')

    
    
    exam_criteria = fields.Selection([
        ('', ''),
        ('pending', 'Pending'),
        ('passed', 'Passed'),
    ], string='Exam Status' , compute="compute_certificate_criteria")
    
    ccmc_online_status = fields.Selection([
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('passed', 'Passed'),
    ], string='CCMC Online Status',default="pending",tracking=True)
    
    # admit_card_status = fields.Selection([
    #     ('pending', 'Pending'),
    #     ('issued', 'Issued')
    # ],default="pending", string='Admit Card Status',store=True,related='ccmc_candidate.institute_batch_id.admit_card_status')
    
    
    stcw_criteria = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Passed'),
    ], string='STCW Criteria',store=True,related='ccmc_candidate.stcw_criteria',tracking=True)

    ship_visit_criteria = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Passed'),
    ], string='Ship Visit Criteria',related='ccmc_candidate.ship_visit_criteria')
    
    exam_violation_state = fields.Selection([
        ('na', 'N/A'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
    ], string='Exam Violation', default='na',tracking=True)
    
    
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
    ], string='Certificate Criteria',compute="compute_pending_certificate_criteria")
    
    user_state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], string='User Status', related='ccmc_candidate.ccmc_user_state', required=True,tracking=True)

    result_status = fields.Selection([
        ('absent','Absent'),
        ('pending','Pending'),
        ('failed','Failed'),
        ('passed','Passed'),
    ],string='Result',compute='_compute_result_status')
    
    result = fields.Selection([
        ('failed','Failed'),
        ('passed','Passed'),
    ],string='Result Status',store=True,compute='_compute_result_status_2')
    
    exam_date = fields.Date(string="Exam Date",tracking=True)
    exam_date_practical = fields.Date(string="Exam Date Practical",tracking=True)
    exam_date_practical_to = fields.Date(string="Exam Date Practical",tracking=True)
    exam_date_online = fields.Date(string="Exam Date Online",tracking=True)
    exam_date_online_to = fields.Date(string="Exam Date Online",tracking=True)
    
    is_processed = fields.Boolean(string="Processed", default=False)

    online_start_time = fields.Datetime("Start Time")
    online_end_time = fields.Datetime("End Time")
    @api.depends('certificate_criteria')
    def _compute_result_status_2(self):
        for record in self:
            
            if record.certificate_criteria == 'passed':
                record.result = 'passed'
            else:
                record.result = 'failed'
    
    edit_marksheet_status = fields.Boolean('edit_marksheet_status',compute='_compute_is_in_group')
    
    edit_register_institute = fields.Boolean(
        string="Can Edit Institute",
        compute="_compute_edit_register_institute",
        store=False  # Don't store as it's computed on the fly
    )

    @api.depends_context('uid')  # Depends on current user
    def _compute_edit_register_institute(self):
        can_edit = self.env.user.has_group('bes.group_bes_coo')
        for record in self:
            record.edit_register_institute = can_edit

    @api.depends_context('uid')  # Depends on current user
    def _compute_is_in_group(self):
        for record in self:
            user = self.env.user
            group_xml_ids = ['bes.edit_marksheet_status']
            record.edit_marksheet_status = any(user.has_group(group) for group in group_xml_ids)

    
    url = fields.Char("URL",compute="_compute_url",tracking=True)
    qr_code = fields.Binary(string="QR Code", compute="_compute_url", store=True,tracking=True)
    certificate_qr_code = fields.Binary(string=" Certificate QR Code", compute="_compute_certificate_url",tracking=True)

    dgs_visible = fields.Boolean("DGS Visible",compute="compute_dgs_visible",tracking=True)
    
    exam_pass_date = fields.Date(string="Date of Examination Passed:",tracking=True)
    certificate_issue_date = fields.Date(string="Date of Issue of Certificate:",tracking=True)
    ccmc_rank = fields.Char("Rank",compute='_compute_rank',tracking=True)
    
    fees_paid_candidate = fields.Char("Fees Paid by Candidate",tracking=True,compute="_fees_paid_by_candidate",store=True)

    
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ],string="Gender",related='ccmc_candidate.gender',store=True,tracking=True)
    
    def _fees_paid_by_candidate(self):
        for rec in self:
            # last_exam = self.env['gp.exam.schedule'].search([('gp_candidate','=',rec.id)], order='attempt_number desc', limit=1)
            # last_exam_dgs_batch = last_exam.dgs_batch.id
            invoice = self.env['account.move'].sudo().search([('repeater_exam_batch','=',rec.dgs_batch.id),('ccmc_candidate','=',rec.ccmc_candidate.id)],order='date desc')
            if invoice:
                batch = invoice.repeater_exam_batch.to_date.strftime("%B %Y")
                if invoice.payment_state == 'paid':
                    rec.fees_paid_candidate = batch + ' - Paid'
                else:
                    rec.fees_paid_candidate = batch + ' - Not Paid'
            else:
                rec.fees_paid_candidate = 'No Fees Paid'
    
    institute_code = fields.Char("Institute code",related='ccmc_candidate.institute_id.code',store=True,tracking=True)
    indos_no = fields.Char(string="INDoS No", related='ccmc_candidate.indos_no',store=True,tracking=True)
    
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
    
    absent_status = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
    ],compute="_compute_absent_status",string="Absent Status",store=True)
    
    @api.depends('cookery_prac_attendance','cookery_prac_carry_forward','cookery_gsk_online_carry_forward','cookery_oral_carry_forward','ccmc_gsk_oral_attendance','ccmc_online_attendance','cookery_bakery_prac_status','ccmc_oral_prac_status','ccmc_online_status')
    def _compute_absent_status(self):
        for record in self:
            row = []
            if record.cookery_prac_carry_forward and record.cookery_bakery_prac_status == 'passed':
                cookery_prac_status = "AP"
                row.append(cookery_prac_status)
            elif record.cookery_bakery_prac_status == "passed":
                cookery_prac_status = "P"
                row.append(cookery_prac_status)
            elif record.cookery_prac_attendance == 'absent':
                cookery_prac_status = "A"
                row.append(cookery_prac_status)
            else:
                cookery_prac_status = "F"
                row.append(cookery_prac_status)
            
            if record.cookery_oral_carry_forward and record.ccmc_oral_prac_status == 'passed':
                ccmc_oral_prac_status = "AP"
                row.append(ccmc_oral_prac_status)
            elif record.ccmc_oral_prac_status == "passed":
                ccmc_oral_prac_status = "P"
                row.append(ccmc_oral_prac_status)
            elif record.ccmc_gsk_oral_attendance == "absent":
                ccmc_oral_prac_status = "A"
                row.append(ccmc_oral_prac_status)
            else:
                ccmc_oral_prac_status = "F"
                row.append(ccmc_oral_prac_status)
                
            if record.cookery_gsk_online_carry_forward and record.ccmc_online_status == 'passed':
                ccmc_online_status = "AP"
                row.append(ccmc_online_status)
            elif record.ccmc_online_status == "passed":
                ccmc_online_status = "P"
                row.append(ccmc_online_status)
            elif record.ccmc_online_attendance == 'absent':
                ccmc_online_status = "A"
                row.append(ccmc_online_status)
            else:
                ccmc_online_status = "F"
                row.append(ccmc_online_status)
            
            allowed_values = {'AP', 'A'}
            
            print(row)      
            
            unique_values = set(row)
            # if record.exam_id == '17002':
            #     print("unique Values")
            #     print("17002")       
            # print(record.exam_id)      
            # print(unique_values)
            # print(unique_values.issubset(allowed_values) and len(unique_values) <= len(allowed_values))                    
            if unique_values.issubset(allowed_values) and len(unique_values) <= len(allowed_values):
                # absent = absent + 1
                record.absent_status = 'absent'
            else:
                record.absent_status = 'present'
            
            
            
            # if record.cookery_prac_attendance == 'absent' and record.ccmc_gsk_oral_attendance == 'absent' and record.ccmc_online_attendance == 'absent':
            #     record.absent_status = "absent"
            # elif record.cookery_prac_attendance == 'absent' or record.ccmc_gsk_oral_attendance == 'absent' or record.ccmc_online_attendance == 'absent':
            #     record.absent_status = "present"
            # else:
            #     record.absent_status = "present"
    
    cookery_prac_attendance = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
    ],string="Cookery Prac Attendance",tracking=True)
    
    ccmc_oral_attendance = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
    ],string="Cookery Oral Attendance",tracking=True)
    
    ccmc_gsk_oral_attendance = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
    ],string="CCMC GSK Oral Attendance",tracking=True)
    
    ccmc_online_attendance = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
    ],string="Cookery Online Attendance",tracking=True)

    ceo_override = fields.Boolean("CEO Override", related='ccmc_candidate.ceo_override',store=True,tracking=True)
    ccmc_online_assignment_id = fields.Many2one("exam.type.oral.practical.examiners",string="CCMC Online Assignment",tracking=True)
    ccmc_practical_assignment_id = fields.Many2one("exam.type.oral.practical.examiners",string="CCMC Practical Assignment",tracking=True)
    ccmc_oral_assignment_id = fields.Many2one("exam.type.oral.practical.examiners",string="CCMC Oral Assignment",tracking=True)
    ccmc_gsk_oral_assignment_id = fields.Many2one("exam.type.oral.practical.examiners",string="CCMC GSK Oral Assignment",tracking=True)
    
    def open_reset_online_exam_wizard(self):
        view_id = self.env.ref('bes.reset_online_exam_wizard').id

        
        
        return {
            'name': 'Reset Online Exam Wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'reset.online.exam.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                "default_model": "ccmc.exam.schedule"
                }
        }

    @api.model
    def action_open_ccmc_admit_card_release_wizard(self, exam_ids=None):
        view_id = self.env.ref('bes.view_release_admit_card_form_ccmc').id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Release CCMC Admit Card',
            'res_model': 'ccmc.admit.card.release',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {
                'default_exam_ids': exam_ids,
            }
        }

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
        

    def HoldAdmitCard(self):
        self.sudo().write({
            'hold_admit_card': True,
        })

    def ReleaseAdmitCard(self):
        self.sudo().write({
            'hold_admit_card': False,
        })


    def HoldCertificate(self):
        self.sudo().write({
            'hold_certificate':True
        })

    def ReleaseCertificate(self):
        self.sudo().write({
            'hold_certificate':False
        })

    def approve_violation(self):
        
        self.exam_violation_state = 'approved'
        self.ccmc_candidate.user_id.sudo().write({'active':False})
        
        if self.attempting_cookery:
            self.cookery_bakery_prac_status = 'failed'
        
        if self.attempting_oral:
            self.ccmc_oral_prac_status = 'failed'
        
        if self.attempting_oral:
            self.attempting_online = 'failed'
        
        self.state = '4-pending'
    
    def format_name(self,name):
        # Split the name into words
        words = name.split()
        
        # Capitalize each word
        capitalized_words = [word.capitalize() for word in words]
        
        # Join the capitalized words back into a single string
        formatted_name = ' '.join(capitalized_words)
        
        return formatted_name
        
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
    
    def report_integrity_violation(self):
        
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Report Integrity Violation',
            'res_model': 'candidate.integrity.violation.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('bes.candidate_integrity_violation_wizard_form').id,
            'target': 'new',
            'context': {
                },
        }            
            
            
        
    
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

    
    @api.depends('stcw_criteria','ship_visit_criteria','cookery_bakery_prac_status','ccmc_online_status','ccmc_gsk_oral_prac_status')
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
    
    @api.depends('overall_percentage','state')
    def _compute_rank(self):
           for record in self:
               if record.overall_percentage > 0:
                   sorted_records = self.env['ccmc.exam.schedule'].search([
                       ('dgs_batch','=',record.dgs_batch.id),
                       ('attempt_number','=',1),
                       ('state','=','3-certified')
                   ], order='overall_percentage desc, institute_code asc, ccmc_candidate asc')
                   
                   total_records = len(sorted_records)
                   top_25_percent = int(total_records * 0.25)
   
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
               else:
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
        if self.attempting_cookery and not self.ccmc_oral_prac_assignment:
            self.cookery_prac_attendance = 'absent'
        
        if self.attempting_oral and not self.ccmc_gsk_oral_assignment:
            self.ccmc_oral_attendance = 'absent'
            self.ccmc_gsk_oral_attendance = 'absent'
            
        if self.attempting_online and not self.ccmc_online_assignment:
            self.ccmc_online_attendance = 'absent'
        
        if self.exam_violation_state == 'na': 
         
            cookery_draft_confirm = self.cookery_bakery.cookery_draft_confirm == 'confirm'
            ccmc_oral_state = self.ccmc_oral.ccmc_oral_draft_confirm == 'confirm'
            ccmc_gsk_oral_state = self.ccmc_gsk_oral.ccmc_oral_draft_confirm == 'confirm'
            ccmc_online_state = self.ccmc_online.state == 'done'
            ccmc_gsk_marks =  self.ccmc_gsk_oral.toal_ccmc_oral_rating
            self.ccmc_oral._compute_ccmc_rating_total()
            self.ccmc_gsk_oral._compute_ccmc_rating_total()
            
            # if not (len(self.cookery_bakery)==0 and len(self.ccmc_oral)==0 and len(self.ccmc_gsk_oral) == 0) or not (len(self.ccmc_online)==0):
            if not (len(self.cookery_bakery)==0) or not (len(self.ccmc_oral)==0 and len(self.ccmc_gsk_oral) == 0) or not (len(self.ccmc_online)==0):

                print("Wokring")
                # if not (len(self.cookery_bakery)==0 and len(self.ccmc_oral)==0 and len(self.ccmc_gsk_oral) == 0 ):
                    
                if not (len(self.cookery_bakery)==0):
                    if cookery_draft_confirm:
                        cookery_bakery_marks = self.cookery_bakery.total_mrks
                        self.cookery_practical = cookery_bakery_marks
                    else:
                        error_msg = _("Cookery/Bakery Not Confirmed for'%s'") % (self.ccmc_candidate.candidate_code)
                        print(error_msg)
                    
                print(not (len(self.ccmc_oral)==0 and len(self.ccmc_gsk_oral) == 0))
                if not (len(self.ccmc_oral)==0 and len(self.ccmc_gsk_oral) == 0):
                    if ccmc_oral_state:
                        print(ccmc_oral_state)
                        ccmc_oral_marks = self.ccmc_oral.toal_ccmc_rating 
                        self.cookery_oral = ccmc_oral_marks
                        
                        #GSK Oral Makrs
                        ccmc_gsk_marks =  self.ccmc_gsk_oral.toal_ccmc_oral_rating
                        self.ccmc_gsk_oral_marks = ccmc_gsk_marks
                    else:
                        error_msg = _("CCMC Oral  Not Confirmed for'%s'") % (self.ccmc_candidate.candidate_code)
                        print(error_msg)

                    
                    if cookery_draft_confirm and ccmc_oral_state and ccmc_gsk_oral_state:
                        cookery_bakery_marks = self.cookery_bakery.total_mrks
                        ccmc_oral_marks = self.ccmc_oral.toal_ccmc_rating 

                        self.cookery_oral = ccmc_oral_marks
                        self.cookery_practical = cookery_bakery_marks
                    else:
                        error_msg = _("CCMC Oral Or Practical Not Confirmed for'%s'") % (self.ccmc_candidate.candidate_code)
                        print(error_msg)
                    
                if not (len(self.ccmc_online)==0):
                    if ccmc_online_state:
                        cookery_gsk_online = self.ccmc_online.scoring_total
                        self.cookery_gsk_online = cookery_gsk_online
                    else:
                        error_msg = _("CCMC Online Not Confirmed for'%s'") % (self.ccmc_candidate.candidate_code)
                        print(error_msg)
                else:
                    cookery_gsk_online = self.cookery_gsk_online
                    self.cookery_gsk_online = cookery_gsk_online
                
                self.overall_marks = self.cookery_practical  + self.ccmc_gsk_oral_marks + self.cookery_oral + self.cookery_gsk_online
                
                #Percentage Calculation
                #  import wdb; wdb.set_trace(); 
                self.cookery_bakery_percentage = (self.cookery_practical/100) * 100
                self.ccmc_oral_percentage = (self.cookery_oral/80) * 100
                self.ccmc_gsk_oral_percentage = (self.ccmc_gsk_oral_marks/20) * 100
                
                self.cookery_gsk_online_percentage = (self.cookery_gsk_online/100) * 100
                self.overall_percentage = (self.overall_marks/300)*100
                
                
                if self.cookery_bakery_percentage >= 60:
                        self.cookery_bakery_prac_status = 'passed'
                else:
                        self.cookery_bakery_prac_status = 'failed'
                
                if self.ccmc_oral_percentage >= 60:
                        self.ccmc_catering_status = 'passed'
                else:
                        self.ccmc_catering_status = 'failed'
                
                if self.ccmc_gsk_oral_percentage >= 60:
                        self.ccmc_gsk_status = 'passed'
                else:
                        self.ccmc_gsk_status = 'failed'
                        
                if self.ccmc_oral_percentage < 60 or self.ccmc_gsk_oral_percentage < 60:
                    self.ccmc_oral_prac_status = 'failed'
                else:
                    self.ccmc_oral_prac_status = 'passed'
                    
                    
                if self.cookery_gsk_online_percentage  >= 60:
                    self.ccmc_online_status = 'passed'
                else:
                    self.ccmc_online_status = 'failed'
                        
                all_passed = all(field == 'passed' for field in [self.ccmc_oral_prac_status,self.cookery_bakery_prac_status,self.ccmc_online_status, self.exam_criteria , self.stcw_criteria , self.ship_visit_criteria , self.attendance_criteria,self.ccmc_gsk_oral_prac_status ])
                if all_passed:
                    self.write({'certificate_criteria':'passed'})
                else:
                    self.write({'certificate_criteria':'pending'})

            else:
            
                # import wdb; wdb.set_trace(); 
                # if cookery_draft_confirm and ccmc_oral_state and ccmc_gsk_oral_state and ccmc_online_state:
                if True:
                    
                    # All CCMC Marks
                    cookery_bakery_marks = self.cookery_practical
                    ccmc_oral_marks = self.cookery_oral
                    self.cookery_oral = ccmc_oral_marks
                    self.cookery_practical = cookery_bakery_marks
                    cookery_gsk_online = self.cookery_gsk_online                    
                    ccmc_gsk_marks =  self.ccmc_gsk_oral.toal_ccmc_oral_rating
                    self.ccmc_gsk_oral_marks = ccmc_gsk_marks

                    
                    self.cookery_gsk_online = cookery_gsk_online
                    self.overall_marks = ccmc_oral_marks + cookery_bakery_marks + cookery_gsk_online
                    
                    
                    
                    #All Percentage
                    self.cookery_bakery_percentage = (cookery_bakery_marks/100) * 100
                    self.ccmc_oral_percentage = (ccmc_oral_marks/100) * 100
                    self.ccmc_gsk_oral_percentage = (ccmc_gsk_marks/20) * 100
                    self.cookery_gsk_online_percentage = (cookery_gsk_online/100) * 100
                    self.overall_percentage = (self.overall_marks/300) * 100
                    
                    
                    if self.cookery_practical >= 60:
                        self.cookery_bakery_prac_status = 'passed'
                    else:
                        self.cookery_bakery_prac_status = 'failed'
                        
                    if self.ccmc_oral_percentage >= 60:
                            self.ccmc_catering_status = 'passed'
                    else:
                            self.ccmc_catering_status = 'failed'
                    
                    if self.ccmc_gsk_oral_percentage >= 60:
                            self.ccmc_gsk_status = 'passed'
                    else:
                            self.ccmc_gsk_status = 'failed'
                            
                    if self.ccmc_oral_percentage < 60 or self.ccmc_gsk_oral_percentage < 60:
                        self.ccmc_oral_prac_status = 'failed'
                    else:
                        self.ccmc_oral_prac_status = 'passed'
                    
                    
                    if self.cookery_gsk_online  >= 60:
                        self.ccmc_online_status = 'passed'
                    else:
                        self.ccmc_online_status = 'failed'
                        
                    all_passed = all(field == 'passed' for field in [self.ccmc_oral_prac_status,self.cookery_bakery_prac_status,self.ccmc_online_status, self.exam_criteria , self.stcw_criteria , self.ship_visit_criteria , self.attendance_criteria,self.ccmc_gsk_oral_prac_status ])

                    if all_passed:
                        self.write({'certificate_criteria':'passed'})
                    else:
                        self.write({'certificate_criteria':'pending'})
                        
                    
                else:
                    raise ValidationError("Not All exam are Confirmed")
        else:
            pass
    
    
    def move_done(self):
        
        if self.attempting_cookery and not self.ccmc_oral_prac_assignment:
            self.cookery_prac_attendance = 'absent'
        
        if self.attempting_oral and not self.ccmc_gsk_oral_assignment:
            self.ccmc_oral_attendance = 'absent'
            self.ccmc_gsk_oral_attendance = 'absent'
        
        # import wdb; wdb.set_trace();
        
        if self.exam_violation_state == 'na': 
         
            cookery_draft_confirm = self.cookery_bakery.cookery_draft_confirm == 'confirm'
            ccmc_oral_state = self.ccmc_oral.ccmc_oral_draft_confirm == 'confirm'
            ccmc_gsk_oral_state = self.ccmc_gsk_oral.ccmc_oral_draft_confirm == 'confirm'
            ccmc_online_state = self.ccmc_online.state == 'done'
            ccmc_gsk_marks =  self.ccmc_gsk_oral.toal_ccmc_oral_rating
            self.ccmc_oral._compute_ccmc_rating_total()
            self.ccmc_gsk_oral._compute_ccmc_rating_total()
            
            # if not (len(self.cookery_bakery)==0 and len(self.ccmc_oral)==0 and len(self.ccmc_gsk_oral) == 0) or not (len(self.ccmc_online)==0):
            if not (len(self.cookery_bakery)==0) or not (len(self.ccmc_oral)==0 and len(self.ccmc_gsk_oral) == 0) or not (len(self.ccmc_online)==0):

                
                # if not (len(self.cookery_bakery)==0 and len(self.ccmc_oral)==0 and len(self.ccmc_gsk_oral) == 0 ):
                    
                if not (len(self.cookery_bakery)==0):
                    if cookery_draft_confirm:
                        cookery_bakery_marks = self.cookery_bakery.total_mrks
                        self.cookery_practical = cookery_bakery_marks
                    else:
                        error_msg = _("Cookery/Bakery Not Confirmed for'%s'") % (self.ccmc_candidate.candidate_code)
                        print(error_msg)
                    
                if not (len(self.ccmc_oral)==0 and len(self.ccmc_gsk_oral) == 0):
                    if ccmc_oral_state:
                        ccmc_oral_marks = self.ccmc_oral.toal_ccmc_rating 
                        self.cookery_oral = ccmc_oral_marks
                        
                        #GSK Oral Makrs
                        ccmc_gsk_marks =  self.ccmc_gsk_oral.toal_ccmc_oral_rating
                        self.ccmc_gsk_oral_marks = ccmc_gsk_marks
                    else:
                        error_msg = _("CCMC Oral  Not Confirmed for'%s'") % (self.ccmc_candidate.candidate_code)
                        print(error_msg)

                    
                    if cookery_draft_confirm and ccmc_oral_state and ccmc_gsk_oral_state:
                        cookery_bakery_marks = self.cookery_bakery.total_mrks
                        ccmc_oral_marks = self.ccmc_oral.toal_ccmc_rating 

                        self.cookery_oral = ccmc_oral_marks
                        self.cookery_practical = cookery_bakery_marks
                    else:
                        error_msg = _("CCMC Oral Or Practical Not Confirmed for'%s'") % (self.ccmc_candidate.candidate_code)
                        print(error_msg)
                    
                if not (len(self.ccmc_online)==0):
                    if ccmc_online_state:
                        cookery_gsk_online = self.ccmc_online.scoring_total
                        self.cookery_gsk_online = cookery_gsk_online
                    else:
                        error_msg = _("CCMC Online Not Confirmed for'%s'") % (self.ccmc_candidate.candidate_code)
                        print(error_msg)
                else:
                    cookery_gsk_online = self.cookery_gsk_online
                    self.cookery_gsk_online = cookery_gsk_online
                
                self.overall_marks = self.cookery_practical  + self.ccmc_gsk_oral_marks + self.cookery_oral + self.cookery_gsk_online
                
                #Percentage Calculation
                #  import wdb; wdb.set_trace(); 
                self.cookery_bakery_percentage = (self.cookery_practical/100) * 100
                self.ccmc_oral_percentage = (self.cookery_oral/80) * 100
                self.ccmc_gsk_oral_percentage = (self.ccmc_gsk_oral_marks/20) * 100
                
                self.cookery_gsk_online_percentage = (self.cookery_gsk_online/100) * 100
                self.overall_percentage = (self.overall_marks/300)*100
                
                
                if self.cookery_bakery_percentage >= 60:
                        self.cookery_bakery_prac_status = 'passed'
                else:
                        self.cookery_bakery_prac_status = 'failed'
                
                if self.ccmc_oral_percentage >= 60:
                        self.ccmc_catering_status = 'passed'
                else:
                        self.ccmc_catering_status = 'failed'
                
                if self.ccmc_gsk_oral_percentage >= 60:
                        self.ccmc_gsk_status = 'passed'
                else:
                        self.ccmc_gsk_status = 'failed'
                        
                if self.ccmc_oral_percentage < 60 or self.ccmc_gsk_oral_percentage < 60:
                    self.ccmc_oral_prac_status = 'failed'
                else:
                    self.ccmc_oral_prac_status = 'passed'
                    
                    
                if self.cookery_gsk_online_percentage  >= 60:
                    self.ccmc_online_status = 'passed'
                else:
                    self.ccmc_online_status = 'failed'
                        
                all_passed = all(field == 'passed' for field in [self.ccmc_oral_prac_status,self.cookery_bakery_prac_status,self.ccmc_online_status, self.exam_criteria , self.stcw_criteria , self.ship_visit_criteria , self.attendance_criteria,self.ccmc_gsk_oral_prac_status ])
                if all_passed:
                    self.write({'certificate_criteria':'passed'})
                else:
                    self.write({'certificate_criteria':'pending'})

                                    
                self.state = '2-done'

            else:
            
                # import wdb; wdb.set_trace(); 
                # if cookery_draft_confirm and ccmc_oral_state and ccmc_gsk_oral_state and ccmc_online_state:
                if True:
                    
                    # All CCMC Marks
                    cookery_bakery_marks = self.cookery_practical
                    ccmc_oral_marks = self.cookery_oral
                    self.cookery_oral = ccmc_oral_marks
                    self.cookery_practical = cookery_bakery_marks
                    cookery_gsk_online = self.cookery_gsk_online                    
                    ccmc_gsk_marks =  self.ccmc_gsk_oral.toal_ccmc_oral_rating
                    self.ccmc_gsk_oral_marks = ccmc_gsk_marks

                    
                    self.cookery_gsk_online = cookery_gsk_online
                    self.overall_marks = ccmc_oral_marks + cookery_bakery_marks + cookery_gsk_online
                    
                    
                    
                    #All Percentage
                    self.cookery_bakery_percentage = (cookery_bakery_marks/100) * 100
                    self.ccmc_oral_percentage = (ccmc_oral_marks/100) * 100
                    self.ccmc_gsk_oral_percentage = (ccmc_gsk_marks/20) * 100
                    self.cookery_gsk_online_percentage = (cookery_gsk_online/100) * 100
                    self.overall_percentage = (self.overall_marks/300) * 100
                    
                    
                    if self.cookery_practical >= 60:
                        self.cookery_bakery_prac_status = 'passed'
                    else:
                        self.cookery_bakery_prac_status = 'failed'
                        
                    if self.ccmc_oral_percentage >= 60:
                            self.ccmc_catering_status = 'passed'
                    else:
                            self.ccmc_catering_status = 'failed'
                    
                    if self.ccmc_gsk_oral_percentage >= 60:
                            self.ccmc_gsk_status = 'passed'
                    else:
                            self.ccmc_gsk_status = 'failed'
                            
                    if self.ccmc_oral_percentage < 60 or self.ccmc_gsk_oral_percentage < 60:
                        self.ccmc_oral_prac_status = 'failed'
                    else:
                        self.ccmc_oral_prac_status = 'passed'
                    
                    
                    if self.cookery_gsk_online  >= 60:
                        self.ccmc_online_status = 'passed'
                    else:
                        self.ccmc_online_status = 'failed'
                        
                    all_passed = all(field == 'passed' for field in [self.ccmc_oral_prac_status,self.cookery_bakery_prac_status,self.ccmc_online_status, self.exam_criteria , self.stcw_criteria , self.ship_visit_criteria , self.attendance_criteria,self.ccmc_gsk_oral_prac_status ])

                    if all_passed:
                        self.write({'certificate_criteria':'passed'})
                    else:
                        self.write({'certificate_criteria':'pending'})
                        
                    
                    self.state = '2-done'
                    
                else:
                    raise ValidationError("Not All exam are Confirmed")
        else:
            pass    
        
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
        user_id = self.env.user
        # import wdb; wdb.set_trace()
        if user_id.has_group('bes.download_not_allowed'):
            # User is in the group
            raise ValidationError("Please Contact Administrator")
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

class ReallocateCandidatesWizard(models.TransientModel):
    _name = 'reallocate.candidates.wizard'
    _description = 'Reallocate Candidates Wizard'

    # Define fields for the wizard
    exam_batch = fields.Many2one('dgs.batches', string='Exam Batch', required=True)
    institute_id = fields.Many2one('bes.institute', string='Institute', required=True)
    examiner_id = fields.Many2one('exam.type.oral.practical.examiners', string='Examiner')
    exam_date = fields.Date(string='Exam Date')
    candidate_ids = fields.Many2many('exam.type.oral.practical.examiners.marksheet',relation="marksheets_ids", string='Candidates')

    def action_reallocate(self):
        confirmed_candidates = []  # List to hold names of confirmed candidates
        # import wdb; wdb.set_trace();
        for candidate in self.candidate_ids:
            # Check the course for the candidate
            if candidate.examiners_id.exam_type != "online":
                if candidate.examiners_id.course.course_code == "GP":
                    if candidate.examiners_id.subject.name == 'GSK':
                        # Check if both oral and practical drafts are confirmed
                        if candidate.gp_marksheet.gsk_oral.gsk_oral_draft_confirm == 'draft' or candidate.gp_marksheet.gsk_prac.gsk_practical_draft_confirm == 'draft':
                            candidate.examiners_id = self.examiner_id.id  # Update the examiner for the candidate 
                            candidate.gp_marksheet.gsk_oral_prac_assignment_id = self.examiner_id.id

                        elif candidate.gp_marksheet.gsk_oral.gsk_oral_draft_confirm == 'confirm' and candidate.gp_marksheet.gsk_prac.gsk_practical_draft_confirm == 'confirm':
                            confirmed_candidates.append(candidate.gp_candidate.name)  # Add to confirmed list
                            candidate.examiners_id.compute_candidates_done()

                    elif candidate.examiners_id.subject.name == 'MEK':
                        if candidate.gp_marksheet.mek_oral.mek_oral_draft_confirm == 'draft' or candidate.gp_marksheet.mek_prac.mek_practical_draft_confirm == 'draft':
                            candidate.examiners_id = self.examiner_id.id  # Update the examiner for the candidate
                            candidate.gp_marksheet.mek_oral_prac_assignment_id = self.examiner_id.id
                        elif candidate.gp_marksheet.mek_oral.mek_oral_draft_confirm == 'confirm' and candidate.gp_marksheet.mek_prac.mek_practical_draft_confirm == 'confirm':
                            confirmed_candidates.append(candidate.gp_candidate.name)  # Add to confirmed list
                            candidate.examiners_id.compute_candidates_done()
                            
                elif candidate.examiners_id.course.course_code == "CCMC":
                    if candidate.examiners_id.subject.name == 'CCMC':
                        if candidate.ccmc_marksheet.cookery_bakery.cookery_draft_confirm == 'draft' or candidate.ccmc_marksheet.ccmc_oral.ccmc_oral_draft_confirm == 'draft':
                            candidate.examiners_id = self.examiner_id.id  # Update the examiner for the candidate
                            if candidate.ccmc_marksheet.attempting_cookery and self.examiner_id.subject.name == 'practical_oral_cookery_bakery':
                                candidate.ccmc_marksheet.ccmc_practical_assignment_id = self.examiner_id.id
                            if candidate.ccmc_marksheet.attempting_oral and self.examiner_id.subject.name == 'ccmc_oral':
                                candidate.ccmc_marksheet.ccmc_oral_assignment_id = self.examiner_id.id
                        elif candidate.ccmc_marksheet.cookery_bakery.cookery_draft_confirm == 'confirm' and candidate.ccmc_marksheet.ccmc_oral.ccmc_oral_draft_confirm == 'confirm':
                            confirmed_candidates.append(candidate.ccmc_candidate.name)  # Add to confirmed list
                            candidate.examiners_id.compute_candidates_done()

                        if candidate.ccmc_marksheet.ccmc_gsk_oral.ccmc_oral_draft_confirm == 'draft':
                            candidate.examiners_id = self.examiner_id.id  # Update the examiner for the candidate
                            if candidate.ccmc_marksheet.attempting_oral and self.examiner_id.subject.name == 'gsk_oral':
                                candidate.ccmc_marksheet.ccmc_gsk_oral_assignment_id = self.examiner_id.id
                        elif candidate.ccmc_marksheet.ccmc_gsk_oral.ccmc_oral_draft_confirm == 'confirm':
                            confirmed_candidates.append(candidate.ccmc_candidate.name)  # Add to confirmed list
                            candidate.examiners_id.compute_candidates_done()
            elif candidate.examiners_id.exam_type == "online":
                if candidate.examiners_id.course.course_code == "GP":
                    if candidate.examiners_id.subject.name == 'GSK':
                        if candidate.gp_marksheet.gsk_online_attendance == 'present' and candidate.gp_marksheet.gsk_online.state == 'done':
                            confirmed_candidates.append(candidate.gp_candidate.name)  # Add to confirmed list
                        elif not candidate.gp_marksheet.gsk_online_attendance or candidate.gp_marksheet.gsk_online_attendance == 'absent':
                            candidate.examiners_id = self.examiner_id.id  # Update the examiner for the candidate
                            candidate.gp_marksheet.gsk_online_assignment_id = self.examiner_id.id
                            # candidate.gp_marksheet.exam_date = self.examiner_id.exam_date
                            candidate.examiners_id.compute_candidates_done()

                    elif candidate.examiners_id.subject.name == 'MEK':
                        if candidate.gp_marksheet.mek_online_attendance == 'present' and candidate.gp_marksheet.mek_online.state == 'done':
                            confirmed_candidates.append(candidate.gp_candidate.name)  # Add to confirmed list
                        elif not candidate.gp_marksheet.mek_online_attendance or candidate.gp_marksheet.mek_online_attendance == 'absent':
                            candidate.examiners_id = self.examiner_id.id  # Update the examiner for the candidate
                            candidate.gp_marksheet.mek_online_assignment_id = self.examiner_id.id
                            # candidate.gp_marksheet.exam_date = self.examiner_id.exam_date
                            candidate.examiners_id.compute_candidates_done()
                elif candidate.examiners_id.course.course_code == "CCMC":
                    if candidate.examiners_id.subject.name == 'CCMC':
                        if candidate.ccmc_marksheet.ccmc_online_attendance == 'present' and candidate.ccmc_marksheet.ccmc_online.state == 'done':
                            confirmed_candidates.append(candidate.ccmc_candidate.name)  # Add to confirmed list
                        elif not candidate.ccmc_marksheet.ccmc_online_attendance or candidate.ccmc_marksheet.ccmc_online_attendance == 'absent':
                            candidate.examiners_id = self.examiner_id.id  # Update the examiner for the candidate
                            candidate.ccmc_marksheet.ccmc_online_assignment_id = self.examiner_id.id
                            # candidate.ccmc_marksheet.exam_date = self.examiner_id.exam_date
                            candidate.examiners_id.compute_candidates_done()

            # else:
            #     candidate.examiners_id = self.examiner_id.id  # For online exams, update the examiner
        

        total_selected = len(self.candidate_ids)
        not_reallocated_count = len(confirmed_candidates)
        reallocated_count = total_selected - not_reallocated_count

        if confirmed_candidates:
            if reallocated_count > 0:
                message = (
                    "The following candidates are marked as confirmed and cannot be reallocated:\n"
                    f"{', '.join(confirmed_candidates)}.\n\n"
                    f"The remaining {reallocated_count} candidates have been allocated to the new examiner ({self.examiner_id.display_name})."
                )
            else:
                message = (
                    "All selected candidates are marked as confirmed and cannot be reallocated.\n"
                    "No reallocation was performed."
                )
        else:
            message = f"Reallocation successful. All selected candidates have been reassigned to the new examiner( {self.examiner_id.display_name} )."

        return {
            'name': 'Reallocation Status',
            'type': 'ir.actions.act_window',
            'res_model': 'batch.pop.up.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'default_message': message},
        }



class OnlineExamWizard(models.TransientModel):
    _name = 'online.exam.wizard'
    _description = 'Online Exam Wizard'

    ip_address = fields.Char(string='IP Address')     
    examiners_id = fields.Many2one('exam.type.oral.practical.examiners', string='Examiners')  # Link to the main model
    exam_date = fields.Date(string='Exam Date')
    institute_id = fields.Many2one('bes.institute', string='Institute')
    dgs_batch =fields.Many2one('dgs.batches', string='Batch')
    online_start_time = fields.Datetime("Start Time")
    online_end_time = fields.Datetime("End Time")

    def convert_to_ist(self, dt_utc):
        """Convert UTC datetime to IST."""
        if not dt_utc:
            return False  # Handle cases where the datetime is not provided
        ist_timezone = timezone('Asia/Kolkata')
        ist_time = dt_utc.replace(tzinfo=timezone('UTC')).astimezone(ist_timezone).replace(tzinfo=None)
        return ist_time

    def save_ip_address(self):
        """Save IP addresses (comma-separated) to examiner's record, institute's record, and external API."""
        # Make POST requests to external API for each IP
        
        config_param = self.env['ir.config_parameter'].sudo().get_param('bes.server_type')
        
        print(config_param)
        
        if config_param == 'production':  
            api_url = "http://178.18.255.245:5000/api/ip/add"
            ip_list = [ip.strip() for ip in self.ip_address.split(',') if ip.strip()]
            
            for ip in ip_list:
                data = {
                    "ip": ip,
                    "location": "survey"
                }
                response = requests.post(api_url, json=data, timeout=5)
            
        # Original functionality - Fetch the related examiner and set the IP address
        online_assignment = self.env['exam.type.oral.practical.examiners'].sudo().search([
            ('dgs_batch','=',self.dgs_batch.id),
            ('institute_id','=',self.institute_id.id),
            ('exam_date','=',self.exam_date),
            ('exam_type','=','online')
            ])

        for examiner in online_assignment:
            examiner.ipaddr = self.ip_address
            examiner.commence_exam = True
            examiner.online_start_time = self.online_start_time  # Convert only once
            examiner.online_end_time = self.online_end_time  # Convert only once

            # import wdb;wdb.set_trace();
            # examiner.online_start_time = self.online_start_time  # Convert only once
            # examiner.online_end_time = self.online_end_time  # Convert only once


            if examiner.course.course_code == 'GP':
                if examiner.subject.name == "GSK":
                    examiner.marksheets.gp_marksheet.write({
                        'ip_address':examiner.ipaddr,
                        'exam_date':examiner.exam_date,
                        })
                    
                    examiner.marksheets.gsk_online.write({
                        'ip_address':examiner.ipaddr,
                        'exam_date':examiner.exam_date,
                        'commence_online_exam':True,
                        'online_start_time':  self.convert_to_ist(self.online_start_time),
                        'online_end_time': self.convert_to_ist(self.online_end_time),
                        })
                    
                if examiner.subject.name == "MEK":
                    examiner.marksheets.gp_marksheet.write({
                        'ip_address':examiner.ipaddr,
                        'exam_date':examiner.exam_date,
                        })
                    
                    examiner.marksheets.mek_online.write({
                        'ip_address':examiner.ipaddr,
                        'exam_date':examiner.exam_date,
                        'commence_online_exam':True,
                        'online_start_time': self.convert_to_ist(self.online_start_time),
                        'online_end_time': self.convert_to_ist(self.online_end_time),
                        })
            elif examiner.course.course_code == 'CCMC':
                examiner.marksheets.ccmc_marksheet.write({
                    'ip_address':examiner.ipaddr,
                    'exam_date':examiner.exam_date
                    })
                
                examiner.marksheets.ccmc_online.write({
                    'ip_address':examiner.ipaddr,
                    'exam_date':examiner.exam_date,
                    'commence_online_exam':True,
                    'online_start_time': self.convert_to_ist(self.online_start_time),
                    'online_end_time': self.convert_to_ist(self.online_end_time),
                    })
        # return {'type': 'ir.actions.act_window_close'}
            # Close the wizard and refresh the page
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

        
    # Online Attendance Sheet
class ExaminerAttendanceWizard(models.TransientModel):
    _name = 'examiner.attendance.wizard'
    _description = 'Examiner Attendance Wizard'
    _table = "examiner"
    _rec_name = "examiner"

    examiner_assignment = fields.Many2many('exam.type.oral.practical.examiners', string='Examiner')
    examiner = fields.Many2one('bes.examiner', string='Examiner')
    online_exam_date = fields.Date("Exam Date",widget="date",date_format="%d-%b-%y")
    examiners = fields.Many2many('bes.examiner', string='Examiners',compute='_compute_examiners')
    course = fields.Many2one("course.master",string="Course")

    @api.depends('examiner_assignment')
    def _compute_examiners(self):
        for rec in self:
            rec.examiners = rec.examiner_assignment.examiner.ids

    def generate_attendance_sheet(self):
        # import wdb;wdb.set_trace()
        examiner_duty_id  = self.env.context.get("active_id")
        print(examiner_duty_id)
        online_assignments = self.env['exam.type.oral.practical.examiners'].sudo().search([
            ('prac_oral_id','=',examiner_duty_id),
            ('exam_type','=','online'),
            ('examiner','=',self.examiner.id),
            ('exam_date','=',self.online_exam_date)
            ])
        
        
        
        # dgs_batch self.env['exam.type.oral.practical'].browse(self.env.context['params']['id']).dgs_batch
        # import wdb;wdb.set_trace()

        if not online_assignments:
            # Handle the case where no records were found due to exam_date
            raise UserError("No online assignments found for the given exam date.")

        
        # examiners = self.env['exam.type.oral.practical.examiners'].browse(self.examiner_assignment.ids)
        examiners = online_assignments
        institute_name = examiners[0].institute_id.name
        examiner_name = examiners[0].examiner.name
        exam_date = self.online_exam_date
        
        
        
        
        # Initialize arrays to store filtered candidates
        if self.course.course_code == "GP":
            gsk_candidates = set() 
            mek_candidates = set()
            gsk_mek_candidates = set()
            
            for examiner in examiners:
                print("examiner.marksheets.gp_marksheet")
                print(examiner.marksheets.gp_marksheet)
                for marksheet in examiner.marksheets.gp_marksheet:

                    # Check if the candidate is attempting both GSK and MEK Online
                    if marksheet.attempting_gsk_online and marksheet.attempting_mek_online:
                        gsk_mek_candidates.add(marksheet.id)

                    # Check if the candidate is attempting only GSK Online (and not MEK)
                    elif marksheet.attempting_gsk_online and not marksheet.attempting_mek_online:
                        gsk_candidates.add(marksheet.id)

                    # Check if the candidate is attempting only MEK Online (and not GSK)
                    elif marksheet.attempting_mek_online and not marksheet.attempting_gsk_online:
                        mek_candidates.add(marksheet.id)

            gsk_candidates = list(gsk_candidates)
            mek_candidates = list(mek_candidates)
            gsk_mek_candidates = list(gsk_mek_candidates)

            # import wdb; wdb.set_trace()
            # Render the report
            return self.env.ref('bes.action_attendance_sheet_online_gp_new').report_action(self,data={
                'docs': [self],  # Pass the current recordset to `docs`
                'gsk_mek_candidates': gsk_mek_candidates,
                'gsk_candidates': gsk_candidates,
                'mek_candidates': mek_candidates,
                'institute_name': institute_name,
                'examiner_name': examiner_name,
                'exam_date': exam_date,
                })
        elif self.course.course_code == "CCMC":
            # import wdb;wdb.set_trace()
            ccmc_candidates = set()
            for examiner in examiners:
                for marksheet in examiner.marksheets.ccmc_marksheet:
                    ccmc_candidates.add(marksheet.id)

            ccmc_candidates = list(ccmc_candidates)

            return self.env.ref('bes.action_attendance_sheet_online_ccmc').report_action(self,data={
                'docs': [self],  # Pass the current recordset to `docs`
                'institute_name': institute_name,
                'examiner_name': examiner_name,
                'exam_date': exam_date,
                'ccmc_candidates': ccmc_candidates
                })


class AttendanceSheetReport(models.AbstractModel):
    _name = 'report.bes.attendance_sheet_online_gp_new'
    _description = 'GP Attendance Sheet'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        
        # data['context']['active_id']

        
        gsk_candidates = self.env['gp.exam.schedule'].sudo().search([('id', 'in', data['gsk_candidates'])], order='exam_id')
        mek_candidates = self.env['gp.exam.schedule'].sudo().search([('id', 'in', data['mek_candidates'])], order='exam_id')
        gsk_mek_candidates = self.env['gp.exam.schedule'].sudo().search([('id', 'in', data['gsk_mek_candidates'])], order='exam_id')

        # import wdb;wdb.set_trace()
        
        print("MEK Candidate")
        print(mek_candidates)
        
        print("GSK Candidate")
        print(gsk_candidates)
        
        print("GSK MEK Candidate")
        print(gsk_mek_candidates)
        
        
        examiner_name = data['examiner_name']
        # Example string date
        exam_date_str = data['exam_date']

        # Convert the string to a datetime object
        exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d')


        return {
                'doc_ids': "",
                'doc_model': 'gp.exam.schedule',
                'docs': data,
                "gsk_candidates":gsk_candidates,
                "mek_candidates":mek_candidates,
                "gsk_mek_candidates":gsk_mek_candidates,
                "examiner_name":examiner_name,
                "exam_date":exam_date,
                }

class CCMCAttendanceSheetReport(models.AbstractModel):
    _name = 'report.bes.attendance_sheet_online_ccmc'
    _description = 'Attendance Sheet Online'
    
    
    @api.model
    def _get_report_values(self, docids, data=None):
        # import wdb;wdb.set_trace()
        docs = self.env['exam.type.oral.practical.examiners'].browse(docids)

        ccmc_candidates = self.env['ccmc.exam.schedule'].sudo().search([('id', 'in', data['ccmc_candidates'])], order='exam_id')

        examiner_name = data['examiner_name']
        # Example string date
        exam_date_str = data['exam_date']

        # Convert the string to a datetime object
        exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d')
        return {
            'doc_ids': '',
            'doc_model': 'ccmc.exam.schedule',
            'docs': data,
            'ccmc_candidates': ccmc_candidates,
            'examiner_name': examiner_name,
            'exam_date': exam_date,
        }