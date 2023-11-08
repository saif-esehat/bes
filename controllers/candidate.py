from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request
from odoo import http
from werkzeug.utils import secure_filename
import base64



class GPCandidatePortal(CustomerPortal):
    
    @http.route(['/my/gpexam/list'],type="http",auth="user",website=True)
    def GPExamListView(self,**kw):
        partner_id = request.env.user.partner_id.id
        registered_exams = request.env["survey.user_input"].sudo().search([('partner_id','=',partner_id)])
        # import wdb; wdb.set_trace(); 
        vals = {"registered_exams":registered_exams}
        return request.render("bes.gp_exam_list_view", vals)
    
    
    
    @http.route(['/my/gpexam/startexam'],type="http",auth="user",website=True)
    def StartExam(self,**kw):
        partner_id = request.env.user.partner_id.id
        registered_exam = request.env["survey.user_input"].sudo().search([('id','=',kw.get("id"))])

        exam_url = registered_exam.survey_id.survey_start_url
        identification_token = registered_exam.access_token
        # vals = {}
        return request.redirect(exam_url+"?answer_token="+identification_token)