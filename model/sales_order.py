from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError


from datetime import datetime


class SalesOrderInherited(models.Model):
    _inherit = 'sale.order'

    payment_slip = fields.Binary("Payment Slip")
    slip_file_name = fields.Char('filename')

    tracking_id = fields.Char('Tracking Id')
    transaction_id = fields.Char("Transaction Id")
    sequence_id = fields.Char("Sequence")


    def _prepare_invoice(self):
        invoice_vals = super(SalesOrderInherited, self)._prepare_invoice()
        
        invoice_vals['transaction_id'] = self.transaction_id
        invoice_vals['transaction_slip'] = self.payment_slip
        invoice_vals['file_name'] = self.slip_file_name

        
        return invoice_vals
    
# class SalesOrderInherited(models.Model):
#     _inherit = 'sale.order.line'

#     tracking_id = fields.Char('Tracking Id')
#     transaction_id = fields.Char("Transaction Id")
#     sequence_id = fields.Char("Sequence")
