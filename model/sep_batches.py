from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
import base64
from io import BytesIO
import xlsxwriter
from datetime import datetime
import xlrd

    


class SepBatches(models.Model):
    _name = "sep.batches"
    # _rec_name = "batch_name"
    # _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'Sep Batches'
    
    
    # institute_id = fields.Many2one("bes.institute",string="Institute",required=True,tracking=True)
    
    
    
    name = fields.Char(string="Sep Batches" ,store=True)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    issue_date = fields.Date(string="Issue Date")


   

    def show_sep_candidate_model(self):
        # This will open a tree view (list) of candidates related to this batch
        return {
            'type': 'ir.actions.act_window',
            'name': 'Batch Candidates',
            'res_model': 'sep.candidates',
            'view_mode': 'tree,form',
            'target': 'new',
            'domain': [('batch_id', '=', self.id)],  # Filter candidates by the current batch
            'context': {
                'default_batch_id': self.id,
            },
        }
    

   