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
    
    def generate_report(self):
        self.institute_wise_pass_percentage()
            
        
        
    def institute_wise_pass_percentage(self):
        
        batch_id = self.examination_batch.id
        
        if self.course == 'gp':
            institute_ids = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',batch_id)]).institute_id.ids
            for institute_id in institute_ids:
                applied = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id)])
                appeared = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('absent_status','=','present')])
                passed = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('absent_status','=','present'),('result','=','passed')])
                vals = {
                    'examination_report_batch': self.id,  # Replace with the actual ID of the examination report batch
                    'institute_id': institute_id,              # Replace with the actual ID of the institute
                    'applied': applied,
                    'appeared': appeared,
                    'passed': passed,
                }
                self.env['institute.pass.percentage'].create(vals)      
        elif self.course == 'ccmc':
            institute_ids = self.env['ccmc.exam.schedule'].sudo().search([('dgs_batch','=',batch_id)]).institute_id.ids
            for institute_id in institute_ids:
                applied = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id)])
                appeared = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('absent_status','=','present')])
                passed = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('absent_status','=','present'),('result','=','passed')])
                vals = {
                    'examination_report_batch': self.id,  # Replace with the actual ID of the examination report batch
                    'institute_id': institute_id,              # Replace with the actual ID of the institute
                    'applied': applied,
                    'appeared': appeared,
                    'passed': passed,
                }
                self.env['institute.pass.percentage'].create(vals)    
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
    percentage = fields.Float("Percentage (%)", compute='_compute_percentage', store=True)
    
    @api.depends('appeared', 'passed')
    def _compute_percentage(self):
        for record in self:
            if record.appeared > 0:
                record.percentage = (record.passed / record.appeared) * 100
            else:
                record.percentage = 0.0

    
    