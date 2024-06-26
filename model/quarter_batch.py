from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import io
import base64



class DGSBatch(models.Model):
    _name = "dgs.batches"
    
    _rec_name = "batch_name"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'Batches'
    
    batch_name = fields.Char("Batch Name",required=True,tracking=True)
    is_current_batch = fields.Boolean(string='Is Current Batch', default=False,tracking=True)
    to_date = fields.Date(string='To Date', 
                      widget="date", 
                      date_format="%b-%y",tracking=True)
    
    from_date = fields.Date(string='From Date', 
                      widget="date", 
                      date_format="%b-%y",tracking=True)
    
    exam_pass_date = fields.Date(string="Date of Examination Passed:",tracking=True)
    certificate_issue_date = fields.Date(string="Date of Issue of Certificate:",tracking=True)
    mumbai_region = fields.Many2one("bes.institute",string="Mumbai Institute",tracking=True,domain="[('exam_center.name', '=','MUMBAI')]")
    kolkatta_region = fields.Many2one("bes.institute",string="Kolkatta Institute",tracking=True,domain="[('exam_center.name', '=','KOLKATA')]")
    chennai_region = fields.Many2one("bes.institute",string="Chennai Institute",tracking=True,domain="[('exam_center.name', '=','CHENNAI')]")
    delhi_region = fields.Many2one("bes.institute",string="Delhi Institute",tracking=True,domain="[('exam_center.name', '=','DELHI')]")
    kochi_region = fields.Many2one("bes.institute",string="Kochi Institute",tracking=True,domain="[('exam_center.name', '=','KOCHI')]")
    goa_region = fields.Many2one("bes.institute",string="Goa Institute",tracking=True,domain="[('exam_center.name', '=','GOA')]")
    state = fields.Selection([
        ('1-on_going', 'On-Going'),
        ('2-confirmed', 'Confirmed'),
        ('3-dgs_approved', 'Approved')     
    ], string='State', default='1-on_going',tracking=True)

    repeater_batch = fields.Boolean("Is Repeater Batch",default=False,tracking=True)
    gp_url = fields.Char('URL for GP candidates',compute="_compute_url")
    ccmc_url = fields.Char('URL for ccmc candidates',compute="_compute_ccmc_url")
    form_deadline = fields.Date(string="Registration Form Dead Line",tracking=True)
    
    plot_image = fields.Binary(string='Pass Percentage Plot')

    
    
    
    def get_pass_percentage(self,exams=None):
        if exams == None:
            exams = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',self.id),('attempt_number','=','1')])
        total_counts = defaultdict(int)
        pass_counts = defaultdict(int)
        # exams = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',self.id),('attempt_number','=','1')])

        
        candidates = []
        
        for record in exams:
            candidates.append({'name': record.gp_candidate.name, 'institute': record.gp_candidate.institute_id.name ,'institute_code': record.gp_candidate.institute_id.code, 'status': record.certificate_criteria},)
        
        
        unique_institutes = {(item['institute'], item['institute_code']) for item in candidates}

        # Convert the set to a list of dictionaries for better readability
        unique_institutes_list = [{'institute': ins, 'institute_code': code} for ins, code in unique_institutes]

        labels = set((d['institute_code'], d['institute']) for d in candidates)

        
        for entry in candidates:
            institute = entry['institute_code']
            total_counts[institute] += 1
            if entry['status'] == 'passed':
                pass_counts[institute] += 1

        pass_percentages = {institute: (pass_counts[institute] / total) * 100 for institute, total in total_counts.items()}
        # import wdb; wdb.set_trace();
        # print(pass_percentages)
        
        institutes = list(pass_percentages.keys())
        percentages = list(pass_percentages.values())

        plt.figure(figsize=(10, 6))
        bars = plt.bar(institutes, percentages, color='skyblue',width=0.5)
        plt.xlabel('Institutes')
        plt.ylabel('Pass Percentage')
        plt.title('Pass Percentage of Students Institute-wise')
        plt.xticks(rotation=45,fontsize=7)
        plt.ylim(0, 110)
        
  

        
        
        plt.legend()
        
        # for ins in unique_institutes_list:
        #     institute = ins['institute']
        #     institute_code = ins['institute_code']
        #     plt.legend(loc='lower left', bbox_to_anchor=(0.5, -0.2), ncol=2,title=institute_code+" - "+institute)
        
        # for i, (ins_code, institute) in enumerate(labels):
        #     plt.text(i - 0.2, -0.6, f'{ins_code:10}         {institute}', fontsize=10, va='top')



        

        
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 1, f'{round(yval, 2)}%', 
                         ha='center', va='bottom', fontsize=6, rotation=70)
            plt.plot([bar.get_x() + bar.get_width()/2, bar.get_x() + bar.get_width()/2], 
                         [yval, yval + 1], color='black', linewidth=0.5)
        
        

        plt.tight_layout()
        # Save the plot to an in-memory buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png',bbox_inches='tight')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')

        # Store the image in the record
        self.write({'plot_image': image_base64}) 
        
        
        # return pass_percentages
    

    @api.depends('repeater_batch')
    def _compute_url(self):
        for record in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            new_url = base_url +"/gpcandidate/repeater/"+str(record.id)
            if record.repeater_batch:
                record.gp_url = new_url
            else:
                record.gp_url = "Default URL" 
    
    @api.depends('repeater_batch')
    def _compute_ccmc_url(self):
        for record in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            new_url = base_url +"/ccmccandidate/repeater/"+str(self.id)
            if record.repeater_batch:
                record.ccmc_url = new_url
            else:
                record.ccmc_url = "Default URL" 

    def move_confirm(self):
        exams = self.env['gp.exam.schedule'].search([('dgs_batch','=',self.id)])
        
        for exam in exams:
            exam.move_done()
            
        percentages = self.get_pass_percentage(exams)
        import wdb; wdb.set_trace();
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
    _inherit = ['mail.thread','mail.activity.mixin']
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
            self.get_pass_percentage(exams)
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

    
