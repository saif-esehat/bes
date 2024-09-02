from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
import base64


class CandidatesGrade(models.Model):
    _name = "candidates.grade"

    _rec_name = "grade"

    grade  = fields.Char(string="Grade")