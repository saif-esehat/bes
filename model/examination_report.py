from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
import random
import logging
import qrcode
import io
import base64
from datetime import datetime , date
import math
from odoo.http import content_disposition, request , Response
from odoo.tools import date_utils
import xlsxwriter



class ExaminationReport(models.Model):
    _name = "examination.report"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'Examination Report'
    _rec_name = 'examination_batch'
    
    
    examination_batch = fields.Many2one("dgs.batches",string="Examination Batch",tracking=True)
    course = fields.Selection([
        ('gp', 'GP'),
        ('ccmc', 'CCMC')
    ], string='Course')
    
    exam_type = fields.Selection([
        ('fresh', 'Fresh'),
        ('repeater', 'Repeater')
    ],string='Type')
    
    # def generate_report(self):
        
        
    def institute_wise_pass_percentage(self):
        
        batch_id = self.examination_batch.id
        
        if self.course == 'gp':
            self.env['gp.exam.schedule'].sudo([('dgs_batch','=',batch_id)])
        
        elif self.course == 'ccmc':
            pass
            
    
    def open_institute_wise_pass_percentage(self):
        
        return {
        'name': 'Institute Wise Pass Percentage',
        'domain': [('examination_report_batch', '=', self.id)],
        'view_type': 'form',
        'res_model': 'institute.pass.percentage',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        'context': {}
        }       
    


class InsititutePassPercentage(models.Model):
    _name = "institute.pass.percentage"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'Institute Pass Percentage'
    
    
    examination_report_batch = fields.Many2one("examination.report",string="Examination Report Batch")
    examination_batch = fields.Many2one("dgs.batches",related="examination_report_batch.examination_batch",string="Examination Batch",tracking=True)
    course = fields.Selection([
        ('gp', 'GP'),
        ('ccmc', 'CCMC')
    ],related="examination_report_batch.course", string='Course')
    
    institute_id = fields.Many2one("bes.institute",string="Institute",tracking=True)
    
    applied = fields.Integer("Applied")
    appeared = fields.Integer("Appeared")
    passed = fields.Integer("Passed")
    percentage = fields.Float("Percentage (%)")

    
    