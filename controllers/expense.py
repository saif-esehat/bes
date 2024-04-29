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
        product_id = request.env['product.product'].sudo().search([('can_be_expensed','=',True),('default_code','not in',('gsk_exam','ccmc_exam','mek_exam','EXP_GEN'))])
        # import wdb;wdb.set_trace();
        
        vals = {'expense_sheet':expense_sheet , 'product_ids':product_id ,'assignment_id':assignment_id}
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
        name = kw.get('name')
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