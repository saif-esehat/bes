from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError


from datetime import datetime


class EmployeeInherited(models.Model):
    _inherit = 'hr.employee'

    examiner = fields.Boolean("Examiner")