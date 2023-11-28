from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError

class BatchWizard(models.TransientModel):
    _name = 'create.institute.batches.wizard'
    _description = 'Create Batches Wizard'
    
    batch_name = fields.Char("Batch Name")
    from_date = fields.Date("From Date")
    to_date = fields.Date("To Date")

    
    
    def create_batches(self):
        
        institutes = self.env['bes.institute'].search([('id','=',self.env.context.get('active_ids'))])        

        for institute in institutes:
            institute_id = institute
            for course in institute.courses:
                self.env['institute.gp.batches'].create({
                    "institute_id":institute_id.id,
                    "batch_name":str(course.course.course_code)+"/"+self.batch_name,
                    "from_date" : self.from_date,
                    "to_date":self.to_date,
                    "course":course.course.id
                })
                