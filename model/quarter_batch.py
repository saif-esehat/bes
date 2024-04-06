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
    to_date = fields.Date(string='To Date', 
                      widget="date", 
                      date_format="%b-%y")
    
    from_date = fields.Date(string='From Date', 
                      widget="date", 
                      date_format="%b-%y")
    
    exam_pass_date = fields.Date(string="Date of Examination Passed:")
    certificate_issue_date = fields.Date(string="Date of Issue of Certificate:")
    
    state = fields.Selection([
        ('1-on_going', 'On-Going'),
        ('2-confirmed', 'Confirmed'),
        ('3-dgs_approved', 'Approved')     
    ], string='State', default='1-on_going')
    
    def move_confirm(self):
        exams = self.env['gp.exam.schedule'].search([('dgs_batch','=',self.id)])
        for exam in exams:
            exam.move_done()
        self.state = '2-confirmed'
        
    def move_dgs_approved(self):
        
        exams = self.env['gp.exam.schedule'].search([('dgs_batch','=',self.id)])
        ccmc_exams = self.env['ccmc.exam.schedule'].search([('dgs_batch','=',self.id)])
        ccmc_exams
        for exam in exams:
            exam.dgs_approval()
        for exam in ccmc_exams:
            exam.dgs_approval()
        
                    
        self.state = '3-dgs_approved'
    
    def print_gp_repeater(self):
        
        datas = {
        'doc_ids': self.id,
        'report_type': 'Repeater',
        'course': 'GP' 
         }
        
        return self.env.ref('bes.report_dgs_gp_fresh_action').report_action(self ,data=datas)
    
    def print_gp_fresh(self):
        
        datas = {
        'doc_ids': self.id,
        'report_type': 'Fresh',
        'course': 'GP' 
         }
        
        return self.env.ref('bes.report_dgs_gp_fresh_action').report_action(self ,data=datas)
    
    
    def open_gp_exams(self):
        
        exam_ids = self.env['gp.exam.schedule'].search([('dgs_batch','=',self.id)]).ids
        # import wdb;wdb.set_trace()

        return {
        'name': 'GP Exams',
        'domain': [ ('id' , 'in' , exam_ids) ],
        'view_type': 'form',
        'res_model': 'gp.exam.schedule',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window'
        }
        
        
    def open_ccmc_exams(self):
        
        # import wdb;wdb.set_trace()
        exam_ids = self.env['ccmc.exam.schedule'].search([('dgs_batch','=',self.id)]).ids
        
        return {
        'name': 'CCMC Exams',
        'domain': [ ('id' , 'in' ,exam_ids) ],
        'view_type': 'form',
        'res_model': 'ccmc.exam.schedule',
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
        
        
        docids = data['doc_ids']
        docs1 = self.env['dgs.batches'].sudo().browse(docids)
        # import wdb; wdb.set_trace(); 
        report_type = data['report_type']
        course = data['course']

        if report_type == 'Fresh' and course == 'GP':
            exams = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',docs1.id),('attempt_number','=','1')])
        elif report_type == 'Repeater' and course == 'GP':
            exams = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',docs1.id),('attempt_number','>','1')])

            # report_action = self.env.ref('bes.dgs_report').with_context(landscape=True).report_action(self, data={})

        
        return {
            'docids': docids,
            'doc_model': 'gp.exam.schedule',
            'docs':docs1,
            'exams':exams,
            'report_type':report_type,
            'course':course
        }

    
