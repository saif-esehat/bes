from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError


class BatchInvoice(models.Model):
    _inherit = "account.move"
    batch_ok = fields.Boolean("Batch Required")
    batch = fields.Many2one("institute.gp.batches","Batch")
