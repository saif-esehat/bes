from odoo import api, fields, models , _
from odoo.exceptions import UserError,ValidationError
from odoo.exceptions import ValidationError

class GPCandidate(models.Model):
    _name = 'gp.candidate'
    _description = 'GP Candidate'
    
    institute_batch_id = fields.Many2one("institute.batches","Batch")
    institute_id = fields.Many2one("bes.institute",string="Name of Institute",required=True)
    candidate_image = fields.Image(string='Candidate Image', help='Select an image in JPEG format.')
    
    name = fields.Char("Full Name of Candidate as in INDOS",required=True)
    age = fields.Char("Age")
    indos_no = fields.Char("Indos No.")
    candidate_code = fields.Char("GP Candidate Code No.")
    roll_no = fields.Char("Roll No.")
    dob = fields.Date("DOB")
    street = fields.Char("Street")
    street2 = fields.Char("Street2")
    city = fields.Char("City",required=True)
    zip = fields.Char("Zip",required=True)
    state_id = fields.Many2one("res.country.state","State",domain=[('country_id.code','=','IN')],required=True)
    phone = fields.Char("Phone")
    mobile = fields.Char("Mobile")
    email = fields.Char("Email")
    tenth_percent = fields.Integer("% Xth Std in Eng.")
    twelve_percent = fields.Integer("% 12th Std in Eng.")
    iti_percent = fields.Integer("% ITI")
    sc_st = fields.Boolean("To be mentioned if Candidate SC/ST")
    ship_visits_count = fields.Char("No. of Ship Visits")
    elligiblity_criteria = fields.Selection([
        ('elligible', 'Elligible'),
        ('not_elligible', 'Not Elligible')
    ],string="Elligiblity Criteria",compute="_compute_eligibility", default='not_elligible')
    
    qualification = fields.Selection([
        ('tenth', '10th std'),
        ('twelve', '12th std'),
        ('iti', 'ITI')
    ],string="Qualification", default='tenth')

    candidate_attendance_record = fields.Integer("Candidate Attendance Record")
    
    
    attendance_compliance_1 = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ],string="Whether Attendance record of the candidate comply with DGS Guidelines 1 of 2018 as per para 3.2 for GP / 7 of 2010 as per para 3.3 for CCMC (YES/ NO)", default='no')
    
    attendance_compliance_2 = fields.Selection([
         ('yes', 'Yes'),
         ('no', 'No')
    ], string="Attendance record of the candidate not comply with DGS Guidelines 1 of 2018 as per para 3.2 for GP / 7 of 2010 as per para 3.3 for CCMC and whether same has been informed to the DGS (YES/ NO)", default='no')

    stcw_certificate = fields.One2many("gp.candidate.stcw.certificate","candidate_id",string="STCW Certificate")
    
    # attendance_compliance_2 = fields.Boolean([
    #     ('yes', 'Yes'),
    #     ('no', 'No')
    # ],string="Attendance record of the candidate not comply with DGS Guidelines 1 of 2018 as per para 3.2 for GP / 7 of 2010 as per para 3.3 for CCMC and whether same has been informed to the DGS (YES/ NO)", default='no')
    
    
    ship_visits = fields.One2many("gp.candidate.ship.visits","candidate_id",string="Ship Visit")

    
    
    
    @api.depends('name', 'age', 'indos_no', 'candidate_code', 'roll_no', 'dob', 'street', 'street2',
                 'city', 'zip', 'state_id', 'phone', 'mobile', 'email', 'sc_st', 'qualification','tenth_percent','twelve_percent','iti_percent')
    def _compute_eligibility(self):
        for candidate in self:
            # candidate.elligibility_criteria = 'not_elligible'
            # Check if all the fields are filled
            # import wdb; wdb.set_trace()
            all_fields_filled = all([candidate.name, candidate.age, candidate.indos_no, candidate.candidate_code, candidate.roll_no,
                    candidate.dob, candidate.street, candidate.street2, candidate.city, candidate.zip,
                    candidate.state_id, candidate.phone, candidate.mobile, candidate.email, candidate.sc_st,
                    candidate.qualification])

            if all_fields_filled:
                # import wdb; wdb.set_trace()
                if candidate.qualification == 'tenth' and candidate.tenth_percent > 40 or candidate.qualification == 'twelve' and candidate.twelve_percent > 40 or candidate.qualification == 'iti' and candidate.iti_percent > 50:
                   candidate.elligiblity_criteria = 'elligible'                
                else:
                   candidate.elligiblity_criteria = 'not_elligible'
            else:
                candidate.elligiblity_criteria = 'not_elligible'       
    
    
    

    # MEK Practical

    mek_practical_child_line = fields.One2many("gp.mek.practical.line","mek_parent",string="MEK Practical")
                    
    # MEK ORAL

    mek_oral_child_line = fields.One2many("gp.mek.oral.line","mek_oral_parent",string="MEK Oral")


    # GSK Practical

    gsk_practical_child_line = fields.One2many("gp.gsk.practical.line","gsk_practical_parent",string="GSK Practical")

    
    # GSK Oral

    gsk_oral_child_line = fields.One2many("gp.gsk.oral.line","gsk_oral_parent",string="GSK Practical")
        

class GPSTCWCandidate(models.Model):
    _name = 'gp.candidate.stcw.certificate'
    _description = 'STCW'
    
    candidate_id = fields.Many2one("gp.candidate","Candidate")

    course_name =  fields.Selection([
        ('pst', 'PST'),
        ('efa', 'EFA'),
        ('fpff', 'FPFF'),
        ('pssr', 'PSSR'),
        ('stsdsd', 'STSDSD')
    ],string="Course")
    institute_name = fields.Many2one("bes.institute","Institute Name")
    marine_training_inst_number = fields.Char("MTI Number")
    mti_indos_no = fields.Char("Indos No.")
    candidate_cert_no = fields.Char("Candidate Certificate Number")
    course_start_date = fields.Date(string="Course Start Date")
    course_end_date = fields.Date(string="Course End Date")
    file_name = fields.Char('File Name')
    certificate_upload = fields.Binary("Certificate Upload")
    






    

class GPCandidateShipVisits(models.Model):
    _name = 'gp.candidate.ship.visits'
    _description = 'Ship Visits'
    candidate_id = fields.Many2one("gp.candidate","Candidate")
    name_of_ships = fields.Char("Name of  the Ship Visited / Ship in Campus")
    imo_no = fields.Char("Ship IMO Number")
    name_of_ports_visited = fields.Char("Name of the Port Visited / Place of SIC")
    date_of_visits = fields.Date("Date Of Visit")
    time_spent_on_ship = fields.Float("Hours")
    bridge = fields.Boolean("Bridge")
    eng_room = fields.Boolean("Eng. Room")
    cargo_area = fields.Boolean("Cargo Area")
    
    

class CCMCCandidate(models.Model):
    _name = 'ccmc.candidate'
    _description = 'CCMC Candidate'
    
    institute_batch_id = fields.Many2one("institute.batches","Batch")
    institute_id = fields.Many2one("bes.institute",string="Name of Institute",required=True)
    candidate_image = fields.Binary(string='Candidate Image', attachment=True, help='Select an image in JPEG format.')
    
    name = fields.Char("Full Name of Candidate as in INDOS",required=True)
    age = fields.Char("Age")
    indos_no = fields.Char("Indos No.")
    candidate_code = fields.Char("CCMC Candidate Code No.")
    roll_no = fields.Char("Roll No.")
    dob = fields.Date("DOB")
    street = fields.Char("Street")
    street2 = fields.Char("Street2")
    city = fields.Char("City",required=True)
    zip = fields.Char("Zip",required=True)
    state_id = fields.Many2one("res.country.state","State",domain=[('country_id.code','=','IN')],required=True)
    phone = fields.Char("Phone")
    mobile = fields.Char("Mobile")
    email = fields.Char("Email")
    tenth_percent = fields.Char("% Xth Std in Eng.")
    twelve_percent = fields.Char("% 12th Std in Eng.")
    iti_percent = fields.Char("% ITI")
    sc_st = fields.Boolean("To be mentioned if Candidate SC/ST")
    ship_visits_count = fields.Char("No. of Ship Visits")
    
    qualification = fields.Selection([
        ('tenth', '10th std'),
        ('twelve', '12th std'),
        ('iti', 'ITI')
    ],string="Qualification", default='tenth')
    
    candidate_attendance_record = fields.Integer("Candidate Attendance Record")
    
    elligiblity_criteria = fields.Selection([
        ('elligible', 'Elligible'),
        ('not_elligible', 'Not Elligible')
    ],string="Elligiblity Criteria",compute="_compute_eligibility", default='not_elligible')
    
    
    attendance_compliance_1 = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ],string="Whether Attendance record of the candidate comply with DGS Guidelines 1 of 2018 as per para 3.2 for GP / 7 of 2010 as per para 3.3 for CCMC (YES/ NO)", default='no')
    
    attendance_compliance_2 = fields.Selection([
         ('yes', 'Yes'),
         ('no', 'No')
    ], string="Attendance record of the candidate not comply with DGS Guidelines 1 of 2018 as per para 3.2 for GP / 7 of 2010 as per para 3.3 for CCMC and whether same has been informed to the DGS (YES/ NO)", default='no')

    stcw_certificate = fields.One2many("ccmc.candidate.stcw.certificate","candidate_id",string="STCW Certificate")
    
    # attendance_compliance_2 = fields.Boolean([
    #     ('yes', 'Yes'),
    #     ('no', 'No')
    # ],string="Attendance record of the candidate not comply with DGS Guidelines 1 of 2018 as per para 3.2 for GP / 7 of 2010 as per para 3.3 for CCMC and whether same has been informed to the DGS (YES/ NO)", default='no')
    
        # Ship Visits
    ship_visits = fields.One2many("ccmc.candidate.ship.visits","candidate_id",string="Ship Visit")

        # Cookery an Bakery
    cookery_child_line = fields.One2many("ccmc.cookery.bakery.line","cookery_parent",string="Cookery & Bakery")
    

        # Start CCMC rating Oral

    gsk_ccmc = fields.Integer("GSK")
    safety_ccmc = fields.Integer("Safety")
    toal_ccmc_rating = fields.Integer("Total", compute="_compute_ccmc_rating_total", store=True)
    
    
    @api.depends('name', 'age', 'indos_no', 'candidate_code', 'roll_no', 'dob', 'street', 'street2',
                 'city', 'zip', 'state_id', 'phone', 'mobile', 'email', 'sc_st', 'qualification','tenth_percent','twelve_percent','iti_percent')
    def _compute_eligibility(self):
        for candidate in self:
            # candidate.elligibility_criteria = 'not_elligible'
            # Check if all the fields are filled
            # import wdb; wdb.set_trace()
            all_fields_filled = all([candidate.name, candidate.age, candidate.indos_no, candidate.candidate_code, candidate.roll_no,
                    candidate.dob, candidate.street, candidate.street2, candidate.city, candidate.zip,
                    candidate.state_id, candidate.phone, candidate.mobile, candidate.email, candidate.sc_st,
                    candidate.qualification])

            if all_fields_filled:
                # import wdb; wdb.set_trace()
                if candidate.qualification == 'tenth' and candidate.tenth_percent > 40 or candidate.qualification == 'twelve' and candidate.twelve_percent > 40 or candidate.qualification == 'iti' and candidate.iti_percent > 50:
                   candidate.elligiblity_criteria = 'elligible'                
                else:
                   candidate.elligiblity_criteria = 'not_elligible'
            else:
                candidate.elligiblity_criteria = 'not_elligible'        

    @api.depends(
        'gsk_ccmc', 'safety_ccmc'
    )
    def _compute_ccmc_rating_total(self):
        for record in self:
            rating_total = (
                record.gsk_ccmc +
                record.safety_ccmc
            )
            record.toal_ccmc_rating = rating_total
    
class CCMCSTCWCandidate(models.Model):
    _name = 'ccmc.candidate.stcw.certificate'
    _description = 'STCW'
    
    candidate_id = fields.Many2one("ccmc.candidate","Candidate")
    course_name =  fields.Selection([
        ('pst', 'PST'),
        ('efa', 'EFA'),
        ('fpff', 'FPFF'),
        ('pssr', 'PSSR'),
        ('stsdsd', 'STSDSD')
    ],string="Course")
    institute_name = fields.Many2one("bes.institute","Institute Name")
    marine_training_inst_number = fields.Char("Marine Training Institute Number")
    mti_indos_no = fields.Char("MTI Indos No.")
    candidate_cert_no = fields.Char("Candidate Certificate Number")
    file_name = fields.Char('File Name')
    certificate_upload = fields.Binary("Certificate Upload")
    course_start_date = fields.Date(string="Course Start Date")
    course_end_date = fields.Date(string="Course End Date")


    

class CCMCCandidateShipVisits(models.Model):
    _name = 'ccmc.candidate.ship.visits'
    _description = 'Ship Visits'
    candidate_id = fields.Many2one("ccmc.candidate","Candidate")
    name_of_ships = fields.Char("Name of  the Ship Visited / Ship in Campus")
    imo_no = fields.Char("Ship IMO Number")
    name_of_ports_visited = fields.Char("Name of the Port Visited / Place of SIC")
    date_of_visits = fields.Date("Date Of Visit")
    time_spent_on_ship = fields.Float("Hours")
    bridge = fields.Boolean("Bridge")
    eng_room = fields.Boolean("Eng. Room")
    cargo_area = fields.Boolean("Cargo Area")

class CookeryBakeryLine(models.Model):
    _name = 'ccmc.cookery.bakery.line'
    _description = 'Cookery and Bakery Line'

    cookery_parent = fields.Many2one("ccmc.candidate",string="Cookery & Bakery Parent")

    hygien_grooming = fields.Integer("Hygiene & Grooming")
    appearance = fields.Integer("Appearance(Dish 1)")
    taste = fields.Integer("Taste(Dish 1)")
    texture = fields.Integer("Texture(Dish 1)")
    appearance_2 = fields.Integer("Appearance(Dish 2)")
    taste_2 = fields.Integer("Taste(Dish 2)")
    texture_2 = fields.Integer("Texture(Dish 2)")
    appearance_3 = fields.Integer("Appearance(Dish 3)")
    taste_3 = fields.Integer("Taste(Dish 3)")
    texture_3 = fields.Integer("Texture(Dish 3)")
    identification_ingredians = fields.Integer("identification of ingredients")
    knowledge_of_menu = fields.Integer("Knowledge of menu")
    total_mrks = fields.Integer("Total", compute="_compute_total_mrks", store=True)
    cookery_examiner = fields.Many2one("bes.examiner",string="Examiner")
    cookery_bekary_start_time = fields.Datetime(string="Start Time")
    cookery_bekary_end_time = fields.Datetime(string="End Time")

    @api.depends(
        'hygien_grooming', 'appearance', 'taste', 'texture', 'appearance_2', 'taste_2',
        'texture_2', 'appearance_3', 'taste_3', 'texture_3', 'identification_ingredians', 'knowledge_of_menu'
    )
    def _compute_total_mrks(self):
        for record in self:
            total = (
                record.hygien_grooming +
                record.appearance +
                record.taste +
                record.texture +
                record.appearance_2 +
                record.taste_2 +
                record.texture_2 +
                record.appearance_3 +
                record.taste_3 +
                record.texture_3 +
                record.identification_ingredians +
                record.knowledge_of_menu
            )
            record.total_mrks = total


class MekPrcticalLine(models.Model):
    _name = 'gp.mek.practical.line'
    _description = 'MEK Practical Line'

    mek_parent = fields.Many2one("gp.candidate",string="Parent")

    using_hand_plumbing_tools_task_1 = fields.Integer("Using Hand & Plumbing Tools (Task 1)")
    using_hand_plumbing_tools_task_2 = fields.Integer("Using Hand & Plumbing Tools (Task 2)")
    using_hand_plumbing_tools_task_3 = fields.Integer("Using Hand & Plumbing Tools (Task 3)")
    use_of_chipping_tools_paint_brushes = fields.Integer("Use of Chipping Tools & paint Brushes")
    use_of_carpentry = fields.Integer("Use of Carpentry Tools")
    use_of_measuring_instruments = fields.Integer("Use of Measuring Instruments")
    welding = fields.Integer("Welding (1 Task)")
    lathe = fields.Integer("Lathe Work (1 Task)")
    electrical = fields.Integer("Electrical (1 Task)")
    
    mek_practical_total_marks = fields.Integer("Total Marks", compute="_compute_mek_practical_total_marks", store=True)
    
    mek_practical_remarks = fields.Text(" Remarks Mention if Absent / Good  /Average / Weak ")
    
    
    
    @api.depends('using_hand_plumbing_tools_task_1', 'using_hand_plumbing_tools_task_2', 'using_hand_plumbing_tools_task_3',
                 'use_of_chipping_tools_paint_brushes', 'use_of_carpentry', 'use_of_measuring_instruments',
                 'welding', 'lathe', 'electrical')
    def _compute_mek_practical_total_marks(self):
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
            record.mek_practical_total_marks = total
    
    
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

class MekOralLine(models.Model):
    _name = 'gp.mek.oral.line'
    _description = 'MEK Oral Line'

    mek_oral_parent = fields.Many2one("gp.candidate", string="Parent")

    using_hand_plumbing_carpentry_tools = fields.Integer("Uses of Hand/Plumbing/Carpentry Tools")
    use_of_chipping_tools_paints = fields.Integer("Use of Chipping Tools & Brushes & Paints")
    welding = fields.Integer("Welding")
    lathe_drill_grinder = fields.Integer("Lathe/Drill/Grinder")
    electrical = fields.Integer("Electrical")
    journal = fields.Integer("Journal")

    mek_oral_total_marks = fields.Integer("Total Marks", compute="_compute_mek_oral_total_marks", store=True)

    mek_oral_remarks = fields.Text("Remarks Mention if Absent / Good / Average / Weak")

    @api.constrains('using_hand_plumbing_carpentry_tools', 'use_of_chipping_tools_paints', 'welding', 'lathe_drill_grinder', 'electrical', 'journal')
    def _check_field_limits(self):
        for record in self:
            if record.using_hand_plumbing_carpentry_tools > 10:
                raise ValidationError("Uses of Hand/Plumbing/Carpentry Tools value cannot exceed 10.")
            if record.use_of_chipping_tools_paints > 10:
                raise ValidationError("Use of Chipping Tools & Brushes & Paints value cannot exceed 10.")
            if record.welding > 10:
                raise ValidationError("Welding value cannot exceed 10.")
            if record.lathe_drill_grinder > 10:
                raise ValidationError("Lathe/Drill/Grinder value cannot exceed 10.")
            if record.electrical > 10:
                raise ValidationError("Electrical value cannot exceed 10.")
            if record.journal > 25:
                raise ValidationError("Journal value cannot exceed 25.")

    @api.depends('using_hand_plumbing_carpentry_tools', 'use_of_chipping_tools_paints', 'welding', 'lathe_drill_grinder', 'electrical', 'journal')
    def _compute_mek_oral_total_marks(self):
        for record in self:
            total = (
                record.using_hand_plumbing_carpentry_tools +
                record.use_of_chipping_tools_paints +
                record.welding +
                record.lathe_drill_grinder +
                record.electrical +
                record.journal
            )
            record.mek_oral_total_marks = total


class GskPracticallLine(models.Model):
    _name = 'gp.gsk.practical.line'
    _description = 'GSK Practical Line'

    gsk_practical_parent = fields.Many2one("gp.candidate", string="Parent")

    climbing_mast = fields.Integer("Climb the mast with safe practices , Prepare and throw Heaving Line ")
    buoy_flags_recognition = fields.Integer("·Recognise buyos and flags .Hoisting a Flag correctly .Steering and Helm Orders")
    bosun_chair = fields.Integer("Rigging Bosun's Chair and self lower and hoist ")
    rig_stage = fields.Integer("Rig a stage for painting shipside ")
    rig_pilot = fields.Integer("Rig a Pilot Ladder ")
    rig_scaffolding = fields.Integer("Rig scaffolding to work at a height ") 
    fast_ropes = fields.Integer("·Making fast Ropes and Wires ·Use Rope-Stopper / Chain Stopper")
    
    knots_bend = fields.Integer(".Knots, Bends, Hitches .Whippings/Seizing/Splicing Ropes/Wires .Reeve 3- fold / 2 fold purchase ")
    sounding_rod = fields.Integer("·Taking Soundings with sounding rod / sounding taps ·Reading of Draft .Mannual lifting of weight ")
    
    gsk_practical_total_marks = fields.Integer("Total Marks",compute="_compute_gsk_practical_total_marks")
    gsk_practical_remarks = fields.Text(" Remarks Mention if Absent / Good  /Average / Weak ")    


    @api.constrains('climbing_mast', 'buoy_flags_recognition', 'bosun_chair', 'rig_stage', 'rig_pilot', 'rig_scaffolding', 'fast_ropes', 'knots_bend', 'sounding_rod')
    def _check_max_value(self):
        for record in self:
            fields_to_check = {
                'climbing_mast': "Climb the mast with safe practices, Prepare and throw Heaving Line",
                'buoy_flags_recognition': "Recognise buyos and flags, Hoisting a Flag correctly, Steering and Helm Orders",
                'bosun_chair': "Rigging Bosun's Chair and self lower and hoist",
                'rig_stage': "Rig a stage for painting shipside",
                'rig_pilot': "Rig a Pilot Ladder",
                'rig_scaffolding': "Rig scaffolding to work at a height",
                'fast_ropes': "Making fast Ropes and Wires, Use Rope-Stopper / Chain Stopper",
                'knots_bend': "Knots, Bends, Hitches, Whippings/Seizing/Splicing Ropes/Wires, Reeve 3-fold / 2-fold purchase",
                'sounding_rod': "Taking Soundings with sounding rod / sounding taps, Reading of Draft, Manual lifting of weight",
            }
            
            for field_name, field_label in fields_to_check.items():
                field_value = record[field_name]
                if field_name == 'climbing_mast' and field_value > 12:
                    raise ValidationError(f"{field_label} value cannot exceed 12.")
                elif field_name == 'buoy_flags_recognition' and field_value > 12:
                    raise ValidationError(f"{field_label} value cannot exceed 12.")
                elif field_name == 'bosun_chair' and field_value > 8:
                    raise ValidationError(f"{field_label} value cannot exceed 8.")
                elif field_name == 'rig_stage' and field_value > 8:
                    raise ValidationError(f"{field_label} value cannot exceed 8.")
                elif field_name == 'rig_pilot' and field_value > 8:
                    raise ValidationError(f"{field_label} value cannot exceed 8.")
                elif field_name == 'rig_scaffolding' and field_value > 8:
                    raise ValidationError(f"{field_label} value cannot exceed 8.")
                elif field_name == 'fast_ropes' and field_value > 8:
                    raise ValidationError(f"{field_label} value cannot exceed 8.")
                elif field_name == 'knots_bend' and field_value > 18:
                    raise ValidationError(f"{field_label} value cannot exceed 18.")
       
    @api.depends('climbing_mast', 'buoy_flags_recognition', 'bosun_chair', 'rig_stage', 'rig_pilot', 'rig_scaffolding', 'fast_ropes', 'knots_bend', 'sounding_rod')
    def _compute_gsk_practical_total_marks(self):
        for record in self:
            total_marks = 0
            total_marks += record.climbing_mast
            total_marks += record.buoy_flags_recognition
            total_marks += record.bosun_chair
            total_marks += record.rig_stage
            total_marks += record.rig_pilot
            total_marks += record.rig_scaffolding
            total_marks += record.fast_ropes
            total_marks += record.knots_bend
            total_marks += record.sounding_rod
            record.gsk_practical_total_marks = total_marks


class GskOralLine(models.Model):
    _name = 'gp.gsk.oral.line'
    _description = 'GSK Oral Line'

    gsk_oral_parent = fields.Many2one("gp.candidate", string="Parent")


    subject_area_1 = fields.Integer("Subject Area 1")
    subject_area_2 = fields.Integer("Subject Area 2")
    subject_area_3 = fields.Integer("Subject Area 3")
    subject_area_4 = fields.Integer("Subject Area 4")
    subject_area_5 = fields.Integer("Subject Area 5")
    subject_area_6 = fields.Integer("Subject Area 6")
    practical_record_journals = fields.Integer("Practical Record Book and Journal")
    
    
    gsk_oral_total_marks = fields.Integer("Total Marks",compute='_compute_gsk_oral_total_marks', store=True)
    gsk_oral_remarks = fields.Text(" Remarks Mention if Absent / Good  /Average / Weak ")
    
    
    @api.constrains('subject_area_1', 'subject_area_2', 'subject_area_3', 'subject_area_4', 'subject_area_5', 'subject_area_6', 'practical_record_journals')
    def _check_max_value(self):
        for record in self:
            fields_to_check = {
                'subject_area_1': record._fields['subject_area_1'].string,
                'subject_area_2': record._fields['subject_area_2'].string,
                'subject_area_3': record._fields['subject_area_3'].string,
                'subject_area_4': record._fields['subject_area_4'].string,
                'subject_area_5': record._fields['subject_area_5'].string,
                'subject_area_6': record._fields['subject_area_6'].string,
                'practical_record_journals': record._fields['practical_record_journals'].string,
            }

            for field_name, field_label in fields_to_check.items():
                field_value = record[field_name]
                if field_name == 'subject_area_1' and field_value > 9:
                    raise ValidationError(f"{field_label} value cannot exceed 9.")
                elif field_name == 'subject_area_2' and field_value > 6:
                    raise ValidationError(f"{field_label} value cannot exceed 6.")
                elif field_name == 'subject_area_3' and field_value > 9:
                    raise ValidationError(f"{field_label} value cannot exceed 9.")
                elif field_name == 'subject_area_4' and field_value > 9:
                    raise ValidationError(f"{field_label} value cannot exceed 9.")
                elif field_name == 'subject_area_5' and field_value > 12:
                    raise ValidationError(f"{field_label} value cannot exceed 12.")
                elif field_name == 'subject_area_6' and field_value > 5:
                    raise ValidationError(f"{field_label} value cannot exceed 5.")
                elif field_name == 'practical_record_journals' and field_value > 25:
                    raise ValidationError(f"{field_label} value cannot exceed 25.")
    
    @api.depends('subject_area_1', 'subject_area_2', 'subject_area_3', 'subject_area_4', 'subject_area_5', 'subject_area_6', 'practical_record_journals')
    def _compute_gsk_oral_total_marks(self):
        for record in self:
            total_marks = sum([
                record.subject_area_1,
                record.subject_area_2,
                record.subject_area_3,
                record.subject_area_4,
                record.subject_area_5,
                record.subject_area_6,
                record.practical_record_journals,
            ])

            record.gsk_oral_total_marks = total_marks


