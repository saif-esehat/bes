from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
from datetime import datetime


class CourseMaster(models.Model):
    _name = "course.master"
    _description= 'Course Master'
    _rec_name = 'name'
    name = fields.Char("Course Master")
    