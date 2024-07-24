from odoo import models, fields

class TimeSheetReport(models.Model):
    _name = 'time.sheet.report'
    _description = 'Time Sheet Report'

    institutes_id = fields.Many2one('bes.institute',string='Name of Institute', default=False, tracking=True)
    place = fields.Char(string='Place')
    exam_date = fields.Char(string='Date of Examination')
    timesheet_examinations = fields.One2many('timesheet.lines', 'parent_id', string="Timesheet for Examinations")
    travel_details = fields.One2many('travel.details', 'parent_id', string="Travel Details")
    custom_form = fields.One2many('custom.form', 'parent_id', string="Custom Form")
    examiner = fields.Many2one('bes.examiner',"Examiner")
    expense_sheet = fields.Many2one('hr.expense.sheet','Expense')

class TimesheetLines(models.Model):
    _name = 'timesheet.lines'

    parent_id = fields.Many2one('time.sheet.report')
    arrival_date_time = fields.Datetime(string='Date & Time of arrival at the Institute')
    commence_exam = fields.Datetime(string="Commencement of Practical/Oral Examination")
    completion_time = fields.Datetime(string='Time of completion')
    lunch_break = fields.Datetime(string='Lunch Break')
    candidate_examined = fields.Integer(string='No.of candidates examined')
    debriefing_inst = fields.Integer(string='Time spent for debriefing the Institute (Last day of examination):')

class TravelDetails(models.Model):
    _name = 'travel.details'
    _description = 'Travel Details'

    parent_id = fields.Many2one('time.sheet.report', string="Parent Id")
    left_residence = fields.Datetime(string='Left Residence')
    arrival_institute_hotel = fields.Datetime(string='Arrival at the Institute/Hotel')
    left_institute_hotel = fields.Datetime(string='Left the Institute/Hotel')
    arrival_residence = fields.Datetime(string='Arrival at Residence')
    mode_of_travel = fields.Selection([
        ('bus',"Bus"),
        ('cab',"Cab"),
        ('railway',"Railways"),
        ('airline',"Airline")
    ],string='Mode of Travel',default="bus")
    expenses = fields.Float(string='Expenses (if incurred)')

class CustomForm(models.Model):
    _name = 'custom.form'
    _description = 'Custom Form'

    parent_id = fields.Many2one('time.sheet.report', string="Parent Id")
    remarks = fields.Text(string='Remark')
    transport_logistics = fields.Text(string='Remark on the quality of transport and logistics')
    examiner_name = fields.Char(string='Name of the Examiner')
    co_ordinator_name = fields.Char(string='Name of the Examination Co-Ordinator')
    bills_attached = fields.Boolean(string="Bills to be attached")
