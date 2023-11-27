from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request
from odoo import http
from werkzeug.utils import secure_filename
import base64
import csv
import io
from io import StringIO
from datetime import datetime
import xlsxwriter
from odoo.exceptions import AccessError
from functools import wraps


def check_user_groups(group_xml_id):
    def decorator(func):
        @wraps(func)
        def wrapper(self,*args, **kwargs):
            if not request.env.user.has_group(group_xml_id):
                raise AccessError("You Do not have Access")
            return func(self,*args, **kwargs)
        return wrapper
    return decorator




class ExaminerPortal(CustomerPortal):
    
    @http.route(['/my/examiner/online_exam'],type="http",auth="user",website=True)
    @check_user_groups("bes.group_examiners")
    def ExamListView(self,**kw):
        user_id = request.env.user.id
        examiner_id = request.env["bes.examiner"].sudo().search(
            [('user_id', '=', user_id)]).id
        
        survey = request.env["survey.survey"].sudo().search(
            [('examiner', '=', examiner_id)])
        
        vals = {"surveys":survey}
        
        return request.render("bes.examiner_portal_online_exam_list", vals)
    
    @http.route(['/my/examiner/online_exam/start/<int:survey_id>'],type="http",auth="user",website=True)
    @check_user_groups("bes.group_examiners")
    def ExamStart(self,survey_id,**kw):
        
        survey = request.env["survey.survey"].sudo().search([('id', '=', survey_id)])
        survey.write({"exam_state":"in_progress"})        
        return request.redirect("/my/examiner/online_exam")
    
    @http.route(['/my/examiner/online_exam/stop/<int:survey_id>'],type="http",auth="user",website=True)
    @check_user_groups("bes.group_examiners")
    def ExamStop(self,survey_id,**kw):
        
        survey = request.env["survey.survey"].sudo().search([('id', '=', survey_id)])
        survey.write({"exam_state":"stopped"})        
        return request.redirect("/my/examiner/online_exam")


    @http.route(['/my/assignments'], type="http", auth="user", website=True)
    def ExaminerAssignmentListView(self, **kw):
        # import wdb; wdb.set_trace()

        user_id = request.env.user.id
        
        examiner_assignments = request.env['bes.examiner'].sudo().search([('user_id','=',user_id)]).assignments
        vals = {'assignments':examiner_assignments}
        # self.env["gp.candidate"].sudo().search([('')])
        return request.render("bes.examiner_assignment_list", vals)

    
    
    # def check_user_groups(group_xml_id):
    #     ​def decorator(func):
    #     ​	​def wrapper(self, *args, **kwargs):
    #     ​	​	​if not request.env.user.has_group(group_xml_id):
    #     ​	​	​	​raise AccessError("You do not have access rights to view this page.")
    #     ​	​	​return func(self, *args, **kwargs)
    #     ​	​return wrapper
    #     ​return decorator
    @http.route('/open_candidate_form', type='http', auth="user", website=True)
    def open_candidate_form(self, **kw):
        rec_id = kw.get('rec_id')
        # print('candidateeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',rec_id)
        assignment = request.env['examiner.assignment'].sudo().browse(int(rec_id))

        # Check if gp_candidate is set
        if assignment.assigned_to == "gp_candidate":
            candidate = assignment.gp_candidates
        # Check if ccmc_candidate is set
        elif assignment.assigned_to == "ccmc_candidate":
            candidate = assignment.ccmc_candidates
        else:
            # Handle the case when both gp_candidate and ccmc_candidate are not set
            candidate = False

        return request.render("bes.examiner_candidate_list", {'candidate': candidate})
    
    
