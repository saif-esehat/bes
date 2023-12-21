from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request
from odoo import http
from werkzeug.utils import secure_filename
import base64



class GPCandidatePortal(CustomerPortal):
    
    @http.route(['/my/gpexam/list'],type="http",auth="user",website=True)
    def GPExamListView(self,**kwargs):
        parameter_value = kwargs.get('gpexamcand')
        print(parameter_value)

        if parameter_value:
            partner_id = request.env.user.id
            candidate = request.env["gp.candidate"].sudo().search([('user_id','=',partner_id)]).id
            registered_exams = request.env["gp.exam.schedule"].sudo().search([('gp_candidate','=',candidate)])
            print('registered_examsssssssssssssssssssssssssssss',registered_exams)
            candidate = registered_exams
            # import wdb; wdb.set_trace(); 
            vals = {"registered_exams":registered_exams,"candidate":registered_exams.gp_candidate}
            return request.render("bes.gp_exam_candidate", vals)
        else:

            partner_id = request.env.user.partner_id.id
            registered_exams = request.env["survey.user_input"].sudo().search([('partner_id','=',partner_id)])
            # import wdb; wdb.set_trace(); 
            vals = {"registered_exams":registered_exams}
            return request.render("bes.gp_exam_list_view", vals)
        
    
    
    # @http.route(['/my/gpexam/startexam'],type="http",auth="user",website=True)
    # def StartExam(self,**kw):
    #     partner_id = request.env.user.partner_id.id
    #     registered_exam = request.env["survey.user_input"].sudo().search([('id','=',kw.get("id"))])

    #     exam_url = registered_exam.survey_id.survey_start_url
    #     identification_token = registered_exam.access_token
    #     # vals = {}
    #     return request.redirect(exam_url+"?answer_token="+identification_token)
    
    
    
    
    @http.route(['/my/gpexam/startexam'],type="http",auth="user",website=True)
    def VerifyToken(self,**kw):
        partner_id = request.env.user.partner_id.id
        
        survey_input_id = kw.get("survey_input_id")
        examiner_token = kw.get("examiner_token")
        
        # import wdb; wdb.set_trace(); 
        registered_exam = request.env["survey.user_input"].sudo().search([('id','=',survey_input_id)])
        
        survey_examiner_token = registered_exam.survey_id.examiner_token
        
        
        if survey_examiner_token == examiner_token:
            exam_url = registered_exam.survey_id.survey_start_url
            identification_token = registered_exam.access_token
            return request.redirect(exam_url+"?answer_token="+identification_token)
        else:
            
            registered_exams = request.env["survey.user_input"].sudo().search([('partner_id','=',partner_id)])
            # import wdb; wdb.set_trace(); 
            vals = {"registered_exams":registered_exams, "error":"Invalid Examiner Token"}
            
            return request.render("bes.gp_exam_list_view", vals)
            

    @http.route(['/my/gpexam/list/download_admit_card/<int:exam_id>'], method=["POST", "GET"], type="http", auth="user", website=True)
    def DownloadAdmitCard(self,exam_id,**kw ):
        # import wdb; wdb.set_trace()
        # exam_id = request.env['gp.exam.schedule'].sudo().search([('gp_candidate','=',candidate_id)])[-1]
        print("INSIDE DOWNLOAD ADMITCARD")
        report_action = request.env.ref('bes.candidate_gp_admit_card_action')
        pdf, _ = report_action.sudo()._render_qweb_pdf(int(exam_id))
        # print(pdf ,"Tbis is PDF")
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)
            