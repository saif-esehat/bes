from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError


class BatchInvoice(models.Model):
    _inherit = "account.move"
    gp_batch_ok = fields.Boolean("GP Batch Required")
    batch = fields.Many2one("institute.gp.batches","Batch")
    ccmc_batch = fields.Many2one("institute.ccmc.batches","CCMC Batch")
    ccmc_batch_ok = fields.Boolean("CCMC Batch Required")
    gp_candidates = fields.Many2many('gp.candidate', string='GP Candidate')
    ccmc_candidates = fields.Many2many('ccmc.candidate', string='CCMC Candidate')
    transaction_id = fields.Char("Transaction ID")
    bank_name = fields.Char("Bank Name & Address")
    total_amount =  fields.Float("Total Amount")
    transaction_slip =  fields.Binary("Transaction Slip")
    file_name = fields.Char("Transaction Slip Filename")
    transaction_date = fields.Date("Transaction Date")
    
    
    
    
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
        
    def open_ccmc_candidate(self):
        
        batch_id  = self.ccmc_batch.id
        return {
                    'name': 'CCMC Candidate',
                    'domain': [('institute_batch_id', '=',batch_id)],
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'ccmc.candidate',
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
        # import wdb;wdb.set_trace();
        account_move_id = self.env.context['active_id']
        invoice = self.env['account.move'].sudo().search([('id','=',account_move_id)])
        print("gopppppppppppppppppppppppppppppppppppppp")
        # import wdb; wdb.set_trace(); 
        if invoice.gp_batch_ok: #in GP Invoice
            print("gopppppppppppppppppppppppppppppppppppppp")
            gp_candidates = invoice.gp_candidates.ids
            batch = invoice.batch
            # self.env['batches.gp.register.exam.wizard'].sudo().register(batch.id)
            # batch.confirm_batch(gp_candidates)
            
            self.env['batches.gp.register.exam.wizard'].sudo().register(batch.id,gp_candidates)
            # batch.confirm_batch(gp_candidates)
            batch.write({'state':'4-invoiced'})
            batch.write({'state':'5-exam_scheduled'})
            
            # import wdb; wdb.set_trace(); 
        elif invoice.ccmc_batch_ok: #if CCMC Inovice
            ccmc_candidates = invoice.ccmc_candidates.ids
            print("cmmmmmmmmmmmmmmmmmmmmmmccccccccccccccccccccccccccc")
            batch = invoice.ccmc_batch
            # self.env['batches.ccmc.register.exam.wizard'].sudo().register(batch.id)
            # batch.confirm_batch_ccmc(ccmc_candidates) # Disable For some time
            
            self.env['batches.ccmc.register.exam.wizard'].sudo().register(batch.id,ccmc_candidates)
            # batch.confirm_batch_ccmc(ccmc_candidates) # Disable For some time
            batch.write({'ccmc_state':'4-invoiced'})
            batch.write({'ccmc_state':'5-exam_scheduled'})
        # Your custom code here after calling the super method
            # For CCMC
            return action
        # For Gp 
        return action
        

        # print("Data")
