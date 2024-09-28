from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError

class CandidateInvoiceResetWizard(models.TransientModel):
    _name = 'candidate.invoice.reset.wizard'
    _description = 'Candidate Invoice Reset Wizard'
    
    
    
    def reset_invoice(self):
        
        invoice_id = self.env.context.get('active_id')
        model_name = 'account.move'

        invoices = self.env[model_name].sudo().browse(invoice_id)
        
        # import wdb;wdb.set_trace()
        
        if invoices.gp_repeater_candidate_ok:
            invoices.write({'gp_candidate':False,'transaction_id':False,'repeater_exam_batch':False,'gp_repeater_candidate_ok':False})
            invoices.button_draft()
        elif invoices.ccmc_repeater_candidate_ok:
            invoices.write({'ccmc_candidate':False ,'transaction_id':False, 'repeater_exam_batch':False, 'ccmc_repeater_candidate_ok':False})
            invoices.button_draft()
            
        

        

        

        

        




class BatchInvoice(models.Model):
    _inherit = "account.move"
    gp_batch_ok = fields.Boolean("GP Batch Required")
    
    gp_repeater_candidate_ok = fields.Boolean("GP Repeater Candidate Ok")
    ccmc_repeater_candidate_ok = fields.Boolean("CCMC Repeater Candidate Ok")
    
    repeater_exam_batch = fields.Many2one('dgs.batches', string='Exam Batch')

    preferred_exam_region = fields.Many2one('exam.center', string='Preferred Exam Region')
    
    
    gp_candidate = fields.Many2one('gp.candidate', string='GP Candidate')
    ccmc_candidate = fields.Many2one('ccmc.candidate', string='CCMC Candidate')
    
    visible_reset_invoice = fields.Boolean("Visible Reset Invoice", compute="_compute_visible_reset_invoice")
    
    def _compute_visible_reset_invoice(self):
        for record in self:
            if record.gp_repeater_candidate_ok or record.ccmc_repeater_candidate_ok and record.state == 'posted':
                record.visible_reset_invoice = True
            else:
                record.visible_reset_invoice = False
                
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
    indos_no  = fields.Char(string="INDoS No.")
    
   
    
    def open_candidate_invoice_reset_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reset Candidate Invoice',
            'res_model': 'candidate.invoice.reset.wizard',
            'view_mode': 'form',
            'target': 'new',
        }
    
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
    
    
    def array_difference(self,array1, array2):
        return [item for item in array1 if item not in array2]

    def action_create_payments(self):
        # import wdb;wdb.set_trace()
        # Your custom code here before or after calling the super method
        # import wdb;wdb.set_trace()
        
        group_name = 'bes.group_no_register_payment_access'  # Replace with the desired group's XML ID
        
        if self.env.user.has_group(group_name) :
            raise ValidationError("Not Allowed")        
        
        
        action = super(CustomPaymentRegister, self).action_create_payments()
        
        
                
        account_move_id = self.env.context['active_ids']
        invoices = self.env['account.move'].sudo().search([('id','in',account_move_id)])
        # if invoice.id == 392:
        #     import wdb;wdb.set_trace();
        # if invoice.id == 391:
        #     import wdb;wdb.set_trace();
        # if invoice.id == 390:
        #     import wdb;wdb.set_trace();
        print("gopppppppppppppppppppppppppppppppppppppp")
        for invoice in invoices:
    
        
        # import wdb; wdb.set_trace(); 
            if invoice.gp_batch_ok: #in GP Invoice
                print("gopppppppppppppppppppppppppppppppppppppp")
                gp_candidates = invoice.gp_candidates.ids
                batch = invoice.batch
                # self.env['batches.gp.register.exam.wizard'].sudo().register(batch.id)
                # batch.confirm_batch(gp_candidates)
                
                self.env['batches.gp.register.exam.wizard'].sudo().register(batch.id,gp_candidates)
                batch.confirm_batch(gp_candidates)
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
                batch.confirm_batch_ccmc(ccmc_candidates) # Disable For some time
                batch.write({'ccmc_state':'4-invoiced'})
                batch.write({'ccmc_state':'5-exam_scheduled'})
            # Your custom code here after calling the super method
                # For CCMC
                return action
            elif invoice.gp_repeater_candidate_ok:
                dgs_exam = invoice.repeater_exam_batch.id
                exam_id = self.env['ir.sequence'].next_by_code("gp.exam.sequence")
                last_exam = self.env['gp.exam.schedule'].sudo().search([('gp_candidate', '=', invoice.gp_candidate.id)], order='attempt_number desc', limit=1)
                
                gp_exam_schedule = self.env["gp.exam.schedule"].sudo().create({'gp_candidate':invoice.gp_candidate.id , "dgs_batch": dgs_exam  , "exam_id":exam_id ,"exam_region":invoice.preferred_exam_region.id})
                
                applied = []
                
                for line in invoice.invoice_line_ids:
                    if line.product_id.default_code == 'mek_po_repeater':
                        mek_practical = self.env["gp.mek.practical.line"].sudo().create({"exam_id":gp_exam_schedule.id,'mek_parent':invoice.gp_candidate.id})
                        mek_oral = self.env["gp.mek.oral.line"].sudo().create({"exam_id":gp_exam_schedule.id,'mek_oral_parent':invoice.gp_candidate.id})
                        mek_practical_marks = last_exam.mek_practical_marks
                        mek_oral_marks = last_exam.mek_oral_marks
                        mek_total = last_exam.mek_total
                        mek_percentage = last_exam.mek_percentage
                        mek_oral_prac_status = 'pending'
                        mek_oral_prac_carry_forward = False
                        attempting_mek_oral_prac = True
                        applied.append(line.product_id.default_code)
                    
                    if line.product_id.default_code == 'gsk_po_repeater':
                        gsk_practical = self.env["gp.gsk.practical.line"].sudo().create({"exam_id":gp_exam_schedule.id,'gsk_practical_parent':invoice.gp_candidate.id})
                        gsk_oral = self.env["gp.gsk.oral.line"].sudo().create({"exam_id":gp_exam_schedule.id,'gsk_oral_parent':invoice.gp_candidate.id})
                    
                        gsk_practical_marks = last_exam.gsk_practical_marks
                        gsk_oral_marks = last_exam.gsk_oral_marks
                        gsk_total = last_exam.gsk_total
                        gsk_percentage = last_exam.gsk_percentage
                        gsk_oral_prac_status = 'pending'
                        gsk_oral_prac_carry_forward = False
                        attempting_gsk_oral_prac = True
                        applied.append(line.product_id.default_code)

                    if line.product_id.default_code == 'gsk_online_repeater':
                        gsk_survey_qb_input = self.env["survey.survey"].sudo().search([('title','=','GSK ONLINE EXIT EXAMINATION SEP-2024')])
                        gsk_survey_qb_input = gsk_survey_qb_input._create_answer(user=invoice.gp_candidate.user_id)
                        token = gsk_survey_qb_input.generate_unique_string()
                        gsk_survey_qb_input.write({'gp_candidate':invoice.gp_candidate.id , 'dgs_batch':dgs_exam})
                        gsk_online_carry_forward = False
                        gsk_online_marks = last_exam.gsk_online_marks
                        gsk_online_percentage = last_exam.gsk_online_percentage
                        gsk_online_status = "pending"
                        attempting_gsk_online = True
                        applied.append(line.product_id.default_code)
                    
                    if line.product_id.default_code == 'mek_online_repeater':
                        mek_survey_qb_input = self.env["survey.survey"].sudo().search([('title','=','MEK ONLINE EXIT EXAMINATION SEP-2024')])
                        mek_survey_qb_input = mek_survey_qb_input._create_answer(user=invoice.gp_candidate.user_id)
                        token = mek_survey_qb_input.generate_unique_string()
                        mek_survey_qb_input.write({'gp_candidate':invoice.gp_candidate.id ,'dgs_batch':dgs_exam  })
                        mek_online_carry_forward = False
                        mek_online_marks = last_exam.mek_online_marks
                        mek_online_status = "pending"
                        attempting_mek_online = True
                        mek_online_percentage = last_exam.mek_online_percentage
                        applied.append(line.product_id.default_code)
                        
                total_applied = ['mek_po_repeater','gsk_po_repeater','gsk_online_repeater','mek_online_repeater']
                carry_forward_subjects = self.array_difference(total_applied, applied)

                for subject in carry_forward_subjects:
                    if subject == 'mek_po_repeater':
                        mek_practical = last_exam.mek_prac
                        mek_oral =last_exam.mek_oral
                        mek_oral_prac_carry_forward = True
                        attempting_mek_oral_prac = False
                        mek_practical_marks = last_exam.mek_practical_marks
                        mek_oral_marks = last_exam.mek_oral_marks
                        mek_total = last_exam.mek_total
                        mek_percentage = last_exam.mek_percentage
                        mek_oral_prac_status = last_exam.mek_oral_prac_status
                    
                    if subject == 'gsk_po_repeater':
                        gsk_practical = last_exam.gsk_prac
                        gsk_oral = last_exam.gsk_oral
                        gsk_practical_marks = last_exam.gsk_practical_marks
                        gsk_oral_marks = last_exam.gsk_oral_marks
                        gsk_total = last_exam.gsk_total
                        gsk_percentage = last_exam.gsk_percentage
                        gsk_oral_prac_status = last_exam.gsk_oral_prac_status
                        gsk_oral_prac_carry_forward = True
                        attempting_gsk_oral_prac = False
                    
                    if subject == 'gsk_online_repeater':
                        gsk_survey_qb_input = last_exam.gsk_online
                        gsk_online_marks = last_exam.gsk_online_marks
                        gsk_online_percentage = last_exam.gsk_online_percentage
                        gsk_online_status = last_exam.gsk_online_status
                        gsk_online_carry_forward = True
                        attempting_gsk_online = False
                    
                    if subject == 'mek_online_repeater':
                        mek_survey_qb_input = last_exam.mek_online
                        mek_online_carry_forward = True
                        mek_online_marks = last_exam.mek_online_marks
                        mek_online_status = last_exam.mek_online_status
                        mek_online_percentage = last_exam.mek_online_percentage
                        attempting_mek_online = False
                
                overall_marks = last_exam.overall_marks
                overall_percentage = last_exam.overall_percentage
                
                if invoice.repeater_exam_batch.to_date.strftime('%B') in ['March','September']:
                    registered_institute = None
                else:
                    registered_institute = invoice.gp_candidate.institute_id.id                
                
                gp_exam_schedule.write({
                                    "registered_institute":registered_institute,
                                    "mek_oral":mek_oral.id,
                                    "mek_prac":mek_practical.id,
                                    "gsk_oral":gsk_oral.id,
                                    "gsk_prac":gsk_practical.id , 
                                    "gsk_online":gsk_survey_qb_input.id,
                                    "gsk_online_status":gsk_online_status,
                                    "gsk_oral_prac_status":gsk_oral_prac_status, 
                                    "mek_online":mek_survey_qb_input.id,
                                    "gsk_practical_marks":gsk_practical_marks,
                                    "gsk_oral_marks":gsk_oral_marks,
                                    "gsk_total":gsk_total,
                                    "gsk_percentage":gsk_percentage,
                                    "mek_practical_marks":mek_practical_marks,
                                    "mek_oral_marks":mek_oral_marks,
                                    "mek_total":mek_total,
                                    "mek_percentage":mek_percentage,
                                    "mek_online_marks":mek_online_marks,
                                    "mek_online_status":mek_online_status,
                                    "mek_online_percentage":mek_online_percentage,
                                    "mek_oral_prac_status":mek_oral_prac_status,
                                    "gsk_online_marks":gsk_online_marks,
                                    "gsk_online_percentage":gsk_online_percentage,
                                    "overall_marks":overall_marks,
                                    "overall_percentage":overall_percentage,
                                    "gsk_oral_prac_carry_forward":gsk_oral_prac_carry_forward,
                                    "mek_oral_prac_carry_forward":mek_oral_prac_carry_forward,
                                    "mek_online_carry_forward":mek_online_carry_forward,
                                    "gsk_online_carry_forward":gsk_online_carry_forward,
                                    "hold_admit_card":True,
                                    "attempting_mek_oral_prac":attempting_mek_oral_prac,
                                    "attempting_gsk_oral_prac":attempting_gsk_oral_prac,
                                    "attempting_gsk_online":attempting_gsk_online,
                                    "attempting_mek_online":attempting_mek_online
                                    })
            
            elif invoice.ccmc_repeater_candidate_ok:
                dgs_batch = invoice.repeater_exam_batch.id      
                exam_id  = self.env['ir.sequence'].next_by_code("ccmc.exam.schedule")
                last_exam = self.env['ccmc.exam.schedule'].sudo().search([('ccmc_candidate', '=', invoice.ccmc_candidate.id)], order='attempt_number desc', limit=1)
                
                cookery_practical = last_exam.cookery_practical
                cookery_oral = last_exam.cookery_oral
                cookery_gsk_online = last_exam.cookery_gsk_online
                overall_marks = last_exam.overall_marks
                    

                #Mark Percentage
                cookery_bakery_percentage = last_exam.cookery_bakery_percentage
                ccmc_oral_percentage = last_exam.ccmc_oral_percentage
                cookery_gsk_online_percentage = last_exam.cookery_gsk_online_percentage
                overall_percentage = last_exam.overall_percentage
                
                ccmc_exam_schedule = self.env["ccmc.exam.schedule"].sudo().create({
                'ccmc_candidate':invoice.ccmc_candidate.id,
                'exam_region':invoice.preferred_exam_region.id,
                'exam_id':exam_id,
                'dgs_batch':dgs_batch,
                'cookery_practical':cookery_practical,
                'cookery_oral':cookery_oral,
                'cookery_gsk_online':cookery_gsk_online,
                'overall_marks':overall_marks ,
                'cookery_bakery_percentage':cookery_bakery_percentage,
                'ccmc_oral_percentage':ccmc_oral_percentage,
                'cookery_gsk_online_percentage':cookery_gsk_online_percentage,
                'overall_percentage':overall_percentage,
                'cookery_bakery_prac_status':last_exam.cookery_bakery_prac_status,
                'ccmc_oral_prac_status':last_exam.ccmc_oral_prac_status
                })
                
                applied = []
                for line in invoice.invoice_line_ids:
                    if line.product_id.default_code == 'ccmc_online_repeater':
                        cookery_bakery_qb_input = self.env["survey.survey"].sudo().search([('title','=','CCMC_NEW_2')])
                        cookery_bakery_qb_input = cookery_bakery_qb_input._create_answer(user=invoice.ccmc_candidate.user_id)
                        cookery_bakery_qb_input.write({'ccmc_candidate':invoice.ccmc_candidate.id , 'dgs_batch': dgs_batch})
                        ccmc_online_status = 'pending'
                        cookery_gsk_online_carry_forward = False
                        applied.append(line.product_id.default_code)
                        attempting_online = True
                        
                    if line.product_id.default_code == 'ccmc_practical_repeater':
                        cookery_bakery = self.env["ccmc.cookery.bakery.line"].sudo().create({"exam_id":ccmc_exam_schedule.id,'cookery_parent':invoice.ccmc_candidate.id})
                        cookery_prac_carry_forward = False
                        cookery_bakery_prac_status = 'pending'
                        applied.append(line.product_id.default_code)
                        attempting_cookery = True
                        
                    if line.product_id.default_code == 'ccmc_oral_repeater':
                        ccmc_oral = self.env["ccmc.oral.line"].sudo().create({"exam_id":ccmc_exam_schedule.id,'ccmc_oral_parent':invoice.ccmc_candidate.id})
                        ccmc_gsk_oral = self.env["ccmc.gsk.oral.line"].sudo().create({"exam_id":ccmc_exam_schedule.id,'ccmc_oral_parent':invoice.ccmc_candidate.id})
                        cookery_oral_carry_forward = False
                        ccmc_oral_prac_status = 'pending'
                        applied.append(line.product_id.default_code)
                        attempting_oral = True

                total_applied = ['ccmc_online_repeater','ccmc_practical_repeater','ccmc_oral_repeater']
                carry_forward_subjects = self.array_difference(total_applied, applied)
                # import wdb; wdb.set_trace();     
                
                for subject in carry_forward_subjects:
                    if subject == 'ccmc_practical_repeater':
                        cookery_bakery = last_exam.cookery_bakery
                        cookery_bakery_prac_status = last_exam.cookery_bakery_prac_status
                        cookery_prac_carry_forward = True
                        attempting_cookery = False
                        
                        
                    if subject == 'ccmc_oral_repeater':
                        ccmc_oral = last_exam.ccmc_oral
                        ccmc_oral_prac_status = last_exam.ccmc_oral_prac_status
                        ccmc_gsk_oral = last_exam.ccmc_gsk_oral
                        cookery_oral_carry_forward = True
                        attempting_oral = False
                    
                    if subject == 'ccmc_online_repeater':
                        cookery_bakery_qb_input = last_exam.ccmc_online
                        ccmc_online_status = last_exam.ccmc_online_status
                        cookery_gsk_online_carry_forward = True
                        attempting_online = False
                        
                if invoice.repeater_exam_batch.to_date.strftime('%B') in ['March','September']:
                    registered_institute = None
                else:
                    registered_institute = invoice.ccmc_candidate.institute_id.id                

                
                ccmc_exam_schedule.sudo().write({
                                        "registered_institute":registered_institute,
                                        "cookery_bakery":cookery_bakery.id,
                                        "cookery_bakery_prac_status":cookery_bakery_prac_status,
                                        "ccmc_gsk_oral":ccmc_gsk_oral.id,
                                        "ccmc_oral":ccmc_oral.id,
                                        "ccmc_oral_prac_status":ccmc_oral_prac_status,
                                        "ccmc_online":cookery_bakery_qb_input.id,
                                        "ccmc_online_status":ccmc_online_status,
                                        "cookery_gsk_online_carry_forward":cookery_gsk_online_carry_forward,
                                        "cookery_oral_carry_forward":cookery_oral_carry_forward,
                                        "cookery_prac_carry_forward":cookery_prac_carry_forward,
                                        "hold_admit_card":True,
                                        "attempting_cookery":attempting_cookery,
                                        "attempting_online":attempting_online,
                                        "attempting_oral":attempting_oral
                                        })  

                        
            
    
                    
                
            # For Gp 
        return action
        

        # print("Data")
