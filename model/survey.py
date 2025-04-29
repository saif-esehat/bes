from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import werkzeug
import secrets
import random
import string
from datetime import datetime
import pandas as pd
import base64
from io import BytesIO
import pytz
from pytz import timezone, UTC



class SurveySectionQuestionWizard(models.TransientModel):
    _name = 'survey.question.section'
    _description = 'My Wizard'

    qb = fields.Many2one("survey.survey",string="Question Bank")
    chapter = fields.Many2one("survey.question",string="Course")
    description = fields.Text(string='Question Description')
    upload_type = fields.Selection([
        ('single', 'Single'),
        ('bulk', 'Bulk')       
    ], string='Upload Type', default='single')
    file = fields.Binary(string="File", required=False)
    delete_prev_ques = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Delete Previous Questions', default='no')

    def excel_to_mcq_json(self,encoded_file):
        # Decode base64-encoded file
        excel_data = base64.b64decode(encoded_file)
        df = pd.read_excel(BytesIO(excel_data))
        # import wdb;wdb.set_trace()

        # Build JSON from the Excel
        df.columns = df.columns.str.strip()
        questions = []
        for _, row in df.iterrows():
            question = {
                "question_number": row['Sr.No'],
                "title": row['Question'],
                "marks": row['Marks'],
                "options": []
            }

            option_map = {'A': 'Option1', 'B': 'Option2', 'C': 'Option3', 'D': 'Option4'}

            for option_letter, column_name in option_map.items():
                option_text = row.get(column_name, '')
                is_correct = row['Correct Answer'].strip().upper() == option_letter
                question["options"].append({
                    "option": option_letter,
                    "text": option_text,
                    "correct": is_correct,
                    "marks": row['Marks'] if is_correct else 0
                })

            questions.append(question)
        
        return questions
    

    def action_add_question(self):
            print("Chapter "+ str(self.chapter.id))
            print("QB "+ str(self.qb.id))
            if self.upload_type == 'single':
                # Get last question in chapter to determine sequence
                last_question = self.env['survey.question'].search([
                    ('page_id', '=', self.chapter.id)
                ], order='sequence desc', limit=1)
                # sequence = last_question.sequence + 1 if last_question else self.chapter.sequence + 1
                sequence = last_question.sequence
                # Count existing questions in this chapter to determine next number
                question_count = self.env['survey.question'].search_count([
                    ('page_id', '=', self.chapter.id)
                ])
                question_id = self.env['survey.question'].sudo().create({
                    'survey_id': self.qb.id,
                    'is_scored_question': True,
                    'question_type': 'simple_choice',
                    'title': self.description,
                    'q_no': f"Q.{question_count + 1}",
                    'sequence': sequence
                })
                question_id.sudo().write({'page_id': self.chapter.id})
                print("QB "+ str(question_id))
                question_ids = self.chapter.question_ids.ids
                print(question_ids)
                self.chapter.sudo().write({'question_ids':[(6,0,question_id.id)]})
            
            elif self.upload_type == 'bulk':
                questions_data = self.excel_to_mcq_json(self.file)
                sequence = self.chapter.sequence
                sequence = sequence + 1
                questions = self.chapter.sudo().question_ids
    
                if self.delete_prev_ques == 'yes':
                    if questions:
                        answers = self.env['survey.question.answer'].sudo().search([('question_id', 'in', questions.ids)])
                        if answers:
                            answers.unlink()
                        questions.unlink()
                
                # Count existing questions in this chapter to determine starting number
                question_count = self.env['survey.question'].search_count([
                    ('page_id', '=', self.chapter.id)
                ])
                
                for i, q in enumerate(questions_data, start=1):
                    question_id = self.env['survey.question'].sudo().create({
                        'q_no': f"Q.{question_count + i}",
                        'survey_id': self.qb.id,
                        'is_scored_question': True,
                        'question_type': 'simple_choice',
                        'title': q['title'],
                        'page_id': self.chapter.id,
                        'sequence': sequence,
                    })
                # sequence += 1

                for option in q['options']:
                    self.env['survey.question.answer'].sudo().create({
                        'question_id': question_id.id,
                        'value': option['text'],
                        'is_correct': option['correct'],
                        'answer_score': option['marks']
                    })
          

            
 

            
        

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
    progression_mode = fields.Selection([
        ('percent', 'Percentage'),
        ('number', 'Number')], string='Progression Mode', default='number',
        help="If Number is selected, it will display the number of questions answered on the total number of question to answer.")
    
    questions_selection = fields.Selection([
        ('all', 'All questions'),
        ('random', 'Randomized per section')],
        string="Selection", required=True, default='random',
        help="If randomized is selected, you can configure the number of random questions by section. This mode is ignored in live session.")
    
    is_time_limited = fields.Boolean('The survey is limited in time',default=True)
    time_limit = fields.Float("Time limit (minutes)", default=0)
    users_can_go_back = fields.Boolean('Users can go back', help="If checked, users can go back to previous pages.",default=False)
    scoring_success_min = fields.Float('Success %', default=0)
    certification = fields.Boolean('Is a Certification',readonly=True, store=True,default=False)
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
# Survey Question Access rights
# bes.admin_survey_question_answer,access_survey_question_answer,model_survey_question_answer,bes.group_bes_admin,1,0,0,0
# access_survey_question_answer,Survey Question Answer,survey.model_survey_question_answer,bes.group_bes_admin,1,0,0,0
    
    
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
    

# class SurveyUserInputLineInherited(models.Model):
#     _inherit = "survey.user_input.line"
    
#     def write(self, vals):
#         # Prevent any write operations
#         raise ValidationError("Not allowed")
    
    


class SurveyUserInputInherited(models.Model):
    _inherit = "survey.user_input"
    survey_id = fields.Many2one('survey.survey', string='Exam', required=True, readonly=True, ondelete='cascade')
    exam_center = fields.Many2one("exam.center","Exam Region", compute="compute_details",store=True)
    examiner_token = fields.Char(string="Examiner Token",compute="compute_details", store=True)
    institute_id = fields.Many2one("bes.institute",string="Institute")
    gp_candidate = fields.Many2one('gp.candidate', string='GP Candidate', readonly=True)
    ccmc_candidate = fields.Many2one('ccmc.candidate', string='CCMC Candidate', readonly=True)
    dgs_batch = fields.Many2one("dgs.batches",string="Exam Batch",required=False)
    gp_exam = fields.Many2one('gp.exam.schedule', string='GP Exam (Roll No)', readonly=True)
    ccmc_exam = fields.Many2one('ccmc.exam.schedule', string='CCMC Exam (Roll No)', readonly=True)
    exam_date = fields.Date(string="Exam Date", readonly=True)
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
    commence_online_exam = fields.Boolean('commence_online_exam', default=False)

    online_start_time = fields.Datetime("Start Time")
    online_end_time = fields.Datetime("End Time")

    # def convert_to_ist(self, dt_utc):
    #     """Convert UTC datetime to IST."""
    #     if not dt_utc:
    #         return False  # Handle cases where the datetime is not provided
    #     ist_timezone = timezone('Asia/Kolkata')
    #     ist_time = dt_utc.replace(tzinfo=timezone('UTC')).astimezone(ist_timezone).replace(tzinfo=None)
    #     return ist_time
    

    # @api.depends('user_input_line_ids','online_start_time','online_end_time')
    # def _compute_online_time(self):
    #     for record in self:
    #         record.online_start_time = self.convert_to_ist(record.online_start_time)
    #         record.online_end_time = self.convert_to_ist(record.online_end_time)
    

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
                record.examiner_token = record.ccmc_exam.token
                record.exam_center = record.ccmc_exam.exam_region

            elif record.is_gp:
                record.indos = record.gp_candidate.indos_no
                record.examiner_token = record.gp_exam.token
                record.exam_center = record.gp_exam.exam_region
    
    @api.depends('user_input_line_ids', 'state')
    def _compute_total_time(self):
        ist_tz = pytz.timezone('Asia/Kolkata')  # Define IST timezone
        for record in self:
            if record.state == 'done' and record.user_input_line_ids:
                start_time_utc = record.user_input_line_ids[0].create_date
                end_time_utc = record.user_input_line_ids[-1].create_date

                if start_time_utc and end_time_utc:
                    # Convert UTC time to IST
                    start_time_ist = start_time_utc.astimezone(ist_tz)
                    end_time_ist = end_time_utc.astimezone(ist_tz)

                    total_time = end_time_ist - start_time_ist

                    # Format the times as hours:minutes:seconds
                    record.start_time = start_time_ist.strftime('%H:%M:%S')
                    record.end_time = end_time_ist.strftime('%H:%M:%S')

                    # Convert total_time (timedelta) to HH:MM:SS
                    total_seconds = int(total_time.total_seconds())
                    hours, remainder = divmod(total_seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)

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
    q_score = fields.Char("Q.Score",compute="_compute_score",store=True)
    answers_count = fields.Integer("No. of Answers",compute="_answer_count",store=True)
    difficulty_level = fields.Selection([
        ('easy','Easy'),
        ('moderate','Moderate'),
        ('hard','Hard')
    ], string="Difficulty Level",default='easy')
    
    # def create(self, vals):
    #     # First create the record
    #     record = super(InheritedSurveyQuestions, self).create(vals)
        
    #     print('vals')
    #     print(vals)
    #     print('page_id')
    #     print(record.page_id.id)
    #     # Count existing questions on same page
    #     question_count = self.search_count([('page_id','=',record.page_id.id)])
        
    #     # Update the sequence number of the new record
    #     record.write({'q_no': "Q." + str(question_count)})
        
    #     return record

        
    
    def unlink(self):
        above_records = self.search([('id', '>', self.id),('page_id','=',self.page_id.id)], order='id asc')
        
        for record in above_records:
            if record.q_no and record.q_no.startswith('Q.'):
                try:
                    q_num = int(record.q_no.split('.')[1])
                    record.q_no = f"Q.{q_num - 1}"
                except (ValueError, IndexError):
                    pass
            
        

        return super(InheritedSurveyQuestions, self).unlink()


    @api.depends('suggested_answer_ids')
    def _answer_count(self):
        for record in self:
            print("Computing count")
            record.answers_count = len(record.suggested_answer_ids)

    # @api.depends('suggested_answer_ids')
    @api.depends('suggested_answer_ids.answer_score', 'suggested_answer_ids.is_correct')
    def _compute_score(self):
        for question in self:
            print("Computing score")
            correct_answers = question.suggested_answer_ids.filtered(lambda ans: ans.is_correct)
            question.q_score = sum(answer.answer_score for answer in correct_answers)
            
            
    def action_confirm_delete(self):
        """ Opens a confirmation popup before deleting the question. """
        self.ensure_one()
        # import wdb;wdb.set_trace()

        return {
            'name': 'Confirm Delete',
            'type': 'ir.actions.act_window',
            'res_model': 'question.delete.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('bes.question_delete_wizard_form').id,
            'target': 'new',
            'context': {
                'default_question_id': self.id,
                'default_question_name': self.title,
                # 'default_chapter': self.chapter,
            }
        }

class QuestionDeleteWizard(models.TransientModel):
    _name = 'question.delete.wizard'
    _description = 'Confirm Question Deletion'
# 
    question_id = fields.Many2one('survey.question', string="Question", required=True)
    question_name = fields.Char(string="Question", readonly=True)
    # chapter = fields.Char(string="Chapter", readonly=True)

    def action_delete_question(self):
        """ Deletes the question after confirmation. """
        self.ensure_one()
        self.question_id.sudo().unlink()
        return {'type': 'ir.actions.act_window_close'}
