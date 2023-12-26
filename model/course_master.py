from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
from datetime import datetime


class CourseMaster(models.Model):
    _name = "course.master"
    _description= 'Course Master'
    _rec_name = 'name'
    name = fields.Char("Course Master")
    course_code = fields.Char("Course Code",required=True)
    exam_fees = fields.Many2one("product.product","Exam Fees Product")
    subjects = fields.One2many("course.master.subject","course_id",string="Subjects")



class CourseMaster(models.Model):
    _name = "course.master.subject"
    _description= 'Course Subject'
    _rec_name = 'name'
    
    course_id = fields.Many2one("course.master","Course ID")
    name = fields.Char("Course Subject")
    
    