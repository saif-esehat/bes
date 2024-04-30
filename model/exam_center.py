from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
from datetime import datetime


class ExamCenter(models.Model):
    _name = "exam.center"
    _rec_name = "name"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "Exam Region"
    
    name = fields.Char("Exam Region",required=True,tracking=True)
    state_id = fields.Many2one("res.country.state","State",domain=[('country_id.code','=','IN')],required=True,tracking=True)
    exam_co_ordinator = fields.Many2one("res.users","Exam Co-ordinator",tracking=True)
    mobile = fields.Char("Mobile",related='exam_co_ordinator.partner_id.mobile')
    email = fields.Char("Email",related='exam_co_ordinator.partner_id.email')
    gp_candidate = fields.Many2one('gp.exam.schedule')


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
        
    def candidates(self):
        # import wdb; wdb.set_trace();

        return {
        'name': 'Candidate',
        'domain': [('exam_region', '=', self.id)],
        'view_type': 'form',
        'res_model': 'gp.exam.schedule',
        'view_id': False,
        'view_mode': 'tree',
        'type': 'ir.actions.act_window',
        'context': {
            'default_exam_coordinator_id': self.id    
            }
        }