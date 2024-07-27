from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError

class BatchWizard(models.TransientModel):
    _name = 'create.institute.batches.wizard'
    _description = 'Create Batches Wizard'
    
    dgs_batch = fields.Many2one("dgs.batches",string="Exam Batch")
    batch_name = fields.Char("Batch Name")
    exam_batch_name = fields.Selection([
        ('jan','Jan - June'),
        ('july','July - Dec'),
        ],string="Batch Name")
    from_date = fields.Date("From Date")
    to_date = fields.Date("To Date")
    
    
    
    def create_batches(self):
        institutes = self.env['bes.institute'].search([('id', '=', self.env.context.get('active_ids'))])
        created_batches = []
        for institute in institutes:
            for course in institute.courses:
                if course.course.course_code == 'GP':
                    if course.batcher_per_year == 1 or course.batcher_per_year > 1:
                        if self.exam_batch_name == 'jan':
                            self.batch_name = 'Jan - June'
                            self.env['institute.gp.batches'].create({
                                "dgs_batch": self.dgs_batch.id,
                                "institute_id": institute.id,
                                "batch_name": str(course.course.course_code) + "/" + self.batch_name + ' ' + self.from_date.strftime('%Y'),
                                "from_date": self.from_date,
                                "to_date": self.to_date,
                                "course": course.course.id
                            })
                            created_batches.append(f"{institute.name} - {course.course.course_code} - {self.batch_name} - {self.from_date.strftime('%Y')}")
                    elif course.batcher_per_year > 1:
                        if self.exam_batch_name == 'july':
                            self.batch_name = 'July - Dec'
                            self.env['institute.gp.batches'].create({
                                "dgs_batch": self.dgs_batch.id,
                                "institute_id": institute.id,
                                "batch_name": str(course.course.course_code) + "/" + self.batch_name + ' ' + self.from_date.strftime('%Y'),
                                "from_date": self.from_date,
                                "to_date": self.to_date,
                                "course": course.course.id
                            })
                            created_batches.append(f"{institute.name} - {course.course.course_code} - {self.batch_name} - {self.from_date.strftime('%Y')}")
                elif course.course.course_code == 'CCMC':
                    if course.batcher_per_year == 1 or course.batcher_per_year > 1:
                        if self.exam_batch_name == 'jan':
                            self.batch_name = 'Jan - June'
                            self.env['institute.ccmc.batches'].create({
                                "institute_id": institute.id,
                                "ccmc_batch_name": str(course.course.course_code) + "/" + self.batch_name + ' ' + self.from_date.strftime('%Y'),
                                "ccmc_from_date": self.from_date,
                                "ccmc_to_date": self.to_date,
                                "ccmc_course": course.course.id
                            })
                            created_batches.append(f"{institute.name} - {course.course.course_code} - {self.batch_name} - {self.from_date.strftime('%Y')}")
                    elif course.batcher_per_year > 1:
                        if self.exam_batch_name == 'july':
                            self.batch_name = 'July - Dec'
                            self.env['institute.ccmc.batches'].create({
                                "institute_id": institute.id,
                                "ccmc_batch_name": str(course.course.course_code) + "/" + self.batch_name + ' ' + self.from_date.strftime('%Y'),
                                "ccmc_from_date": self.from_date,
                                "ccmc_to_date": self.to_date,
                                "ccmc_course": course.course.id
                            })
                            created_batches.append(f"{institute.name} - {course.course.course_code} - {self.batch_name} - {self.from_date.strftime('%Y')}")
        
        message = "Batches Created Successfully for: \n" + "\n".join(created_batches)
        
        # Open the popup with the message
        return {
            'name': 'Batch Created',
            'type': 'ir.actions.act_window',
            'res_model': 'batch.pop.up.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'default_message': message},
        }
class hr_wizard(models.TransientModel):

    _name = 'batch.pop.up.wizard'

    _description = 'Batch Pop Up Wizard'

    message = fields.Text(string="Message", readonly=True, store=True)
    
    def action_close(self):
        return {'type': 'ir.actions.act_window_close'}
