from odoo import api, fields, models , _, exceptions
from datetime import datetime, timedelta

class TimeSheetReport(models.Model):
    _name = 'time.sheet.report'
    _description = 'Time Sheet Report'

    # examiner_assignment = fields.Many2one('exam.type.oral.practical.examiners',"Examiner Assignment")
    examiner = fields.Many2one('bes.examiner', string="Examiner",tracking=True)
    # assignment_id = fields.Many2one('exam.type.oral.practical',related='examiner_assignment.prac_oral_id', string="Assignment ID")
    institutes_id = fields.Many2one('bes.institute',string='Name of Institute', default=False, tracking=True)
    dgs_batch = fields.Many2one('dgs.batches',string='DGS Batch', default=False, tracking=True)
    # exam_date = fields.Date("Exam Date",tracking=True,related='examiner_assignment.exam_date')

    place = fields.Char(string='Place')
    timesheet_examinations = fields.One2many('timesheet.lines', 'time_sheet_id', string="Timesheet for Examinations")
    travel_details = fields.One2many('travel.details', 'time_sheet_id', string="Travel Details")
    custom_form = fields.One2many('custom.form', 'time_sheet_id', string="Custom Form")
    expense_sheet = fields.Many2one('hr.expense.sheet','Expense')

class TimesheetLines(models.Model):
    _name = 'timesheet.lines'

    time_sheet_id = fields.Many2one('time.sheet.report')

    arrival_date_time = fields.Datetime(string='Date & Time of arrival at the Institute')
    commence_exam = fields.Datetime(string="Commencement of Practical/Oral Examination")
    completion_time = fields.Datetime(string='Time of completion')
    lunch_break = fields.Datetime(string='Lunch Break')
    candidate_examined = fields.Integer(string='No.of candidates examined')
    debriefing_inst = fields.Integer(string='Time spent for debriefing the Institute (Last day of examination):')

class TravelDetails(models.Model):
    _name = 'travel.details'
    _description = 'Travel Details'

    time_sheet_id = fields.Many2one('time.sheet.report', string="Parent Id")
    travelling_details = fields.Char(string='Travelling Details')
    date_time = fields.Datetime(string='Date & Time')
    mode_of_travel = fields.Char(string='Mode of travel')
    expenses = fields.Float(string='Expenses (if incurred)')


    @api.model
    def create_travel_lines(self, timesheet_id, kw):
        """
        Create lines for each travel phase using direct creation for each predefined phase.
        The `kw` parameter contains the form data.
        """
        # Predefined phases with dynamic data (DateTime, Mode of Travel, Expense)
        travel_phases = [
            ('Left Residence', datetime.strptime(kw.get('left_residence_date_time'), '%Y-%m-%dT%H:%M'), kw.get('left_residence_mode_of_travel'), kw.get('left_residence_expenses')),
            ('Arrival at the Institute/Hotel', datetime.strptime(kw.get('arrival_institute_hotel_date_time'), '%Y-%m-%dT%H:%M'), kw.get('arrival_institute_hotel_mode_of_travel'), kw.get('arrival_institute_hotel_expenses')),
            ('Left Institute/Hotel', datetime.strptime(kw.get('left_institute_date_time'), '%Y-%m-%dT%H:%M'), kw.get('left_institute_mode_of_travel'), kw.get('left_institute_expenses')),
            ('Arrival at Residence', datetime.strptime(kw.get('arrival_residence_date_time'), '%Y-%m-%dT%H:%M'), kw.get('arrival_residence_mode_of_travel'), kw.get('arrival_residence_expenses'))
        ]

        # Loop through each travel phase and create a travel detail line
        for detail, date_time, mode_of_travel, expenses in travel_phases:
            self.env['travel.details'].sudo().create({
                'time_sheet_id': timesheet_id,
                'travelling_details': detail,
                'date_time': date_time,
                'mode_of_travel': mode_of_travel,
                'expenses': expenses,
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
