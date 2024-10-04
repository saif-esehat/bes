from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError

from datetime import datetime



class GSKPractical(models.Model):
    _name = "practical.gsk"
    _rec_name = "marksheet_name"
    _description= 'Practical GSK Marksheet'
    
    
    exam_bes_candidate_id = fields.Many2one("exam.schedule.bes.candidate",string="Exam BES Candidate",required=True)
    marksheet_name = fields.Char("Marksheet Name",default="Practical GSK Marksheet")
    climbing_mast_bosun_chair= fields.Integer("Climb the mast with safe practices , Prepare and throw Heaving Line,Rigging Bosun's Chair and self lower and hoist")
    # bosun_chair = fields.Integer("Rigging Bosun's Chair and self lower and hoist ")
    rig_stage_rig_pilot_rig_scaffolding = fields.Integer("Rig a stage for painting shipside,Rig a Pilot Ladder,Rig scaffolding to work at a height")
    # rig_pilot = fields.Integer("Rig a Pilot Ladder ")
    # rig_scaffolding = fields.Integer("Rig scaffolding to work at a height ") 
    fast_ropes_knots_bend_sounding_rod = fields.Integer("·Making fast Ropes and Wires ·Use Rope-Stopper / Chain Stopper,.Knots, Bends, Hitches .Whippings/Seizing/Splicing Ropes/Wires .Reeve 3- fold / 2 fold purchase,·Taking Soundings with sounding rod / sounding taps ·Reading of Draft .Mannual lifting of weight")
    buoy_flags_recognition = fields.Integer("·Recognise buyos and flags .Hoisting a Flag correctly .Steering and Helm Orders")
    
    # knots_bend = fields.Integer(".Knots, Bends, Hitches .Whippings/Seizing/Splicing Ropes/Wires .Reeve 3- fold / 2 fold purchase ")
    # sounding_rod = fields.Integer("·Taking Soundings with sounding rod / sounding taps ·Reading of Draft .Mannual lifting of weight ")
    
    total_marks = fields.Integer("Total Marks",compute="_compute_total_marks")
    remarks = fields.Text(" Remarks Mention if Absent / Good  /Average / Weak ")
    
    
    @api.constrains('climbing_mast_bosun_chair', 'buoy_flags_recognition', 'rig_stage_rig_pilot_rig_scaffolding', ' fast_ropes_knots_bend_sounding_rod')
    def _check_max_value(self):
        for record in self:
            fields_to_check = {
                'climbing_mast_bosun_chair': "Climb the mast with safe practices, Prepare and throw Heaving Line,Rigging Bosun's Chair and self lower and hoist",
                'buoy_flags_recognition': "Recognise buyos and flags, Hoisting a Flag correctly, Steering and Helm Orders",
                # 'bosun_chair': "Rigging Bosun's Chair and self lower and hoist",
                'rig_stage_rig_pilot_rig_scaffolding': "Rig a stage for painting shipside,Rig a Pilot Ladder,Rig scaffolding to work at a height",
                # 'rig_pilot': "Rig a Pilot Ladder",
                # 'rig_scaffolding': "Rig scaffolding to work at a height",
                'fast_ropes_knots_bend_sounding_rod': "Making fast Ropes and Wires, Use Rope-Stopper / Chain Stopper",
                # 'knots_bend': "Knots, Bends, Hitches, Whippings/Seizing/Splicing Ropes/Wires, Reeve 3-fold / 2-fold purchase",
                # 'sounding_rod': "Taking Soundings with sounding rod / sounding taps, Reading of Draft, Manual lifting of weight",
            }
            
            for field_name, field_label in fields_to_check.items():
                field_value = record[field_name]
                if field_name == 'climbing_mast_bosun_chair' and field_value > 30:
                    raise ValidationError(f"{field_label} value cannot exceed 30.")
                elif field_name == 'buoy_flags_recognition' and field_value > 12:
                    raise ValidationError(f"{field_label} value cannot exceed 12.")
                # elif field_name == 'bosun_chair' and field_value > 8:
                #     raise ValidationError(f"{field_label} value cannot exceed 8.")
                elif field_name == 'rig_stage_rig_pilot_rig_scaffolding' and field_value > 30:
                    raise ValidationError(f"{field_label} value cannot exceed 30.")
                # elif field_name == 'rig_pilot' and field_value > 8:
                #     raise ValidationError(f"{field_label} value cannot exceed 8.")
                # elif field_name == 'rig_scaffolding' and field_value > 8:
                #     raise ValidationError(f"{field_label} value cannot exceed 8.")
                elif field_name == 'fast_ropes_knots_bend_sounding_rod' and field_value > 30:
                    raise ValidationError(f"{field_label} value cannot exceed 30.")
                # elif field_name == 'knots_bend' and field_value > 18:
                #     raise ValidationError(f"{field_label} value cannot exceed 18.")



    
    
    @api.model
    def create(self, values):
        gsk_practical = super(GSKPractical, self).create(values)
        gsk_practical.exam_bes_candidate_id.write({'gsk_practical_id':gsk_practical.id})
        return gsk_practical

    
    
            
    @api.depends('climbing_mast_bosun_chair', 'buoy_flags_recognition', 'rig_stage_rig_pilot_rig_scaffolding', 'fast_ropes_knots_bend_sounding_rod')
    def _compute_total_marks(self):
        for record in self:
            total_marks = 0
            total_marks += record.climbing_mast_bosun_chair
            total_marks += record.buoy_flags_recognition
            # total_marks += record.bosun_chair
            total_marks += record.rig_stage_rig_pilot_rig_scaffolding
            # total_marks += record.rig_pilot
            # total_marks += record.rig_scaffolding
            total_marks += record.fast_ropes_knots_bend_sounding_rod
            # total_marks += record.knots_bend
            # total_marks += record.sounding_rod
            record.total_marks = total_marks
    
    

class GSKOral(models.Model):
    _name = "oral.gsk"
    _rec_name = "marksheet_name"
    _description= 'Oral GSK Marksheet'
    
    marksheet_name = fields.Char("Marksheet Name",default="Oral GSK Marksheet")
    exam_bes_candidate_id = fields.Many2one("exam.schedule.bes.candidate",string="Exam BES Candidate",required=True)
    subject_area_1_2_3 = fields.Integer("Subject Area 1, 2, 3 ",tracking=True)
    # subject_area_2 = fields.Integer("Subject Area 2",tracking=True)
    # subject_area_3 = fields.Integer("Subject Area 3",tracking=True)
    subject_area_4_5_6 = fields.Integer("Subject Area 4, 5, 6",tracking=True)
    practical_record_journals = fields.Integer("Practical Record Book and Journal")
    
    
    total_marks = fields.Integer("Total Marks",compute='_compute_total_marks', store=True)
    remarks = fields.Text(" Remarks Mention if Absent / Good  /Average / Weak ")
    
    @api.constrains('subject_area_1_2_3', 'subject_area_4_5_6', 'practical_record_journals')
    def _check_max_value(self):
        for record in self:
            fields_to_check = {
                'subject_area_1_2_3': record._fields['subject_area_1_2_3'].string,
                'subject_area_4_5_6': record._fields['subject_area_4_5_6'].string,
                # 'subject_area_3': record._fields['subject_area_3'].string,
                # 'subject_area_4': record._fields['subject_area_4'].string,
                # 'subject_area_5': record._fields['subject_area_5'].string,
                # 'subject_area_6': record._fields['subject_area_6'].string,
                'practical_record_journals': record._fields['practical_record_journals'].string,
            }

            for field_name, field_label in fields_to_check.items():
                field_value = record[field_name]
                if field_name == 'subject_area_1_2_3' and field_value > 25:
                    raise ValidationError(f"{field_label} value cannot exceed 25.")
                elif field_name == 'subject_area_4_5_6' and field_value > 25:
                    raise ValidationError(f"{field_label} value cannot exceed 25.")
                # elif field_name == 'subject_area_3' and field_value > 9:
                #     raise ValidationError(f"{field_label} value cannot exceed 9.")
                # elif field_name == 'subject_area_4' and field_value > 9:
                #     raise ValidationError(f"{field_label} value cannot exceed 9.")
                # elif field_name == 'subject_area_5' and field_value > 12:
                #     raise ValidationError(f"{field_label} value cannot exceed 12.")
                # elif field_name == 'subject_area_6' and field_value > 5:
                    # raise ValidationError(f"{field_label} value cannot exceed 5.")
                elif field_name == 'practical_record_journals' and field_value > 25:
                    raise ValidationError(f"{field_label} value cannot exceed 25.")

    
    
    
    @api.model
    def create(self, values):
        gsk_oral = super(GSKOral, self).create(values)
        gsk_oral.exam_bes_candidate_id.write({'gsk_oral_id':gsk_oral.id})
        return gsk_oral

    
    @api.depends('subject_area_1_2_3', 'subject_area_4_5_6', 'practical_record_journals')
    def _compute_total_marks(self):
        for record in self:
            total_marks = sum([
                record.subject_area_1_2_3,
                record.subject_area_4_5_6,
                # record.subject_area_3,
                # record.subject_area_4,
                # record.subject_area_5,
                # record.subject_area_6,
                record.practical_record_journals,
            ])

            record.total_marks = total_marks


    
    
    
     
    
    
    
    
    
    