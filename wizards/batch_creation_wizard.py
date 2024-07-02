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
        
        institutes = self.env['bes.institute'].search([('id','=',self.env.context.get('active_ids'))])        
        print('institutes')
        print(institutes)
        for institute in institutes:
            institute_id = institute
            
            # import wdb; wdb.set_trace()
            for course in institute.courses:
                if course.course.course_code == 'GP':
                    if course.batcher_per_year == 1: 
                        print('batcher_per_year')
                        if self.exam_batch_name == 'jan':
                            print('jan')
                            self.batch_name = 'Jan - June'
                            self.env['institute.gp.batches'].create({
                                "dgs_batch": self.dgs_batch.id,
                                "institute_id":institute_id.id,
                                "batch_name":str(course.course.course_code)+"/"+self.batch_name+' '+self.from_date.strftime('%Y'),
                                "from_date" : self.from_date,
                                "to_date":self.to_date,
                                "course":course.course.id
                            })
                    elif course.batcher_per_year > 1:
                            if self.exam_batch_name == 'july':
                                print('July')
                                # import wdb; wdb.set_trace()
                                self.batch_name = 'July - Dec'
                                self.env['institute.gp.batches'].create({
                                    "dgs_batch": self.dgs_batch.id,
                                    "institute_id":institute_id.id,
                                    "batch_name":str(course.course.course_code)+"/"+self.batch_name+' '+self.from_date.strftime('%Y'),
                                    "from_date" : self.from_date,
                                    "to_date":self.to_date,
                                    "course":course.course.id
                            })
                elif course.course.course_code == 'CCMC':
                    if course.batcher_per_year == 1: 
                        if self.exam_batch_name == 'jan':
                            self.batch_name = 'Jan - June'
                            self.env['institute.ccmc.batches'].create({
                                "institute_id":institute_id.id,
                                "ccmc_batch_name":str(course.course.course_code)+"/"+self.batch_name+' '+self.from_date.strftime('%Y'),
                                "ccmc_from_date" : self.from_date,
                                "ccmc_to_date":self.to_date,
                                "ccmc_course":course.course.id
                            })
                    elif course.batcher_per_year > 1:
                            if self.exam_batch_name == 'july':
                                self.batch_name = 'July - Dec'
                                self.env['institute.ccmc.batches'].create({
                                    "institute_id":institute_id.id,
                                    "ccmc_batch_name":str(course.course.course_code)+"/"+self.batch_name+' '+self.from_date.strftime('%Y'),
                                    "ccmc_from_date" : self.from_date,
                                    "ccmc_to_date":self.to_date,
                                    "ccmc_course":course.course.id
                                })
                    