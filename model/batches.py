from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError


from datetime import datetime



class InstituteGPBatches(models.Model):
    _name = "institute.gp.batches"
    _rec_name = "batch_name"
    _description= 'Batches'
    
    institute_id = fields.Many2one("bes.institute",string="Institute",required=True)
    batch_name = fields.Char("Batch Name",required=True)
    faculty_name = fields.Char("Faculty name")
    candidate_count = fields.Integer("Candidate Count",compute="_compute_candidate_count")
    from_date = fields.Date("From Date")
    to_date = fields.Date("To Date")
    course = fields.Many2one("course.master","Course")
    account_move = fields.Many2one("account.move",string="Invoice")
    invoice_created = fields.Boolean("Invoice Created")
    create_invoice_button_invisible = fields.Boolean("Invoice Button Visiblity",
                                                      compute="_compute_invoice_button_visible",
                                                      store=False,  # This field is not stored in the database
                                                            )

    state = fields.Selection([
        ('1-ongoing', 'On-Going'),
        ('2-indos_pending', 'Indos Pending'),
        ('3-pending_invoice', 'Invoice Pending'),
        ('4-invoiced', 'Invoiced'),
        ('5-exam_scheduled', 'Exam Scheduled'),
        ('6-done', 'Done')        
    ], string='State', default='1-ongoing')
    
    payment_state = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid')     
    ], string='Payment State', default='not_paid',compute="_compute_payment_state",)
    
    @api.depends('account_move')
    def _compute_payment_state(self):
        for rec in self:
            if rec.account_move.payment_state == 'not_paid':
                rec.payment_state = 'not_paid'
            elif rec.account_move.payment_state == 'paid':
                rec.payment_state = 'paid'
            elif rec.account_move.payment_state == 'partial':
                rec.payment_state = 'partial'
            else:
                rec.payment_state = 'not_paid'
                
    
    @api.depends('state', 'invoice_created')
    def _compute_invoice_button_visible(self):
        for record in self:
            record.create_invoice_button_invisible = (record.state == '3-pending_invoice' and not record.invoice_created)
  
    @api.depends("candidate_count")
    def _compute_candidate_count(self):
        for rec in self:
            candidate_count = self.env["ccmc.candidate"].search_count([('institute_batch_id','=', rec.id)])
            rec.candidate_count = candidate_count
    
    def move_to_invoiced(self):
        if self.payment_state == 'not_paid':
            raise ValidationError("Invoice is not Paid")
        self.write({"state":'4-invoiced'})
        
    
    def register_for_exam(self):
        candidates = self.env["gp.candidate"].search([('institute_batch_id','=',self.id)])
        for candidate in candidates:
            gp_exam_schedule = self.env["gp.exam.schedule"].create({'gp_candidate':candidate.id})
            mek_practical = self.env["gp.mek.practical.line"].create({"exam_id":gp_exam_schedule.id,'mek_parent':candidate.id})
            mek_oral = self.env["gp.mek.oral.line"].create({"exam_id":gp_exam_schedule.id,'mek_oral_parent':candidate.id})
            
            gsk_practical = self.env["gp.gsk.practical.line"].create({"exam_id":gp_exam_schedule.id,'gsk_practical_parent':candidate.id})
            gsk_oral = self.env["gp.gsk.oral.line"].create({"exam_id":gp_exam_schedule.id,'gsk_oral_parent':candidate.id})
            
            gp_exam_schedule.write({"mek_oral":mek_oral.id,"mek_prac":mek_practical.id,"gsk_oral":gsk_oral.id,"gsk_prac":gsk_practical.id})
        
        self.write({"state":'5-exam_scheduled'})
        

          
    
    def create_invoice(self):
        
        # import wdb; wdb.set_trace()

        partner_id = self.institute_id.user_id.partner_id.id
        product_id = self.course.exam_fees.id
        product_price = self.course.exam_fees.lst_price
        qty = self.candidate_count
        line_items = [(0, 0, {
        'product_id': product_id,
        'price_unit':product_price,
        'quantity':qty
        })]
        
        invoice_vals = {
            'partner_id': partner_id,  # Replace with the partner ID for the customer
            'move_type': 'out_invoice',
            'invoice_line_ids':line_items,
            'batch_ok':True,
            'batch':self.id
            # Add other invoice fields as needed
        }
        new_invoice = self.env['account.move'].create(invoice_vals)    
        
        self.write({"invoice_created":True,"account_move":new_invoice.id})
        
        
        return {
        'name': 'New Invoice',
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'account.move',
        'type': 'ir.actions.act_window',
        'res_id': new_invoice.id,
        'target': 'current',  # Open in the current window
        }
    
    def confirm_batch(self):
        
        self.write({"state":"2-indos_pending"})
        
    
    def confirm_indos(self):
        self.write({"state":"3-pending_invoice"})
        


    def open_batch_candidate(self):
        
        return {
        'name': 'GP Batch',
        'domain': [('institute_batch_id', '=', self.id)],
        'view_type': 'form',
        'res_model': 'gp.candidate',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        'context': {
            'default_institute_batch_id': self.id    
            }
        }        

    def open_batch_faculty(self):
        
        return {
        'name': 'Faculties',
        'domain': [('gp_batches_id', '=', self.id)],
        'view_type': 'form',
        'res_model': 'institute.faculty',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        'context': {
            # 'default_batches_id': self.id
            'default_gp_batches_id': self.id,
            'default_gp_or_ccmc_batch': 'gp'   
            }
        } 

    def open_register_for_exam_wizard(self):
        view_id = self.env.ref('bes.batches_gp_register_exam_wizard').id
        
        return {
            'name': 'Register For Exam',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'batches.gp.register.exam.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_institute_id': self.institute_id.id,
                'default_batch_id': self.id
            }
        }
    
    


class InstituteCcmcBatches(models.Model):
    _name = "institute.ccmc.batches"
    _rec_name = "ccmc_batch_name"
    _description= 'Batches'
    
    institute_id = fields.Many2one("bes.institute",string="Institute",required=True)
    ccmc_batch_name = fields.Char("Batch Name",required=True)
    ccmc_faculty_name = fields.Char("Faculty name")
    ccmc_candidate_count = fields.Integer("Candidate Count",compute="ccmc_compute_candidate_count")
    ccmc_from_date = fields.Date("From Date")
    ccmc_to_date = fields.Date("To Date")
    ccmc_course = fields.Many2one("course.master","Course")
    ccmc_account_move = fields.Many2one("account.move",string="Invoice")
    ccmc_invoice_created = fields.Boolean("Invoice Created")
    ccmc_create_invoice_button_invisible = fields.Boolean("Invoice Button Visiblity",
                                                      compute="ccmc_compute_invoice_button_visible",
                                                      store=False,  # This field is not stored in the database
                                                            )

    ccmc_state = fields.Selection([
        ('1-ongoing', 'On-Going'),
        ('2-indos_pending', 'Indos Pending'),
        ('3-pending_invoice', 'Invoice Pending'),
        ('4-invoiced', 'Invoiced'),
        ('5-exam_scheduled', 'Exam Scheduled'),
        ('6-done', 'Done')        
    ], string='State', default='1-ongoing')
    
    payment_state = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid')     
    ], string='Payment State', default='not_paid',compute="_compute_payment_state",)
    
    @api.depends('ccmc_account_move')
    def _compute_payment_state(self):
        for rec in self:
            if rec.ccmc_account_move.payment_state == 'not_paid':
                rec.payment_state = 'not_paid'
            elif rec.ccmc_account_move.payment_state == 'paid':
                rec.payment_state = 'paid'
            elif rec.ccmc_account_move.payment_state == 'partial':
                rec.payment_state = 'partial'
            else:
                rec.payment_state = 'not_paid'
                
    
    @api.depends('ccmc_state', 'ccmc_invoice_created')
    def ccmc_compute_invoice_button_visible(self):
        for record in self:
            record.ccmc_create_invoice_button_invisible = (record.ccmc_state == '3-pending_invoice' and not record.ccmc_invoice_created)
  
    @api.depends("ccmc_candidate_count")
    def ccmc_compute_candidate_count(self):
        for rec in self:
            ccmc_candidate_count = self.env["ccmc.candidate"].search_count([('institute_batch_id','=', rec.id)])
            rec.ccmc_candidate_count = ccmc_candidate_count
    
    def move_to_invoiced_ccmc(self):
        if self.payment_state == 'not_paid':
            raise ValidationError("Invoice is not Paid")
        self.write({"ccmc_state":'4-invoiced'})

          
    
    def create_invoice_ccmc(self):
        
        # import wdb; wdb.set_trace()

        ccmc_partner_id = self.institute_id.user_id.ccmc_partner_id.id
        product_id_ccmc = self.ccmc_course.exam_fees.id
        product_price = self.ccmc_course.exam_fees.lst_price
        qty = self.ccmc_candidate_count
        line_items = [(0, 0, {
        'product_id_ccmc': product_id_ccmc,
        'price_unit':product_price,
        'quantity':qty
        })]
        
        invoice_vals = {
            'ccmc_partner_id': ccmc_partner_id,  # Replace with the partner ID for the customer
            'move_type': 'out_invoice',
            'invoice_line_ids':line_items,
            'batch_ok':True,
            'batch':self.id
            # Add other invoice fields as needed
        }
        new_invoice = self.env['account.move'].create(invoice_vals)    
        
        self.write({"ccmc_invoice_created":True,"ccmc_account_move":new_invoice.id})
        
        
        return {
        'name': 'New Invoice',
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'account.move',
        'type': 'ir.actions.act_window',
        'res_id': new_invoice.id,
        'target': 'current',  # Open in the current window
        }
    
    def confirm_batch_ccmc(self):
        
        self.write({"ccmc_state":"2-indos_pending"})
        
    
    def confirm_indos_ccmc(self):
        self.write({"ccmc_state":"3-pending_invoice"})
        


    def open_ccmc_batch_candidate(self):
        
        return {
        'name': 'CCMC Batch',
        'domain': [('institute_batch_id', '=', self.id)],
        'view_type': 'form',
        'res_model': 'ccmc.candidate',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        'context': {
            'default_institute_batch_id': self.id    
            }
        } 
          

    def open_ccmc_batch_faculty(self):
        
        return {
        'name': 'Faculties',
        'domain': [('ccmc_batches_id', '=', self.id)],
        'view_type': 'form',
        'res_model': 'institute.faculty',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        'context': {
            # 'default_ccmc_batches_id': self.id
            'default_ccmc_batches_id': self.id,
            'default_gp_or_ccmc_batch': 'ccmc'     
            }
        } 

    
        
    

        
        
        
        
class BatchesRegisterExamWizard(models.TransientModel):
    _name = 'batches.gp.register.exam.wizard'
    _description = 'Register Exam'

    institute_id = fields.Many2one("bes.institute",string="Institute",required=True)
    batch_id = fields.Many2one("institute.gp.batches",string="Batches",required=True)
    survey_qb = fields.Many2one("survey.survey",string="Question Bank")
    
    
    
    def register(self):
        candidates = self.env["gp.candidate"].search([('institute_batch_id','=',self.batch_id.id)])
        for candidate in candidates:
            gp_exam_schedule = self.env["gp.exam.schedule"].create({'gp_candidate':candidate.id})
            mek_practical = self.env["gp.mek.practical.line"].create({"exam_id":gp_exam_schedule.id,'mek_parent':candidate.id})
            mek_oral = self.env["gp.mek.oral.line"].create({"exam_id":gp_exam_schedule.id,'mek_oral_parent':candidate.id})
            
            gsk_practical = self.env["gp.gsk.practical.line"].create({"exam_id":gp_exam_schedule.id,'gsk_practical_parent':candidate.id})
            gsk_oral = self.env["gp.gsk.oral.line"].create({"exam_id":gp_exam_schedule.id,'gsk_oral_parent':candidate.id})
            
            gp_exam_schedule.write({"mek_oral":mek_oral.id,"mek_prac":mek_practical.id,"gsk_oral":gsk_oral.id,"gsk_prac":gsk_practical.id})
        
        self.batch_id.write({"state":'5-exam_scheduled'})


   
