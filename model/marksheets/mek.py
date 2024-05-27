from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError

from datetime import datetime


class MekPractical(models.Model):
    _name = "practical.mek"
    _rec_name = "marksheet_name"
    _description= 'Practical MEK Marksheet'
    
    marksheet_name = fields.Char("Marksheet Name",default="Practical MEK Marksheet")
    exam_bes_candidate_id = fields.Many2one("exam.schedule.bes.candidate",string="Exam BES Candidate",required=True)
    using_hand_plumbing_tools_task_1 = fields.Integer("Using Hand & Plumbing Tools (Task 1)")
    using_hand_plumbing_tools_task_2 = fields.Integer("Using Hand & Plumbing Tools (Task 2)")
    using_hand_plumbing_tools_task_3 = fields.Integer("Using Hand & Plumbing Tools (Task 3)")
    use_of_chipping_tools_paint_brushes = fields.Integer("Use of Chipping Tools & paint Brushes")
    use_of_carpentry = fields.Integer("Use of Carpentry Tools")
    use_of_measuring_instruments = fields.Integer("Use of Measuring Instruments")
    welding = fields.Integer("Welding (1 Task)")
    lathe = fields.Integer("Lathe Work (1 Task)")
    electrical = fields.Integer("Electrical (1 Task)")
    
    total_marks = fields.Integer("Total Marks", compute="_compute_total_marks", store=True)
    
    remarks = fields.Text(" Remarks Mention if Absent / Good  /Average / Weak ")

    
    @api.model
    def create(self, values):
        # import wdb; wdb.set_trace()
        mek_practical = super(MekPractical, self).create(values)
        mek_practical.exam_bes_candidate_id.write({'mek_practical_id':mek_practical.id})
        return mek_practical
    
    @api.depends('using_hand_plumbing_tools_task_1', 'using_hand_plumbing_tools_task_2', 'using_hand_plumbing_tools_task_3',
                 'use_of_chipping_tools_paint_brushes', 'use_of_carpentry', 'use_of_measuring_instruments',
                 'welding', 'lathe', 'electrical')
    def _compute_total_marks(self):
        for record in self:
            total = (
                record.using_hand_plumbing_tools_task_1 +
                record.using_hand_plumbing_tools_task_2 +
                record.using_hand_plumbing_tools_task_3 +
                record.use_of_chipping_tools_paint_brushes +
                record.use_of_carpentry +
                record.use_of_measuring_instruments +
                record.welding +
                record.lathe +
                record.electrical
            )
            record.total_marks = total
    
    
    @api.constrains('using_hand_plumbing_tools_task_1', 'using_hand_plumbing_tools_task_2', 'using_hand_plumbing_tools_task_3', 'use_of_chipping_tools_paint_brushes', 'use_of_carpentry', 'use_of_measuring_instruments', 'welding', 'lathe', 'electrical')
    def _check_values(self):
        for record in self:
            fields_to_check = {
                'using_hand_plumbing_tools_task_1': "Using Hand & Plumbing Tools (Task 1)",
                'using_hand_plumbing_tools_task_2': "Using Hand & Plumbing Tools (Task 2)",
                'using_hand_plumbing_tools_task_3': "Using Hand & Plumbing Tools (Task 3)",
                'use_of_chipping_tools_paint_brushes': "Use of Chipping Tools & Paint Brushes",
                'use_of_carpentry': "Use of Carpentry Tools",
                'use_of_measuring_instruments': "Use of Measuring Instruments",
                'welding': "Welding (1 Task)",
                'lathe': "Lathe Work (1 Task)",
                'electrical': "Electrical (1 Task)",
            }

            for field_name, field_label in fields_to_check.items():
                field_value = record[field_name]
                if field_name == 'welding' and field_value > 20:
                    raise ValidationError(f"{field_label} value cannot exceed 20.")
                elif field_value > 10:
                    raise ValidationError(f"{field_label} value cannot exceed 10.")
                

class MekOral(models.Model):
    _name = "oral.mek"
    
    _rec_name = "marksheet_name"
    _description= 'Oral MEK Marksheet'
    
    exam_bes_candidate_id = fields.Many2one("exam.schedule.bes.candidate",string="Exam BES Candidate",required=True)
    marksheet_name = fields.Char("Marksheet Name",default="Oral MEK Marksheet")
    using_of_tools = fields.Integer("Uses of Hand/Plumbing/Carpentry Tools & Chipping Tools & Brushes & Paints",tracking=True)
    # use_of_chipping_tools_paints = fields.Integer("Use of Chipping Tools & Brushes & Paints",tracking=True)
    welding_lathe_drill_grinder = fields.Integer("Welding & Lathe/Drill/Grinder",tracking=True)
    electrical = fields.Integer("Electrical")
    journal = fields.Integer("Journal")
    
    
    total_marks = fields.Integer("Total Marks", compute="_compute_total_marks", store=True)

    remarks = fields.Text(" Remarks Mention if Absent / Good  /Average / Weak ")
   
    
    @api.model
    def create(self, values):
        mek_oral = super(MekOral, self).create(values)
        mek_oral.exam_bes_candidate_id.write({'mek_oral_id':mek_oral.id})
        return mek_oral
    
    
    @api.constrains('using_of_tools', 'welding_lathe_drill_grinder', 'electrical', 'journal')
    def _check_field_limits(self):
         for record in self:
            field_names = {
                'using_of_tools': record.using_of_tools,
                'welding_lathe_drill_grinder': record.welding_lathe_drill_grinder,
                # 'welding': record.welding,
                # 'lathe_drill_grinder': record.lathe_drill_grinder,
                'electrical': record.electrical,
                'journal': record.journal,
            }
            for field_name, field_value in field_names.items():
                if field_value > 10 and field_name != 'journal':
                    raise ValidationError(f"{self._fields[field_name].string} value cannot exceed 10.")
                if field_value > 25 and field_name == 'journal':
                    raise ValidationError(f"{self._fields[field_name].string} value cannot exceed 25.")
    
    @api.depends('using_of_tools', 'welding_lathe_drill_grinder', 'electrical', 'journal')
    def _compute_total_marks(self):
        for record in self:
            total = (
                record.using_of_tools +
                record.welding_lathe_drill_grinder +
                # record.welding +
                # record.lathe_drill_grinder +
                record.electrical +
                record.journal
            )
            record.total_marks = total
    
    