from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError


from datetime import datetime


class EmployeeInherited(models.Model):
    _inherit = 'hr.employee'

    examiner = fields.Boolean("Examiner")
<<<<<<< HEAD
    institute_id = fields.Many2many("bes.institute",'institute_id',string="Institute")
    expense_sheet = fields.Many2one('hr.expense.sheet','Expense')
    time_sheet = fields.Many2one('time.sheet.report','Time Sheet')
=======
    # institute_id = fields.Many2many("bes.institute",'institute_id',string="Institute")
    # expense_sheet = fields.Many2one('hr.expense.sheet','Expense')
    # time_sheet = fields.Many2one('time.sheet.report','Time Sheet')
>>>>>>> d739911 (datA)
