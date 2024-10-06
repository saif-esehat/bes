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

    assignment_expense_ids = fields.One2many('exam.assignment.expense', 'examiner_expenses_id', string="Practical Oral Expenses")
    
    online_assignment_expense = fields.One2many('exam.assignment.online.expense', 'examiner_expenses_id', string="Online Expenses")

    team_lead_expense = fields.One2many('institute.team.lead', 'examiner_expenses_id', string="Online Expenses")
    
    misc_expense_ids = fields.One2many('exam.misc.expense', 'examiner_expenses_id', string="Miscellaneous Expenses")

    total = fields.Integer("Total Expense",compute='_compute_total_expense',store=True)
    
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


class InstituteTeamLead(models.Model):
    _name = 'institute.team.lead'
    _description = 'Institute Team Lead'
    

    examiner_expenses_id = fields.Many2one('examiner.expenses', string="Examiner Expenses")
    examiner_duty = fields.Many2one('exam.type.oral.practical', string="Examiner Duty")
    price = fields.Integer("Price")
            

            
class ExamAssignmentOnlineExpense(models.Model):
    _name = 'exam.assignment.online.expense'
    _description = 'Exam Assignment Online Expense'
    
    examiner_expenses_id = fields.Many2one('examiner.expenses', string="Examiner Expenses")
    exam_date = fields.Date("Exam Date")
    assignments_onlines = fields.Many2many('exam.type.oral.practical.examiners',relation="examiner_online_assignment", string="Online Assignments")
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