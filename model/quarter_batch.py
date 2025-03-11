from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import io
import base64
from io import BytesIO
# from PyPDF2 import PdfMerger

class ReleaseAdmitCard(models.TransientModel):
    _name = 'release.admit.card'
    _description = 'Release Admit Card'

    admit_card_type = fields.Selection([
        ('gp', 'GP'),
        ('ccmc', 'CCMC')
    ], string='Admit Card Type',default='gp')
    exam_region = fields.Many2one("exam.center",string="Region")
    
    
    
    def release_admit_card(self):
        self.ensure_one()  # Ensure the wizard is accessed by a single record

        exam_batch_id = self.env.context.get('active_id')
        
        exam_batch = self.env['dgs.batches'].sudo().search([('id','=',exam_batch_id)])
        mumbai_region = exam_batch.mumbai_region
        kolkata_region = exam_batch.kolkatta_region
        chennai_region = exam_batch.chennai_region
        delhi_region = exam_batch.delhi_region
        kochi_region = exam_batch.kochi_region
        goa_region = exam_batch.goa_region
        is_march_september = exam_batch.is_march_september
        # self.admit_card_type
                    
        if not self.exam_region:
            raise ValidationError("Please select an exam region.")
        
        if self.admit_card_type == 'gp':
            candidates_count = self.env['gp.exam.schedule'].sudo().search_count([
                ('hold_admit_card','=',False),
                ('dgs_batch','=',exam_batch_id),
                ('exam_region','=',self.exam_region.id)
                ]) 
            candidates = self.env['gp.exam.schedule'].sudo().search([
                ('hold_admit_card','=',False),
                ('dgs_batch','=',exam_batch_id),
                ('exam_region','=',self.exam_region.id)
                ]) 
            
            if self.exam_region.name == 'MUMBAI' and mumbai_region:
                candidates.write({'hold_admit_card':False, 'registered_institute':mumbai_region.id})
                message = "GP Admit Card Released for the "+str(candidates_count)+" Candidate for Exam Region "+self.exam_region.name+". The exam center set is "+mumbai_region.name
            elif self.exam_region.name == 'KOLKATA' and kolkata_region:
                candidates.write({'hold_admit_card':False,  'registered_institute':kolkata_region.id})
                message = "GP Admit Card Released for the "+str(candidates_count)+" Candidate for Exam Region "+self.exam_region.name+". The exam center set is "+kolkata_region.name
            elif self.exam_region.name == 'CHENNAI' and chennai_region:
                candidates.write({'hold_admit_card':False,   'registered_institute':chennai_region.id})
                message = "GP Admit Card Released for the "+str(candidates_count)+" Candidate for Exam Region "+self.exam_region.name+". The exam center set is "+chennai_region.name
            elif self.exam_region.name == 'DELHI' and delhi_region:
                candidates.write({'hold_admit_card':False,'registered_institute':delhi_region.id})
                message = "GP Admit Card Released for the "+str(candidates_count)+" Candidate for Exam Region "+self.exam_region.name+". The exam center set is "+delhi_region.name
            elif self.exam_region.name == 'KOCHI' and kochi_region:
                candidates.write({'hold_admit_card':False,'registered_institute':kochi_region.id})
                message = "GP Admit Card Released for the "+str(candidates_count)+" Candidate for Exam Region "+self.exam_region.name+". The exam center set is "+kochi_region.name
            elif self.exam_region.name == 'GOA' and goa_region:
                candidates.write({'hold_admit_card':False,'registered_institute':goa_region.id})
                message = "GP Admit Card Released for the "+str(candidates_count)+" Candidate for Exam Region "+self.exam_region.name+". The exam center set is "+goa_region.name            
            else:
                candidates.write({'hold_admit_card':False})
                message = "GP Admit Card Released for the "+str(candidates_count)+" Candidate for Exam Region "+self.exam_region.name+" but the exam center is not set"    
            
            return {
                'name': 'Admit Card Released',
                'type': 'ir.actions.act_window',
                'res_model': 'batch.pop.up.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'context': {'default_message': message},
            }
            
        elif self.admit_card_type == 'ccmc':
            candidate_count = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',exam_batch_id),('exam_region','=',self.exam_region.id)]) 
            candidates = self.env['ccmc.exam.schedule'].sudo().search([('dgs_batch','=',exam_batch_id),('exam_region','=',self.exam_region.id)]) 
           
            
            
            if self.exam_region.name == 'MUMBAI' and mumbai_region:
                candidates.write({'hold_admit_card':False,'registered_institute':mumbai_region.id})
                message = "CCMC Admit Card Released for the "+str(candidate_count)+" Candidate for Exam Region "+self.exam_region.name+". The exam center set is "+mumbai_region.name
            elif self.exam_region.name == 'KOLKATA' and kolkata_region:
                candidates.write({'hold_admit_card':False,'registered_institute':kolkata_region.id})
                message = "CCMC Admit Card Released for the "+str(candidate_count)+" Candidate for Exam Region "+self.exam_region.name+". The exam center set is "+kolkata_region.name
            elif self.exam_region.name == 'CHENNAI' and chennai_region:
                candidates.write({'hold_admit_card':False,'registered_institute':chennai_region.id})
                message = "CCMC Admit Card Released for the "+str(candidate_count)+" Candidate for Exam Region "+self.exam_region.name+". The exam center set is "+chennai_region.name
            elif self.exam_region.name == 'DELHI' and delhi_region:
                candidates.write({'hold_admit_card':False,'registered_institute':delhi_region.id})
                message = "CCMC Admit Card Released for the "+str(candidate_count)+" Candidate for Exam Region "+self.exam_region.name+". The exam center set is "+delhi_region.name
            elif self.exam_region.name == 'KOCHI' and kochi_region:
                candidates.write({'hold_admit_card':False,'registered_institute':kochi_region.id})
                message = "CCMC Admit Card Released for the "+str(candidate_count)+" Candidate for Exam Region "+self.exam_region.name+". The exam center set is "+kochi_region.name
            elif self.exam_region.name == 'GOA' and goa_region:
                candidates.write({'hold_admit_card':False,'registered_institute':goa_region.id})
                message = "CCMC Admit Card Released for the "+str(candidate_count)+" Candidate for Exam Region "+self.exam_region.name+". The exam center set is "+goa_region.name
            else:
                candidates.write({'hold_admit_card':False})
                message = "CCMC Admit Card Released for the "+str(candidate_count)+" Candidate for Exam Region "+self.exam_region.name+" but the exam center is not set"

            
            
            
            return {
                'name': 'Admit Card Released',
                'type': 'ir.actions.act_window',
                'res_model': 'batch.pop.up.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'context': {'default_message': message},
            }
            
        
        
    




class DGSBatch(models.Model):
    _name = "dgs.batches"
    
    _rec_name = "batch_name"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'Batches'
    
    batch_name = fields.Char("Batch Name",required=True,tracking=True)
    ccmc_batches = fields.Many2one('institute.ccmc.batches', string="Batch")
    is_current_batch = fields.Boolean(string='Current Fresher Batch', default=False,tracking=True)
    to_date = fields.Date(string='To Date', 
                      widget="date", 
                      date_format="%b-%y",tracking=True)
    
    from_date = fields.Date(string='From Date', 
                      widget="date", 
                      date_format="%b-%y",tracking=True)
    

    
    exam_pass_date = fields.Date(string="Date of Examination Passed:",tracking=True)
    certificate_issue_date = fields.Date(string="Date of Issue of Certificate:",tracking=True)
    mumbai_region = fields.Many2one("bes.institute",string="Mumbai Region",tracking=True,domain="[('exam_center.name', '=','MUMBAI')]")
    kolkatta_region = fields.Many2one("bes.institute",string="Kolkatta Region",tracking=True,domain="[('exam_center.name', '=','KOLKATA')]")
    chennai_region = fields.Many2one("bes.institute",string="Chennai Region",tracking=True,domain="[('exam_center.name', '=','CHENNAI')]")
    delhi_region = fields.Many2one("bes.institute",string="Delhi Region",tracking=True,domain="[('exam_center.name', '=','DELHI')]")
    kochi_region = fields.Many2one("bes.institute",string="Kochi Region",tracking=True,domain="[('exam_center.name', '=','KOCHI')]")
    goa_region = fields.Many2one("bes.institute",string="Goa Region",tracking=True,domain="[('exam_center.name', '=','GOA')]")
    
    mumbai_prac_oral_date = fields.Date(string="Mumbai Practical/Oral From Date")
    mumbai_prac_oral_to_date = fields.Date(string="Mumbai Practical/Oral To Date")
    
    mumbai_online_date = fields.Date(sting="Mumbai Online From Date")
    mumbai_online_to_date = fields.Date(sting="Mumbai Online To Date")

    kolkatta_prac_oral_date = fields.Date(string="Kolkatta Practical/Oral From Date")
    kolkatta_prac_oral_to_date = fields.Date(string="Kolkatta Practical/Oral To Date")
    
    kolkatta_online_date = fields.Date(string="Kolkatta Online From Date")
    kolkatta_online_to_date = fields.Date(string="Kolkatta Online To Date")
    
    chennai_prac_oral_date = fields.Date(string="Chennai Practical/Oral From Date")
    chennai_prac_oral_to_date = fields.Date(string="Chennai Practical/Oral To Date")
    
    chennai_online_date  = fields.Date(string="Chennai Online From Date")
    chennai_online_to_date = fields.Date(string="Chennai Online To Date")
    
    delhi_prac_oral_date = fields.Date(string="Delhi Practical/Oral From Date")
    delhi_prac_oral_to_date = fields.Date(string="Delhi Practical/Oral To Date")
    
    delhi_online_date  = fields.Date(string="Delhi Online From Date")
    delhi_online_to_date = fields.Date(string="Delhi Online To Date")
    
    kochi_prac_oral_date = fields.Date(string="Kochi Practical/Oral From Date")
    kochi_prac_oral_to_date = fields.Date(string="Kochi Practical/Oral To Date")
    
    kochi_online_date  =  fields.Date(string="Kochi Online From Date")
    kochi_online_to_date = fields.Date(string="Kochi Online To Date")
    
    goa_prac_oral_date = fields.Date(string="Goa Practical/Oral From Date")
    goa_prac_oral_to_date = fields.Date(string="Goa Practical/Oral To Date")
    
    goa_online_date  =  fields.Date(string="Goa Online From Date")
    goa_online_to_date = fields.Date(string="Goa Online To Date")
    
    

    
    state = fields.Selection([
        ('1-on_going', 'On-Going'),
        ('2-confirmed', 'Confirmed'),
        ('3-dgs_approved', 'Approved')     
    ], string='State', default='1-on_going',tracking=True)
    
    is_march_september = fields.Boolean(string="March/September Examination")
    

    
    def _compute_march_september(self):
        for record in self:
            # if record.to_date.strftime('%B') in ['March','September']:
            #     record.is_march_september = True
            # else:
            record.is_march_september = False

    repeater_batch = fields.Boolean("Repeater Batch",default=False,tracking=True)
    gp_url = fields.Char('URL for GP candidates',compute="_compute_url")
    ccmc_url = fields.Char('URL for CCMC candidates',compute="_compute_ccmc_url")
    
    form_deadline_start = fields.Date(string="Start Date of Registration for Examination",tracking=True)
    form_deadline = fields.Date(string="Last Date of Registration for Examination",tracking=True)
    
    gp_plot_image = fields.Binary(string='Pass Percentage Graph')
    ccmc_plot_image = fields.Binary(string='Pass Percentage Graph')
    
    active = fields.Boolean(string="Active",default=True)
    
    report_status = fields.Selection([
        ('pending', 'Pending'),
        ('generated', 'Generated'),
    
    ], string='Exam Result Report Status', default='pending',tracking=True)
    
    
    visible_generate_report = fields.Boolean(string='Visible Generate Button',compute="show_generate_report_button",tracking=True)

    instruction_document = fields.Binary(string="Instruction Document")
    instruction_document_name = fields.Char(string="Document Name")  # Name of the file

    dgs_approval_state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    ], string='DGS Approval', default='pending',tracking=True)
    
    dgs_approval_button_visible = fields.Boolean("DGS Approval Button Visible",compute="compute_dgs_approval_button_visible")
    
    @api.depends('state','dgs_approval_state')
    def compute_dgs_approval_button_visible(self):
        for record in self:
            if record.state == '2-confirmed' and record.dgs_approval_state == 'pending':
                record.dgs_approval_button_visible = True
            else:
                record.dgs_approval_button_visible = False
             

    def dgs_approved(self):
        self.dgs_approval_state = 'approved'
    
    def open_release_admit_card_wizard(self):
        view_id = self.env.ref('bes.view_release_admit_card_form').id
        
        return {
            'name': 'Release Admit Card',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'release.admit.card',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {}
        }
    
    
    @api.depends('state','report_status')    
    def show_generate_report_button(self):
        for record in self:
            if record.state == '2-confirmed' and record.report_status == 'pending':
                record.visible_generate_report = True
            else:
                record.visible_generate_report = False
                

    def open_reports(self):
        
        return {
        'name': 'Reports',
        'domain': [('examination_batch', '=', self.id)],
        'view_type': 'form',
        'res_model': 'examination.report',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        'context': {}
        }

    def open_expense_sheet(self):
        
        return {
        'name': 'Expense Reports',
        'domain': [('batch', '=', self.id)],
        'view_type': 'form',
        'res_model': 'examiner.expense.report',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        'context': {}
        }        
    
    def generate_report(self):
        self.get_pass_percentage()
        self.ccmc_get_pass_percentage()
        if not self.repeater_batch:
            gp = self.env['examination.report'].sudo().create({'examination_batch':self.id,'course':'gp','exam_type':'fresh'})
            gp.generate_report()
            ccmc = self.env['examination.report'].sudo().create({'examination_batch':self.id,'course':'ccmc','exam_type':'fresh'})
            ccmc.generate_report()
            
            self.report_status = 'generated'
        else:
            gp = self.env['examination.report'].sudo().create({'examination_batch':self.id,'course':'gp','exam_type':'repeater'})
            gp.generate_report()
            ccmc = self.env['examination.report'].sudo().create({'examination_batch':self.id,'course':'ccmc','exam_type':'repeater'})
            ccmc.generate_report()
            self.report_status = 'generated'
    
    
    def get_pass_percentage(self,exams=None):
        if self.repeater_batch:
            # if exams == None:
            exams = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',self.id)]).sorted(key=lambda r: r.institute_code)
        else:
            # if exams == None:
            exams = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',self.id)]).sorted(key=lambda r: r.institute_code)
            
        print(exams)
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
        plt.title('GP Rating Pass Percentage of Students Institute-wise')
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
        self.write({'gp_plot_image': image_base64}) 
        
        
        # return pass_percentages
        

    def ccmc_get_pass_percentage(self,exams=None):
        if self.repeater_batch:
            # if exams == None:
            exams = self.env['ccmc.exam.schedule'].sudo().search([('dgs_batch','=',self.id)]).sorted(key=lambda r: r.institute_code)
        else:
            # if exams == None:
            exams = self.env['ccmc.exam.schedule'].sudo().search([('dgs_batch','=',self.id)]).sorted(key=lambda r: r.institute_code)
        total_counts = defaultdict(int)
        pass_counts = defaultdict(int)
        # exams = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',self.id),('attempt_number','=','1')])

        
        candidates = []
        
        for record in exams:
            candidates.append({'name': record.ccmc_candidate.name, 'institute': record.ccmc_candidate.institute_id.name ,'institute_code': record.ccmc_candidate.institute_id.code, 'status': record.certificate_criteria},)
        
        
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
        plt.title('CCMC Rating Pass Percentage of Students Institute-wise')
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
        self.write({'ccmc_plot_image': image_base64}) 
        
        
        # return pass_percentages


        
    @api.depends('repeater_batch')
    def _compute_url(self):
        for record in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            new_url = "/gpcandidate/repeater/"+str(record.id)
            if record.repeater_batch:
                record.gp_url = new_url
            else:
                record.gp_url = "Default URL" 
    
    @api.depends('repeater_batch')
    def _compute_ccmc_url(self):
        for record in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            new_url = "/ccmccandidate/repeater/"+str(record.id)
            if record.repeater_batch:
                record.ccmc_url = new_url
            else:
                record.ccmc_url = "Default URL" 

    def move_confirm(self):
        exams = self.env['gp.exam.schedule'].search([('dgs_batch','=',self.id)])
        ccmc_exams = self.env['ccmc.exam.schedule'].search([('dgs_batch','=',self.id)])
        
        for exam in exams:
            exam.move_done()
        for exam in ccmc_exams:
            exam.move_done()
            
        # percentages = self.get_pass_percentage(exams)
        # import wdb; wdb.set_trace();
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
    
    # def print_gp_repeater(self):
        
    #     datas = {
    #     'doc_ids': self.id,
    #     'report_type': 'Repeater',
    #     'course': 'GP' 
    #      }
        
    #     return self.env.ref('bes.report_dgs_gp_fresh_action').report_action(self ,data=datas)
    
    def print_gp_fresh(self):
        
        if self.repeater_batch:
            datas = {
            'doc_ids': self.id,
            'report_type': 'Repeater',
            'course': 'GP' 
            }
        
        else:
            datas = {
            'doc_ids': self.id,
            'report_type': 'Fresh',
            'course': 'GP' 
            }
        
        return self.env.ref('bes.report_dgs_gp_fresh_action').report_action(self ,data=datas)
    
    def print_ccmc_fresh(self):
        
        if self.repeater_batch:
            datas = {
            'doc_ids': self.id,
            'report_type': 'Repeater',
            'course': 'CCMC' 
            }
        else:     
            datas = {
            'doc_ids': self.id,
            'report_type': 'Fresh',
            'course': 'CCMC' 
            }
        
        return self.env.ref('bes.report_dgs_ccmc_fresh_action').report_action(self ,data=datas)

    def print_ccmc_batch_report(self):
        datas = {
            'doc_ids': self.id,
        }

        return self.env.ref('bes.action_report_ccmc_batch_ship_visit').report_action(self, data=datas)

    def print_gp_batch_report(self):
        datas = {
            'doc_ids': self.id,
        }

        return self.env.ref('bes.action_report_gp_batch_ship_visit').report_action(self, data=datas)




    

    
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
        

    # def print_ship_visit_report(self):
        
    #     datas = {
    #         'doc_ids': self.id  # Assuming examination_batch is a recordset and you want its ID
    #     }
        
            
        # return self.env.ref('bes.ship_visit_report_actions').report_action(self ,data=datas) 
    #     return self.env.ref('bes.ship_visit_report_action').report_action(self ,data=datas) 

    # def print_summarised_gp_report(self):
    #     doc_id = self.env['examination.report'].sudo().search([('examination_batch','=',self.id),('course','=','gp')], limit=1)

    #     datas = {
    #         'doc_ids': doc_id.id,
    #         'course': 'GP',
    #         'batch_id': self.id  # Assuming examination_batch is a recordset and you want its ID
    #     }
        
    #     if self.repeater_batch:
    #         datas['report_type'] = 'Repeater'
    #     else:
    #         datas['report_type'] = 'Fresh'
            
    #     return self.env.ref('bes.summarised_gp_report_action').report_action(self ,data=datas)
    
    # def print_summarised_ccmc_report(self):
    #     doc_id = self.env['examination.report'].sudo().search([('examination_batch','=',self.id),('course','=','ccmc')], limit=1)
    #     exam_sequence = 12
    #     datas = {
    #         'doc_ids': doc_id.id,
    #         'course': 'CCMC',
    #         'batch_id': self.id,  # Assuming examination_batch is a recordset and you want its ID
    #         'exam_sequence': exam_sequence
    #     }
        
    #     if self.repeater_batch:
    #         datas['report_type'] = 'Repeater'
    #         datas['exam_sequence'] = exam_sequence
    #     else:
    #         datas['report_type'] = 'Fresh'
    #         datas['exam_sequence'] = exam_sequence
            
    #     return self.env.ref('bes.summarised_ccmc_report_action').report_action(self ,data=datas) 


        

class DGSBatchReport(models.AbstractModel):
    _name = "report.bes.dgs_report"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "DGS Batch GP Report"
    
    
    

    
    
    @api.model
    def _get_report_values(self, docids, data=None):
        
        
        docids = data['doc_ids']
        # docids = docids

        docs1 = self.env['dgs.batches'].sudo().browse(docids)
        report_type = data['report_type']
        course = data['course']

        if report_type == 'Fresh' and course == 'GP':
            exams = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',docs1.id),('attempt_number','=','1')]).sorted(key=lambda r: r.institute_code)
            # self.get_pass_percentage(exams)
        elif report_type == 'Repeater' and course == 'GP':
            exams = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',docs1.id),('attempt_number','>','1')]).sorted(key=lambda r: r.institute_code)
            print(exams)
            # report_action = self.env.ref('bes.dgs_report').with_context(landscape=True).report_action(self, data={})
        institute = self.env['bes.institute'].sudo().search([])
        # import wdb; wdb.set_trace(); 
        
        return {
            'docids': docids,
            'doc_model': 'gp.exam.schedule',
            'docs':docs1,
            'exams':exams,
            'institutes':institute,
            'report_type':report_type,
            'course':course
        }
    

class CCMCDGSBatchReport(models.AbstractModel):
    _name = "report.bes.ccmc_dgs_report"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "DGS Batch CCMC Report"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        
        
        docids = data['doc_ids']
        docs1 = self.env['dgs.batches'].sudo().browse(docids)
        report_type = data['report_type']
        course = data['course']

        if report_type == 'Fresh' and course == 'CCMC':
            exams = self.env['ccmc.exam.schedule'].sudo().search([('dgs_batch','=',docs1.id),('attempt_number','=','1')]).sorted(key=lambda r: r.institute_code)
        elif report_type == 'Repeater' and course == 'CCMC':
            exams = self.env['ccmc.exam.schedule'].sudo().search([('dgs_batch','=',docs1.id),('attempt_number','>','1')]).sorted(key=lambda r: r.institute_code)
            # report_action = self.env.ref('bes.dgs_report').with_context(landscape=True).report_action(self, data={})
        institute = self.env['bes.institute'].sudo().search([])
        # import wdb; wdb.set_trace(); 

        
        return {
            'docids': docids,
            'doc_model': 'ccmc.exam.schedule',
            'docs':docs1,
            'exams':exams,
            'institutes':institute,
            'report_type':report_type,
            'course':course,
            'name':'Report'
        }
    
class ShipVisitReport(models.Model):
    _name = "ship.visit.report"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'Ship Visit Report'
    
    examination_report_batch = fields.Many2one("examination.report",string="Examination Report Batch")
    examination_batch = fields.Many2one("dgs.batches",related="examination_report_batch.examination_batch",string="Examination Batch",tracking=True)
    
    institute = fields.Many2one('bes.institute',"Name of Institute",tracking=True)
    exam_region = fields.Many2one("exam.center", "Exam Region",store=True,related="institute.exam_center",tracking=True)
    code_no = fields.Char(related="institute.code", string="code_no")
    name_institute = fields.Char(related="institute.name", string="Name_of_the_institute")
    no_of_candidates = fields.Char(string="No_Of_Candidates")
    no_of_ship_visit = fields.Char(string="No_Of_Ship_visit")
    Name_of_ship_visit = fields.Char(string="Name_of_the_Ship_Visited_Ship_in_Campus")
    imo_no = fields.Char(string="IMO_No")
    name_of_the_port = fields.Char(string="Name_of_the_Port_Visited_Place_of_SIC")
    date_visit = fields.Char(string="Date_of_Visit")
    time_spend_on_ship = fields.Char(string="Time_Spend_on_Ship_Hrs")
    provided= fields.Char(string="Provided_Evidence")
    remark = fields.Char(string="Remark")
    center = fields.Char(string="Center")

    
    @api.depends('candidate_appeared', 'overall_pass')
    def _compute_percentage(self):
        for record in self:
            if record.candidate_appeared > 0:
                record.overall_pass_per = (record.overall_pass / record.candidate_appeared) * 100
            else:
                record.overall_pass_per = 0.0


class ShipVisitReportModel(models.AbstractModel):
    _name = "report.bes.candidate_ship_visit_reports"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "Ship Visit Reports"
    
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docids = data['doc_ids']
        
        docs1 = self.env['dgs.batches'].sudo().browse(docids)        
        gp_ship_visits = self.env['gp.candidate.ship.visits'].sudo().search([('dgs_batch','=',docs1.id)])
        print('gp_ship_visits.institute.id')
        institutes_data = gp_ship_visits.sorted(key=lambda r: r.institute_code).institute.ids
        print(institutes_data)
        
        
        
        # batch_id = docs1.id
        # institutes_data = []
        # # if docs1.course == 'gp':
        # gp_institutes = self.env['gp.candidate'].sudo().search([('dgs_batch','=',batch_id)]).sorted(key=lambda r: r.institute_id.code).institute_id
        # # elif docs1.course == 'ccmc':
        # ccmc_institutes = self.env['ccmc.candidate'].sudo().search([('dgs_batch','=',batch_id)]).sorted(key=lambda r: r.institute_id.code).institute_id
    
        # for institute in gp_institutes:
        #     ins = {'code':institute.code , 'name':institute.name}
        #     institutes_data.append(ins)
        
        
        
        # exam_region = data.exam_region.ids
       

        return {
            # 'docids': docids,
            'doc_model': 'dgs.batches',
            'docs':docs1,
            # 'institutes_data':institutes_data
            # 'exams': exams,
            # 'institutes': institutes,
            # 'exam_centers': exam_centers,
            # 'report_type': report_type,
            # 'course': course
        }

class CCMCBatchShipVisitReport(models.AbstractModel):
    _name = "report.bes.ccmc_batch_ship_visit_report"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "DGS Batch CCMC Report"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docids = data['doc_ids']
        docs1 = self.env['dgs.batches'].sudo().browse(docids)
        

        # Fetch exams without filtering by report_type and course
        exams = self.env['institute.ccmc.batches'].sudo().search([('dgs_batch', '=', docs1.id)]).sorted(key=lambda r: r.code)
        institute_ids = exams.mapped('institute_id.id')

        ship_visits = self.env['ccmc.batches.ship.visit'].sudo().search([('dgs_batch', '=', docs1.id), ('institute_id', 'in', institute_ids)])

      

        print("Ship Visits Found: ", ship_visits)

        exams_with_ship_visits = exams.filtered(lambda exam: ship_visits.filtered(lambda visit: visit.institute_id == exam.institute_id))


        institute = self.env['bes.institute'].sudo().search([])


        

        # Return the values for the report
        return {
            'docids': docids,
            'doc_model': 'institute.ccmc.batches',
            'docs': docs1,
            'exams': exams_with_ship_visits,
            'institutes': institute,
            'ship_visits': ship_visits, 
            'name': 'Report'
        }


class GPBatchShipVisitReport(models.AbstractModel):
    _name = "report.bes.gp_batch_ship_visit_report"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "DGS Batch Gp Report"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docids = data['doc_ids']
        docs1 = self.env['dgs.batches'].sudo().browse(docids)
        

        # Fetch exams without filtering by report_type and course
        exams = self.env['institute.gp.batches'].sudo().search([('dgs_batch', '=', docs1.id)]).sorted(key=lambda r: r.code)
        institute_ids = exams.mapped('institute_id.id')

        ship_visits = self.env['gp.batches.ship.visit'].sudo().search([('dgs_batch', '=', docs1.id), ('institute_id', 'in', institute_ids)])

      

        print("Ship Visits Found: ", ship_visits)
        # import wdb; wdb.set_trace();

        exams_with_ship_visits = exams.filtered(lambda exam: ship_visits.filtered(lambda visit: visit.institute_id == exam.institute_id))


        institute = self.env['bes.institute'].sudo().search([])


        

        # Return the values for the report
        return {
            'docids': docids,
            'doc_model': 'institute.gp.batches',
            'docs': docs1,
            'exams': exams_with_ship_visits,
            'institutes': institute,
            'ship_visits': ship_visits, 
            'name': 'Report'
        }
    

# class SummarisedGPReport(models.AbstractModel):
#     _name = "report.bes.summarised_gp_report"
#     _inherit = ['mail.thread','mail.activity.mixin']
#     _description = "Summarised GP Report"
    
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         docids = data['doc_ids']
#         docs1 = self.env['examination.report'].sudo().browse(docids)
        
#         data = self.env['summarised.gp.report'].sudo().search(
#                     [('examination_report_batch', '=', docs1.id)]).sorted(key=lambda r: r.institute_code)
#         exam_region = data.exam_region.ids
        
#         data = self.env['summarised.gp.report'].sudo().search([('examination_report_batch','=',docs1.id)])

        
#         print(exam_region)
#         # report_type = data['report_type']
#         # course = data['course']

#         # if report_type == 'Fresh' and course == 'GP':
#         #     exams = self.env['gp.exam.schedule'].sudo().search([('dgs_batch','=',docs1.id), ('attempt_number', '=', '1')])
#         # elif report_type == 'Repeater' and course == 'GP':
#         #     exams = self.env['gp.exam.schedule'].sudo().search([('dgs_batch', '=', docs1.id), ('attempt_number', '>', '1')])
        
#         # institutes = self.env['bes.institute'].sudo().search([], order='code asc')
#         # exam_centers = self.env['exam.center'].sudo().search([])

#         return {
#             'docids': docids,
#             'doc_model': 'summarised.gp.report',
#             'docs': data,
#             'exam_regions': exam_region,
#             'examination_report':docs1
#             # 'exams': exams,
#             # 'institutes': institutes,
#             # 'exam_centers': exam_centers,
#             # 'report_type': report_type,
#             # 'course': course
#         }
    
    
# class SummarisedCCMCReport(models.AbstractModel):
#     _name = "report.bes.summarised_ccmc_report"
#     _inherit = ['mail.thread','mail.activity.mixin']
#     _description = "Summarised CCMC Report"
    
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         docids = data['doc_ids']
#         exam_sequence = data['exam_sequence']
#         print(data)
#         docs1 = self.env['examination.report'].sudo().browse(docids)
#         data = self.env['summarised.ccmc.report'].sudo().search([('examination_report_batch','=',docs1.id)]).sorted(key=lambda r: r.institute_code)
#         print(docs1)
#         print(data)
#         exam_region = data.exam_region.ids
#         print(exam_region)
#         # report_type = data['report_type']
#         # course = data['course']

#         # if report_type == 'Fresh' and course == 'CCMC':
#         #     exams = self.env['ccmc.exam.schedule'].sudo().search([('dgs_batch','=',docs1.id), ('attempt_number', '=', '1')])
#         # elif report_type == 'Repeater' and course == 'CCMC':
#         #     exams = self.env['ccmc.exam.schedule'].sudo().search([('dgs_batch', '=', docs1.id), ('attempt_number', '>', '1')])
        
#         # institutes = self.env['bes.institute'].sudo().search([], order='code asc')
#         # exam_centers = self.env['exam.center'].sudo().search([])

#         return {
#             'docids': docids,
#             'doc_model': 'summarised.ccmc.report',
#             'docs': docids,
#             'exam_regions': exam_region,
#             'examination_report':docs1,
#             'exam_sequence':exam_sequence
#             # 'exams': exams,
#             # 'institutes': institutes,
#             # 'exam_centers': exam_centers,
#             # 'report_type': report_type,
#             # 'course': course
#         }