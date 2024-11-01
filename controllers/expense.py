from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import db_monodb, request, root
from odoo import fields
from odoo import http
from werkzeug.utils import secure_filename
import base64
from datetime import datetime, timedelta
from odoo.service import security
from odoo.exceptions import UserError,ValidationError


class ExpenseController(http.Controller):

    @http.route(['/my/assignments/batches/expenses/<int:assignment_id>'], type="http", auth="user", website=True)
    def ExpenseSheet(self,assignment_id, **kw):
        expense_sheet = request.env['exam.type.oral.practical.examiners'].sudo().search([('id','=',assignment_id)]).expense_sheet
        product_id = request.env['product.product'].sudo().search([('can_be_expensed','=',True),('default_code','not in',('gsk_exam','gsk_online_exam','ccmc_exam','mek_exam','EXP_GEN'))])

        exam_date = request.env['exam.type.oral.practical.examiners'].sudo().search([('id','=',assignment_id)]).exam_date
        # import wdb;wdb.set_trace();
        vals = {'expense_sheet':expense_sheet , 'product_ids':product_id ,'assignment_id':assignment_id,'exam_date':exam_date}
        return request.render("bes.examiner_expenses",vals)
    
    @http.route(['/my/assignments/batches/addexpenses/submit'], type="http", auth="user", website=True)
    def SubmitExpense(self, **kw):
        # {'assignment_id': '18', 'expensesheet_id': '9'}

        expensesheet_id = kw.get('expensesheet_id')
        assignment_id = kw.get('assignment_id')
        # import wdb;wdb.set_trace();
        request.env['hr.expense.sheet'].sudo().search([('id','=',expensesheet_id)]).action_submit_sheet()
        # vals = {}
        return request.redirect('my/assignments/batches/expenses/'+str(assignment_id))
        # return request.render("bes.examiner_expenses",vals)
    
    @http.route(['/my/assignments/batches/addexpenses'], type="http", auth="user", website=True)
    def AddExpense(self, **kw):
        
        attachments = request.httprequest.files.getlist('attachments[]')
        expense_date = kw.get('expense_date')
        product_id = kw.get('product_id')
        unit_price = kw.get('unit_price')
        name = kw.get('name').title()
        employee_id = kw.get('modal_employee_id')
        expensesheet_id = kw.get('expensesheet_id')
        assignment_id = kw.get('assignment_id')
        
        expense = request.env['hr.expense'].sudo().create(
                                {'product_id': product_id, 'employee_id': employee_id,'name':name,'unit_amount': unit_price ,'quantity': 1 }
                            )
        # import wdb;wdb.set_trace();
        request.env['hr.expense.sheet'].sudo().search([('id','=',expensesheet_id)]).write({
            'expense_line_ids': [(4, expense.id)]
        })
        
        

            
        if not attachments[0].filename:
            
            print("File Not Present")
            
        else:
            for attachment in attachments:
                file_content = attachment.read()
                filename = attachment.filename
                request.env['ir.attachment'].sudo().create({'res_model':'hr.expense','res_id':expense.id,'datas':base64.b64encode(file_content),'name': filename })
            


        
        
        return request.redirect('my/assignments/batches/expenses/'+str(assignment_id))
    
    @http.route(['/my/assignments/timesheet/<int:batch_id>/<int:assignment_id>'], type="http", auth="user", website=True)
    def TimeSheet(self,batch_id,assignment_id, **kw):

        user_id = request.env.user.id
        examiner = request.env['bes.examiner'].sudo().search([('user_id','=',user_id)])

        assignment = request.env['exam.type.oral.practical.examiners'].sudo().search([('id','=',assignment_id)])
        timesheets = request.env['time.sheet.report'].sudo().search([('examiner_assignment','=',assignment.id)])
        
        # Get associated institute and duty records
        exam_duty = request.env['exam.type.oral.practical'].sudo().search([('dgs_batch.id', '=', batch_id), ('institute_id', '=', assignment.institute_id.id)])

        # Collect all exam dates for the examiner's assignments
        exam_dates = []
        for exam in exam_duty:
            assignments = request.env['exam.type.oral.practical.examiners'].sudo().search([
                ('prac_oral_id', '=', exam.id),
                ('examiner', '=', examiner.id)
            ])
            exam_dates.extend(assignments.mapped('exam_date'))

        # Determine the first and last dates
        first_date = min(exam_dates) if exam_dates else None
        last_date = max(exam_dates) if exam_dates else None
        
        vals = {
            'timesheets': timesheets,
            'assignment':assignment,
            'batch_id':batch_id,
            'examiner_id':examiner.id,
            'exam_date':kw.get('exam_date'),
            'first_date':first_date,
            'last_date':last_date,
            'page_name': 'timesheet'
                }
        return request.render("bes.timesheet_form", vals)

    # @http.route(['/my/assignments/batches/timesheet/add'], methods=['POST','GET'],type="http", auth="user", website=True)
    # def TimeSheetAdd(self, **kw):

    #     user_id = request.env.user.id
    #     examiner = request.env['bes.examiner'].sudo().search([('user_id','=',user_id)])

    #     institute_id = request.env['bes.institute'].sudo().search([('id','=',kw.get('institute_id'))])
    #     dgs_batch = request.env['dgs.batches'].sudo().search([('id','=',kw.get('dgs_batch'))])

    #     # import wdb;wdb.set_trace();
    #     timesheet = request.env['time.sheet.report'].sudo().create({
    #         'examiner': examiner.id,
    #         'dgs_batch': dgs_batch.id,
    #         'institutes_id': institute_id.id
    #     })

    #     # return request.redirect('/my/assignments/timesheet/'+str(dgs_batch.id) +'/' +str(examiner.id))
    #     return request.redirect('/my/assignments/timesheet/list/'+str(timesheet.id))

    
    # @http.route(['/my/assignments/timesheet/list/<int:timesheet_id>'], type="http", auth="user", website=True)
    # def TimeSheetLists(self,timesheet_id, **kw):
    #     # import wdb;wdb.set_trace();
    #     user_id = request.env.user.id
    #     examiner = request.env['bes.examiner'].sudo().search([('user_id','=',user_id)])

    #     timesheets = request.env['time.sheet.report'].sudo().search([('id','=',timesheet_id)])
    #     institute_id = timesheets.institutes_id
    #     dgs_batch = timesheets.dgs_batch
    #     assignments = request.env['exam.type.oral.practical.examiners'].sudo().search([
    #         ('dgs_batch','=',dgs_batch.id),('examiner','=',examiner.id),('institute_id','=',institute_id.id)])

    #     # Assuming first_exam_date and last_exam_date are datetime objects
    #     def generate_date_range(first_exam_date, last_exam_date):
    #             # Assuming the format of your date strings is 'YYYY-MM-DD'
    #         date_format = '%d-%m-%Y'

    #         # Convert the strings to datetime objects
    #         first_exam_date = datetime.strptime(first_exam_date, date_format).date()
    #         last_exam_date = datetime.strptime(last_exam_date, date_format).date()

    #         # Now calculate the delta
    #         delta = last_exam_date - first_exam_date
    #         date_list = [first_exam_date + timedelta(days=i) for i in range(delta.days + 1)]
    #         return date_list
        

    #     exam_dates = assignments.mapped('exam_date')  # Get a list of exam dates
    #     first_exam_date = exam_dates[0].strftime('%d-%m-%Y') if exam_dates else None
    #     last_exam_date = exam_dates[-1].strftime('%d-%m-%Y') if exam_dates else None
    #     exam_days = generate_date_range(first_exam_date, last_exam_date)

    #     vals = {
    #         'assignments':assignments,
    #         'timesheets': timesheets,
    #         'institute':institute_id,
    #         'dgs_batch':dgs_batch,
    #         'examiner':examiner,
    #         'first_exam_date': first_exam_date,
    #         'last_exam_date': last_exam_date,
    #         'exam_days': exam_days,
    #         'page_name': 'institute_timesheets'
    #         }
    #     return request.render("bes.timesheet_display", vals)
    
    @http.route('/my/assignments/batches/timesheet/submit', type='http', auth='user', methods=['POST'], website=True)
    def submit_timesheet(self, **kw):
        # import wdb;wdb.set_trace();
        user_id = request.env.user.id
        examiner = request.env['bes.examiner'].sudo().search([('user_id','=',user_id)])

        assignment = request.env['exam.type.oral.practical.examiners'].sudo().search([('id','=',kw.get('assign_id'))])

        # Get all dates for this examiner assignment to determine first and last dates
        exam_dates = assignment.mapped('exam_date')
        first_date = min(exam_dates) if exam_dates else None
        last_date = max(exam_dates) if exam_dates else None
        
        timesheet = request.env['time.sheet.report'].sudo().create({
            'examiner_assignment': assignment.id,
        })

        assignment.time_sheet = timesheet.id

        # Check if the current date matches either first or last date before creating timesheet lines
        
        timesheet_line = request.env['timesheet.lines'].sudo().create({'time_sheet_id': timesheet.id})
        timesheet_line.write({
            'arrival_date_time': datetime.strptime(kw.get('arrival_time'), '%Y-%m-%dT%H:%M'),
            'commence_exam': datetime.strptime(kw.get('commencement_time'), '%Y-%m-%dT%H:%M'),
            'completion_time': datetime.strptime(kw.get('completion_time'), '%Y-%m-%dT%H:%M'),
            'candidate_examined': kw.get('candidates_examined'),
            'debriefing_inst': kw.get('debriefing_time'),
        })

        # travel_details = request.env['travel.details'].sudo().create({'time_sheet_id': timesheet.id})
        # Dynamically create travel lines using predefined phases
        if kw.get('left_residence_date_time') and kw.get('arrival_institute_hotel_date_time') and kw.get('left_institute_date_time') and kw.get('arrival_residence_date_time'):
            request.env['travel.details'].sudo().create_travel_lines(timesheet.id, kw)
        else:
            pass


        return request.redirect('/my/assignments/timesheet/'+str(assignment.dgs_batch.id) +'/' +str(assignment.id))
    