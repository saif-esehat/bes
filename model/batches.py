from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError


from datetime import datetime

class BesBatches(models.Model):
    _name = "bes.batches"
    _rec_name = "schedule_name"
    _description= 'Schedule'
    schedule_name = fields.Char("Schedule Name",required=True)
    exam_date = fields.Datetime("Exam Date",required=True)
    course = fields.Many2one("course.master",string="Course",required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('notified', 'Notified'),
        ('done', 'Done'),        
    ], string='State', default='draft')
    exam_center = fields.Many2one("exam.center","Exam Center",required=True)

    


class InstituteBatches(models.Model):
    _name = "institute.batches"
    
    institute_id = fields.Many2one("bes.institute",string="Institute",required=True)
    batch_name = fields.Many2one("bes.batches",string="Batch",required=True)

        
