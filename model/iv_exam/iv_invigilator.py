from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
import base64
from io import BytesIO
import xlsxwriter
from datetime import datetime
import xlrd


    
class IVInvigilator(models.Model):
    _name = "iv.invigilator.sheet"
    _description= 'IV Invigilator Sheet'

    competency = fields.Selection([
        ('deck', 'Deck'),
        ('engine', 'Engine'),

        ], string='Competency')
    classroom_no = fields.Integer("Classroom No")
    classroom_capacity = fields.Integer('Classroom Capacity')
    invigilators = fields.One2many('invigilators.assigned','parent_id',string="Invigilators")
    batch_id = fields.Many2one(
        'iv.batches', 
        string="IV Batch", 
    )
    candidates_1cm = fields.Integer("1CM Candidates")
    candidates_2cm = fields.Integer("2CM Candidates")
    candidates_ser = fields.Integer("SER Candidates")

    candidates_eng = fields.Integer("ENGR Candidates")
    candidates_1ed = fields.Integer("1ED Candidates")
    candidates_2ed = fields.Integer("2ED Candidates")


    def print_iv_invigilator_report(self):
        datas = {
            'doc_ids': self.id,
        }

        return self.env.ref('bes.action_report_iv_invigilator').report_action(self, data=datas)
    
    def print_iv_invigilator_report1(self):
        # import wdb; wdb.set_trace(); 

        datas = {
            'doc_ids': self.id,
        }

        return self.env.ref('bes.action_report_iv_invigilator1').report_action(self, data=datas)



class IVinvigilatorAssigned(models.Model):
    _name="invigilators.assigned"

    parent_id = fields.Many2one('iv.invigilator.sheet')

    invigilator = fields.Many2one('res.partner',string="Invigilator",domain=[('category_id.name', 'ilike', 'Invigilator')])

