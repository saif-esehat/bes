from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError



class ExpenseReport(models.Model):
    _name = 'examiner.expense.report'
    _rec_name = "examiner"

    batch = fields.Many2one('dgs.batches',string="Batch")
    examiner = fields.Many2one('bes.examiner',string="Examiner")
    institute_id = fields.Many2one("bes.institute",string="Institute")
    exam_type = fields.Many2many('expense.report.exam.type','expense_id',string="Exam Type")
    gp_candidate_count = fields.Integer("No of GP Candidates")
    ccmc_candidate_count = fields.Integer("No of CCMC Candidates")
    repeater_candidate_count = fields.Integer("No of Repeater Candidates")
    total_candidate_count = fields.Integer("No of Candidates")
    rate_per_unit = fields.Integer("Rate Per Unit")
    exam_fee = fields.Integer("Exam Fee")


class ExpenseReportExamType(models.Model):
    _name = 'expense.report.exam.type'
    _rec_name = "exam_type_name"


    expense_id = fields.Many2one('examiner.expense.report',string="Expense")
    exam_type_name = fields.Char('Exam Type')