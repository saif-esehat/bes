from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError


class BatchInvoice(models.Model):
    _inherit = "account.move"
    batch_ok = fields.Boolean("Batch Required")
    batch = fields.Many2one("institute.gp.batches","Batch")
    
    
    
    
    def open_gp_candidate(self):
        
        batch_id  = self.batch.id
        return {
                    'name': 'GP Candidate',
                    'domain': [('institute_batch_id', '=',batch_id)],
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'gp.candidate',
                    'type': 'ir.actions.act_window',
                    'view_id': False,
                    'context': {'search_default_fees_paid':1}
                    
                }
        
        
        
        
class CustomPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def action_create_payments(self):
        # import wdb;wdb.set_trace()

        # Your custom code here before or after calling the super method
        action = super(CustomPaymentRegister, self).action_create_payments()
        account_move_id = self.env.context['active_id']
        invoice = self.env['account.move'].sudo().search([('id','=',account_move_id)])
        if invoice.batch_ok:
            batch = invoice.batch
            batch.write({'state':'4-invoiced'})
        # Your custom code here after calling the super method
        return action
        

        # print("Data")
