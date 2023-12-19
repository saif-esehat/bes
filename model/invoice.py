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
        
        
        
        
        
        

        # print("Data")
