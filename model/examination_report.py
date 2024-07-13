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
        self.subject_wise_pass_percentage()
            
    
    def subject_wise_pass_percentage(self):
        
        if self.course == 'gp':
            batch_id = self.examination_batch.id
            examination_report_batch = self.id
            appeared = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch', '=', batch_id), ('absent_status', '=', 'present')])

            gsk_oral_prac = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch', '=', batch_id), ('gsk_oral_prac_status', '=', 'passed')])
            try:
                gsk_oral_prac_percentage = (gsk_oral_prac / appeared) * 100
            except ZeroDivisionError:
                gsk_oral_prac_percentage = 0

            mek_oral_prac = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch', '=', batch_id), ('mek_oral_prac_status', '=', 'passed')])
            try:
                mek_oral_prac_percentage = (mek_oral_prac / appeared) * 100
            except ZeroDivisionError:
                mek_oral_prac_percentage = 0

            mek_online = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch', '=', batch_id), ('mek_online_status', '=', 'passed')])
            try:
                mek_online_percentage = (mek_online / appeared) * 100
            except ZeroDivisionError:
                mek_online_percentage = 0

            gsk_online = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch', '=', batch_id), ('gsk_online_status', '=', 'passed')])
            try:
                gsk_online_percentage = (gsk_online / appeared) * 100
            except ZeroDivisionError:
                gsk_online_percentage = 0

            
            for i in range(4):
                
                if i == 0:
                    subject = 'gsk_prac_oral'
                    data = {
                        'examination_report_batch': examination_report_batch,
                        'subject': subject,
                        'percentage': gsk_oral_prac_percentage
                        }
                elif i == 1:
                    subject = 'mek_prac_oral'
                    data = {
                        'examination_report_batch': examination_report_batch,
                        'subject': subject,
                        'percentage': mek_oral_prac_percentage
                        }
                elif i == 2:
                    subject = 'gsk_online'
                    data = {
                        'examination_report_batch': examination_report_batch,
                        'subject': subject,
                        'percentage': gsk_online_percentage
                        }
                elif i == 3:
                    subject = 'mek_online'
                    data = {
                        'examination_report_batch': examination_report_batch,
                        'subject': subject,
                        'percentage': mek_online_percentage
                        }
                self.env['subject.pass.percentage'].sudo().create(data)
        
        elif self.course == 'ccmc':
            examination_report_batch = self.id
            batch_id = self.examination_batch.id
            appeared = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('absent_status','=','present')])
            print(appeared)
            cookery_bakery_prac = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('cookery_bakery_prac_status','=','passed')])
            
            try:
                cookery_bakery_prac_percentage = (cookery_bakery_prac / appeared) * 100
            except ZeroDivisionError:
                cookery_bakery_prac_percentage = 0

            ccmc_oral_prac = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('ccmc_oral_prac_status','=','passed')])
            try:
                ccmc_oral_prac_percentage = (ccmc_oral_prac / appeared) * 100
            except ZeroDivisionError:
                ccmc_oral_prac_percentage = 0

            ccmc_online = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('ccmc_online_status','=','passed')])
            try:
                ccmc_online_percentage = (ccmc_online / appeared) * 100
            except ZeroDivisionError:
                ccmc_online_percentage = 0
                
            for i in range(3):
                if i == 0:
                    subject = 'cookery_bakery'
                    data = {
                        'examination_report_batch': examination_report_batch,
                        'subject': subject,
                        'percentage': cookery_bakery_prac_percentage
                        }
                    # data = self.env['subject.pass.percentage'].sudo().create(data)
                    # data 

                elif i == 1:
                    subject = 'ccmc_oral'
                    data = {
                        'examination_report_batch': examination_report_batch,
                        'subject': subject,
                        'percentage': ccmc_oral_prac_percentage
                        }
                elif i == 2:
                    subject = 'ccmc_online'
                    data = {
                        'examination_report_batch': examination_report_batch,
                        'subject': subject,
                        'percentage': ccmc_online_percentage
                        }
                self.env['subject.pass.percentage'].sudo().create(data)

                    

            
                
                

                    
         
            
                    
                    
                    
        
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
    
    def open_subject_wise_pass_percentage(self):
        
        return {
            'name': 'Subject Wise Pass Percentage',
            'domain': [('examination_report_batch', '=', self.id)],
            'view_type': 'form',
            'res_model': 'subject.pass.percentage',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'context': {}
            }  
    
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

    def print_summarised_gp_report(self):
        
        datas = {
            'doc_ids': self.id,
            'course': 'GP',
            'batch_id': self.examination_batch  # Assuming examination_batch is a recordset and you want its ID
        }
        
        if self.exam_type == 'repeater':
            datas['report_type'] = 'Repeater'
        elif self.exam_type == 'fresh':
            datas['report_type'] = 'Fresh'
            
        return self.env.ref('bes.summarised_gp_report_action').report_action(self ,data=datas) 
   
    def print_summarised_ccmc_report(self):
        
        datas = {
            'doc_ids': self.id,
            'course': 'CCMC',
            'batch_id': self.examination_batch  # Assuming examination_batch is a recordset and you want its ID
        }
        
        if self.exam_type == 'repeater':
            datas['report_type'] = 'Repeater'
        elif self.exam_type == 'fresh':
            datas['report_type'] = 'Fresh'
            
        return self.env.ref('bes.summarised_ccmc_report_action').report_action(self ,data=datas) 
    


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

<<<<<<< HEAD
class SummarisedGPReport(models.AbstractModel):
    _name = "report.bes.summarised_gp_report"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "Summarised GP Report"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docids = data['doc_ids']
        docs1 = self.env['examination.report'].sudo().browse(docids)
        report_type = data['report_type']
        course = data['course']

        if report_type == 'Fresh' and course == 'GP':
            exams = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',docs1.id), ('attempt_number', '=', '1')])
        elif report_type == 'Repeater' and course == 'GP':
            exams = self.env['gp.exam.schedule'].sudo().search([('dgs_batch', '=', docs1.id), ('attempt_number', '>', '1')])
        
        institutes = self.env['bes.institute'].sudo().search([], order='code asc')
        exam_centers = self.env['exam.center'].sudo().search([])

        return {
            'docids': docids,
            'doc_model': 'gp.exam.schedule',
            'docs': docs1,
            'exams': exams,
            'institutes': institutes,
            'exam_centers': exam_centers,
            'report_type': report_type,
            'course': course
        }

class SummarisedCCMCReport(models.AbstractModel):
    _name = "report.bes.summarised_ccmc_report"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "Summarised CCMC Report"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docids = data['doc_ids']
        docs1 = self.env['examination.report'].sudo().browse(docids)
        report_type = data['report_type']
        course = data['course']

        if report_type == 'Fresh' and course == 'CCMC':
            exams = self.env['ccmc.exam.schedule'].sudo().search([('dgs_batch','=',docs1.id), ('attempt_number', '=', '1')])
        elif report_type == 'Repeater' and course == 'CCMC':
            exams = self.env['ccmc.exam.schedule'].sudo().search([('dgs_batch', '=', docs1.id), ('attempt_number', '>', '1')])
        
        institutes = self.env['bes.institute'].sudo().search([], order='code asc')
        exam_centers = self.env['exam.center'].sudo().search([])

        return {
            'docids': docids,
            'doc_model': 'ccmc.exam.schedule',
            'docs': docs1,
            'exams': exams,
            'institutes': institutes,
            'exam_centers': exam_centers,
            'report_type': report_type,
            'course': course
        }

=======

class SubjectPassPercentage(models.Model):
    _name = "subject.pass.percentage"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'Subject Pass Percentage'
    
    
    examination_report_batch = fields.Many2one("examination.report",string="Examination Report Batch")
    examination_batch = fields.Many2one("dgs.batches",related="examination_report_batch.examination_batch",string="Examination Batch",tracking=True)
    subject = fields.Selection([
        ('gsk_prac_oral', 'GSK Practical/Oral'),
        ('mek_prac_oral', 'MEK Practical/Oral'),
        ('gsk_online', 'GSK Online'),
        ('mek_online', 'MEK Online'),
        ('cookery_bakery', 'Cookery Bakery'),
        ('ccmc_oral', 'CCMC Oral'),
        ('ccmc_online', 'CCMC Online')
    ], string='Subject')
    
    percentage = fields.Float("Percentage (%)")
    
    # percentage = fields.Float("Percentage (%)", compute='_compute_percentage', store=True)
    
    # @api.depends('appeared', 'passed')
    # def _compute_percentage(self):
    #     for record in self:
    #         if record.appeared > 0:
    #             record.percentage = (record.passed / record.appeared) * 100
    #         else:
    #             record.percentage = 0.0
>>>>>>> 5e7f195c06c30d24f688fc2cd45e21b9919851f6
    