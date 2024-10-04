from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import werkzeug
import secrets
import random
import string
from datetime import datetime


class SurveySectionQuestionWizard(models.TransientModel):
    _name = 'survey.question.section'
    _description = 'My Wizard'

    qb = fields.Many2one("survey.survey",string="Question Bank")
    chapter = fields.Many2one("survey.question",string="Course")
    description = fields.Text(string='Question Description')

    def action_add_question(self):
        print("Chapter "+ str(self.chapter.id))
        print("QB "+ str(self.qb.id))

        question_id = self.env['survey.question'].sudo().create({'survey_id':self.qb.id ,'is_scored_question':True,'question_type':'simple_choice', 'title': self.description })
        question_id.write({'page_id':self.chapter.id})
        print("QB "+ str(question_id))
        question_ids = self.chapter.question_ids.ids
        print(question_ids)
        seq = 0
        # chapters = self.env['survey.question'].sudo().search([('survey_id','=',self.qb.id),('is_page','=',True)])
        # for chapter in chapters:
        #     seq = seq + 1
        #     chapter.write({'sequence':seq})
        #     for question in chapter.question_ids:
        #         # question = self.env['survey.question'].sudo().search([('id','=',question_id.id)]).write({'page_id':self.chapter.id})
        #         seq = seq + 1
        #         question.write({'sequence':seq})
                
            
        
        # self.chapter.write({'question_ids':[(6,0,question_id.id)]})
        

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
    # users_login_required = fields.Boolean('Login Required',default=True, help="If checked, users have to login before answering even with a valid token.")
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
    
    def action_open_add_section(self):
        self.ensure_one()
        return {
            'name': 'Add Question Wizard',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'survey.question.section',
            'target': 'new',
            'context': {
                'default_qb':self.id
            }
            
        }

    
    
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
        
    
    def add_question_section(self):
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
    gp_exam = fields.Many2one('gp.exam.schedule', string='GP Exam', readonly=True)
    ccmc_exam = fields.Many2one('ccmc.exam.schedule', string='CCMC Exam', readonly=True)

    is_gp = fields.Boolean('Is GP')
    is_ccmc = fields.Boolean('Is CCMC')

    indos = fields.Char(string="Indos No", compute="compute_details", store=True)

    start_time = fields.Char(string="Start Time", readonly=True, compute="_compute_total_time", store=True)
    end_time = fields.Char(string="End Time", readonly=True, compute="_compute_total_time", store=True)    
    total_time = fields.Char(string="Total Time", compute="_compute_total_time", store=True)
    ip_address = fields.Char(string="IP Address")

    correct_answers = fields.Integer(string="Correct Answers", compute="_compute_correct_answers", store=True)
    wrong_answers = fields.Integer(string="Wrong Answers", compute="_compute_wrong_answers", store=True)
    skipped_questions = fields.Integer(string="Unanswered Questions", compute="_compute_skipped_questions", store=True)
    result_status = fields.Selection([
        ('', ''),
        ('passed', 'Passed'),
        ('failed', 'Failed')
    ], string='Result', compute="_compute_result_status", store=True)

    user_input_line_ids = fields.One2many(
        'survey.user_input.line', 'user_input_id', string='Answers', copy=True
    )

    token_regenrated = fields.Boolean("Token Regenerated", default=False)


    @api.depends('user_input_line_ids')
    def _compute_correct_answers(self):
        for record in self:
            record.correct_answers = len(record.user_input_line_ids.filtered(lambda line: line.answer_is_correct))

    @api.depends('user_input_line_ids')
    def _compute_wrong_answers(self):
        for record in self:
            record.wrong_answers = len(record.user_input_line_ids.filtered(lambda line: not line.answer_is_correct))

    @api.depends('user_input_line_ids')
    def _compute_skipped_questions(self):
        for record in self:
            record.skipped_questions = len(record.user_input_line_ids.filtered(lambda line: line.skipped))

    @api.depends('scoring_success','state')
    def _compute_result_status(self):
        for record in self:
            if record.state == 'done':
                if record.scoring_success:
                    record.result_status = 'passed'
                else:
                    record.result_status = 'failed'
            else:
                record.result_status = ''


    @api.depends('gp_candidate', 'ccmc_candidate')
    def compute_details(self):
        for record in self:
            if record.is_ccmc:
                record.indos = record.ccmc_candidate.indos_no
            elif record.is_gp:
                record.indos = record.gp_candidate.indos_no
    

    @api.depends('user_input_line_ids','state')
    def _compute_total_time(self):
        for record in self:
            if record.state == 'done' and record.user_input_line_ids:
                # print(record.user_input_line_ids,"gellllllllllloooooooooooooooooooooooo")
                start_time = record.user_input_line_ids[0].create_date
                end_time = record.user_input_line_ids[-1].create_date

                total_time = end_time - start_time
                # Format the times as hours:minutes:seconds
                record.start_time = start_time.strftime('%H:%M:%S')
                record.end_time = end_time.strftime('%H:%M:%S')
                
                # Convert the total_time (timedelta) to hours, minutes, and seconds
                total_seconds = int(total_time.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                # Format total_time as HH:MM:SS
                record.total_time = f"{hours:02}:{minutes:02}:{seconds:02}"
            else:
                record.total_time = "00:00:00"
                record.start_time = "00:00:00"
                record.end_time = "00:00:00"

    def calculate_time(self):
        for record in self:
            if record.user_input_line_ids:
                # import wdb;wdb.set_trace()
                start_time = record.user_input_line_ids[0].create_date
                end_time = record.user_input_line_ids[-1].create_date
                total_time = end_time - start_time
                
                record.start_time = start_time.strftime('%H:%M:%S')
                record.end_time = end_time.strftime('%H:%M:%S')

                # Convert the total_time (timedelta) to hours, minutes, and seconds
                total_seconds = int(total_time.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                # Format total_time as HH:MM:SS
                record.total_time = f"{hours:02}:{minutes:02}:{seconds:02}"
            else:
                record.total_time = "00:00:00"


    # @api.onchange('institute_id')
    # def _onchange_institute_id(self):
    #     """Fetch the IP address from the selected institute."""
    #     if self.institute_id:
    #         self.ip_address = self.institute_id.ip_address
    #     else:
    #         self.ip_address = False
    
    
    def generate_unique_string(self):
    # Define the length of the desired string
        # characters = string.ascii_letters + string.digits

    # Use secrets module to generate a random string of the specified length
        # random_string = ''.join(secrets.choice(characters) for _ in range(10))

        return ''.join(random.choices('0123456789', k=6))
    
    # ,compute="compute_institute_name",store=True
    # def compute_institute_name(self):
    #     for record in self:
    #         if record.gp_candidate:
    #             institute_id = record.gp_candidate.institute_id
    #         elif record.ccmc_candidate:
    #             institute_id = record.ccmc_candidate.institute_id
    #         else:
    #             institute_id = False
    
    # def generate_token(self):
    #     self.examiner_token = self.generate_unique_string()
        


class InheritedSurveyQuestions(models.Model):
    _inherit = "survey.question"
    
    q_no = fields.Char("Q.No")
