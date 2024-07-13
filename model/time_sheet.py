from odoo import models, fields

class TimeSheetReport(models.Model):
    _name = 'time.sheet.report'
    _description = 'Time Sheet Report'

    institutes_id = fields.Many2one('bes.institute',string='Name of Institute', default=False, tracking=True)
    place = fields.Char(string='Place')
    exam_dates = fields.Char(string='Date(s) of Examination')
    timesheet_examinations = fields.One2many('timesheet.lines', 'parent_id', string="Timesheet for Examinations")
    travel_details = fields.One2many('travel.details', 'parent_id', string="Travel Details")
    custom_form = fields.One2many('custom.form', 'parent_id', string="Custom Form")
    examiner = fields.Many2one('bes.examiner',"Examiner")

class TimesheetLines(models.Model):
    _name = 'timesheet.lines'

    parent_id = fields.Many2one('time.sheet.report')
    arrival_date_time = fields.Datetime(string='Date & Time of arrival at the Institute')
    online_examination = fields.Char(string='Date/Time of completion')
    completion_time = fields.Datetime(string='Time of completion')
    candidate_examined = fields.Integer(string='No.of candidates examined')

class TravelDetails(models.Model):
    _name = 'travel.details'
    _description = 'Travel Details'

    parent_id = fields.Many2one('time.sheet.report', string="Parent Id")
    left_residence = fields.Datetime(string='Left Residence')
    arrival_institute_hotel = fields.Datetime(string='Arrival at the Institute/Hotel')
    left_institute_hotel = fields.Datetime(string='Left the Institute/Hotel')
    arrival_residence = fields.Datetime(string='Arrival at Residence')
    mode_of_travel = fields.Char(string='Mode of Travel')
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
