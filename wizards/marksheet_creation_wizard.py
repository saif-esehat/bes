from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError


class GPMarksheetCreateWizard(models.TransientModel):
    _name = 'gp.marksheet.creation.wizard'
    gp_candidate = fields.Many2one("gp.candidate","GP Candidate")
    attempt_number = fields.Integer("Attempt Number")
    institute_name = fields.Many2one("bes.institute","Institute Name")
    gsk_oral_marks = fields.Float("GSK Oral/Journal")
    mek_oral_marks = fields.Float("MEK Oral/Journal")
    gsk_practical_marks = fields.Float("GSK Practical")
    mek_practical_marks = fields.Float("MEK Practical")
    gsk_total = fields.Float("GSK Oral/Practical",compute="_compute_gsk_total")
    gsk_percentage = fields.Float("GSK Oral/Practical Precentage",compute="_compute_gsk_percentage")
    mek_online_marks = fields.Float("MEK Online")
    gsk_online_marks = fields.Float("GSK Online")
    mek_online_percentage = fields.Float("MEK Online (%)",compute="_compute_mek_online_percentage")
    gsk_online_percentage = fields.Float("GSK Online (%)",compute="_compute_gsk_online_percentage")    
    mek_total = fields.Float("MEK Oral/Practical",compute="_compute_mek_total")
    mek_percentage = fields.Float("MEK Oral/Practical Percentage",compute="_compute_mek_percentage")
    overall_marks = fields.Float("Overall Marks",compute="_compute_overall_marks")
    overall_percentage = fields.Float("Overall (%)",compute="_compute_overall_percentage")
    
    
    def add_marksheet(self):
        data = {
            "gp_candidate": self.gp_candidate.id,
            "attempt_number": self.attempt_number,
            "institute_name": self.institute_name.id,
            "gsk_oral_marks": self.gsk_oral_marks,
            "mek_oral_marks": self.mek_oral_marks,
            "gsk_practical_marks": self.gsk_practical_marks,
            "mek_practical_marks": self.mek_practical_marks,
            "gsk_total": self.gsk_total,
            "gsk_percentage": self.gsk_percentage,
            "mek_online_marks": self.mek_online_marks,
            "gsk_online_marks": self.gsk_online_marks,
            "mek_online_percentage": self.mek_online_percentage,
            "gsk_online_percentage": self.gsk_online_percentage,
            "mek_total": self.mek_total,
            "mek_percentage": self.mek_percentage,
            "overall_marks": self.overall_marks,
            "overall_percentage": self.overall_percentage,
            "state":"2-done"
        }
        
        self.env['gp.exam.schedule'].create(data)
    
    
    @api.depends("overall_marks")
    def _compute_overall_percentage(self):
        for record in self:
            record.overall_percentage = (record.overall_marks/500) * 100

    @api.depends("mek_online_marks")
    def _compute_mek_online_percentage(self):
        for record in self:
            record.mek_online_percentage = (record.mek_online_marks/75) * 100
    
    
    @api.depends("gsk_online_marks")
    def _compute_gsk_online_percentage(self):
        for record in self:
            record.gsk_online_percentage = (record.gsk_online_marks/75) * 100
    
    @api.depends("gsk_total")
    def _compute_gsk_percentage(self):
        for record in self:
            record.gsk_percentage = (record.gsk_total/175) * 100
    
    @api.depends("mek_total")
    def _compute_mek_percentage(self):
        for record in self:
            record.mek_percentage = (record.mek_total/175) * 100

    @api.depends("gsk_total","mek_total","mek_online_marks","gsk_online_marks")
    def _compute_overall_marks(self):
        for record in self:
            record.overall_marks = record.gsk_total + record.mek_total + record.mek_online_marks + record.gsk_online_marks
             

    @api.constrains('mek_online_marks')
    def _check_mek_online_marks_value(self):
        for record in self:
            max_mark = 75  # Maximum allowed mark for MEK Online
            if record.mek_online_marks > max_mark:
                raise ValidationError(f"MEK Online marks must not be greater than {max_mark}.")

    @api.constrains('gsk_online_marks')
    def _check_gsk_online_marks_value(self):
        for record in self:
            max_mark = 75  # Maximum allowed mark for GSK Online
            if record.gsk_online_marks > max_mark:
                raise ValidationError(f"GSK Online marks must not be greater than {max_mark}.")


    @api.depends("gsk_oral_marks","gsk_practical_marks")
    def _compute_gsk_total(self):
        for record in self:
            record.gsk_total = record.gsk_oral_marks +  record.gsk_practical_marks
            
    @api.depends("mek_oral_marks","mek_practical_marks")
    def _compute_mek_total(self):
        for record in self:
            record.mek_total = record.mek_oral_marks +  record.mek_practical_marks
            
    
    @api.constrains('gsk_oral_marks')
    def _check_gsk_oral_marks_value(self):
        for record in self:
            max_mark = 75  # Maximum allowed mark
            if record.gsk_oral_marks > max_mark:
                raise ValidationError(f"GSK Oral/Journal marks must not be greater than {max_mark}.")
    
    @api.constrains('gsk_practical_marks')
    def _check_gsk_practical_marks_value(self):
        for record in self:
            max_mark = 100  # Maximum allowed mark
            if record.gsk_practical_marks > max_mark:
                raise ValidationError(f"GSK Practical marks must not be greater than {max_mark}.")
    
    @api.constrains('mek_practical_marks')
    def _check_mek_practical_marks_value(self):
        for record in self:
            max_mark = 100  # Maximum allowed mark for MEK Practical
            if record.mek_practical_marks > max_mark:
                raise ValidationError(f"MEK Practical marks must not be greater than {max_mark}.")

    @api.constrains('mek_oral_marks')
    def _check_mek_oral_marks_value(self):
        for record in self:
            max_mark = 75  # Maximum allowed mark for MEK Oral/Journal
            if record.mek_oral_marks > max_mark:
                raise ValidationError(f"MEK Oral/Journal marks must not be greater than {max_mark}.")


        
        


