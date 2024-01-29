from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
from datetime import datetime



class DGSBatch(models.Model):
    _name = "dgs.batches"
    
    _rec_name = "batch_name"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'Batches'
    
    batch_name = fields.Char("Batch Name",required=True)
    is_current_batch = fields.Boolean(string='Is Current Batch', default=False)
    
    
    def open_gp_exams(self):
        
        # import wdb;wdb.set_trace()
        exam_ids = self.env['gp.exam.schedule'].search([('dgs_batch','=',self.id)]).ids
        
        return {
        'name': 'GP Exams',
        'domain': [ ('id' , 'in' ,exam_ids) ],
        'view_type': 'form',
        'res_model': 'gp.exam.schedule',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window'
        }
        
    @api.onchange('is_current_batch')
    def on_change_current_batch(self):
        if self.is_current_batch:
            self.set_current_batch()

    @api.model
    def set_current_batch(self):
        other_batches = self.search([('is_current_batch', '=', True)])
        other_batches.write({'is_current_batch': False})
        

class DGSBatchReport(models.AbstractModel):
    _name = "report.bes.dgs_report"
    _description = "DGS Batch Report"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        
        
        
        docs1 = self.env['dgs.batches'].sudo().browse(docids)
        import wdb; wdb.set_trace(); 
        exams = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',docs1.id)])
        # report_action = self.env.ref('bes.dgs_report').with_context(landscape=True).report_action(self, data={})

        
        return {
            'docids': docids,
            'doc_model': 'gp.exam.schedule',
            'docs':docs1,
            'exams':exams
        }

    
