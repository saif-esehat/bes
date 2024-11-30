from odoo import api, fields, models , _, exceptions
import base64
import binascii
from datetime import datetime, timedelta

class TimeSheetReport(models.Model):
    _name = 'time.sheet.report'
    _description = 'Time Sheet Report'

    examiner_assignment = fields.Many2one('exam.type.oral.practical.examiners',"Examiner Assignment")
    examiner = fields.Many2one('bes.examiner',related='examiner_assignment.examiner', string="Examiner",tracking=True)
    institutes_id = fields.Many2one('bes.institute',related='examiner_assignment.institute_id',string='Name of Institute', tracking=True)
    dgs_batch = fields.Many2one('dgs.batches',related='examiner_assignment.dgs_batch',string='DGS Batch', tracking=True)
    exam_date = fields.Date("Exam Date",tracking=True,related='examiner_assignment.exam_date')

    place = fields.Char(string='Place')
    timesheet_examinations = fields.One2many('timesheet.lines', 'time_sheet_id', string="Timesheet for Examinations")
    travel_details = fields.One2many('travel.details', 'time_sheet_id', string="Travel Details")
    custom_form = fields.One2many('custom.form', 'time_sheet_id', string="Custom Form")
    expense_sheet = fields.Many2one('hr.expense.sheet','Expense')

    total_expenses = fields.Integer(string="Total Expenses", compute='_compute_total_expenses',store=True)

    approval_status = fields.Selection([
        ('ceo_approved', 'CEO Approved'),
        ('rejected_ceo', 'Rejected by CEO'),
        ('approved_ec', 'EC Approved'),
        ('pending','Pending')
    ], string='State', default='pending')
    
    reject_reason = fields.Text("Reject Reason")

    
    @api.depends('travel_details.expenses')
    def _compute_total_expenses(self):
        for record in self:
            record.total_expenses = sum(detail.expenses for detail in record.travel_details)

    
class TimesheetLines(models.Model):
    _name = 'timesheet.lines'

    time_sheet_id = fields.Many2one('time.sheet.report')

    arrival_date_time = fields.Datetime(string='Date & Time of arrival at the Institute')
    commence_exam = fields.Datetime(string="Commencement of Practical/Oral Examination")
    completion_time = fields.Datetime(string='Time of completion')
    lunch_break = fields.Datetime(string='Lunch Break')
    candidate_examined = fields.Integer(string='No.of candidates examined',related='time_sheet_id.examiner_assignment.candidates_count')
    debriefing_inst = fields.Integer(string='Time spent for debriefing the Institute (Last day of examination):')
    travel_details = fields.One2many('travel.details', 'time_sheet_id', string="Travel Details")

class TravelDetails(models.Model):
    _name = 'travel.details'
    _description = 'Travel Details'

    time_sheet_id = fields.Many2one('time.sheet.report', string="Parent Id")
    travelling_details = fields.Char(string='Travelling Details')
    date_time = fields.Datetime(string='Date & Time')
    mode_of_travel = fields.Char(string='Mode of travel')
    expenses = fields.Float(string='Expenses (if incurred)')
    supporting_document = fields.Binary(string="Supporting Document")
    supporting_document_filename = fields.Char(string="Document Filename")
    timesheet_examinations = fields.Many2one('timesheet.lines')
    remark = fields.Text(string='Remark')

    @api.model
    def create_travel_lines(self, timesheet_id,time_line_id, kw):
        """
        Create lines for each travel phase using direct creation for each predefined phase.
        The `kw` parameter contains the form data.
        """
        # Predefined phases with dynamic data (DateTime, Mode of Travel, Expense)
        travel_phases = [
            ('Left Residence', datetime.strptime(kw.get('left_residence_date_time'), '%Y-%m-%dT%H:%M'), kw.get('left_residence_mode_of_travel'), kw.get('left_residence_expenses'),kw.get('supporting_document_left_residence')),
            ('Arrival at the Institute/Hotel', datetime.strptime(kw.get('arrival_institute_hotel_date_time'), '%Y-%m-%dT%H:%M'), kw.get('arrival_institute_hotel_mode_of_travel'), kw.get('arrival_institute_hotel_expenses'),kw.get('supporting_document_arrival_institute')),
            ('Left Institute/Hotel', datetime.strptime(kw.get('left_institute_date_time'), '%Y-%m-%dT%H:%M'), kw.get('left_institute_mode_of_travel'), kw.get('left_institute_expenses'),kw.get('supporting_document_left_institute')),
            ('Arrival at Residence', datetime.strptime(kw.get('arrival_residence_date_time'), '%Y-%m-%dT%H:%M'), kw.get('arrival_residence_mode_of_travel'), kw.get('arrival_residence_expenses'),kw.get('supporting_document_arrival_residence'))
        ]

        # Loop through each travel phase and create a travel detail line
        for detail, date_time, mode_of_travel, expenses, supporting_document in travel_phases:
            travel_details = self.env['travel.details'].sudo().create({
                'time_sheet_id': timesheet_id,
                'timesheet_examinations': time_line_id,
                'travelling_details': detail,
                'date_time': date_time,
                'mode_of_travel': mode_of_travel,
                'expenses': expenses,
            })

            # Handle the supporting document
            if supporting_document:
                # Check if the supporting_document is base64 or file-like object
                if isinstance(supporting_document, str):
                    # If it's a string, assume it's base64 encoded
                    # filename = supporting_document.filename
                    travel_details.sudo().write({
                        'supporting_document': base64.b64encode(supporting_document.encode('utf-8')),
                        # 'supporting_document_filename': filename
                    })
                else:
                    # If it's a file-like object, read its content and encode it in base64
                    file_content = supporting_document.read()
                    # filename = supporting_document.filename
                    travel_details.sudo().write({
                        'supporting_document': base64.b64encode(file_content),
                        # 'supporting_document_filename': filename
                    })

    
class CustomForm(models.Model):
    _name = 'custom.form'
    _description = 'Custom Form'

    time_sheet_id = fields.Many2one('time.sheet.report', string="Parent Id")
    remarks = fields.Text(string='Remark')
    transport_logistics = fields.Text(string='Remark on the quality of transport and logistics')
    examiner_name = fields.Char(string='Name of the Examiner')
    co_ordinator_name = fields.Char(string='Name of the Examination Co-Ordinator')
    bills_attached = fields.Boolean(string="Bills to be attached")
