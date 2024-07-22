from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import werkzeug
import secrets
import random
import string


class HrExpenseInherited(models.Model):
    _inherit = 'hr.expense.sheet'
    
    dgs_exam = fields.Boolean("Exam Exam")
    dgs_batch = fields.Many2one("dgs.batches",string="DGS Batch",required=False)
    institute_id = fields.Many2one("bes.institute",string="Institute")
    time_sheet = fields.Many2one("time.sheet.report",string="Time sheet")