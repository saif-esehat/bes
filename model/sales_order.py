from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError


from datetime import datetime


class SalesOrderInherited(models.Model):
    _inherit = 'sale.order'

    payment_slip = fields.Binary("Payment Slip")
    slip_file_name = fields.Char('filename')
    
