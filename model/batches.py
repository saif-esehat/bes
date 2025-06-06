from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
import base64
from io import BytesIO
import xlsxwriter
from datetime import datetime
import xlrd


class SendMailWizard(models.TransientModel):
    _name = 'send.mail.wizard'
    _description = 'Wizard to Send Mail'

    template_id = fields.Many2one('mail.template', string='Mail Template', required=True)
    subject = fields.Char(string='Subject')
    body_html = fields.Html(string='Body')

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            self.subject = self.template_id.subject
            self.body_html = self.template_id.body_html

    def action_send_mail(self):
        self.ensure_one()
        active_ids = self.env.context.get('active_ids', [])
        active_model = self.env.context.get('active_model', False)
        
        
        # import wdb;wdb.set_trace()
        if active_model and active_ids:
            records = self.env[active_model].browse(active_ids)
            for record in records:
                email_context = {
                    'email_to': record.institute_id.email,
                    'subject': self.subject,
                    'body_html': self.body_html,
                    'auto_delete': False
                    
                }
                self.template_id.send_mail(record.id,email_values=email_context, force_send=True)
        return {'type': 'ir.actions.act_window_close'}





class InstituteGPBatches(models.Model):
    _name = "institute.gp.batches"
    _rec_name = "batch_name"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'GP Batches'
    
    
    
    
    institute_id = fields.Many2one("bes.institute",string="Institute",required=True,tracking=True)

    candidate_ids = fields.Many2many('gp.candidate', string="Candidates")
    ship_visit_id = fields.Many2one('gp.batches.ship.visit', string='Ship Visit')
    
    
    
    code = fields.Char(string="Code",related='institute_id.code', store=True ,tracking=True)
    exam_region = fields.Char("Exam Region",related ='institute_id.exam_center.name',store=True,tracking=True)
    dgs_batch = fields.Many2one("dgs.batches",string="Exam Batch",required=False,tracking=True)
    batch_name = fields.Char("Batch Name",required=True,tracking=True)
    faculty_name = fields.Char("Faculty name",tracking=True)
    candidate_count = fields.Integer("Candidate Count",compute="_compute_candidate_count",tracking=True)
    candidate_user_invoice_criteria = fields.Boolean("Invoice Criteria",compute="compute_candidate_user_invoice_criteria")
    all_invoice_generated = fields.Boolean("All Invoice Generated",compute="compute_all_invoice_generated")

    from_date = fields.Date("From Date",tracking=True)
    to_date = fields.Date("To Date",tracking=True)
    course = fields.Many2one("course.master","Course",tracking=True)
    account_move = fields.Many2one("account.move",string="Invoice",tracking=True)
    invoice_created = fields.Boolean("Invoice Created",tracking=True)
    
    admit_card_status = fields.Selection([
        ('pending', 'Pending'),
        ('issued', 'Issued')
    ],default="pending", string='Admit Card Status')

    admit_card_alloted = fields.Integer("No. of Candidate Eligible for Admit Card",compute="_compute_admit_card_count")
    
    create_invoice_button_invisible = fields.Boolean("Invoice Button Visiblity",
                                                      compute="_compute_invoice_button_visible",
                                                      store=False,tracking=True # This field is not stored in the database
                                                            )

    
    state = fields.Selection([
        ('1-ongoing', 'Invoice Not Generated'),
        ('2-indos_pending', 'Confirmed'),
        ('3-pending_invoice', 'Invoice Generated'),
        ('4-invoiced', 'Paid'),
        ('5-exam_scheduled', 'Exam Scheduled'),
        ('6-done', 'Batch Closed')        
    ], string='State', default='1-ongoing',tracking=True)
    
    active = fields.Boolean(string="Active",default=True,tracking=True)
    
    payment_state = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid')     
    ], string='Payment State', default='not_paid',compute="_compute_payment_state",tracking=True)
    
    dgs_approved_capacity = fields.Integer(string="DGS Approved Capacity",tracking=True)
    dgs_approval_state = fields.Boolean(string="DGS Approval Status",tracking=True)
    dgs_document = fields.Binary(string="DGS Document",tracking=True)
    document_name = fields.Char("Name of Document",tracking=True)
    document_file = fields.Binary(string='Upload Document',tracking=True)
    
    mek_survey_qb = fields.Many2one("survey.survey",string="Mek Question Bank",tracking=True)
    gsk_survey_qb = fields.Many2one("survey.survey",string="Gsk Question Bank",tracking=True)
    
    all_candidates_have_indos = fields.Boolean(string="All Candidates Have INDOS", compute="_compute_all_candidates_have_indos")
    
    def action_open_send_mail_wizard(self):

        return {
            'type': 'ir.actions.act_window',
            'name': 'Send Mail',
            'res_model': 'send.mail.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {            
                'active_ids': self.ids
            },
        }
    
    def _compute_all_candidates_have_indos(self):
        for record in self:
            # import wdb; wdb.set_trace()
            candidate_count = self.env["gp.candidate"].search_count([('institute_batch_id', '=', record.id),('withdrawn_state','!=','yes')])

            if candidate_count > 0:
                candidates_with_indos = self.env["gp.candidate"].search_count([('institute_batch_id', '=', record.id), ('indos_no', '!=', ''),('withdrawn_state','!=','yes')])
                if candidate_count == candidates_with_indos:
                    record.all_candidates_have_indos = True
                else:
                    record.all_candidates_have_indos = False
            else:
                record.all_candidates_have_indos = False

    # @api.depends('institute_id')
    # def _compute_batch_capacity(self):
    #     for rec in self:
    #         if rec.institute_id.courses[0].course.course_code == 'GP':
    #             # import wdb; wdb.set_trace()
    #             rec.dgs_approved_capacity = rec.institute_id.courses[0].intake_capacity

    # @api.depends("dgs_approved_capacity")


    def close_batch(self):
        for rec in self:
            rec.state = '6-done'
    
    def open_batch(self):
        for rec in self:
            rec.state = '5-exam_scheduled'

    def update_dgs_capacity(self):
        """
        Enforces capacity rules for DGS batches based on the associated course's batcher_per_year.
        """
        for batch in self:
            year = batch.from_date.year if batch.from_date else None
            if not year:
                continue

            # Fetch the total intake capacity and batcher_per_year from the associated course
            course_record = self.env['institute.courses'].search([
                ('institute_id', '=', batch.institute_id.id),
                ('course.course_code', '=', 'GP')
            ], limit=1)

            # import wdb; wdb.set_trace()
            if not course_record:
                raise ValidationError("No course record found for the selected institute and course.")

            if course_record.batcher_per_year == 1:
                # Allocate full capacity if there's only one batch per year
                batch.dgs_approved_capacity = course_record.total
                batch.dgs_approval_state = True

            elif course_record.batcher_per_year == 2:
                # Divide capacity equally between two batches
                half_capacity = course_record.total // 2
                batch.dgs_approved_capacity = half_capacity
                batch.dgs_approval_state = True

            else:
                # Validate total capacity across multiple batches
                jan_to_jun_batches = self.env['institute.gp.batches'].search([
                    ('institute_id', '=', batch.institute_id.id),
                    ('from_date', '>=', f'{year}-01-01'),
                    ('to_date', '<=', f'{year}-06-30')
                ])
                jul_to_dec_batches = self.env['institute.gp.batches'].search([
                    ('institute_id', '=', batch.institute_id.id),
                    ('from_date', '>=', f'{year}-07-01'),
                    ('to_date', '<=', f'{year}-12-31')
                ])

                # Calculate total approved capacity
                jan_to_jun_capacity = sum(jan_to_jun_batches.mapped('dgs_approved_capacity'))
                jul_to_dec_capacity = sum(jul_to_dec_batches.mapped('dgs_approved_capacity'))
                total_capacity = jan_to_jun_capacity + jul_to_dec_capacity

                if total_capacity > course_record.total:
                    raise ValidationError(
                        f"DGS Capacity exceeded for the year {year}. "
                        f"Total approved capacity ({total_capacity}) exceeds the intake capacity "
                        f"({course_record.total})."
                    )




    @api.model
    def create(self, values):
        record = super(InstituteGPBatches, self).create(values)
        course_id = self.env["course.master"].sudo().search([('course_code','=','GP')]).id
        record.write({'course': course_id})
        record.update_dgs_capacity()  # Validate after creation
        return record
    
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
    
    @api.depends("all_invoice_generated")
    def compute_all_invoice_generated(self):
        for record in self:
             candidate_count = self.env["gp.candidate"].search_count([('institute_batch_id','=', record.id)])

             if candidate_count > 0:
               
               candidate_with_generated_invoice = self.env['gp.candidate'].sudo().search_count([('institute_batch_id','=',record.id),('fees_paid','=','yes'),('invoice_generated','=',True)]) 
               
               if candidate_with_generated_invoice == candidate_count:
                    record.all_invoice_generated = True
               else: 
                   record.all_invoice_generated = False
                 
             else:
                 record.all_invoice_generated = False
                 
    
    @api.depends("candidate_user_invoice_criteria")
    def compute_candidate_user_invoice_criteria(self):
        for record in self:
            # import wdb; wdb.set_trace()
            candidate_count = self.env["gp.candidate"].search_count([('institute_batch_id','=', record.id)])

            if candidate_count > 0 :
            
                gp_batch_id = record.id
                candidate_with_correct_data = self.env["gp.candidate"].search_count([('institute_batch_id','=', record.id),('candidate_user_invoice_criteria','=',True)])
                
                if candidate_count == candidate_with_correct_data:
                    record.candidate_user_invoice_criteria = True
                else:
                    record.candidate_user_invoice_criteria = False
            else :
                record.candidate_user_invoice_criteria = False
 

    @api.model
    def action_delete_batches(self, batch_ids=None):
        if batch_ids is None or not batch_ids:
            raise ValidationError("No batches selected for deletion.")

        # Retrieve records to be deleted based on provided IDs
        batches_to_delete = self.browse(batch_ids)
        
        if not batches_to_delete:
            raise ValidationError("No valid batches found to delete.")
        
        # Construct message with batch names and corresponding institute names
        batch_info = []
        for batch in batches_to_delete:
            institute_name = batch.institute_id.name or 'Unknown Institute'
            batch_info.append(f"(Institute: {institute_name}) - {batch.batch_name} \n")
        
        batch_info_str = ', '.join(batch_info)
        
        # Pass the message and batch IDs to the wizard
        return {
            'name': 'Batch Delete Confirmation',
            'type': 'ir.actions.act_window',
            'res_model': 'batch.delete.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {
                'default_message': f"Batches to be deleted:\n{batch_info_str}",
                'batch_ids': batch_ids,
            }
        }
    
            
    
    
    @api.depends("candidate_count")
    def _compute_candidate_count(self):
        for rec in self:
            candidate_count = self.env["gp.candidate"].search_count([('institute_batch_id','=', rec.id),])
            rec.candidate_count = candidate_count
    
    @api.depends("admit_card_alloted")
    def _compute_admit_card_count(self):
        for rec in self:
            candidate_count = self.env["gp.candidate"].search_count([('institute_batch_id','=', rec.id),('stcw_criteria','=','passed'),('ship_visit_criteria','=','passed'),('attendance_criteria','=','passed')])
            # import wdb; wdb.set_trace()
            # for i in candidate:
                # candidate_count = self.env["gp.exam.schedule"].search_count([('gp_candidate','=',i.id),('stcw_criteria','=','passed'),('ship_visit_criteria','=','passed'),('attendance_criteria','=','passed')])
            rec.admit_card_alloted = candidate_count
            # self.write({"admit_card_alloted":candidate_count})
            
    def move_to_invoiced(self):
        if self.payment_state == 'not_paid':
            raise ValidationError("Invoice is not Paid")
        self.write({"state":'4-invoiced'})
        
    
    def register_for_exam(self):

        # import wdb; wdb.set_trace()
        
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
            'gp_batch_ok':True,
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
    
    # Added method to generate sequence
    def generate_sequence(self):
        # import wdb; wdb.set_trace()
        batch_year = self.to_date.strftime('%y')
        batch_month = self.to_date.strftime('%m')
        half = '06' if int(batch_month) <= 6 else '12'
        institute_code = self.institute_id.code # Replace this with your actual institute code
        
        # Count the number of candidates in the batch
        # candidate_count = self.env['gp.candidate'].sudo().search_count([('institute_batch_id','=',self.id),('user_id','=',True)])
        candidate_count = self.env['gp.candidate'].sudo().search_count([('institute_batch_id','=',self.id),('user_id','!=',None)])

        # import wdb; wdb.set_trace()
        # Generate the sequence number starting from '001'
        candidate_count = candidate_count+1
        
        next_sequence_number = str(candidate_count).zfill(3)
        

        sequence = f'G{batch_year}{half}{institute_code}{next_sequence_number}'
        return sequence




    def confirm_batch(self,candidate_ids):
        
        # import wdb;wdb.set_trace();
        # candidate_count = self.env['gp.candidate'].sudo().search_count([('institute_batch_id','=',self.id),('user_status','=','active')])
        canidate_list_no_indos = []
        candidate_missing_data_id = []
        
        candidates = self.env['gp.candidate'].sudo().browse(candidate_ids)
        print("Candidates")
        print(candidates)
        for candidate in candidates:
        # for candidate in self.env['gp.candidate'].sudo().search([('institute_batch_id','=',self.id),('fees_paid','=','yes')]):
            if not candidate.indos_no or not candidate.candidate_image or not candidate.candidate_signature :
                
                missing_data=""
                if not candidate.indos_no:
                    missing_data +="Indos No,"  
                
                if not candidate.candidate_image:
                    missing_data +="Candidate Image,"  
                
                if not candidate.candidate_signature:
                    missing_data +="Candidate Signature,"
                
                missing_data = missing_data.rstrip(',')    
                
                candidate_data = {"candidate_name" : candidate.name , "candidate_mobile":candidate.mobile , "missing_data": missing_data }
                canidate_list_no_indos.append(candidate_data)
                candidate_missing_data_id.append(candidate.id)
        # import wdb; wdb.set_trace()
        if len(canidate_list_no_indos) > 0:
        
            
            template_id = self.env.ref('bes.indos_check_mail').id
            official_institute_mail_id = self.institute_id.user_id.partner_id.ids
            # import wdb; wdb.set_trace()

            ctx = {
                'default_res_id': self.id,
                'default_template_id': template_id,
                'default_use_template': bool(template_id),
                'default_composition_mode': 'comment',
                'default_partner_ids': official_institute_mail_id,
                "default_candidate_lists": canidate_list_no_indos
            }

            
            mail_template = self.env.ref('bes.indos_check_mail')
            mail_template.with_context(ctx).send_mail(self.id,force_send=True)

            
            
        gp_candidates = candidates.ids
        print("Candidates IDs " + str(gp_candidates) )

        set1 = set(gp_candidates)
        set2 = set(candidate_missing_data_id)
        
        # Remove common elements from both sets
        array1_without_common = list(set1 - set2)

        gp_candidates = self.env['gp.candidate'].sudo().browse(array1_without_common)
        print("gp_candidates s " + str(gp_candidates))
        group_xml_ids = [
        'bes.group_gp_candidates',
        'base.group_portal'
        ]
        # # import wdb; wdb.set_trace()
        group_ids = [self.env.ref(xml_id).id for xml_id in group_xml_ids]
        
        # import wdb; wdb.set_trace()
        for gp_candidate in gp_candidates:
            user_values = {
            'name': gp_candidate.name,
            'login': gp_candidate.indos_no.strip(),  # You can set the login as the same as the user name
            'password': str(gp_candidate.indos_no.strip())+"1",  # Generate a random password
            'sel_groups_1_9_10':9,
            'groups_id':  [(4, group_id, 0) for group_id in group_ids]
            }
            # import wdb; wdb.set_trace()
            # 
            try:
                portal_user = self.env['res.users'].sudo().create(user_values)
            except:
                print("Duplicate")
                print(user_values)
            
            candidate_count = self.env['gp.candidate'].sudo().search_count([('institute_batch_id','=',self.id)]) 
            
        
            sequence = self.generate_sequence()

            # '
            gp_candidate.write({'user_id': portal_user.id,
                                'candidate_code': sequence  # Assign the generated sequence to the partner
                                })
            
            # gp_candidate.write({'user_id': portal_user.id})
            candidate_tag = self.env.ref('bes.candidates_tags').id
            portal_user.partner_id.write({
                'email': gp_candidate.email,
                'phone':gp_candidate.phone,
                'mobile':gp_candidate.mobile,
                'street':gp_candidate.street,
                'street2':gp_candidate.street2,
                'city':gp_candidate.city,
                'zip':gp_candidate.zip,
                'state_id':gp_candidate.state_id.id,
                'category_id':[candidate_tag]
                                    })
                
             
        self.write({"state":"2-indos_pending"})
        
    
    def confirm_indos(self):
        self.write({"state":"3-pending_invoice"})
    
    def issue_admit_card(self):
        # import wdb; wdb.set_trace()
        candidates = self.env["gp.candidate"].search([('institute_batch_id','=',self.id)])
        for candidate in candidates:
            gp_exam = self.env["gp.exam.schedule"].search([('gp_candidate', '=', candidate.id)])
            gp_exam.sudo().write({"hold_admit_card":False})

        self.write({"admit_card_status":"issued"})
        


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
        # 'res_model': 'batches.faculty',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        'context': {
            # 'default_batches_id': self.id
            'default_gp_batches_id': self.id,
            'default_gp_or_ccmc_batch': 'gp'   
            }
        } 

    # def open_gp_ship_visit(self):
        # """
        # This method opens the GP Ship Visit form, filtered by selected candidates.
        # """
        # domain = []
        # default_candidate_ids = []

        # # Check if candidate_ids are available for filtering
        # if self.candidate_ids:
        #     domain = [('candidate_ids', 'in', self.candidate_ids.ids)]
        #     default_candidate_ids = [(6, 0, self.candidate_ids.ids)]
        
        # Return the action to open the tree and form views
        # return {
        #     'name': _('GP Ship Visit'),
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'gp.batches.ship.visit',
        #     'view_mode': 'tree,form',
        #     'view_type': 'form',
        #     'domain': domain,
        #     'context': {
        #         'default_candidate_ids': default_candidate_ids,
        #     },
        #     'target': 'current',
        # }


    def open_gp_ship_visit(self):
        
        return {
        'name': 'GP Ship Visit',
        'domain': [('gp_ship_batch_id', '=', self.id)],
        'view_type': 'form',
        'res_model': 'gp.batches.ship.visit',
        # 'res_model': 'batches.faculty',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        'context': {
            # 'default_batches_id': self.id
            'default_gp_ship_batch_id': self.id,
            'default_gp_or_ccmc_batch': 'gp',
            'default_dgs_batch': self.dgs_batch.id,
            'default_institute_id': self.institute_id.id,   
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
                'default_batch_id': self.id,
                'default_dgs_batch': self.dgs_batch.id
            }
        }
    
    
    def open_faculty_upload_wizard(self):
        return {
            'name': 'Upload Faculty',
            'type': 'ir.actions.act_window',
            'res_model': 'faculty.upload.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_batch_id': self.id},
        }

class FacultyUploadWizard(models.TransientModel):
    _name = 'faculty.upload.wizard'
    _description = 'Faculty Upload Wizard'

    batch_id = fields.Many2one('institute.gp.batches', string="Batch")
    faculty_file = fields.Binary(string="Faculty File", required=True)
    faculty_file_name = fields.Char(string="File Name")
    faculty_image = fields.Binary(string="Faculty Image")

    def action_upload_faculty(self):
        file_content = base64.b64decode(self.faculty_file)
        print(file_content)
        workbook = xlrd.open_workbook(file_contents=file_content)
        worksheet = workbook.sheet_by_index(0)

        if not self.faculty_file:
            raise ValidationError(_("Please select a file to upload."))

        try:
            for row_num in range(1, worksheet.nrows):  # Assuming first row contains headers
                print(f"Processing row {row_num}")
                row = worksheet.row_values(row_num)
                try:
                    faculty_image = row[0]
                except Exception as e:
                    print(f"Error processing faculty image in row {row_num}: {str(e)}")
                    faculty_image = False
                course_name = row[1]
                faculty_name = row[2]
                date_value = xlrd.xldate_as_datetime(row[3], workbook.datemode)
                date_string = date_value.strftime('%d-%b-%y')
                dob = date_value
                designation = row[4]
                qualification = row[5]
                contract_terms = row[6]
                # courses_taught = [self.env['course.master'].search([('name', '=', course)]).id for course in row[7].split(',')]

                # Create or update faculty record
                faculty = self.env['institute.faculty'].search([('faculty_name', '=', faculty_name)])
                if faculty:
                    try:
                        faculty.write({
                            'gp_batches_id': self.batch_id.id if self.batch_id else False,
                            'faculty_photo': faculty_image,
                            'faculty_name': faculty_name,
                            'course_name': self.env['course.master'].search([('name', '=', course_name)]).id,
                            'dob': dob,
                            'designation': designation,
                            'qualification': qualification,
                            'contract_terms': contract_terms,
                            # 'courses_taught': [(6, 0, courses_taught)],
                        })
                    except Exception as e:
                        print(f"Error updating faculty record for {faculty_name} in row {row_num}: {str(e)}")
                        continue
                else:
                    try:
                        self.env['institute.faculty'].create({
                            'faculty_photo': faculty_image,
                            'faculty_name': faculty_name,
                            'course_name': self.env['course.master'].search([('name', '=', course_name)]).id,
                            'dob': dob,
                            'designation': designation,
                            'qualification': qualification,
                            'contract_terms': contract_terms,
                            # 'courses_taught': [(6, 0, courses_taught)],
                            'gp_batches_id': self.batch_id.id if self.batch_id else False,
                        })
                    except Exception as e:
                        print(f"Error creating faculty record for {faculty_name} in row {row_num}: {str(e)}")
                        continue

            return {'type': 'ir.actions.act_window_close'}
        except xlrd.XLRDError as e:
            raise ValidationError(_("Error reading the Excel file: %s") % str(e))
        except Exception as e:
            raise ValidationError(_("Error uploading faculty file: %s") % str(e))

class InstituteCcmcBatches(models.Model):
    _name = "institute.ccmc.batches"
    _rec_name = "ccmc_batch_name"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'CCMC Batches'
    
    institute_id = fields.Many2one("bes.institute",string="Institute",required=True)
    code = fields.Char(string="Code",related='institute_id.code', store=True ,tracking=True)
    exam_region = fields.Char("Exam Region",related ='institute_id.exam_center.name',store=True,tracking=True)
    ccmc_batch_name = fields.Char("Batch Name",required=True)
    dgs_batch = fields.Many2one("dgs.batches",string="Exam Batch",required=False)
    ccmc_faculty_name = fields.Char("Faculty name")
    candidate_user_invoice_criteria = fields.Boolean("Invoice Criteria",compute="compute_candidate_user_invoice_criteria")
    all_invoice_generated = fields.Boolean("All Invoice Generated",compute="compute_all_invoice_generated")
    ccmc_candidate_count = fields.Integer("Candidate Count",compute="ccmc_compute_candidate_count")
    candidate_count = fields.Integer("Candidate Count",compute="_compute_candidate_count")
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
        ('1-ongoing', 'Invoice Not Generated'),
        ('2-indos_pending', 'Confirmed'),
        ('3-pending_invoice', 'Invoice Pending'),
        ('4-invoiced', 'Invoice Generated'),
        ('5-exam_scheduled', 'Exam Scheduled'),
        ('6-done', 'Batch Closed')        
    ], string='State', default='1-ongoing',tracking=True)
    
    payment_state = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid')     
    ], string='Payment State', default='not_paid',compute="_compute_payment_state",)
    
    active = fields.Boolean(string="Active",default=True)

    admit_card_status = fields.Selection([
        ('pending', 'Pending'),
        ('issued', 'Issued')
    ],default="pending", string='Admit Card Status')
    
    
    dgs_approved_capacity = fields.Integer(string="DGS Approved Capacity")
    dgs_approval_state = fields.Boolean(string="DGS Approval Status")
    dgs_document = fields.Binary(string="DGS Document")
    document_name = fields.Char("Name of Document")
    document_file = fields.Binary(string='Upload Document')
    
    cookery_bakery_qb =fields.Many2one("survey.survey",string="Cookery Bakery Question Bank")
    
    admit_card_alloted = fields.Integer("No. of Candidate Eligible for Admit Card",compute="_compute_admit_card_count")

    all_candidates_have_indos = fields.Boolean(string="All Candidates Have INDOS", compute="_compute_all_candidates_have_indos")
    candidate_ids = fields.Many2many('gp.candidate', string="Candidates")

    def close_batch(self):
        for rec in self:
            rec.ccmc_state = '6-done'
    
    def open_batch(self):
        for rec in self:
            rec.ccmc_state = '5-exam_scheduled'

    def _compute_all_candidates_have_indos(self):
        for record in self:
            # import wdb; wdb.set_trace()
            candidate_count = self.env["ccmc.candidate"].search_count([('institute_batch_id', '=', record.id),('withdrawn_state','!=','yes')])

            if candidate_count > 0:
                candidates_with_indos = self.env["ccmc.candidate"].search_count([('institute_batch_id', '=', record.id), ('indos_no', '!=', ''),('withdrawn_state','!=','yes')])
                if candidate_count == candidates_with_indos:
                    record.all_candidates_have_indos = True
                else:
                    record.all_candidates_have_indos = False
            else:
                record.all_candidates_have_indos = False

    def update_dgs_capacity(self):
        """
        Enforces capacity rules for DGS batches based on the associated course's batcher_per_year.
        """
        for batch in self:
            year = batch.ccmc_from_date.year if batch.ccmc_from_date else None
            if not year:
                continue

            # Fetch the total intake capacity and batcher_per_year from the associated course
            course_record = self.env['institute.courses'].search([
                ('institute_id', '=', batch.institute_id.id),
                ('course.course_code', '=', 'CCMC')
            ], limit=1)

            if not course_record:
                raise ValidationError("No course record found for the selected institute and course.")

            if course_record.batcher_per_year == 1:
                # Allocate full capacity if there's only one batch per year
                batch.dgs_approved_capacity = course_record.total
                batch.dgs_approval_state = True

            elif course_record.batcher_per_year == 2:
                # Divide capacity equally between two batches
                half_capacity = course_record.total // 2
                batch.dgs_approved_capacity = half_capacity
                batch.dgs_approval_state = True

            else:
                # Validate total capacity across multiple batches
                jan_to_jun_batches = self.env['institute.ccmc.batches'].search([
                    ('institute_id', '=', batch.institute_id.id),
                    ('ccmc_from_date', '>=', f'{year}-01-01'),
                    ('ccmc_to_date', '<=', f'{year}-06-30')
                ])
                jul_to_dec_batches = self.env['institute.ccmc.batches'].search([
                    ('institute_id', '=', batch.institute_id.id),
                    ('ccmc_from_date', '>=', f'{year}-07-01'),
                    ('ccmc_to_date', '<=', f'{year}-12-31')
                ])

                # Calculate total approved capacity
                jan_to_jun_capacity = sum(jan_to_jun_batches.mapped('dgs_approved_capacity'))
                jul_to_dec_capacity = sum(jul_to_dec_batches.mapped('dgs_approved_capacity'))
                total_capacity = jan_to_jun_capacity + jul_to_dec_capacity

                if total_capacity > course_record.total:
                    raise ValidationError(
                        f"DGS Capacity exceeded for the year {year}. "
                        f"Total approved capacity ({total_capacity}) exceeds the intake capacity "
                        f"({course_record.total})."
                    )




    @api.model
    def create(self, values):
        record = super(InstituteCcmcBatches, self).create(values)
        course_id = self.env["course.master"].sudo().search([('course_code','=','CCMC')]).id
        record.write({'ccmc_course': course_id})
        record.update_dgs_capacity()  # Validate after creation
        return record

        
    @api.depends("admit_card_alloted")
    def _compute_admit_card_count(self):
        for rec in self:
            candidate_count = self.env["ccmc.candidate"].search_count([('institute_batch_id','=', rec.id),('stcw_criteria','=','passed'),('ship_visit_criteria','=','passed'),('attendance_criteria','=','passed')])
            # import wdb; wdb.set_trace()
            # for i in candidate:
                # candidate_count = self.env["gp.exam.schedule"].search_count([('gp_candidate','=',i.id),('stcw_criteria','=','passed'),('ship_visit_criteria','=','passed'),('attendance_criteria','=','passed')])
    
            self.write({"admit_card_alloted":candidate_count})


    def issue_admit_card(self):
        candidates = self.env["ccmc.candidate"].search([('institute_batch_id','=',self.id)])
        for candidate in candidates:
            ccmc_exam = self.env["ccmc.exam.schedule"].search([('ccmc_candidate', '=', candidate.id)])
            ccmc_exam.sudo().write({"hold_admit_card":False})
        self.write({"admit_card_status":"issued"})
    
    
    @api.depends("candidate_user_invoice_criteria")
    def compute_candidate_user_invoice_criteria(self):
        for record in self:
            # import wdb; wdb.set_trace()
            candidate_count = self.env["ccmc.candidate"].search_count([('institute_batch_id','=', record.id)])

            if candidate_count > 0 :
            
                ccmc_batch_id = record.id
                candidate_with_correct_data = self.env["ccmc.candidate"].search_count([('institute_batch_id','=', ccmc_batch_id),('candidate_user_invoice_criteria','=',True)])
                
                if candidate_count == candidate_with_correct_data:
                    record.candidate_user_invoice_criteria = True
                else:
                    record.candidate_user_invoice_criteria = False
            else :
                record.candidate_user_invoice_criteria = False
    
    @api.depends("all_invoice_generated")
    def compute_all_invoice_generated(self):
        for record in self:
             candidate_count = self.env["ccmc.candidate"].search_count([('institute_batch_id','=', record.id)])

             if candidate_count > 0:
               
               candidate_with_generated_invoice = self.env['ccmc.candidate'].sudo().search_count([('institute_batch_id','=',record.id),('fees_paid','=','yes'),('invoice_generated','=',True)]) 
               
               if candidate_with_generated_invoice == candidate_count:
                    record.all_invoice_generated = True
               else: 
                   record.all_invoice_generated = False
                 
             else:
                 record.all_invoice_generated = False
    
    @api.depends("candidate_count")
    def _compute_candidate_count(self):
        for rec in self:
            candidate_count = self.env["ccmc.candidate"].search_count([('institute_batch_id','=', rec.id)])
            rec.candidate_count = candidate_count
    
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
        
        
    @api.model
    def action_delete_batches(self, batch_ids=None):
        if batch_ids is None or not batch_ids:
            raise ValidationError("No batches selected for deletion.")

        # Retrieve records to be deleted based on provided IDs
        batches_to_delete = self.browse(batch_ids)
        
        if not batches_to_delete:
            raise ValidationError("No valid batches found to delete.")
        
        # Construct message with batch names and corresponding institute names
        batch_info = []
        for batch in batches_to_delete:
            institute_name = batch.institute_id.name or 'Unknown Institute'
            batch_info.append(f"(Institute: {institute_name}) - {batch.ccmc_batch_name} \n")
        
        batch_info_str = ', '.join(batch_info)
        
        # Pass the message and batch IDs to the wizard
        return {
            'name': 'Batch Delete Confirmation',
            'type': 'ir.actions.act_window',
            'res_model': 'batch.delete.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {
                'default_message': f"Batches to be deleted:\n{batch_info_str}",
                'batch_ids': batch_ids,
            }
        }
          
    
    def create_invoice_ccmc(self):
        
        # import wdb; wdb.set_trace()

        ccmc_partner_id = self.institute_id.user_id.partner_id.id
        product_id_ccmc = self.ccmc_course.exam_fees.id
        product_price = self.ccmc_course.exam_fees.lst_price
        qty = self.ccmc_candidate_count
        line_items = [(0, 0, {
        'product_id': product_id_ccmc,
        'price_unit':product_price,
        'quantity':qty
        })]
        
        invoice_vals = {
            'partner_id': ccmc_partner_id,  # Replace with the partner ID for the customer
            'move_type': 'out_invoice',
            'invoice_line_ids':line_items,
            'ccmc_batch_ok':True,
            'ccmc_batch':self.id
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
    
    # def confirm_batch_ccmc(self):
        
    #     self.write({"ccmc_state":"2-indos_pending"})
    # Added method to generate sequence
    def generate_sequence(self):
        # import wdb; wdb.set_trace()
        batch_year = self.ccmc_to_date.strftime('%y')
        batch_month = self.ccmc_to_date.strftime('%m')
        half = '06' if int(batch_month) <= 6 else '12'
        institute_code = self.institute_id.code # Replace this with your actual institute code
        
        # Count the number of candidates in the batch
        # candidate_count = self.env['gp.candidate'].sudo().search_count([('institute_batch_id','=',self.id),('user_id','=',True)])
        candidate_count = self.env['ccmc.candidate'].sudo().search_count([('institute_batch_id','=',self.id),('user_id','!=',None)])

        # import wdb; wdb.set_trace()
        # Generate the sequence number starting from '001'
        candidate_count = candidate_count+1
        
        next_sequence_number = str(candidate_count).zfill(3)
        

        sequence = f'C{batch_year}{half}{institute_code}{next_sequence_number}'
        return sequence


    def confirm_batch_ccmc(self,candidate_ids):

        print(self,"selfffffffffffffffffffffffffffffffffffffffffffffffffffff")

        candidate_list_no_indos = []
        candidate_missing_data_id = []
        
        candidates = self.env['ccmc.candidate'].sudo().browse(candidate_ids)

        
        
        for candidate in candidates:
            if not candidate.indos_no or not candidate.candidate_image or not candidate.candidate_signature:
                
                missing_data = ""
                if not candidate.indos_no:
                    missing_data += "Indos No,"
                
                if not candidate.candidate_image:
                    missing_data += "Candidate Image,"
                
                if not candidate.candidate_signature:
                    missing_data += "Candidate Signature,"
                
                missing_data = missing_data.rstrip(',')
                
                candidate_data = {"candidate_name": candidate.name, "candidate_mobile": candidate.mobile, "missing_data": missing_data}
                candidate_list_no_indos.append(candidate_data)
                candidate_missing_data_id.append(candidate.id)

        if len(candidate_list_no_indos) > 0:


            template_id = self.env.ref('bes.ccmc_indos_check_mail').id
            official_institute_mail_id = self.institute_id.user_id.partner_id.ids


            ctx = {
                'default_res_id': self.id,
                'default_template_id': template_id,
                'default_use_template': bool(template_id),
                'default_composition_mode': 'comment',
                'default_partner_ids': official_institute_mail_id,
                "default_candidate_lists": candidate_list_no_indos
            }

            mail_template = self.env.ref('bes.ccmc_indos_check_mail')
            mail_template.with_context(ctx).send_mail(self.id, force_send=True)

        ccmc_candidates = candidates.ids
            
        set1 = set(ccmc_candidates)
        set2 = set(candidate_missing_data_id)    
            
        array1_without_common = list(set1 - set2)
            
        ccmc_candidates = self.env['ccmc.candidate'].sudo().browse(array1_without_common)
        group_xml_ids = [
            'bes.group_ccmc_candidates',
            'base.group_portal'
        ]
            
        group_ids = [self.env.ref(xml_id).id for xml_id in group_xml_ids]

        for ccmc_candidate in ccmc_candidates:
            user_values = {
                'name': ccmc_candidate.name,
                'login': ccmc_candidate.indos_no.strip(), # You can set the login as the same as the user name
                'password': str(ccmc_candidate.indos_no.strip()) + "1",  # Generate a random password
                'sel_groups_1_9_10': 9,
                'groups_id': [(4, group_id, 0) for group_id in group_ids]
            }
            
            try:
                portal_user = self.env['res.users'].sudo().create(user_values)
            except:
                print("Duplicate")
                print(user_values)


            candidate_count = self.env['ccmc.candidate'].sudo().search_count([('institute_batch_id','=',self.id)])
            sequence = self.generate_sequence()
            ccmc_candidate.write({'user_id': portal_user.id,
                                'candidate_code': sequence  # Assign the generated sequence to the partner
            
                                })
            # You may need to adjust the following fields based on your actual field names in ccmc_candidate
            ccmc_candidate_tag = self.env.ref('bes.candidates_tags').id

            portal_user.partner_id.write({
                'email': ccmc_candidate.email,
                'phone': ccmc_candidate.phone,
                'mobile': ccmc_candidate.mobile,
                'street': ccmc_candidate.street,
                'street2': ccmc_candidate.street2,
                'city': ccmc_candidate.city,
                'zip': ccmc_candidate.zip,
                'state_id': ccmc_candidate.state_id.id,
                'category_id': [ccmc_candidate_tag]
            })

        
        # Update the state field based on your actual field name in ccmc_batches
        self.write({"ccmc_state": "2-indos_pending"})
    
    
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
        # 'res_model': 'batches.faculty',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        'context': {
            # 'default_ccmc_batches_id': self.id
            'default_ccmc_batches_id': self.id,
            'default_gp_or_ccmc_batch': 'ccmc'     
            }
        } 

    def open_ccmc_ship_visit(self):

        return {
            'name': 'CCMC Ship Visit',
            'domain': [('ccmc_ship_batch_ids', '=', self.id)],
            'view_type': 'form',
            'res_model': 'ccmc.batches.ship.visit',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'context': {
                'default_ccmc_ship_batch_ids':self.id ,
                'default_ccmc_batch': 'ccmc',  # Ensure this is correctly passed as default
                'default_dgs_batch': self.dgs_batch.id,
                'default_institute_id': self.institute_id.id,
            }
        }

    def open_register_for_exam_wizard(self):
        view_id = self.env.ref('bes.batches_ccmc_register_exam_wizard').id
        
        return {
            'name': 'Register For Exam',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'batches.ccmc.register.exam.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_institute_id': self.institute_id.id,
                'default_batch_id': self.id
            }
        }

    
        
    

        
        
        
        
class BatchesRegisterExamWizard(models.TransientModel):
    _name = 'batches.gp.register.exam.wizard'
    _description = 'Register Exam'

    institute_id = fields.Many2one("bes.institute",string="Institute",required=True)
    batch_id = fields.Many2one("institute.gp.batches",string="Batches",required=True)
    dgs_batch = fields.Many2one("dgs.batches",string="Exam Batch",required=True)
    mek_survey_qb = fields.Many2one("survey.survey",string="Mek Question Bank")
    gsk_survey_qb = fields.Many2one("survey.survey",string="Gsk Question Bank")
    
    
    
    def register(self,batch_id,candidates_ids):
        candidates = self.env["gp.candidate"].sudo().browse(candidates_ids)
        # mek_survey_qb = self.env['survey.survey'].sudo().search([('title','=','MEK ONLINE EXIT EXAMINATION')])
        # gsk_survey_qb = self.env['survey.survey'].sudo().search([('title','=','GSK ONLINE EXIT EXAMINATION')])
        gsk_survey_qb = self.env["course.master.subject"].sudo().search([('name','=','GSK')]).qb_online
        mek_survey_qb = self.env["course.master.subject"].sudo().search([('name','=','MEK')]).qb_online
        batch = self.env['institute.gp.batches'].sudo().search([('id','=',batch_id)])
        for candidate in candidates:
            exam_id = self.env['ir.sequence'].next_by_code("gp.exam.sequence")
            gp_exam_schedule = self.env["gp.exam.schedule"].create({
                'gp_candidate':candidate.id ,
                'exam_id':exam_id, 
                'dgs_batch': batch.dgs_batch.id , 
                'institute_name':batch.institute_id.id ,
                'hold_admit_card':True,
                'registered_institute':batch.institute_id.id,
                'exam_region':batch.institute_id.exam_center.id,
                'attempt_number':1,
                })
            mek_practical = self.env["gp.mek.practical.line"].create({"exam_id":gp_exam_schedule.id,'mek_parent':candidate.id,'institute_id': batch.institute_id.id})
            mek_oral = self.env["gp.mek.oral.line"].create({"exam_id":gp_exam_schedule.id,'mek_oral_parent':candidate.id,'institute_id': batch.institute_id.id})
            gsk_practical = self.env["gp.gsk.practical.line"].create({"exam_id":gp_exam_schedule.id,'gsk_practical_parent':candidate.id,'institute_id': batch.institute_id.id})
            gsk_oral = self.env["gp.gsk.oral.line"].create({"exam_id":gp_exam_schedule.id,'gsk_oral_parent':candidate.id,'institute_id': batch.institute_id.id})
            gp_exam_schedule.write({
                "mek_oral":mek_oral.id,
                "mek_prac":mek_practical.id,
                "gsk_oral":gsk_oral.id,
                "gsk_prac":gsk_practical.id,
                "attempting_gsk_oral_prac":True,
                "attempting_mek_oral_prac":True,
                "attempting_mek_online":True,
                "attempting_gsk_online":True})
            
            candidate.write({'batch_exam_registered':True})
            mek_predefined_questions = mek_survey_qb._prepare_user_input_predefined_questions()
            gsk_predefined_questions = gsk_survey_qb._prepare_user_input_predefined_questions()
            # import wdb;wdb.set_trace()

            mek_survey_qb_input = mek_survey_qb._create_answer(user=candidate.user_id)
            # mek_survey_qb_input.write({'predefined_question_ids':mek_predefined_questions.ids})
            
            gsk_survey_qb_input = gsk_survey_qb._create_answer(user=candidate.user_id)
            # gsk_survey_qb_input.write({'predefined_question_ids':gsk_predefined_questions.ids})            
            mek_survey_qb_input.write({
                                    'gp_candidate':candidate.id,
                                    'gp_exam':gp_exam_schedule.id,
                                    'dgs_batch':batch.dgs_batch.id,
                                    'institute_id':batch.institute_id.id,
                                    'ip_address':gp_exam_schedule.ip_address,
                                    'exam_date': gp_exam_schedule.exam_date,
                                    'is_gp':True})
            
            gsk_survey_qb_input.write({
                                    'gp_candidate':candidate.id,
                                    'gp_exam':gp_exam_schedule.id,
                                    'dgs_batch':batch.dgs_batch.id,
                                    'institute_id':batch.institute_id.id,
                                    'ip_address':gp_exam_schedule.ip_address,
                                    'exam_date': gp_exam_schedule.exam_date,
                                    'is_gp':True})
            candidate.write({'batch_exam_registered':True})
            gp_exam_schedule.write({
                "gsk_online":gsk_survey_qb_input.id,
                "mek_online":mek_survey_qb_input.id})
        
        self.batch_id.write({"state":'5-exam_scheduled',"mek_survey_qb":mek_survey_qb_input,"gsk_survey_qb":gsk_survey_qb_input})

class CCMCBatchesRegisterExamWizard(models.TransientModel):
    _name = 'batches.ccmc.register.exam.wizard'
    _description = 'Register Exam'

    institute_id = fields.Many2one("bes.institute",string="Institute",required=True)
    batch_id = fields.Many2one("institute.ccmc.batches",string="Batches",required=True)
    cookery_bakery_qb = fields.Many2one("survey.survey",string="Cookery Bakery Question Bank Template")
    dgs_batch = fields.Many2one("dgs.batches",string="Exam Batch",required=False)
    
    
    def register(self,batch_id,candidates_ids):
        candidates = self.env["ccmc.candidate"].sudo().browse(candidates_ids)
        # print(candidates)
        # cookery_bakery_qb = self.env['survey.survey'].sudo().search([('title','=','CCMC ONLINE EXIT EXAMINATION')])
        cookery_bakery_qb = self.env["course.master.subject"].sudo().search([('name','=','CCMC')]).qb_online
        # ccmc_qb_input = self.env["course.master.subject"].sudo().search([('name','=','CCMC')]).qb_online
        batch = self.env['institute.ccmc.batches'].sudo().search([('id','=',batch_id)])
        # import wdb; wdb.set_trace(); 
        for candidate in candidates:
            exam_id = self.env['ir.sequence'].next_by_code("ccmc.exam.schedule")            
            ccmc_exam_schedule = self.env["ccmc.exam.schedule"].create({
                'ccmc_candidate':candidate.id, 
                'exam_id':exam_id, 
                'dgs_batch': batch.dgs_batch.id ,
                'hold_admit_card':True , 
                'institute_name':batch.institute_id.id ,
                'registered_institute':batch.institute_id.id,
                'exam_region':batch.institute_id.exam_center.id,
                'attempt_number':1,
                })

            cookery_bakery = self.env["ccmc.cookery.bakery.line"].create({"exam_id":ccmc_exam_schedule.id,'cookery_parent':candidate.id,'institute_id': batch.institute_id.id})
            ccmc_oral = self.env["ccmc.oral.line"].create({"exam_id":ccmc_exam_schedule.id,'ccmc_oral_parent':candidate.id,'institute_id': batch.institute_id.id})
            ccmc_gsk_oral = self.env["ccmc.gsk.oral.line"].create({"exam_id":ccmc_exam_schedule.id,'ccmc_oral_parent':candidate.id,'institute_id': batch.institute_id.id})
            
            ccmc_exam_schedule.write({
                'cookery_bakery':cookery_bakery.id ,
                'ccmc_gsk_oral':ccmc_gsk_oral.id, 
                'ccmc_oral':ccmc_oral.id,
                'attempting_cookery':True,
                'attempting_oral':True,
                'attempting_online':True})
            
            # cookery_bakery_qb.generate_token()
            cookery_bakery_qb_input = cookery_bakery_qb._create_answer(user=candidate.user_id)
            # ccmc_qb_input = ccmc_qb_input._create_answer(user=ccmc_exam.ccmc_candidate.user_id)
            
            # import wdb;wdb.set_trace(

            cookery_bakery_qb_input.write({
                                    'ccmc_candidate':candidate.id,
                                    'ccmc_exam':ccmc_exam_schedule.id,
                                    'dgs_batch':batch.dgs_batch.id,
                                    'institute_id':batch.institute_id.id,
                                    'ip_address':ccmc_exam_schedule.ip_address,
                                    'exam_date': ccmc_exam_schedule.exam_date,
                                    'is_ccmc':True
                                    })
            
            ccmc_exam_schedule.write({"ccmc_online":cookery_bakery_qb_input.id,
                                    # "ip_address":ccmc_exam_schedule.ip_address
                                })
            candidate.write({'batch_exam_registered':True})
        batch.write({"ccmc_state":'5-exam_scheduled',"cookery_bakery_qb":cookery_bakery_qb.id})

class BatchFaculty(models.Model):
    _name = 'batches.faculty'
    _description = 'Faculty Batches'
    
    ccmc_faculty = fields.Many2one('institute.ccmc.batches',string="CCMC Faculty")
    gp_faculty = fields.Many2one('institute.gp.batches',string="gp Faculty")

   
