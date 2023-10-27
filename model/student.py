from odoo import api, fields, models , _
from odoo.exceptions import UserError,ValidationError

class Candidate(models.Model):
    _name = 'bes.candidate'
    _description = 'Candidate'
    
    institute_batch_id = fields.Many2one("institute.batches","Batch")
    name = fields.Char("Name of Candidate",required=True)
    indos_no = fields.Char("Indos No.")
    candidate_code = fields.Char("Candidate Code No.")
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
    attendance_id = fields.Many2one("candidate.attendance","Attendance ID")
    stcw_certificate_id = fields.Many2one("candidate.stcw.certificate","STCW Certificate")
    ship_visits_count = fields.Char("No. of Ship Visits")
    
    
    attendance_compliance_1 = fields.Boolean("Whether Attendance record of the candidate comply with DGS Guidelines 1 of 2018 as per para 3.2 for GP / 7 of 2010 as per para 3.3 for CCMC (YES/ NO)")
    attendance_compliance_2 = fields.Boolean("Attendance record of the candidate not comply with DGS Guidelines 1 of 2018 as per para 3.2 for GP / 7 of 2010 as per para 3.3 for CCMC and whether same has been informed to the DGS (YES/ NO)")
    
    
    ship_visits = fields.One2many("candidate.ship.visits","candidate_id",string="Ship Visit")


    
    def open_ship_visits(self):
        
        return {
                    'name': _('Candidate Ship Visit'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'candidate.ship.visits',
                    'type': 'ir.actions.act_window',
                    'view_id': False,
                    'target': 'current',
                    'domain': [('candidate_id', '=', self.id)],
                    'context':{
                        'default_candidate_id': self.id    
                     }
                }
        


    
    def open_ship_visits(self):
        
        return {
                    'name': _('Candidate Ship Visit'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'candidate.ship.visits',
                    'type': 'ir.actions.act_window',
                    'view_id': False,
                    'target': 'current',
                    'domain': [('candidate_id', '=', self.id)],
                    'context':{
                        'default_candidate_id': self.id    
                     }
                }
        

    def open_stcw(self):
        
        if self.stcw_certificate_id:
            
            return {
                    'name': _('Candidate STCW Certificate'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'candidate.stcw.certificate',
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': self.stcw_certificate_id.id,
                    }
        else:
            return {
                    'name': _('Candidate STCW Certificate'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'candidate.stcw.certificate',
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'context': {
                    'default_candidate_id': self.id    
                    }
                    }
            
    
    def open_attendance(self):
        
        if self.attendance_id:
            return {
                'name': _('Candidate Attendance Form'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'candidate.attendance',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': self.attendance_id.id,
                }
            
        else:
            
            return {
                'name': _('Candidate Attendance Form'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'candidate.attendance',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'context': {
                    'default_candidate_id': self.id    
                    }
                }
        
        


class CandidateAttendance(models.Model):
    _name = 'candidate.attendance'
    _description = 'Attendance'
    candidate_id = fields.Many2one("bes.candidate","Candidate")
    compliance_1 = fields.Boolean("Whether Attendance record of the candidate comply with DGS Guidelines 1 of 2018 as per para 3.2 for GP / 7 of 2010 as per para 3.3 for CCMC (YES/ NO)")
    compliance_2 = fields.Boolean("Attendance record of the candidate not comply with DGS Guidelines 1 of 2018 as per para 3.2 for GP / 7 of 2010 as per para 3.3 for CCMC and whether same has been informed to the DGS (YES/ NO)")
    
    @api.model
    def create(self, values):
        attendance = super(CandidateAttendance, self).create(values)
        attendance.candidate_id.write({
            'attendance_id':attendance.id
        })
        
        return attendance

class CandidateSTCWV2(models.Model):
    _name = 'candidate.stcw.certificate.v2'
    _description = 'STCW'
    
    candidate_id = fields.Many2one("bes.candidate","Candidate")
    course_name = fields.Char("Name of  the Ship Visited / Ship in Campus")


class CandidateSTCW(models.Model):
    _name = 'candidate.stcw.certificate'
    _description = 'STCW'
    candidate_id = fields.Many2one("bes.candidate","Candidate")
    
    pst_certifcate = fields.Boolean("PST Certificates")
    pst_document_file = fields.Binary(string='Upload Document for PST Certificates', attachment=True)
    
    efa_certifcate = fields.Boolean("EFA Certificates")
    efa_document_file = fields.Binary(string='Upload Document for EFA Certificates', attachment=True)
    
    fpff_certifcate = fields.Boolean("FPFF Certificates")
    fpff_document_file = fields.Binary(string='Upload Document for FPFF Certificates', attachment=True)
    
    pssr_certifcate = fields.Boolean("PSSR Certificates")  # Corrected field name
    pssr_document_file = fields.Binary(string='Upload Document for PSSR Certificates', attachment=True)
    
    stsdsd_certifcate = fields.Boolean("STSDSD Certificates")  # Corrected field name
    stsdsd_document_file = fields.Binary(string='Upload Document for STSDSD Certificates', attachment=True)
    
    other_certificates = fields.One2many("other.certificates","stcw_certificate",string="Other Certificate")
    
    
    @api.model
    def create(self, values):
        stcw = super(CandidateSTCW, self).create(values)
        stcw.candidate_id.write({
            'stcw_certificate_id':self.id
        })
        
        return stcw


class CandidateSTCW(models.Model):
    _name = 'other.certificates'
    _description = 'Cerificate'
    stcw_certificate = fields.Many2one("candidate.stcw.certificate","STCW Certificate")
    name = fields.Char("Certificate Name")
    certificate_file = fields.Binary(string='Upload Document', attachment=True)
    

class CandidateShipVisits(models.Model):
    _name = 'candidate.ship.visits'
    _description = 'Ship Visits'
    candidate_id = fields.Many2one("bes.candidate","Candidate")
    name_of_ships = fields.Char("Name of  the Ship Visited / Ship in Campus")
    imo_no = fields.Char("Ship IMO Number")
    name_of_ports_visited = fields.Char("Name of the Port Visited / Place of SIC")
    date_of_visits = fields.Date("Date Of Visit")
    time_spent_on_ship = fields.Float("Hours")
    bridge = fields.Boolean("Bridge")
    eng_room = fields.Boolean("Eng. Room")
    cargo_area = fields.Boolean("Cargo Area")
    
    