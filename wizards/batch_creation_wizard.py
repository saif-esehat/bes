from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError

class BatchWizard(models.TransientModel):
    _name = 'create.institute.batches.wizard'
    _description = 'Create Batches Wizard'
    
    dgs_batch = fields.Many2one("dgs.batches", string="Exam Batch")
    batch_name = fields.Char("Batch Name")
    exam_batch_name = fields.Selection([
        ('jan', 'Jan - June'),
        ('july', 'July - Dec'),
    ], string="Batch Name")
    from_date = fields.Date("From Date")
    to_date = fields.Date("To Date")
    
    def create_batches(self):
        institutes = self.env['bes.institute'].search([('id', '=', self.env.context.get('active_ids'))])
        created_batches = []
        unique_gp_institutes = set()
        unique_ccmc_institutes = set()

        duplicate_institutes = []  # Initialize list for duplicate institute names

        for institute in institutes:
            for course in institute.courses:
                batch_model = None
                # Determine the appropriate batch model based on course code
                if course.course.course_code == 'GP':
                    batch_model = 'institute.gp.batches'
                elif course.course.course_code == 'CCMC':
                    batch_model = 'institute.ccmc.batches'

                # Define batch name based on selection
                if self.exam_batch_name == 'jan':
                    self.batch_name = 'Jan - June'
                elif self.exam_batch_name == 'july':
                    self.batch_name = 'July - Dec'

                # Build the full batch name (e.g., GP/Jan - June 2024)
                full_batch_name = f"{course.course.course_code}/{self.batch_name} {self.from_date.strftime('%Y')}"

                # Validation: Check if batch with the same name, start date, and end date exists
                if batch_model == 'institute.ccmc.batches':
                    existing_batch = self.env[batch_model].search([
                        # ('ccmc_batch_name', '=', full_batch_name),
                        ('institute_id', '=', institute.id),
                        # ('ccmc_from_date', '=', self.from_date),
                        # ('ccmc_to_date', '=', self.to_date),
                        ('dgs_batch', '=', self.dgs_batch.id)  # Check uniqueness of dgs_batch.id
                    ])
                else:
                    existing_batch = self.env[batch_model].search([
                        # ('batch_name', '=', full_batch_name),
                        ('institute_id', '=', institute.id),
                        # ('from_date', '=', self.from_date),
                        # ('to_date', '=', self.to_date),
                        ('dgs_batch', '=', self.dgs_batch.id)  # Check uniqueness of dgs_batch.id
                    ])
                
                # Check for existing batch and add to duplicates
                if existing_batch:
                    duplicate_institutes.append(institute.name + ' - ' + course.course.course_code)  # Add institute name to list
                else:
                    # Create batch if no duplicates found
                    if batch_model == 'institute.ccmc.batches':
                        batch_data = {
                            "dgs_batch": self.dgs_batch.id,
                            "institute_id": institute.id,
                            "ccmc_batch_name": full_batch_name,
                            "ccmc_from_date": self.from_date,
                            "ccmc_to_date": self.to_date,
                            "ccmc_course": course.course.id
                        }
                    else:
                        batch_data = {
                            "dgs_batch": self.dgs_batch.id,
                            "institute_id": institute.id,
                            "batch_name": full_batch_name,
                            "from_date": self.from_date,
                            "to_date": self.to_date,
                            "course": course.course.id
                        }

                    # Create the batch
                    self.env[batch_model].create(batch_data)
                    created_batches.append(f"{institute.name} - {course.course.course_code} - {self.batch_name} - {self.from_date.strftime('%Y')}")

                    # Track unique institutes for reporting
                    if course.course.course_code == 'GP':
                        unique_gp_institutes.add(institute.id)
                    elif course.course.course_code == 'CCMC':
                        unique_ccmc_institutes.add(institute.id)

        # If there are any duplicate batches, raise a validation error
        if duplicate_institutes:
            duplicate_list_str = ', '.join(duplicate_institutes)
            raise ValidationError(f"The batch '{full_batch_name}' already exists for the following institute(s) with the same dates: {duplicate_list_str}")

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
