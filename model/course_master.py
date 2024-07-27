from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
from datetime import datetime


class CourseMaster(models.Model):
    _name = "course.master"
    _description= 'Course Master'
    _rec_name = 'name'
    _inherit = ['mail.thread','mail.activity.mixin']
    name = fields.Char("Course Master",tracking=True)
    course_code = fields.Char("Course Code",required=True,tracking=True)
    exam_fees = fields.Many2one("product.product","Exam Fees Product",tracking=True)
    subjects = fields.One2many("course.master.subject","course_id",string="Subjects",tracking=True)



class CourseMaster(models.Model):
    _name = "course.master.subject"
    _description= 'Course Subject'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    course_id = fields.Many2one("course.master","Course ID",tracking=True)
    name = fields.Char("Course Subject",tracking=True)
    
    