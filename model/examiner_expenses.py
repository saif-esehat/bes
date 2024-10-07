from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
from datetime import datetime

class BatchExpenses(models.Model):
    _name = 'exam.batch.expenses'
    _rec_name = 'dgs_batch'
  
    
    dgs_batch = fields.Many2one("dgs.batches",string="Exam Batch",tracking=True)
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
    practical_oral_expenses = fields.Integer("Practical/Oral Expenses")
    online_expenses = fields.Integer("Online Expenses")
    
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
    


    
    
    

class ExaminerExpenses(models.Model):
    _name = 'examiner.expenses'
    _description = 'Examiner Expenses'
    _rec_name = 'examiner_id'

    expense_batch = fields.Many2one("exam.batch.expenses",string="Exam Batch",tracking=True)
    dgs_batch = fields.Many2one("dgs.batches",string="Exam Batch",tracking=True)
    examiner_id = fields.Many2one('bes.examiner', string="Examiners")
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

    total = fields.Integer("Total Expense",compute='_compute_total_expense',store=True)
    
    practical_oral_total = fields.Integer("Practical/Oral Expense",compute="_compute_total")
    
    online_total = fields.Integer("Online Expense",compute="_compute_total")
    
    team_lead_total = fields.Integer("Team Lead Expense",compute="_compute_total")
    
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
                
            if record.misc_expense_ids:
                record.misc_total = sum(record.misc_expense_ids.mapped('price'))
            else:
                record.misc_total = 0
     
    
    @api.depends('assignment_expense_ids.total', 'online_assignment_expense.price', 'team_lead_expense.price', 'misc_expense_ids.price')
    def _compute_total_expense(self):
        for record in self:
            total_assignment = sum(record.assignment_expense_ids.mapped('total'))
            total_online = sum(record.online_assignment_expense.mapped('price'))
            total_team_lead = sum(record.team_lead_expense.mapped('price'))
            total_misc = sum(record.misc_expense_ids.mapped('price'))
            record.total = total_assignment + total_online + total_team_lead + total_misc
    
    
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

    
    
    
    
class InstituteTeamLead(models.Model):
    _name = 'institute.team.lead'
    _description = 'Institute Team Lead'
    

    examiner_expenses_id = fields.Many2one('examiner.expenses', string="Examiner Expenses")
    examiner_duty = fields.Many2one('exam.type.oral.practical', string="Examiner Duty")
    institute = fields.Many2one('bes.institute',related="examiner_duty.institute_id", string="Institute",store=True)
    price = fields.Integer("Price")
    
    
            

            
class ExamAssignmentOnlineExpense(models.Model):
    _name = 'exam.assignment.online.expense'
    _description = 'Exam Assignment Online Expense'
    
    examiner_expenses_id = fields.Many2one('examiner.expenses', string="Examiner Expenses")
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
    price = fields.Float(string="Price")
    docs = fields.Many2many('ir.attachment', string="Documents")
    examiner_expenses_id = fields.Many2one('examiner.expenses', string="Examiner Expenses")