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
    attendance = fields.Boolean('Candidate Present',default=True)
    roll_no = fields.Char("Roll No")
    indos_no = fields.Char(string="Indos No")

    status = fields.Selection([
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('absent', 'Absent'),
        ], string='Status',default='failed',compute="_compute_status")
    
    mmb_status = fields.Selection([
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('absent', 'Absent'),
        ], string='MMB Status',default='failed',compute="_compute_mmb_status")
    
    @api.onchange('marks')
    def _change_marks(self):
        for record in self:
            record.mmb_marks = record.marks

    @api.depends('attendance','marks')
    def _compute_status(self):
        for record in self:
            if record.marks < 25:
                record.status = 'failed'
            if record.marks >= 25:
                record.status = 'passed'
            if record.attendance == False:
                record.status = 'absent'

    @api.depends('attendance','mmb_marks')
    def _compute_mmb_status(self):
        for record in self:
            if record.mmb_marks < 25:
                record.mmb_status = 'failed'
            if record.mmb_marks >= 25:
                record.mmb_status = 'passed'
            if record.attendance == False:
                record.mmb_status = 'absent'


    def create_oral_exam_records(self):
        # Filter candidates who passed the written exam
        passed_candidates = self.filtered(lambda rec: rec.status == 'passed')
        
        if passed_candidates:
            for rec in passed_candidates:
                self.env['iv.oral.exam'].create({
                    'candidate': rec.candidate.id,
                    'batch_id': rec.batch_id.id,
                    'grade': rec.grade,
                })
        else:
            raise UserError("No candidates have passed the written exam.")           
        

    def create_oral_attendance(self):
        for record in self:
            if record.status == 'passed':
                record.env['iv.oral.attendance.sheet'].sudo().create({
                    'candidate_name':record.candidate.id,
                    'roll_no':record.roll_no,
                    'grade_applied':record.grade,
                    'batch_id':record.batch_id.id,
                    'indos_no':record.indos_no
                })


    

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

    

class IVWrittenExamReportA(models.AbstractModel):
    _name = 'report.bes.reports_iv_written_exam_a_list'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['iv.written.exam'].sudo().browse(docids)

        grade_order = ['1CM', '2CM', 'SER', 'ME', '1ED', '2ED']
        
        # Sort the records based on the grade_applied field
        sorted_docs = docs.sorted(
            key=lambda r: grade_order.index(r.grade) if r.grade in grade_order else len(grade_order)
          )
        
        candidates = []
        for doc in sorted_docs:
            # Fetch candidate-related data
            candidate = doc.candidate
            if candidate:
                candidates.append({
                    'indos_no': candidate.indos_no,
                    'roll_no': candidate.roll_no,
                 
                })

        return {
            'docids': docids,
            'doc_model': 'iv.written.exam',
            'data': data,
            'docs': sorted_docs,
            'candidates': candidates
        }

     
     

class IVWrittenExamReportB(models.AbstractModel):
    _name = 'report.bes.reports_iv_written_exam_b_list'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['iv.written.exam'].sudo().browse(docids)

        grade_order = ['1CM', '2CM', 'SER', 'ME', '1ED', '2ED']
        
        # Sort the records based on the grade_applied field
        sorted_docs = docs.sorted(
            key=lambda r: grade_order.index(r.grade) if r.grade in grade_order else len(grade_order)
        )

        candidates = []
        for doc in sorted_docs:
            # Fetch candidate-related data
            candidate = doc.candidate
            if candidate:
                candidates.append({
                    'indos_no': candidate.indos_no,
                    'roll_no': candidate.roll_no,
                 
                })

        return {
            'docids': docids,
            'doc_model': 'iv.written.exam',
            'data': data,
            'docs': sorted_docs,
            'candidates': candidates
          
        }


class IVOralExamResultA(models.AbstractModel):
    _name = 'report.bes.reports_iv_oral_exam_a_list'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['iv.oral.exam'].sudo().browse(docids)

        grade_order = ['1CM', '2CM', 'SER', 'ME', '1ED', '2ED']
        
        # Sort the records based on the grade_applied field
        sorted_docs = docs.sorted(
            key=lambda r: grade_order.index(r.grade) if r.grade in grade_order else len(grade_order)
        )

        candidates = []
        for doc in sorted_docs:
            # Fetch candidate-related data
            candidate = doc.candidate
            if candidate:
                candidates.append({
                    'indos_no': candidate.indos_no,
                    'roll_no': candidate.roll_no,
                    'dob':candidate.dob,
                 
                })

        return {
            'docids': docids,
            'doc_model': 'iv.oral.exam',
            'data': data,
            'docs': sorted_docs,
            'candidates': candidates
          
        }


class IVOralExamResultB(models.AbstractModel):
    _name = 'report.bes.reports_iv_oral_exam_b_list'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['iv.oral.exam'].sudo().browse(docids)

        grade_order = ['1CM', '2CM', 'SER', 'ME', '1ED', '2ED']
        
        # Sort the records based on the grade_applied field
        sorted_docs = docs.sorted(
            key=lambda r: grade_order.index(r.grade) if r.grade in grade_order else len(grade_order)
        )

        candidates = []
        for doc in sorted_docs:
            # Fetch candidate-related data
            candidate = doc.candidate
            if candidate:
                candidates.append({
                    'indos_no': candidate.indos_no,
                    'roll_no': candidate.roll_no,
                    'dob':candidate.dob,
                 
                })

        return {
            'docids': docids,
            'doc_model': 'iv.oral.exam',
            'data': data,
            'docs': sorted_docs,
            'candidates': candidates
        }


class IVOralAssessmentSheet(models.AbstractModel):
    _name = 'report.bes.reports_iv_oral_assement_shhet_list'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['iv.oral.exam'].sudo().browse(docids)

        grade_order = ['1CM', '2CM', 'SER', 'ME', '1ED', '2ED']
        
        # Sort the records based on the grade_applied field
        sorted_docs = docs.sorted(
            key=lambda r: grade_order.index(r.grade) if r.grade in grade_order else len(grade_order)
        )

        candidates = []
        for doc in sorted_docs:
            # Fetch candidate-related data
            candidate = doc.candidate
            if candidate:
                candidates.append({
                    'indos_no': candidate.indos_no,
                    'roll_no': candidate.roll_no,
                    'dob':candidate.dob,
                 
                })

        return {
            'docids': docids,
            'doc_model': 'iv.oral.exam',
            'data': data,
            'docs': sorted_docs,
            'candidates': candidates       }
    

