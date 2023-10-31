from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import werkzeug



class InheritedSurvey(models.Model):
    _inherit = "survey.survey"
    
    title = fields.Char('Exam Title', required=True, translate=True)
    course = fields.Many2one("course.master",string="Course",required=True)
    subject_ids = fields.Many2many("course.master.subject",string="Subject IDS",compute="_compute_subject_ids")
    subject = fields.Many2one("course.master.subject","Subject",required=True)
    users_login_required = fields.Boolean('Login Required',default=True, help="If checked, users have to login before answering even with a valid token.")
    is_attempts_limited = fields.Boolean('Limited number of attempts', help="Check this option if you want to limit the number of attempts per user",
                                         compute="_compute_is_attempts_limited",default=True, store=True, readonly=False)
    scoring_type = fields.Selection([
        ('no_scoring', 'No scoring'),
        ('scoring_with_answers', 'Scoring with answers at the end'),
        ('scoring_without_answers', 'Scoring without answers at the end')],
        string="Scoring", required=True, default='scoring_without_answers')
    is_trigger_exam = fields.Boolean('Trigger Exam')
    trigger_exam = fields.Many2one("survey.survey","Triggering Exam")
    trigger_exam_url = fields.Char("Trigger Exam URL",compute="_compute_exam_start_url")
    
    questions_layout = fields.Selection([
        ('one_page', 'One page with all the questions'),
        ('page_per_section', 'One page per section'),
        ('page_per_question', 'One page per question')],
        string="Layout", required=True, default='page_per_section')
    
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
