from math import ceil
from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
import base64
from io import BytesIO
import xlsxwriter
from datetime import datetime
import xlrd
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)



    
class IVAttendanceSheet(models.Model):
    _name = "iv.attendance.sheet"
    _description= 'IV Attendance Sheet'

    _rec_name = "candidate_name"
    
    candidate_name = fields.Many2one('iv.candidates',string="Candidate Name", store=True)

    batch_id = fields.Many2one(
        'iv.batches', 
        string="IV Batch", 
       
    )
    
    roll_no = fields.Char(string="Roll No.")
    grade_applied = fields.Selection([
        ('1CM', 'First Class Master'),
        ('2CM', 'Second Class Master'),
        ('SER', 'Serang'),
        ('ME', 'Motor Engineer'),
        ('1ED', 'First Class Engine Driver'),
        ('2ED', 'Second Class Engine Driver'),
        ], string='Grade')

    dob = fields.Date(string="Date of Birth")
    
    indos_no = fields.Char(string="Indos No")

    candidate_signature = fields.Binary(string="Candidate Signature")
    classroom_no = fields.Char("Classroom No")
   

   
    # def action_print_bulk_attendance(self):
    #     # Logic to handle the printing of bulk allotment data
    #     return self.env.ref('bes.reports_iv_written_attendance').report_action(self)

    def print_report(self):
        return self.env.ref('bes.action_report_iv_attendance_sheet').report_action(self)

    def open_classroom_assignment_wizard(self):
        """Open the wizard and pass active_ids."""
        return {
            'name': 'Assign Classroom',
            'type': 'ir.actions.act_window',
            'res_model': 'iv.class.assignment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_model': self._name,  # Pass the current model
                'active_ids': self.ids,  # Pass selected record IDs
            },
        }
    


    
    

    def generate_written_marksheets(self):
        for record in self:
            record.env['iv.written.exam'].sudo().create({
                'candidate':record.candidate_name.id,
                'batch_id':record.batch_id.id,
                'grade':record.grade_applied,
                'roll_no':record.roll_no,
                'indos_no':record.indos_no
            })

    def create_invigilator_record(self):
        active_ids = self._context['active_ids']
        records = []

        candidates_1cm = 0
        candidates_2cm = 0
        candidates_ser = 0
        candidates_eng = 0
        candidates_1ed = 0
        candidates_2ed = 0
        for candidate_id in active_ids:
            records.append(self.env['iv.attendance.sheet'].sudo().search([('id','=',candidate_id)]))
        for record in records:
            if record.grade_applied == '1CM':
                candidates_1cm += 1
            if record.grade_applied == '2CM':
                candidates_2cm += 1
            if record.grade_applied == 'SER':
                candidates_ser += 1
            if record.grade_applied == 'ME':
                candidates_eng += 1
            if record.grade_applied == '1ED':
                candidates_1ed += 1
            if record.grade_applied == '2ED':
                candidates_2ed += 1
        # import wdb; wdb.set_trace(); 
        


        return {
            'type': 'ir.actions.act_window',
            'name': 'Invigilator Wizard',
            'view_mode': 'form',
            'res_model': 'iv.invigilator.assignment.wizard',
            'target': 'new',
            'context': {'default_batch_id': self.batch_id.id,'default_classroom_no':int(self[0].classroom_no),'candidates_1cm':candidates_1cm,
                        'candidates_2cm':candidates_2cm,
                        'candidates_ser':candidates_ser,
                        'candidates_eng':candidates_eng,
                        'candidates_1ed':candidates_1ed,
                        'candidates_2ed':candidates_2ed}
        }



    
class IvinvigilatorAssignmentWizard(models.TransientModel):
    _name='iv.invigilator.assignment.wizard'

    classroom_capacity = fields.Integer("Classroom Capacity")
    # classroom_no = fields.Integer("Classroom No")
    # batch_id = fields.Many2one('iv.batches')
    invigilators = fields.One2many('invigilator.assignment.lines','parent_id',string="Invigilators")
    

    def generate_invigilators_records(self):
        classroom_no = self._context['default_classroom_no']
        batch_id = int(self._context['default_batch_id'])
        candidates_1cm = self._context['candidates_1cm']
        candidates_2cm = self._context['candidates_2cm']
        candidates_ser = self._context['candidates_ser']
        candidates_eng = self._context['candidates_eng']
        candidates_1ed = self._context['candidates_1ed']
        candidates_2ed = self._context['candidates_2ed']

        for record in self:
            invigilators_data = [
                (0, 0, {'invigilator': inv.invigilator.id})  # Prepare a new One2many record
                for inv in record.invigilators if inv.invigilator
            ]
            record.env['iv.invigilator.sheet'].sudo().create({
                'classroom_no': classroom_no,
                'classroom_capacity': record.classroom_capacity,
                'batch_id': batch_id,
                'candidates_1cm': candidates_1cm,
                'candidates_2cm': candidates_2cm,
                'candidates_ser': candidates_ser,
                'candidates_eng': candidates_eng,
                'candidates_1ed': candidates_1ed,
                'candidates_2ed': candidates_2ed,
                'invigilators': invigilators_data,  # Create One2many records
            })


class InvigilatorAssignmentLine(models.TransientModel):
    _name='invigilator.assignment.lines'

    parent_id = fields.Many2one('iv.invigilator.assignment.wizard')
    invigilator = fields.Many2one('res.partner',"Invigilator",domain=[('category_id.name', 'ilike', 'Invigilator')])

import logging
class IVWrittenAttendance(models.AbstractModel):
    _name = 'report.bes.reports_iv_written_attendance_sheet1'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
  
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['iv.attendance.sheet'].sudo().browse(docids)

        grade_order = ['1CM', '2CM', 'SER', 'ME', '1ED', '2ED']
        
        # Sort the records based on the grade_applied field
        sorted_docs = docs.sorted(
            key=lambda r: grade_order.index(r.grade_applied) if r.grade_applied in grade_order else len(grade_order)
        )

        
        total_records = len(docs)
        records_per_page_pattern = [20, 8]  
        total_pages = 0
        page_splits = []
        
        remaining_records = total_records
        current_start_index = 0

        while remaining_records > 0:
            records_on_this_page = records_per_page_pattern[total_pages % 2]  
            records_on_this_page = min(records_on_this_page, remaining_records)  

            page_splits.append({
                'start': current_start_index,
                'end': current_start_index + records_on_this_page,
            })

            current_start_index += records_on_this_page
            remaining_records -= records_on_this_page
            total_pages += 1

        return {
            'docids': docids,
            'doc_model': 'iv.attendance.sheet',
            'data': data,
            'docs': sorted_docs,
            'page_splits': page_splits,
            'total_pages': total_pages,
        }


class IvClassAssignmentWizard(models.TransientModel):
    _name='iv.class.assignment.wizard'

    classroom_assign = fields.Integer("Classroom No")

    
   
    def assign_classroom(self):
        """Assign the classroom to selected attendance sheets."""
        # Retrieve active model and record IDs from context
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids')

        if active_model and active_ids:
            # Browse the selected records and update them
            recordset = self.env[active_model].browse(active_ids)
            recordset.write({'classroom_no': self.classroom_assign})





    