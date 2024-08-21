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
        # New code
        # Counters for GP and CCMC
        gp_institute_count = 0
        ccmc_institute_count = 0

        # Track unique institutes
        unique_gp_institutes = set()
        unique_ccmc_institutes = set()

        for institute in institutes:
            for course in institute.courses:
                if course.course.course_code == 'GP':
                    if course.batcher_per_year == 1:
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
                            gp_institute_count += 1  # Increment GP counter
                            unique_gp_institutes.add(institute.id)  # Track unique GP institutes
                    elif course.batcher_per_year > 1:
                        # New Code
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
                            gp_institute_count += 1  # Increment GP counter
                            unique_gp_institutes.add(institute.id)  # Track unique GP institutes

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
                            gp_institute_count += 1  # Increment GP counter
                            unique_gp_institutes.add(institute.id)  # Track unique GP institutes
                elif course.course.course_code == 'CCMC':
                    if course.batcher_per_year == 1:
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
                            ccmc_institute_count += 1  # Increment CCMC counter
                            unique_ccmc_institutes.add(institute.id)  # Track unique CCMC institutes
                    elif course.batcher_per_year > 1:
                        # New code
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
                            ccmc_institute_count += 1  # Increment CCMC counter
                            unique_ccmc_institutes.add(institute.id)  # Track unique CCMC institutes

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
                            ccmc_institute_count += 1  # Increment CCMC counter
                            unique_ccmc_institutes.add(institute.id)  # Track unique CCMC institutes
        
        # Count the number of unique institutes
        total_unique_gp_institutes = len(unique_gp_institutes)
        total_unique_ccmc_institutes = len(unique_ccmc_institutes)

        # Create message
        message = (
            f"Batches created for {total_unique_gp_institutes} GP institutes and "
            f"{total_unique_ccmc_institutes} CCMC institutes.\n\n"
            "List of created batches:\n" + "\n".join(created_batches)
        )
        
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
    


class BatchDeleteWizard(models.TransientModel):
    _name = 'batch.delete.wizard'
    _description = 'Batch Delete Confirmation Wizard'

    message = fields.Text(string='Message', readonly=True)
    
    @api.model
    def default_get(self, fields):
        res = super(BatchDeleteWizard, self).default_get(fields)
        # Get the context value for the message
        if self.env.context.get('default_message'):
            res.update({
                'message': self.env.context['default_message']
            })
        return res

    def action_confirm_delete(self):
        # Perform the actual deletion here
        # Get the selected batch IDs from the context
        batch_ids = self.env.context.get('batch_ids')
        if batch_ids:
            if self.env.context.get('active_model') == 'institute.gp.batches':
                batches_to_delete = self.env['institute.gp.batches'].browse(batch_ids)
                batches_to_delete.unlink()
            elif self.env.context.get('active_model') == 'institute.ccmc.batches':
                batches_to_delete = self.env['institute.ccmc.batches'].browse(batch_ids)
                batches_to_delete.unlink()
        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}
