from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
from datetime import datetime


class ExamCenter(models.Model):
    _name = "exam.center"
    _rec_name = "name"
    _description = "Exam Region"
    
    name = fields.Char("Exam Region",required=True)
    state_id = fields.Many2one("res.country.state","State",domain=[('country_id.code','=','IN')],required=True)
    exam_co_ordinator = fields.Many2one("res.users","Exam Co-ordinator")
    
    def examiners(self):
        
        return {
        'name': 'Examiners',
        'domain': [('exam_center', '=', self.id)],
        'view_type': 'form',
        'res_model': 'bes.examiner',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        'context': {
            'default_exam_coordinator_id': self.id    
            }
        }
    
    def assignment(self):
        
        return {
        'name': 'Exam Assignment',
        'domain': [('exam_region', '=', self.id)],
        'view_type': 'form',
        'res_model': 'examiner.assignment',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        'context': {
            'default_exam_coordinator_id': self.id    
            }
        }
        
    def time_sheet(self):
        
        return {
        'name': 'Time Sheets',
        'domain': [('exam_region', '=', self.id)],
        'view_type': 'form',
        'res_model': 'examiner.time.sheet',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        'context': {
            'default_exam_coordinator_id': self.id    
            }
        }