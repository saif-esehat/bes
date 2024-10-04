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
    
    sequence_report = fields.Char("Exam Sequence No.")
    
    visible_gp_report_button = fields.Boolean(string='Visible GP Report Button',compute="show_repeater_report_button",tracking=True)
    visible_ccmc_report_button = fields.Boolean(string='Visible CCMC Report Button',compute="show_repeater_report_button",tracking=True)
    visible_gp_repeater_report_button = fields.Boolean(string='Visible GP Repeater Report Button',compute="show_repeater_report_button",tracking=True)
    visible_ccmc_repeater_report_button = fields.Boolean(string='Visible CCMC Repeater Report Button',compute="show_repeater_report_button",tracking=True)

    
    @api.depends('exam_type','course')
    def show_repeater_report_button(self):
        for record in self:
            if record.exam_type == 'fresh' and record.course == 'gp':
                record.visible_gp_report_button = True
                record.visible_ccmc_report_button = False
                record.visible_gp_repeater_report_button = False
                record.visible_ccmc_repeater_report_button = False
            elif record.exam_type == 'fresh' and record.course == 'ccmc':
                record.visible_gp_report_button = False
                record.visible_ccmc_report_button = True
                record.visible_gp_repeater_report_button = False
                record.visible_ccmc_repeater_report_button = False
            elif record.exam_type == 'repeater' and record.course == 'gp':
                record.visible_gp_report_button = False
                record.visible_ccmc_report_button = False
                record.visible_gp_repeater_report_button = True
                record.visible_ccmc_repeater_report_button = False
            elif record.exam_type == 'repeater' and record.course == 'ccmc':
                record.visible_gp_report_button = False
                record.visible_ccmc_report_button = True
                record.visible_gp_repeater_report_button = False
                record.visible_ccmc_repeater_report_button = True
            else:
                record.visible_gp_report_button = False
                record.visible_ccmc_report_button = False
                record.visible_gp_repeater_report_button = False
                record.visible_ccmc_repeater_report_button = False
            
    
    def generate_report(self):
        self.institute_wise_pass_percentage()
        self.subject_wise_pass_percentage()
        self.summarised_report()
        self.attempt_wise_report()
        
    
    def ordinal(self,n):
        if 10 <= n % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return str(n) + suffix + " attempt"
    
    
    def attempt_wise_report(self):
        
        if self.course == 'gp' and self.exam_type == 'repeater':
            batch_id = self.examination_batch.id
            exam_schedules = self.env['gp.exam.schedule'].sudo().search([('dgs_batch', '=', batch_id)])

            # Extract the attempt numbers and get the unique values
            attempt_numbers = list(set(exam_schedules.mapped('attempt_number')))
            attempt_numbers.sort(reverse=True)
            print(attempt_numbers)
            
            for attempt_number in  attempt_numbers:
                absent = 0
                attempt_number = attempt_number
                applied_records = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',batch_id),('attempt_number','=',attempt_number)])
                for record in applied_records:
                    index = 0
                    row = [ ]
                    if record.gsk_oral_prac_carry_forward:
                        gsk_status = "AP"
                        row.append(gsk_status)
                    elif record.gsk_oral_prac_status == 'passed':
                        gsk_status = "P"
                        row.append(gsk_status)
                    elif record.gsk_oral_prac_attendance == 'absent':
                         gsk_status = "A"
                         row.append(gsk_status)
                    else:
                        gsk_status = "F"
                        row.append(gsk_status)
                         
                    if record.mek_oral_prac_carry_forward:
                        mek_status = "AP"
                        row.append(mek_status)
                    elif record.mek_oral_prac_status == 'passed':
                        mek_status = "P"
                        row.append(mek_status)
                    elif record.mek_oral_prac_attendance == 'absent':
                         mek_status = "A"
                         row.append(mek_status)
                    else:
                        mek_status = "F"
                        row.append(mek_status)
                    
                    if record.mek_online_carry_forward:
                        mek_online_status = "AP"
                        row.append(mek_online_status)
                    elif record.mek_online_status == 'passed':
                        mek_online_status = "P"
                        row.append(mek_online_status)
                    elif record.mek_online_attendance == 'absent':
                         mek_online_status = "A"
                         row.append(mek_online_status)
                    else:
                        mek_online_status = "F"
                        row.append(mek_online_status)
                    
                    if record.gsk_online_carry_forward:
                        gsk_online_status = "AP"
                        row.append(gsk_online_status)
                    elif record.gsk_online_status == 'passed':
                        gsk_online_status = "P"
                        row.append(gsk_online_status)
                    elif record.gsk_online_attendance == 'absent':
                         gsk_online_status = "A"
                         row.append(gsk_online_status)
                    else:
                        gsk_online_status = "F"
                        row.append(gsk_online_status)
                    
                    allowed_values = {'AP', 'A'}
    
                    # Convert the record to a set to find unique values
                    unique_values = set(row)
                    # absent_status = False
                    # Check if the unique values are a subset of allowed values
                    if unique_values.issubset(allowed_values) and len(unique_values) <= len(allowed_values):
                        absent = absent + 1

                appeared = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('attempt_number','=',attempt_number)])
                appeared = appeared - absent
                passed = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('attempt_number','=',attempt_number),('result','=','passed')])
                print('appeared')
                print(appeared)
                print('passed')
                print(passed)
                
                data = {
                    'examination_report_batch':self.id,
                    'attempt_number': self.ordinal(attempt_number),
                    'appeared':appeared,
                    'passed':passed
                }
                
                self.env['attempt.wise.report'].sudo().create(data)
        
        elif self.course == 'ccmc' and self.exam_type == 'repeater':
            batch_id = self.examination_batch.id
            exam_schedules = self.env['ccmc.exam.schedule'].sudo().search([('dgs_batch', '=', batch_id)])

            # Extract the attempt numbers and get the unique values
            attempt_numbers = list(set(exam_schedules.mapped('attempt_number')))
            attempt_numbers.sort(reverse=True)
            print(attempt_numbers)
            
            for attempt_number in  attempt_numbers:
                absent = 0
                attempt_number = attempt_number
                applied_records = self.env['ccmc.exam.schedule'].sudo().search([('dgs_batch','=',batch_id),('attempt_number','=',attempt_number)])
                for record in applied_records:
                    row = []
                    if record.cookery_prac_carry_forward and record.cookery_bakery_prac_oral_status == 'passed':
                        cookery_prac_status = "AP"
                        row.append(cookery_prac_status)
                    elif record.cookery_bakery_prac_oral_status == "passed":
                        cookery_prac_status = "P"
                        row.append(cookery_prac_status)
                    elif record.cookery_prac_attendance:
                        cookery_prac_status = "A"
                        row.append(cookery_prac_status)
                    else:
                        cookery_prac_status = "F"
                        row.append(cookery_prac_status)
                    
                    if record.cookery_oral_carry_forward and record.ccmc_oral_prac_status == 'passed':
                        ccmc_oral_prac_status = "AP"
                        row.append(ccmc_oral_prac_status)
                    elif record.ccmc_oral_prac_status == "passed":
                        ccmc_oral_prac_status = "P"
                        row.append(ccmc_oral_prac_status)
                    elif record.ccmc_gsk_oral_attendance:
                        ccmc_oral_prac_status = "A"
                        row.append(ccmc_oral_prac_status)
                    else:
                        ccmc_oral_prac_status = "F"
                        row.append(ccmc_oral_prac_status)
                        
                    if record.cookery_gsk_online_carry_forward and record.ccmc_online_status == 'passed':
                        ccmc_online_status = "AP"
                        row.append(ccmc_online_status)
                    elif record.ccmc_oral_prac_status == "passed":
                        ccmc_online_status = "P"
                        row.append(ccmc_online_status)
                    elif record.ccmc_gsk_oral_attendance:
                        ccmc_online_status = "A"
                        row.append(ccmc_online_status)
                    else:
                        ccmc_online_status = "F"
                        row.append(ccmc_online_status)
                    
                    allowed_values = {'AP', 'A'}
                    
                    unique_values = set(row)
                    
                    if unique_values.issubset(allowed_values) and len(unique_values) <= len(allowed_values):
                        absent = absent + 1    
                
                appeared = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('attempt_number','=',attempt_number)])
                appeared = appeared - absent
                passed = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('attempt_number','=',attempt_number),('result','=','passed')])
                print('appeared')
                print(appeared)
                print('passed')
                print(passed)
                
                data = {
                    'examination_report_batch':self.id,
                    'attempt_number': self.ordinal(attempt_number),
                    'appeared':appeared,
                    'passed':passed
                }
                
                self.env['attempt.wise.report'].sudo().create(data)
        
        else:
            pass

                
            
            # self.env['attempt.wise.report'].sudo().create({})
            
        
               

    def summarised_report(self):
        batch_id = self.examination_batch.id
        
        if self.course == 'gp' and self.exam_type == 'fresh':
            institute_ids = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',batch_id)]).institute_id.ids
            for institute_id in institute_ids:
                applied = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id)])
                appeared = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('absent_status','=','present')])
                
                #GSK Prac/Oral
                gsk_passed_count =  self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('gsk_oral_prac_status','=','passed')])
                gsk_passed_percentage = (gsk_passed_count/appeared) * 100
                
                #MEK Prac/Oral
                mek_passed_count =  self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('mek_oral_prac_status','=','passed')])
                mek_passed_percentage = (mek_passed_count/appeared) * 100
                
                #GSK Online
                gsk_online_passed_count =  self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('gsk_online_status','=','passed')])
                gsk_online_passed_percentage = (gsk_online_passed_count/appeared) * 100
                
                #MEK Online
                mek_online_passed_count =  self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('mek_online_status','=','passed')])
                mek_online_passed_percentage = (mek_online_passed_count/appeared) * 100
                
                
                overall_passed = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('absent_status','=','present'),('result','=','passed')])
                
                vals = {
                    'examination_report_batch': self.id,  # Assuming 1 is the ID of the examination report batch
                    'institute': institute_id,  # Assuming 2 is the ID of the institute
                    'applied': applied,
                    'candidate_appeared': appeared,
                    'gsk_prac_oral_pass': gsk_passed_count,
                    'gsk_prac_oral_pass_per': gsk_passed_percentage,
                    'mek_prac_oral_pass': mek_passed_count,
                    'mek_prac_oral_pass_per': mek_passed_percentage,
                    'gsk_online_pass': gsk_online_passed_count,
                    'gsk_online_pass_per': gsk_online_passed_percentage,
                    'mek_online_pass': mek_online_passed_count,
                    'mek_online_pass_per': mek_online_passed_percentage,
                    'overall_pass': overall_passed,  # Sum of all passes
                    # The overall_pass_per will be computed automatically
                }
                
                self.env['summarised.gp.report'].create(vals)
        
        elif self.course == 'ccmc' and self.exam_type == 'fresh':
            
            batch_id = self.examination_batch.id

            institute_ids = self.env['ccmc.exam.schedule'].sudo().search([('dgs_batch','=',batch_id)]).institute_id.ids
            for institute_id in institute_ids:


                applied = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id)])
                appeared = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('absent_status','=','present')])

                practical = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('cookery_bakery_prac_status','=','passed')])
                practical_percentage = (practical/appeared) * 100
                
                oral = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('ccmc_oral_prac_status','=','passed')])
                oral_percentage = (oral/appeared) * 100
                
                online = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('ccmc_online_status','=','passed')])
                online_percentage = (online/appeared) * 100
                
                overall_passed = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('absent_status','=','present'),('result','=','passed')])
                
                vals = {
                        'examination_report_batch': self.id,  # Assuming 1 is the ID of the examination report batch
                        'institute': institute_id,  # Assuming 2 is the ID of the institute
                        'applied': applied,
                        'candidate_appeared': appeared,
                        'practical_pass_appeared': appeared,
                        'practical_pass': practical,
                        'practical_pass_per': practical_percentage,
                        'oral_pass_appeared': appeared,
                        'oral_pass': oral,
                        'oral_pass_per': oral_percentage,
                        'online_pass_appeared': appeared,
                        'online_pass': online,
                        'online_pass_per': online_percentage,
                        'overall_pass': overall_passed,  # Sum of all passes
                        # The overall_pass_per will be computed automatically
                    }
                self.env['summarised.ccmc.report'].create(vals)
        
        elif self.course == 'gp' and self.exam_type == 'repeater':
            institute_ids = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',batch_id)]).institute_id.ids
            overall_absent = 0
            for institute_id in institute_ids:
                absent = 0
                applied_records = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',batch_id),('institute_id','=',institute_id)])

                for record in applied_records:
                    index = 0
                    row = [ ]
                    if record.gsk_oral_prac_carry_forward:
                        gsk_status = "AP"
                        row.append(gsk_status)
                    elif record.gsk_oral_prac_status == 'passed':
                        gsk_status = "P"
                        row.append(gsk_status)
                    elif record.gsk_oral_prac_attendance == 'absent':
                         gsk_status = "A"
                         row.append(gsk_status)
                    else:
                        gsk_status = "F"
                        row.append(gsk_status)
                         
                    if record.mek_oral_prac_carry_forward:
                        mek_status = "AP"
                        row.append(mek_status)
                    elif record.mek_oral_prac_status == 'passed':
                        mek_status = "P"
                        row.append(mek_status)
                    elif record.mek_oral_prac_attendance == 'absent':
                         mek_status = "A"
                         row.append(mek_status)
                    else:
                        mek_status = "F"
                        row.append(mek_status)
                    
                    if record.mek_online_carry_forward:
                        mek_online_status = "AP"
                        row.append(mek_online_status)
                    elif record.mek_online_status == 'passed':
                        mek_online_status = "P"
                        row.append(mek_online_status)
                    elif record.mek_online_attendance == 'absent':
                         mek_online_status = "A"
                         row.append(mek_online_status)
                    else:
                        mek_online_status = "F"
                        row.append(mek_online_status)
                    
                    if record.gsk_online_carry_forward:
                        gsk_online_status = "AP"
                        row.append(gsk_online_status)
                    elif record.gsk_online_status == 'passed':
                        gsk_online_status = "P"
                        row.append(gsk_online_status)
                    elif record.gsk_online_attendance == 'absent':
                         gsk_online_status = "A"
                         row.append(gsk_online_status)
                    else:
                        gsk_online_status = "F"
                        row.append(gsk_online_status)
                    
                    allowed_values = {'AP', 'A'}
    
                    # Convert the record to a set to find unique values
                    unique_values = set(row)
                    # absent_status = False
                    # Check if the unique values are a subset of allowed values
                    if unique_values.issubset(allowed_values) and len(unique_values) <= len(allowed_values):
                        absent = absent + 1

                ins_name = self.env['bes.institute'].sudo().search([('id','=',institute_id)])
                print("Institute  "+str(ins_name.name)+" Absent "+ str(absent))
                    
                
                applied = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id)])
                # appeared = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('absent_status','=','present')])
                appeared = applied - absent
                
                #GSK Prac/Oral
                
                gsk_appeared =  self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('gsk_oral_prac_carry_forward','=',False),('gsk_oral_prac_attendance','=','present')])                
                gsk_passed_count =  self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('gsk_oral_prac_carry_forward','=',False),('gsk_oral_prac_status','=','passed')])
                try:
                    gsk_passed_percentage = (gsk_passed_count/gsk_appeared) * 100
                except ZeroDivisionError:
                    gsk_passed_percentage = 0
                
                #MEK Prac/Oral
                mek_appeared =  self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('mek_oral_prac_carry_forward','=',False),('mek_oral_prac_attendance','=','present')])                
                mek_passed_count =  self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('mek_oral_prac_status','=','passed'),('mek_oral_prac_carry_forward','=',False)])
                try:
                    mek_passed_percentage = (mek_passed_count/mek_appeared) * 100
                except ZeroDivisionError:
                    mek_passed_percentage = 0
                
                #GSK Online
                gsk_online_appeared =  self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('gsk_online_carry_forward','=',False),('gsk_online_attendance','=','present')])
                gsk_online_passed_count =  self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('gsk_online_status','=','passed'),('gsk_online_carry_forward','=',False)])
                try:
                    gsk_online_passed_percentage = (gsk_online_passed_count/gsk_online_appeared) * 100
                except ZeroDivisionError:
                    gsk_online_passed_percentage = 0
                    
                #MEK Online
                mek_online_appeared =  self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('mek_online_carry_forward','=',False),('mek_online_attendance','=','present')])                
                mek_online_passed_count =  self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('mek_online_status','=','passed'),('mek_online_carry_forward','=',False)])
                try:
                    mek_online_passed_percentage = (mek_online_passed_count/mek_online_appeared) * 100
                except ZeroDivisionError:
                    mek_online_passed_percentage = 0
                    
                
                overall_passed = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('absent_status','=','present'),('result','=','passed')])
                
                vals = {
                    'examination_report_batch': self.id,  # Assuming 1 is the ID of the examination report batch
                    'institute': institute_id,  # Assuming 2 is the ID of the institute
                    'applied': applied,
                    'candidate_appeared': appeared,
                    'gsk_prac_oral_appeared':gsk_appeared,
                    'gsk_prac_oral_pass': gsk_passed_count,
                    'gsk_prac_oral_pass_per': gsk_passed_percentage,
                    'mek_prac_oral_appeared':mek_appeared,
                    'mek_prac_oral_pass': mek_passed_count,
                    'mek_prac_oral_pass_per': mek_passed_percentage,
                    'gsk_online_appeared':gsk_online_appeared,
                    'gsk_online_pass': gsk_online_passed_count,
                    'gsk_online_pass_per': gsk_online_passed_percentage,
                    'mek_online_appeared':mek_online_appeared,
                    'mek_online_pass': mek_online_passed_count,
                    'mek_online_pass_per': mek_online_passed_percentage,
                    'overall_pass': overall_passed,  # Sum of all passes
                    # The overall_pass_per will be computed automatically
                }
                
                self.env['summarised.gp.repeater.report'].create(vals)
            
            print("overall_absent")    
            print(overall_absent)
        
        elif self.course == 'ccmc' and self.exam_type == 'repeater':
            batch_id = self.examination_batch.id
            institute_ids = self.env['ccmc.exam.schedule'].sudo().search([('dgs_batch','=',batch_id)]).institute_id.ids
            overall_absent = 0
            for institute_id in institute_ids:
                absent = 0
                applied_records = self.env['ccmc.exam.schedule'].sudo().search([('dgs_batch','=',batch_id),('institute_id','=',institute_id)])
                
                for record in applied_records:
                    index = 0
                    row = []
                    if record.cookery_prac_carry_forward and record.cookery_bakery_prac_oral_status == 'passed':
                        cookery_prac_status = "AP"
                        row.append(cookery_prac_status)
                    elif record.cookery_bakery_prac_oral_status == "passed":
                        cookery_prac_status = "P"
                        row.append(cookery_prac_status)
                    elif record.cookery_prac_attendance:
                        cookery_prac_status = "A"
                        row.append(cookery_prac_status)
                    else:
                        cookery_prac_status = "F"
                        row.append(cookery_prac_status)
                    
                    if record.cookery_oral_carry_forward and record.ccmc_oral_prac_status == 'passed':
                        ccmc_oral_prac_status = "AP"
                        row.append(ccmc_oral_prac_status)
                    elif record.ccmc_oral_prac_status == "passed":
                        ccmc_oral_prac_status = "P"
                        row.append(ccmc_oral_prac_status)
                    elif record.ccmc_gsk_oral_attendance:
                        ccmc_oral_prac_status = "A"
                        row.append(ccmc_oral_prac_status)
                    else:
                        ccmc_oral_prac_status = "F"
                        row.append(ccmc_oral_prac_status)
                        
                    if record.cookery_gsk_online_carry_forward and record.ccmc_online_status == 'passed':
                        ccmc_online_status = "AP"
                        row.append(ccmc_online_status)
                    elif record.ccmc_oral_prac_status == "passed":
                        ccmc_online_status = "P"
                        row.append(ccmc_online_status)
                    elif record.ccmc_gsk_oral_attendance:
                        ccmc_online_status = "A"
                        row.append(ccmc_online_status)
                    else:
                        ccmc_online_status = "F"
                        row.append(ccmc_online_status)
                    
                    allowed_values = {'AP', 'A'}
                    
                    unique_values = set(row)
                    
                    if unique_values.issubset(allowed_values) and len(unique_values) <= len(allowed_values):
                        absent = absent + 1    
                
                applied = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id)])
       
                appeared = applied - absent                        
                # appeared = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('absent_status','=','present')])

                practical_appeared = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('cookery_prac_carry_forward','=',False),('cookery_prac_attendance','=','present')])
                practical = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('cookery_bakery_prac_status','=','passed'),('cookery_prac_carry_forward','=',False),('cookery_prac_attendance','=','present')])
                try :
                    practical_percentage = (practical/practical_appeared) * 100
                except ZeroDivisionError:
                    practical_percentage = 0
                    
                oral_appeared = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('cookery_oral_carry_forward','=',False),('ccmc_gsk_oral_attendance','=','present')])                
                oral = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('ccmc_oral_prac_status','=','passed'),('cookery_oral_carry_forward','=',False),('ccmc_gsk_oral_attendance','=','present')])
                
                try:
                    oral_percentage = (oral/oral_appeared) * 100
                except ZeroDivisionError:
                    oral_percentage = 0

                online_appeared = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('cookery_gsk_online_carry_forward','=',False),('ccmc_online_attendance','=','present')])                
                online = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('ccmc_online_status','=','passed'),('cookery_gsk_online_carry_forward','=',False),('ccmc_online_attendance','=','present')])
                
                try:
                    online_percentage = (online/online_appeared) * 100
                except ZeroDivisionError:
                    online_percentage = 0
                
                overall_passed = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('absent_status','=','present'),('result','=','passed')])
                
                vals = {
                        'examination_report_batch': self.id,  # Assuming 1 is the ID of the examination report batch
                        'institute': institute_id,  # Assuming 2 is the ID of the institute
                        'applied': applied,
                        'candidate_appeared': appeared,
                        'practical_pass_appeared': practical_appeared,
                        'practical_pass': practical,
                        'practical_pass_per': practical_percentage,
                        'oral_pass_appeared': oral_appeared,
                        'oral_pass': oral,
                        'oral_pass_per': oral_percentage,
                        'online_pass_appeared': online_appeared,
                        'online_pass': online,
                        'online_pass_per': online_percentage,
                        'overall_pass': overall_passed,  # Sum of all passes
                        # The overall_pass_per will be computed automatically
                    }
                self.env['summarised.ccmc.report'].create(vals)
            
                
    
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
        
        if self.course == 'gp' and self.exam_type == 'fresh':
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
        
        elif self.course == 'gp' and self.exam_type == 'repeater':
            institute_ids = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',batch_id)]).institute_id.ids
            for institute_id in institute_ids:
                absent = 0
                applied_records = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',batch_id),('institute_id','=',institute_id)])

                for record in applied_records:
                    index = 0
                    row = [ ]
                    if record.gsk_oral_prac_carry_forward:
                        gsk_status = "AP"
                        row.append(gsk_status)
                    elif record.gsk_oral_prac_status == 'passed':
                        gsk_status = "P"
                        row.append(gsk_status)
                    elif record.gsk_oral_prac_attendance == 'absent':
                         gsk_status = "A"
                         row.append(gsk_status)
                    else:
                        gsk_status = "F"
                        row.append(gsk_status)
                         
                    if record.mek_oral_prac_carry_forward:
                        mek_status = "AP"
                        row.append(mek_status)
                    elif record.mek_oral_prac_status == 'passed':
                        mek_status = "P"
                        row.append(mek_status)
                    elif record.mek_oral_prac_attendance == 'absent':
                         mek_status = "A"
                         row.append(mek_status)
                    else:
                        mek_status = "F"
                        row.append(mek_status)
                    
                    if record.mek_online_carry_forward:
                        mek_online_status = "AP"
                        row.append(mek_online_status)
                    elif record.mek_online_status == 'passed':
                        mek_online_status = "P"
                        row.append(mek_online_status)
                    elif record.mek_online_attendance == 'absent':
                         mek_online_status = "A"
                         row.append(mek_online_status)
                    else:
                        mek_online_status = "F"
                        row.append(mek_online_status)
                    
                    if record.gsk_online_carry_forward:
                        gsk_online_status = "AP"
                        row.append(gsk_online_status)
                    elif record.gsk_online_status == 'passed':
                        gsk_online_status = "P"
                        row.append(gsk_online_status)
                    elif record.gsk_online_attendance == 'absent':
                         gsk_online_status = "A"
                         row.append(gsk_online_status)
                    else:
                        gsk_online_status = "F"
                        row.append(gsk_online_status)
                    
                    allowed_values = {'AP', 'A'}
    
                    # Convert the record to a set to find unique values
                    unique_values = set(row)
                    # absent_status = False
                    # Check if the unique values are a subset of allowed values
                    if unique_values.issubset(allowed_values) and len(unique_values) <= len(allowed_values):
                        absent = absent + 1
                
                applied = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id)])
                # appeared = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',batch_id),('institute_id','=',institute_id),('absent_status','=','present')])
                appeared = applied - absent
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
    
    def open_attempt_wise_report(self):
        
        return {
            'name': 'Attempt Wise Report',
            'domain': [('examination_report_batch', '=', self.id)],
            'view_type': 'form',
            'res_model': 'attempt.wise.report',
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
    
    def open_summarised_gp_report(self):
        
        return {
        'name': 'Summarised GP Report',
        'domain': [('examination_report_batch', '=', self.id)],
        'view_type': 'form',
        'res_model': 'summarised.gp.report',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        'context': {}
        }    
        
    def open_summarised_gp_repeater_report(self):
        
        return {
        'name': 'Summarised GP Repeater Report',
        'domain': [('examination_report_batch', '=', self.id)],
        'view_type': 'form',
        'res_model': 'summarised.gp.repeater.report',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        'context': {}
        }      
        
    def open_summarised_ccmc_report(self):
        
        return {
        'name': 'Summarised CCMC Report',
        'domain': [('examination_report_batch', '=', self.id)],
        'view_type': 'form',
        'res_model': 'summarised.ccmc.report',
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
    
    def get_ordinal(self,n):
        n = int(n)
        if 10 <= n % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return f"{n}{suffix}"

    

    def print_summarised_gp_repeater_report(self):
        exam_sequence = self.get_ordinal(self.sequence_report) 
        datas = {
            'doc_ids': self.id,
            'course': 'GP',
            'batch_id': self.examination_batch,  # Assuming examination_batch is a recordset and you want its ID
            'exam_sequence': exam_sequence
        } 
        if self.exam_type == 'repeater':
            datas['report_type'] = 'Repeater'
            datas['exam_sequence'] = exam_sequence
        elif self.exam_type == 'fresh':
            datas['report_type'] = 'Fresh'
            datas['exam_sequence'] = exam_sequence
            
        return self.env.ref('bes.summarised_gp_repeater_report_action').report_action(self ,data=datas)
    
    def print_bar_graph_report(self):
        
        datas = {
            'doc_ids': self.id,
            'course': 'GP',
            'batch_id': self.examination_batch  # Assuming examination_batch is a recordset and you want its ID
        }
        
        if self.exam_type == 'repeater':
            datas['report_type'] = 'Repeater'
        elif self.exam_type == 'fresh':
            datas['report_type'] = 'Fresh'
            
        return self.env.ref('bes.bar_graph_report_action').report_action(self ,data=datas)  
   
    def print_summarised_ccmc_report(self):
        exam_sequence = self.get_ordinal(self.sequence_report) 
        datas = {
            'doc_ids': self.id,
            'course': 'CCMC',
            'batch_id': self.examination_batch,  # Assuming examination_batch is a recordset and you want its ID
            'exam_sequence': exam_sequence
        }
        
        if self.exam_type == 'repeater':
            datas['report_type'] = 'Repeater'
            datas['exam_sequence'] = exam_sequence
        elif self.exam_type == 'fresh':
            datas['report_type'] = 'Fresh'
            datas['exam_sequence'] = exam_sequence
            
        return self.env.ref('bes.summarised_ccmc_report_action').report_action(self ,data=datas) 
           
           
    # def print_ship_visit_report(self):
        
    #     datas = {
    #         'doc_ids': self.id,
    #         'course': 'CCMC',
    #         'batch_id': self.examination_batch  # Assuming examination_batch is a recordset and you want its ID
    #     }
        
    #     if self.exam_type == 'repeater':
    #         datas['report_type'] = 'Repeater'
    #     elif self.exam_type == 'fresh':
    #         datas['report_type'] = 'Fresh'
            
    #     return self.env.ref('bes.ship_visit_report_action').report_action(self ,data=datas) 

        
    
               
    def print_ship_visit_report(self):
        
        datas = {
            'doc_ids': self.id,
            'course': self.course,
            'batch_id': self.examination_batch  # Assuming examination_batch is a recordset and you want its ID
        }
        
        if self.exam_type == 'repeater':
            datas['report_type'] = 'Repeater'
        elif self.exam_type == 'fresh':
            datas['report_type'] = 'Fresh'
            
        return self.env.ref('bes.ship_visit_report_actions').report_action(self ,data=datas) 

        
    
    def print_gp_graph_report(self):
        
        datas = {
            'doc_ids': self.id,
            'doc_model': 'examination.report',
            'docs': self,

            'batch_id': self.examination_batch,  # Assuming examination_batch is a recordset and you want its ID
        }
        
        if self.exam_type == 'repeater':
            datas['report_type'] = 'Repeater'
        elif self.exam_type == 'fresh':
            datas['report_type'] = 'Fresh'
            
        return self.env.ref('bes.bar_graph_report').report_action(self ,data=datas) 
    


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
    institute_code = fields.Char("Institute Code",store=True,related="institute_id.code",tracking=True)    
    
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

class SummarisedGPRepeaterReport(models.AbstractModel):
    _name = "report.bes.summarised_gp_repeater_report"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "Summarised GP Repeater Report"
    
    
    def get_ordinal(self,n):
        n = int(n)
        if 10 <= n % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return f"{n}{suffix}"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docids = data['doc_ids']
        docs1 = self.env['examination.report'].sudo().browse(docids)
        print('sasad')
        # print(docids)
        exam_sequence = data['exam_sequence']
        # print(data['exam_sequence'])
        # print(data)
        data = self.env['summarised.gp.repeater.report'].sudo().search(
                    [('examination_report_batch', '=', docs1.id)]).sorted(key=lambda r: r.institute_code)
        exam_region = data.exam_region.ids


        data = self.env['summarised.gp.repeater.report'].sudo().search([('examination_report_batch','=',docs1.id)])

        # print(self.env.context)
        # exam_sequence = self.env.context.get("exam_sequence")       
        print('exam_sequence')

        # report_type = data['report_type']
        # course = data['course']

        # if report_type == 'Fresh' and course == 'GP':
        #     exams = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',docs1.id), ('attempt_number', '=', '1')])
        # elif report_type == 'Repeater' and course == 'GP':
        #     exams = self.env['gp.exam.schedule'].sudo().search([('dgs_batch', '=', docs1.id), ('attempt_number', '>', '1')])
        
        # institutes = self.env['bes.institute'].sudo().search([], order='code asc')
        # exam_centers = self.env['exam.center'].sudo().search([])

        return {
            'docids': docids,
            'doc_model': 'summarised.gp.repeater.report',
            'docs': data,
            'exam_regions': exam_region,
            'examination_report':docs1,
            'exam_sequence':exam_sequence
            # 'exams': exams,
            # 'institutes': institutes,
            # 'exam_centers': exam_centers,
            # 'report_type': report_type,
            # 'course': course
        }    

class SummarisedGPReport(models.AbstractModel):
    _name = "report.bes.summarised_gp_report"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "Summarised GP Report"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docids = data['doc_ids']
        docs1 = self.env['examination.report'].sudo().browse(docids)
        
        data = self.env['summarised.gp.report'].sudo().search(
                    [('examination_report_batch', '=', docs1.id)]).sorted(key=lambda r: r.institute_code)
        exam_region = data.exam_region.ids
        
        data = self.env['summarised.gp.report'].sudo().search([('examination_report_batch','=',docs1.id)])

        
        print(exam_region)
        # report_type = data['report_type']
        # course = data['course']

        # if report_type == 'Fresh' and course == 'GP':
        #     exams = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',docs1.id), ('attempt_number', '=', '1')])
        # elif report_type == 'Repeater' and course == 'GP':
        #     exams = self.env['gp.exam.schedule'].sudo().search([('dgs_batch', '=', docs1.id), ('attempt_number', '>', '1')])
        
        # institutes = self.env['bes.institute'].sudo().search([], order='code asc')
        # exam_centers = self.env['exam.center'].sudo().search([])

        return {
            'docids': docids,
            'doc_model': 'summarised.gp.report',
            'docs': data,
            'exam_regions': exam_region,
            'examination_report':docs1
            # 'exams': exams,
            # 'institutes': institutes,
            # 'exam_centers': exam_centers,
            # 'report_type': report_type,
            # 'course': course
        }

class SummarisedCCMCReport(models.AbstractModel):
    _name = "report.bes.summarised_ccmc_report"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "Summarised CCMC Report"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docids = data['doc_ids']
        exam_sequence = data['exam_sequence']
        print(data)
        docs1 = self.env['examination.report'].sudo().browse(docids)
        data = self.env['summarised.ccmc.report'].sudo().search([('examination_report_batch','=',docs1.id)]).sorted(key=lambda r: r.institute_code)
        print(docs1)
        print(data)
        exam_region = data.exam_region.ids
        print(exam_region)
        # report_type = data['report_type']
        # course = data['course']

        # if report_type == 'Fresh' and course == 'CCMC':
        #     exams = self.env['ccmc.exam.schedule'].sudo().search([('dgs_batch','=',docs1.id), ('attempt_number', '=', '1')])
        # elif report_type == 'Repeater' and course == 'CCMC':
        #     exams = self.env['ccmc.exam.schedule'].sudo().search([('dgs_batch', '=', docs1.id), ('attempt_number', '>', '1')])
        
        # institutes = self.env['bes.institute'].sudo().search([], order='code asc')
        # exam_centers = self.env['exam.center'].sudo().search([])

        return {
            'docids': docids,
            'doc_model': 'summarised.ccmc.report',
            'docs': docids,
            'exam_regions': exam_region,
            'examination_report':docs1,
            'exam_sequence':exam_sequence
            # 'exams': exams,
            # 'institutes': institutes,
            # 'exam_centers': exam_centers,
            # 'report_type': report_type,
            # 'course': course
        }



class GPSummarisedReport(models.Model):
    _name = "summarised.gp.report"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'Summarised GP Report'
    
    
    examination_report_batch = fields.Many2one("examination.report",string="Examination Report Batch")
    examination_batch = fields.Many2one("dgs.batches",related="examination_report_batch.examination_batch",string="Examination Batch",tracking=True)
    
    institute = fields.Many2one('bes.institute',"Name of Institute",tracking=True)
    institute_code = fields.Char("Institute Code",store=True,related="institute.code",tracking=True)    
    exam_region = fields.Many2one("exam.center", "Exam Region",store=True,related="institute.exam_center",tracking=True)
    applied = fields.Integer("Applied",tracking=True)
    candidate_appeared = fields.Integer("Candidate Appeared",tracking=True)
    
    gsk_prac_oral_pass = fields.Integer("GSK (P.O.J)  - Applied",tracking=True)
    gsk_prac_oral_pass_per = fields.Float("GSK (P.O.J) - % Passed",tracking=True)
    
    mek_prac_oral_pass = fields.Integer("MEK (P.O.J)  - Applied",tracking=True)
    mek_prac_oral_pass_per = fields.Float("MEK (P.O.J) - % Passed",tracking=True)
    
    gsk_online_pass = fields.Integer("GSK Online  - Applied",tracking=True)
    gsk_online_pass_per = fields.Float("GSK Online - % Passed",tracking=True)
    
    mek_online_pass = fields.Integer("MEK Online  - Applied",tracking=True)
    mek_online_pass_per = fields.Float("MEK Online - % Passed",tracking=True)
    
    overall_pass = fields.Integer("Overall Passed",tracking=True)
    overall_pass_per = fields.Float("Overall Passed %",compute="_compute_percentage",store=True,tracking=True)
    
    @api.depends('candidate_appeared', 'overall_pass')
    def _compute_percentage(self):
        for record in self:
            if record.candidate_appeared > 0:
                record.overall_pass_per = (record.overall_pass / record.candidate_appeared) * 100
            else:
                record.percentage = 0.0
    
class GPSummarisedRepeaterReport(models.Model):
    _name = "summarised.gp.repeater.report"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'Summarised GP Repeater Report'
    
    
    examination_report_batch = fields.Many2one("examination.report",string="Examination Report Batch")
    examination_batch = fields.Many2one("dgs.batches",related="examination_report_batch.examination_batch",string="Examination Batch",tracking=True)
    
    institute = fields.Many2one('bes.institute',"Name of Institute",tracking=True)
    institute_code = fields.Char("Institute Code",store=True,related="institute.code",tracking=True)    
    exam_region = fields.Many2one("exam.center", "Exam Region",store=True,related="institute.exam_center",tracking=True)
    applied = fields.Integer("Applied",tracking=True)
    candidate_appeared = fields.Integer("Candidate Appeared",tracking=True)
    
    gsk_prac_oral_appeared = fields.Integer("GSK (P.O.J)  - Appeared",tracking=True)
    gsk_prac_oral_pass = fields.Integer("GSK (P.O.J)  - Passed",tracking=True)
    gsk_prac_oral_pass_per = fields.Float("GSK (P.O.J) - % Passed",tracking=True)
    
    mek_prac_oral_appeared = fields.Integer("MEK (P.O.J)  - Appeared",tracking=True)
    mek_prac_oral_pass = fields.Integer("MEK (P.O.J)  - Passed",tracking=True)
    mek_prac_oral_pass_per = fields.Float("MEK (P.O.J) - % Passed",tracking=True)
    
    gsk_online_appeared = fields.Integer("GSK Online  - Appeared",tracking=True)
    gsk_online_pass = fields.Integer("GSK Online  - Passed",tracking=True)
    gsk_online_pass_per = fields.Float("GSK Online - % Passed",tracking=True)
    
    mek_online_appeared = fields.Integer("MEK Online  - Appeared",tracking=True)
    mek_online_pass = fields.Integer("MEK Online  - Passed",tracking=True)
    mek_online_pass_per = fields.Float("MEK Online - % Passed",tracking=True)
    
    overall_pass = fields.Integer("Overall Passed",tracking=True)
    overall_pass_per = fields.Float("Overall Passed %",compute="_compute_percentage",store=True,tracking=True)
    
    @api.depends('candidate_appeared', 'overall_pass')
    def _compute_percentage(self):
        for record in self:
            if record.candidate_appeared > 0:
                record.overall_pass_per = (record.overall_pass / record.candidate_appeared) * 100
            else:
                record.overall_pass_per = 0.0
    
    
    

class CCMCSummarisedReport(models.Model):
    _name = "summarised.ccmc.report"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'Summarised CCMC Report'
    
    
    examination_report_batch = fields.Many2one("examination.report",string="Examination Report Batch")
    examination_batch = fields.Many2one("dgs.batches",related="examination_report_batch.examination_batch",string="Examination Batch",tracking=True)
    institute_code = fields.Char("Institute Code",store=True,related="institute.code",tracking=True)    
    institute = fields.Many2one('bes.institute',"Name of Institute",tracking=True)
    exam_region = fields.Many2one("exam.center", "Exam Region",store=True,related="institute.exam_center",tracking=True)
    applied = fields.Integer("Applied",tracking=True)
    candidate_appeared = fields.Integer("Candidate Appeared",tracking=True)
    
    practical_pass_appeared = fields.Integer("Practical - Appeared",tracking=True)
    practical_pass = fields.Integer("Practical Passed",tracking=True)
    practical_pass_per = fields.Float("Practical Passed - % Passed",tracking=True)
    
    oral_pass_appeared = fields.Integer("Oral - Appeared",tracking=True)
    oral_pass = fields.Integer("Oral Passed",tracking=True)
    oral_pass_per = fields.Float("Oral - % Passed",tracking=True)
    
    online_pass_appeared = fields.Integer("Online - Appeared",tracking=True)
    online_pass = fields.Integer("Online Passed",tracking=True)
    online_pass_per = fields.Float("Online - % Pass",tracking=True)
    
    overall_pass = fields.Integer("Overall Passed",tracking=True)
    overall_pass_per = fields.Float("Overall Passed %",compute="_compute_percentage",tracking=True)
    
    @api.depends('candidate_appeared', 'overall_pass')
    def _compute_percentage(self):
        for record in self:
            if record.candidate_appeared > 0:
                record.overall_pass_per = (record.overall_pass / record.candidate_appeared) * 100
            else:
                record.overall_pass_per = 0.0



class AttemptWiseReport(models.Model):
    _name = "attempt.wise.report"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'Attempt Wise Report'
    examination_report_batch = fields.Many2one("examination.report",string="Examination Report Batch")
    examination_batch = fields.Many2one("dgs.batches",related="examination_report_batch.examination_batch",string="Examination Batch",tracking=True)
    attempt_number = fields.Char("Attempt Number")
    appeared = fields.Integer("Appeared")
    passed = fields.Integer("Passed")
    pass_percentage = fields.Float("Pass Percentage", compute='_compute_pass_percentage', store=True)

    
    
    @api.depends('appeared', 'passed')
    def _compute_pass_percentage(self):
        for record in self:
            if record.appeared > 0:
                record.pass_percentage = (record.passed / record.appeared) * 100
            else:
                record.pass_percentage = 0
    
    

    @api.depends('candidate_appeared', 'overall_pass')
    def _compute_percentage(self):
        for record in self:
            if record.candidate_appeared > 0:
                record.overall_pass_per = (record.overall_pass / record.candidate_appeared) * 100
            else:
                record.overall_pass_per = 0.0

class ShipVisitReport(models.Model):
    _name = "ship.visit.report"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'Ship Visit Report'
    
    examination_report_batch = fields.Many2one("examination.report",string="Examination Report Batch")
    examination_batch = fields.Many2one("dgs.batches",related="examination_report_batch.examination_batch",string="Examination Batch",tracking=True)
    
    institute = fields.Many2one('bes.institute',"Name of Institute",tracking=True)
    exam_region = fields.Many2one("exam.center", "Exam Region",store=True,related="institute.exam_center",tracking=True)
    code_no = fields.Char(related="institute.code", string="code_no")
    name_institute = fields.Char(related="institute.name", string="Name_of_the_institute")
    no_of_candidates = fields.Char(string="No_Of_Candidates")
    no_of_ship_visit = fields.Char(string="No_Of_Ship_visit")
    Name_of_ship_visit = fields.Char(string="Name_of_the_Ship_Visited_Ship_in_Campus")
    imo_no = fields.Char(string="IMO_No")
    name_of_the_port = fields.Char(string="Name_of_the_Port_Visited_Place_of_SIC")
    date_visit = fields.Char(string="Date_of_Visit")
    time_spend_on_ship = fields.Char(string="Time_Spend_on_Ship_Hrs")
    provided= fields.Char(string="Provided_Evidence")
    remark = fields.Char(string="Remark")
    center = fields.Char(string="Center")
                

class BarGraphReport(models.AbstractModel):
    _name = "report.bes.bar_graph_report"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "Bar Graph Report"
    
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docids = data['doc_ids']
        docs1 = self.env['examination.report'].sudo().browse(docids)
        batch_id = docs1.examination_batch.id
        institutes_data = []
        if docs1.course == 'gp':
            institutes = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',batch_id)]).sorted(key=lambda r: r.institute_code).institute_id
        elif docs1.course == 'ccmc':
            institutes = self.env['ccmc.exam.schedule'].sudo().search([('dgs_batch','=',batch_id)]).sorted(key=lambda r: r.institute_code).institute_id
    
        for institute in institutes:
            ins = {'code':institute.code , 'name':institute.name}
            institutes_data.append(ins)
        
        
        
        # exam_region = data.exam_region.ids
       

        return {
            # 'docids': docids,
            'doc_model': 'examination.report',
            # 'docs': docids,
            # 'exam_regions': exam_region,
            'docs':docs1,
            'institutes_data':institutes_data
            # 'exams': exams,
            # 'institutes': institutes,
            # 'exam_centers': exam_centers,
            # 'report_type': report_type,
            # 'course': course
        }
