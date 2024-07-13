from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import werkzeug
import secrets
import random
import string




class InheritedSurvey(models.Model):
    _inherit = "survey.survey"
    
    title = fields.Char('Exam Title', required=True, translate=True)
    template = fields.Boolean("Template")
    institute = fields.Many2one("bes.institute",string="Institute")
    course = fields.Many2one("course.master",string="Course")
    examiner = fields.Many2one("bes.examiner",string="Examiner")
    examiner_token = fields.Char(string="Examiner Token")
    start_time = fields.Datetime("Start Time")
    end_time = fields.Datetime("End Time")
    exam_state = fields.Selection([ 
        ('stopped', 'Stopped'),
        ('in_progress', 'In-Progress'),
        ('done', 'Done')     
    ], string='Exam State', default='stopped')
    subject_ids = fields.Many2many("course.master.subject",string="Subject IDS",compute="_compute_subject_ids")
    subject = fields.Many2one("course.master.subject","Subject")
    users_login_required = fields.Boolean('Login Required',default=True, help="If checked, users have to login before answering even with a valid token.")
    is_attempts_limited = fields.Boolean('Limited number of attempts', help="Check this option if you want to limit the number of attempts per user",
                                         compute="_compute_is_attempts_limited",default=True, store=True, readonly=False)
    users_login_required = fields.Boolean('Login Required',default=True, help="If checked, users have to login before answering even with a valid token.")
    scoring_type = fields.Selection([
        ('no_scoring', 'No scoring'),
        ('scoring_with_answers', 'Scoring with answers at the end'),
        ('scoring_without_answers', 'Scoring without answers at the end')],
        string="Scoring", required=True, default='scoring_without_answers')
    is_trigger_exam = fields.Boolean('Trigger Exam')
    trigger_exam = fields.Many2one("survey.survey","Triggering Exam")
    trigger_exam_url = fields.Char("Trigger Exam URL",compute="_compute_exam_start_url")
    survey_start_url = fields.Char('Survey URL', compute='_compute_survey_start_url')
    questions_layout = fields.Selection([
        ('one_page', 'One page with all the questions'),
        ('page_per_section', 'One page per section'),
        ('page_per_question', 'One page per question')],
        string="Layout", required=True, default='page_per_section')
    
    
    def generate_unique_string(self):
    # Define the length of the desired string
        # characters = string.ascii_letters + string.digits

    # Use secrets module to generate a random string of the specified length
        # random_string = ''.join(secrets.choice(characters) for _ in range(10))

        return ''.join(random.choices('0123456789', k=6))

    
    
    def generate_token(self):
        self.examiner_token = self.generate_unique_string()
        
    
    def start_exam(self):
        self.exam_state = 'in_progress'
    
    def stop_exam(self):
        self.exam_state = 'stopped'
    
    def done_exam(self):
        self.exam_state = 'done'
        

        

    
    
    @api.depends('access_token')
    def _compute_survey_start_url(self):
        for survey in self:
            survey.survey_start_url = werkzeug.urls.url_join(survey.get_base_url(), survey.get_start_url()) if survey else False

    
    @api.depends('course')
    def _compute_subject_ids(self):
        for exam in self:
            if exam.course:
                exam.subject_ids = exam.course.subjects.ids
            else:
                exam.subject_ids = False
                
    
    @api.depends('trigger_exam.access_token')
    def _compute_exam_start_url(self):
        for exam in self:
            exam.trigger_exam_url = werkzeug.urls.url_join(exam.trigger_exam.get_base_url(), exam.trigger_exam.get_start_url()) if exam.trigger_exam else False
    


class SurveyUserInputInherited(models.Model):
    _inherit = "survey.user_input"
    survey_id = fields.Many2one('survey.survey', string='Exam', required=True, readonly=True, ondelete='cascade')
    exam_center = fields.Many2one("exam.center","Exam Region",required=True)
    examiner_token = fields.Char(string="Examiner Token")
    institute_id = fields.Many2one("bes.institute",string="Institute")
    gp_candidate = fields.Many2one('gp.candidate', string='GP Candidate', readonly=True)
    ccmc_candidate = fields.Many2one('ccmc.candidate', string='CCMC Candidate', readonly=True)
    dgs_batch = fields.Many2one("dgs.batches",string="Exam Batch",required=False)
    
    
    def generate_unique_string(self):
    # Define the length of the desired string
        # characters = string.ascii_letters + string.digits

    # Use secrets module to generate a random string of the specified length
        # random_string = ''.join(secrets.choice(characters) for _ in range(10))

        return ''.join(random.choices('0123456789', k=6))
    
    def generate_token(self):
        self.examiner_token = self.generate_unique_string()
        


class InheritedSurveyQuestions(models.Model):
    _inherit = "survey.question"
    
    q_no = fields.Char("Q.No")
