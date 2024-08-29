from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
import base64
from io import BytesIO
import xlsxwriter
from datetime import datetime
import xlrd

    


class IVBatches(models.Model):
    _name = "iv.batches"
    # _rec_name = "batch_name"
    # _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'IV Batches'
    
    
    # institute_id = fields.Many2one("bes.institute",string="Institute",required=True,tracking=True)
    
    
    
    name = fields.Char(string="IV Batches" ,store=True)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    issue_date = fields.Date(string="Issue Date")


    @api.constrains('issue_date')
    def _check_issue_date(self):
        for record in self:
            if not record.issue_date:
                raise ValidationError("The Issue Date must be filled.")

    @api.constrains('start_date')
    def _check_start_date(self):
        for record in self:
            if not record.start_date:
                raise ValidationError("The Start Date must be filled.")

    @api.constrains('end_date')
    def _check_end_date(self):
        for record in self:
            if not record.end_date:
                raise ValidationError("The End Date must be filled.")


   

    def show_iv_candidate_model(self):
        # This will open a tree view (list) of candidates related to this batch
        return {
            'type': 'ir.actions.act_window',
            'name': 'Batch Candidates',
            'res_model': 'iv.candidates',
            'view_mode': 'tree,form',
            'target': 'new',
            'domain': [('batch_id', '=', self.id)],  # Filter candidates by the current batch
            'context': {
                'default_batch_id': self.id,
            },
        }
    

   