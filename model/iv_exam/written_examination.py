from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
import base64
from io import BytesIO
import xlsxwriter
from datetime import datetime
import xlrd


    
class IVWrittenExam(models.Model):
    _name = "iv.written.exam"
    _description= 'IV Candidate Written Exam'
    
    candidate = fields.Many2one('iv.candidates',string="Candidate")
    batch_id = fields.Many2one('iv.batches', string="IV Batch")
    grade = fields.Selection([
        ('1CM', 'First Class Master'),
        ('2CM', 'Second Class Master'),
        ('SER', 'Serang'),
        ('ME', 'Motor Engineer'),
        ('1ED', 'First Class Engine Driver'),
        ('2ED', 'Second Class Engine Driver'),
        ], string='Grade')
    marks = fields.Float('Total Marks')
    mmb_marks = fields.Float("MMB Marks")
    attendance = fields.Boolean('Candidate Present')

    status = fields.Selection([
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('absent', 'Absent'),
        ], string='Status',default='failed',compute="_compute_status")
    
    @api.onchange('marks')
    def _change_marks(self):
        for record in self:
            record.mmb_marks = record.marks

    @api.depends('attendance','mmb_marks')
    def _compute_status(self):
        for record in self:
            if record.mmb_marks < 25:
                record.status = 'failed'
            if record.mmb_marks >= 25:
                record.status = 'passed'
            if record.attendance == False:
                record.status = 'absent'

    

class IVOralExam(models.Model):
    _name = "iv.oral.exam"
    _description= 'IV Candidate Oral Exam'
    
    candidate = fields.Many2one('iv.candidates',string="Candidate")
    batch_id = fields.Many2one('iv.batches', string="IV Batch")
    grade = fields.Selection([
        ('1CM', 'First Class Master'),
        ('2CM', 'Second Class Master'),
        ('SER', 'Serang'),
        ('ME', 'Motor Engineer'),
        ('1ED', 'First Class Engine Driver'),
        ('2ED', 'Second Class Engine Driver'),
        ], string='Grade')

    marks = fields.Float('Total Marks')
    attendance = fields.Boolean('Candidate Present')

    status = fields.Selection([
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('absent', 'Absent'),
        ], string='Status',default='failed',compute="_compute_status")
    
   
    @api.depends('attendance','marks')
    def _compute_status(self):
        for record in self:
            if record.marks < 25:
                record.status = 'failed'
            if record.marks >= 25:
                record.status = 'passed'
            if record.attendance == False:
                record.status = 'absent'