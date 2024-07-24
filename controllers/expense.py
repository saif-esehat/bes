from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import db_monodb, request, root
from odoo import fields
from odoo import http
from werkzeug.utils import secure_filename
import base64
import datetime
from odoo.service import security


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
    
    @http.route(['/my/assignments/batches/timesheet/<int:assignment_id>'], type="http", auth="user", website=True)
    def TimeSheet(self,assignment_id, **kw):
        # Fetch the timesheet data for the given assignment_id
        timesheets = request.env['time.sheet.report'].sudo().search([('id', '=', assignment_id)])
        assignment = request.env['exam.type.oral.practical.examiners'].sudo().search([('id','=',assignment_id)])
        exam_date = request.env['exam.type.oral.practical.examiners'].sudo().search([('id','=',assignment_id)]).exam_date

        vals = {
            'timesheets': timesheets,
            'exam_date':exam_date,
            'assignment':assignment
                }
        return request.render("bes.timesheet_display", vals)
    
    @http.route(['/my/assignments/batches/timesheet/submit'], type="http", auth="user", methods=['POST'], website=True)
    def submit_time_sheet(self, **kw):
        try:
            # Extract the data from the form
            institute_name = kw.get('institute_name')
            date_examination_from = kw.get('date_examination_from')
            date_examination_to = kw.get('date_examination_to')
            
            # Create TimeSheetReport
            institute = request.env['bes.institute'].search([('name', '=', institute_name)], limit=1)
            if not institute:
                return request.redirect('/my/assignments/batches?error=Institute not found')
            
            timesheet_report = request.env['time.sheet.report'].sudo().create({
                'institutes_id': institute.id,
                # 'exam_dates': f"{date_examination_from} to {date_examination_to}",
                # Add other necessary fields here
            })
            
            # Create TimesheetLines
            for day in range(1, 5):
                request.env['timesheet.lines'].sudo().create({
                    'parent_id': timesheet_report.id,
                    'arrival_date_time': kw.get(f'arrival_institute_day{day}'),
                    'commence_exam': kw.get(f'commencement_exam_day{day}'),
                    'completion_time': kw.get(f'completion_time_day{day}'),
                    # 'lunch_break': kw.get(f'lunch_break_day{day}'),
                    'candidate_examined': kw.get(f'candidates_examined_day{day}'),
                    'debriefing_inst': kw.get('debriefing_time'),
                })
            
            # Create TravelDetails
            request.env['travel.details'].sudo().create({
                'parent_id': timesheet_report.id,
                'left_residence': kw.get('left_residence_date_time'),
                'arrival_institute_hotel': kw.get('arrival_institute_hotel_date_time'),
                'left_institute_hotel': kw.get('left_institute_hotel_date_time'),
                'arrival_residence': kw.get('arrival_residence_date_time'),
                'mode_of_travel': kw.get('arrival_residence_mode_of_travel'),
                'expenses': kw.get('expenses', 0.0),
            })
            
            # Redirect or render a success page
            return request.redirect('/my/assignments/batches?success=true')
        except Exception as e:
            # Log the error and redirect with error message
            # _logger.error('Error in time sheet submission: %s', e)
            return request.redirect('/my/assignments/batches?error=Submission failed')