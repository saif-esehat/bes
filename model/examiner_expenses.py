from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
from datetime import datetime

class BatchExpenses(models.Model):
    _name = 'exam.batch.expenses'
    _rec_name = 'dgs_batch'
  
    
    dgs_batch = fields.Many2one("dgs.batches",string="Exam Batch",tracking=True)
    
    
    total_expense = fields.Integer("Total Batch Expense",compute="_compute_total_expense")
    
    @api.depends('dgs_batch')
    def _compute_total_expense(self):
        for record in self:
            expenses = self.env["examiner.expenses"].sudo().search([('dgs_batch','=',record.dgs_batch.id)])
            expense_total = 0
            for expense in expenses:
                expense_total = expense.total + expense_total
            
            record.total_expense = expense_total  
            # record.total_expense = total
    
    
    _sql_constraints = [
        ('dgs_batch_unique', 'unique(dgs_batch)', 'The Exam Batch must be unique!')
    ]
    
    
    def open_institute_expense(self):
        
        return {
        'name': 'Institute Wise Expense',
        'domain': [('expense_batch', '=', self.id)],
        'view_type': 'form',
        'res_model': 'institute.exam.expenses',
        # 'res_model': 'batches.faculty',
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        } 

    
    def open_expense_record(self):
        
        
        return {
        'name': 'Expenses',
        'domain': [('expense_batch', '=', self.id)],
        'view_type': 'form',
        'res_model': 'examiner.expenses',
        # 'res_model': 'batches.faculty',
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        } 

class InstituteExpenseReport(models.Model):
    _name = 'institute.exam.expenses'
    _description = 'Expenses'
    _rec_name = 'dgs_batch'
    
    
    expense_batch = fields.Many2one("exam.batch.expenses",string="Exam Batch")
    dgs_batch = fields.Many2one("dgs.batches",string="Exam Batch",tracking=True)
    institute = fields.Many2one("bes.institute",string="Institute")
    
    practical_oral_expenses = fields.Integer("Practical/Oral Expenses",compute="_compute_practical_expense")
    online_expenses = fields.Integer("Online Expenses",compute="_compute_online_expense")
    outstation_expenses = fields.Integer("Outstation Expenses",compute="_compute_outstation_expense")
    team_lead_expense = fields.Integer("Team Lead Expense",compute="_compute_tl_expense")
    non_mariner_expense = fields.Integer("Non Mariner Expense",compute="_compute_nm_expense")
    total = fields.Integer("Total Expense",compute="_compute_total")
    
    @api.depends('dgs_batch','institute')
    def _compute_total(self):
        for record in self:
            record.total = record.practical_oral_expenses + record.online_expenses + record.team_lead_expense + record.non_mariner_expense
    
    @api.depends('dgs_batch','institute')
    def _compute_nm_expense(self):
        for record in self:
            data = self.env["examiner.expense.non.mariner"].sudo().search([('dgs_batch','=',record.dgs_batch.id),('institute','=',record.institute.id)])
            record.non_mariner_expense= sum(data.mapped('price'))        
    
    @api.depends('dgs_batch','institute')
    def _compute_outstation_expense(self):
        for record in self:
            data = self.env["examiner.outstation.expense"].sudo().search([('dgs_batch','=',record.dgs_batch.id),('institute','=',record.institute.id)])
            record.outstation_expenses = sum(data.mapped('price'))
    
    
    
    @api.depends('dgs_batch','institute')
    def _compute_practical_expense(self):
        for record in self:
            # import wdb;wdb.set_trace()
            data = self.env["exam.assignment.expense"].sudo().search([('dgs_batch','=',record.dgs_batch.id),('institute','=',record.institute.id)])
            record.practical_oral_expenses= sum(data.mapped('total'))
    
    @api.depends('dgs_batch','institute')
    def _compute_online_expense(self):
        for record in self:
            # import wdb;wdb.set_trace()
            data = self.env["exam.assignment.online.expense"].sudo().search([('dgs_batch','=',record.dgs_batch.id),('institute','=',record.institute.id)])
            record.online_expenses = sum(data.mapped('price'))
            # record.
    
    @api.depends('dgs_batch','institute')
    def _compute_tl_expense(self):
        for record in self:
            # import wdb;wdb.set_trace()
            data = self.env["institute.team.lead"].sudo().search([('dgs_batch','=',record.dgs_batch.id),('institute','=',record.institute.id)])
            record.team_lead_expense = sum(data.mapped('price'))
    
    # assignments = fields.Many2one('exam.type.oral.practical.examiners', string="Assignments")
    # exam_type = fields.Selection([
    #     ('practical_oral', 'Practical/Oral'),
    #     ('online', 'Online'),
    #     ('practical_oral_cookery_bakery', 'Practical (Cookery Bakery)'),
    #     ('ccmc_oral', 'CCMC Oral'),3
    #     ('gsk_oral', 'CCMC(GSK Oral)'),    
    # ], string='Exam Type',related='assignments.exam_type')

    # institute = fields.Many2one("bes.institute",string="Institute",related='assignments.institute_id')
    # candidates_count = fields.Integer("Candidates Count",related='assignments.candidates_count')
    


class ExamNonMariner(models.Model):
    _name = 'examiner.expense.non.mariner'
    _description = 'Expense Non Mariner'

    examiner_expenses_id = fields.Many2one('examiner.expenses', string="Examiner Expenses")
    dgs_batch = fields.Many2one("dgs.batches",string="Exam Batch",tracking=True)
    exam_date = fields.Date("Exam Date")
    non_mariner_assignment = fields.Many2one("exam.type.non.mariner",string="Non Mariner Assignment",tracking=True)
    institute = fields.Many2one("bes.institute",string="Institute",related='non_mariner_assignment.institute',store=True)
    price = fields.Integer("Price")
    
    

class ExaminerExpenses(models.Model):
    _name = 'examiner.expenses'
    _description = 'Examiner Expenses'
    _rec_name = 'examiner_id'

    expense_batch = fields.Many2one("exam.batch.expenses",string="Exam Batch",tracking=True)
    dgs_batch = fields.Many2one("dgs.batches",string="Exam Batch",tracking=True)
    examiner_id = fields.Many2one('bes.examiner', string="Examiners")
    designation = fields.Selection([
        ('non-mariner', 'Non Mariner'),
        ('master', 'Master Mariner'),
        ('chief', 'Chief Engineer'),
        ('catering','Catering Officer')
    ], string='Designation',related='examiner_id.designation',store=True,tracking=True)
    team_lead = fields.Boolean(string="Team Lead")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('ec_approval', 'EC Approval'),
        ('ceo_approval', 'CEO Approval'),
        ('approved', 'Approved')
    ], string='State', default='draft')
    
    
    overall_expense_ids = fields.One2many('examiner.overall.expenses', 'examiner_expenses_id', string="Overall Expenses")

    assignment_expense_ids = fields.One2many('exam.assignment.expense', 'examiner_expenses_id', string="Practical Oral Expenses")
    
    online_assignment_expense = fields.One2many('exam.assignment.online.expense', 'examiner_expenses_id', string="Online Expenses")

    team_lead_expense = fields.One2many('institute.team.lead', 'examiner_expenses_id', string="Online Expenses")
    
    misc_expense_ids = fields.One2many('exam.misc.expense', 'examiner_expenses_id', string="Miscellaneous Expenses")
    
    non_mariner_expense = fields.One2many('examiner.expense.non.mariner', 'examiner_expenses_id', string="Non Mariner Expenses")

    outstation_travel_expenses = fields.One2many('examiner.outstation.expense', 'examiner_expenses_id', string="Outstation Expenses")

    total = fields.Integer("Total Expense",compute='_compute_total_expense',store=True)
    
    practical_oral_total = fields.Integer("Practical/Oral Expense",compute="_compute_total")
    
    online_total = fields.Integer("Online Expense",compute="_compute_total")
    
    team_lead_total = fields.Integer("Team Lead Expense",compute="_compute_total")
    
    outstation_total = fields.Integer("Outstation Expense",compute="_compute_total")
    
    misc_total = fields.Integer("Misc. Expense",compute="_compute_total")
    
    @api.depends('assignment_expense_ids.total','online_assignment_expense.price','team_lead_expense.price','misc_expense_ids.price')
    def _compute_total(self):
        for record in self:
            if record.assignment_expense_ids:
                record.practical_oral_total = sum(record.assignment_expense_ids.mapped('total'))
            else:
                record.practical_oral_total = 0
            
            if record.online_assignment_expense:
                record.online_total = sum(record.online_assignment_expense.mapped('price'))
            else:
                record.online_total = 0
                
            if record.team_lead_expense:
                record.team_lead_total = sum(record.team_lead_expense.mapped('price'))
            else:
                record.team_lead_total = 0
            
            
            if record.outstation_travel_expenses:
                record.outstation_total = sum(record.outstation_travel_expenses.mapped('price'))
            else:
                record.outstation_total = 0
                
            if record.misc_expense_ids:
                record.misc_total = sum(record.misc_expense_ids.mapped('price'))
            else:
                record.misc_total = 0
     
    
    @api.depends('assignment_expense_ids.total', 'online_assignment_expense.price', 'team_lead_expense.price', 'misc_expense_ids.price','outstation_travel_expenses','non_mariner_expense.price')
    def _compute_total_expense(self):
        for record in self:
            total_assignment = sum(record.assignment_expense_ids.mapped('total'))
            total_online = sum(record.online_assignment_expense.mapped('price'))
            total_team_lead = sum(record.team_lead_expense.mapped('price'))
            total_non_mariner = sum(record.non_mariner_expense.mapped('price'))
            total_outstation = sum(record.outstation_travel_expenses.mapped('price'))
            total_misc = sum(record.misc_expense_ids.mapped('price'))
            record.total = total_assignment + total_online + total_team_lead + total_misc + total_non_mariner + total_outstation
    
    
    def action_set_ec_approval(self):
        for record in self:
            record.state = 'ec_approval'

    def action_set_ceo_approval(self):
        for record in self:
            record.state = 'ceo_approval'

    def action_set_approved(self):
        for record in self:
            record.state = 'approved'
            
    def cancel(self):
        for record in self:
            record.state = 'draft'


class ExaminerOutstationExpense(models.Model):
    _name = 'examiner.outstation.expense'
    _description = 'Examiner Outstation Expenses'

    examiner_expenses_id = fields.Many2one('examiner.expenses', string="Examiner Expenses")
    dgs_batch = fields.Many2one('dgs.batches',related="examiner_expenses_id.dgs_batch",store=True)
    assignment = fields.Many2one('exam.type.oral.practical.examiners', string="Assignment")
    institute = fields.Many2one('bes.institute',related="assignment.institute_id", string="Institute",store=True)
    exam_date = fields.Date("Exam Date")
    price = fields.Integer("Cost")
    
    


class ExaminerOverAllExpenses(models.Model):
    _name = 'examiner.overall.expenses'
    _description = 'Examiner Expenses'
    
    examiner_expenses_id = fields.Many2one('examiner.expenses', string="Examiner Expenses")
    
    expenses_type = fields.Selection([
        ('practical_oral', 'Practical/Oral'),
        ('online', 'Online'),
        ('team_lead', 'Team Lead'),
        ('misc', 'Miscellaneous')
    ], string='Expense Type')
    
    price = fields.Integer("Price",compute="_compute_total")
    
    @api.depends('examiner_expenses_id.assignment_expense_ids','examiner_expenses_id.online_assignment_expense','examiner_expenses_id.team_lead_expense','examiner_expenses_id.misc_expense_ids')
    def _compute_total(self):
        for record in self:
            if record.expenses_type == 'practical_oral':
                if record.examiner_expenses_id.assignment_expense_ids:
                    record.price = sum(record.examiner_expenses_id.assignment_expense_ids.mapped('total'))
                else:
                    record.price = 0
            elif record.expenses_type == 'online':
                if record.examiner_expenses_id.online_assignment_expense:
                    record.price = sum(record.examiner_expenses_id.online_assignment_expense.mapped('price'))
                else:
                    record.price = 0
            elif record.expenses_type == 'team_lead':
                if record.examiner_expenses_id.team_lead_expense:
                    record.price = sum(record.examiner_expenses_id.team_lead_expense.mapped('price'))
                else:
                    record.price = 0
            
            elif record.expenses_type == 'misc':
                if record.examiner_expenses_id.misc_expense_ids:
                    record.price = sum(record.examiner_expenses_id.misc_expense_ids.mapped('price'))
                else:
                    record.price = 0

    

# class InstituteNo(models.Model):
#     _name = 'institute.team.lead'    
    
    
class InstituteTeamLead(models.Model):
    _name = 'institute.team.lead'
    _description = 'Institute Team Lead'
    

    examiner_expenses_id = fields.Many2one('examiner.expenses', string="Examiner Expenses")
    dgs_batch = fields.Many2one('dgs.batches',related="examiner_expenses_id.dgs_batch",store=True)
    examiner_duty = fields.Many2one('exam.type.oral.practical', string="Examiner Duty")
    institute = fields.Many2one('bes.institute',related="examiner_duty.institute_id", string="Institute",store=True)
    price = fields.Integer("Price")
    
    
            

            
class ExamAssignmentOnlineExpense(models.Model):
    _name = 'exam.assignment.online.expense'
    _description = 'Exam Assignment Online Expense'
    
    examiner_expenses_id = fields.Many2one('examiner.expenses', string="Examiner Expenses")
    dgs_batch = fields.Many2one('dgs.batches',related="examiner_expenses_id.dgs_batch",store=True)
    exam_date = fields.Date("Exam Date")
    assignments_onlines = fields.Many2many('exam.type.oral.practical.examiners',relation="examiner_online_assignment", string="Online Assignments")
    institute = fields.Many2one('bes.institute',string="Institute",compute="_compute_institute",store=True)
    
    @api.depends('assignments_onlines.institute_id')
    def _compute_institute(self):
        for record in self:
            if record.assignments_onlines:
                record.institute = record.assignments_onlines[0].institute_id.id
            else:
                record.institute = None
    
    candidate_count = fields.Integer("Candidates Count")
    price = fields.Integer("Price")
    # total = fields.Float(string="Total", compute='_compute_total', store=True)

    
    # @api.depends('price', 'candidate_count')
    # def _compute_total(self):
    #     for record in self:
    #         record.total = record.candidate_count * record.price

class ExamAssignmentExpense(models.Model):
    _name = 'exam.assignment.expense'
    _description = 'Exam Assignment Expense'

    examiner_id = fields.Many2one('bes.examiner', string="Examiners", related="examiner_expenses_id.examiner_id")
    dgs_batch = fields.Many2one('dgs.batches',related="examiner_expenses_id.dgs_batch",store=True)
    assignment = fields.Many2one('exam.type.oral.practical.examiners', string="Assignment", domain="[('examiner', '=', examiner_id)]")
    institute = fields.Many2one('bes.institute',related="assignment.institute_id", string="Institute",store=True)
    no_of_candidates = fields.Integer(string="No. of Candidates", compute='_compute_no_of_candidates', store=True)
    price_per_unit = fields.Float(string="Price per Unit")
    total = fields.Float(string="Total", compute='_compute_total', store=True)

    @api.depends('no_of_candidates', 'price_per_unit')
    def _compute_total(self):
        for record in self:
            record.total = record.no_of_candidates * record.price_per_unit
    
    
    examiner_expenses_id = fields.Many2one('examiner.expenses', string="Examiner Expenses")

    # Fields to hold values from the assignment record
    assignment_total_candidates = fields.Integer(related='assignment.candidates_count', string="Total Candidates", store=True)
    assignment_absent_candidates = fields.Char(related='assignment.absent_candidates', string="Absent Candidates", store=True)

    @api.depends('assignment', 'assignment_total_candidates', 'assignment_absent_candidates')
    def _compute_no_of_candidates(self):
        for record in self:
            if record.assignment:
                if record.assignment_absent_candidates == 'NA':
                    # If absent candidates are 'NA', consider all candidates as present
                    record.no_of_candidates = record.assignment_total_candidates
                else:
                    # Convert absent candidates to integer and calculate present candidates
                    try:
                        record.no_of_candidates = record.assignment_total_candidates - int(record.assignment_absent_candidates)
                    except ValueError:
                        # In case of any unexpected value, fall back to total candidates
                        record.no_of_candidates = record.assignment_total_candidates
            else:
                record.no_of_candidates = 0

    @api.onchange('examiner_id')
    def _onchange_examiner_id(self):
        if self.examiner_id:
            return {
                'domain': {
                    'assignment': [('examiner', '=', self.examiner_id.id)]
                }
            }
        else:
            return {
                'domain': {
                    'assignment': []
                }
            }


class ExamMiscExpense(models.Model):
    _name = 'exam.misc.expense'
    _description = 'Exam Miscellaneous Expense'

    description = fields.Char(string="Description")
    price = fields.Float(string="Cost")
    docs = fields.Many2many('ir.attachment', string="Documents")
    examiner_expenses_id = fields.Many2one('examiner.expenses', string="Examiner Expenses")
    ex_expense = fields.Many2one('ec.expenses', string="EC Expense")


class ECExpense(models.Model):
    _name = 'ec.expenses'
    _description = 'EC Expenses'

    dgs_batch = fields.Many2one('dgs.batches',store=True)

    exam_region = fields.Many2one('exam.center', 'Exam Region',default=lambda self: self.get_examiner_region(),tracking=True)
    no_of_candidates = fields.Integer(string="No. of Candidates", compute='_compute_no_of_candidates', store=True)

    coordination_fees = fields.Integer(string="Coordination Fees",compute='_compute_coordination_fees', store=True)
    total_candidate_price = fields.Integer(string="Total Candidate Cost", compute='_compute_total_candidate_price', store=True)
    misc_expense_ids = fields.One2many('exam.misc.expense', 'ex_expense', string="Miscellaneous expenses")

    total_expense = fields.Integer(string="Total Expense", compute='_compute_total_expense', store=True)

    practical_oral_total = fields.Integer("Practical/Oral Expense")

    online_assignment_expense = fields.Integer("Online expenses")

    def get_examiner_region(self):
        user_id = self.env.user.id
        region = self.env['exam.center'].sudo().search([('exam_co_ordinator','=',user_id)]).id
        return region


    # @api.depends('dgs_batch','exam_region')
    # def _compute_total(self):
    #     for record in self:
    #         assignment = self.env['exam.type.oral.practical'].sudo().search([('dgs_batch','=',record.dgs_batch.id),('exam_region','=',record.exam_region.id)])



    @api.depends('dgs_batch')
    def _compute_coordination_fees(self):
        for record in self:
            
            if record.dgs_batch.is_march_september:
                product = self.env['product.template'].sudo().search([('default_code','=','repeater_batch_fees')])
                record.coordination_fees = product.list_price
            else:
                product = self.env['product.template'].sudo().search([('default_code','=','fresh_batch_fees')])
                record.coordination_fees = product.list_price

    @api.depends('dgs_batch','exam_region')
    def _compute_no_of_candidates(self):
        for record in self:
            if record.dgs_batch:
                gp_candidates = self.env['gp.exam.schedule'].sudo().search_count([('dgs_batch','=',record.dgs_batch.id),('exam_region','=',record.exam_region.id),('absent_status','=','present')])
                ccmc_candidates = self.env['ccmc.exam.schedule'].sudo().search_count([('dgs_batch','=',record.dgs_batch.id),('exam_region','=',record.exam_region.id),('absent_status','=','present')])
                record.no_of_candidates = gp_candidates + ccmc_candidates


    @api.depends('no_of_candidates')
    def _compute_total_candidate_price(self):
        product = self.env['product.template'].sudo().search([('default_code','=','ec_candidate_cost')])
        for record in self:
            record.total_candidate_price = record.no_of_candidates * product.list_price


    @api.depends('total_candidate_price','misc_expense_ids','practical_oral_total','online_assignment_expense','coordination_fees')
    def _compute_total_expense(self):
        for record in self:
            record.total_expense = record.total_candidate_price + sum(record.misc_expense_ids.mapped('price')) + record.practical_oral_total + record.online_assignment_expense + record.coordination_fees

    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        dgs_batch = vals.get('dgs_batch')
        exam_region = vals.get('exam_region')
        batch = self.env['ec.expenses'].sudo().search([('dgs_batch', '=', dgs_batch),('exam_region', '=', exam_region)])
        if batch:
            raise ValidationError("Batch already exists.")
        else:
            record = super(ECExpense, self).create(vals)
            return record
        # record = super(ECExpense, self).create(vals)
        pass