from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import db_monodb, request, root
from odoo import fields
from odoo import http
from werkzeug.utils import secure_filename
import base64
import datetime
from odoo.service import security



def _rotate_session(httprequest):
    if httprequest.session.rotate:
        root.session_store.delete(httprequest.session)
        httprequest.session.sid = root.session_store.generate_key()
        if httprequest.session.uid:
            httprequest.session.session_token = security.compute_session_token(
                httprequest.session, request.env
            )
        httprequest.session.modified = True


class GPCandidatePortal(CustomerPortal):
    
    @http.route(['/my/gpexam/list'],type="http",auth="user",website=True)
    def GPExamListView(self,**kwargs):
        parameter_value = kwargs.get('gpexamcand')
        print(parameter_value)
        if parameter_value:
            partner_id = request.env.user.id
            candidate = request.env["gp.candidate"].sudo().search([('user_id','=',partner_id)]).id
            exam_region = request.env["gp.candidate"].sudo().search([('user_id','=',partner_id)]).institute_id.exam_center.name
            institute_code = request.env["gp.candidate"].sudo().search([('user_id','=',partner_id)]).institute_id.code
            registered_exams = request.env["gp.exam.schedule"].sudo().search([('gp_candidate','=',candidate),('state','=','3-certified')])
            
            print('registered_examsssssssssssssssssssssssssssss',registered_exams)
            candidate = registered_exams
            # import wdb; wdb.set_trace(); 
            show_certificate = candidate.state == '3-certified' or False
            show_admit_card = candidate.state == '1-in_process'
            vals = {"registered_exams":registered_exams,"candidate":registered_exams.gp_candidate,"show_certificate":show_certificate,'show_admit_card':show_admit_card,'exam_region':exam_region,'institute_code':institute_code}
            print(vals)
            return request.render("bes.gp_exam_candidate", vals)
        else:

            partner_id = request.env.user.partner_id.id
            registered_exams = request.env["survey.user_input"].sudo().search([('partner_id','=',partner_id)])
            # import wdb; wdb.set_trace(); 
            vals = {"registered_exams":registered_exams}
            return request.render("bes.gp_exam_list_view", vals)
        

    @http.route(['/my/ccmcexam/list'],type="http",auth="user",website=True)
    def CCMCExamListView(self,**kwargs):
        parameter_value = kwargs.get('ccmcexamcand')
        print(parameter_value)

        if parameter_value:
            partner_id = request.env.user.id
            candidate = request.env["ccmc.candidate"].sudo().search([('user_id','=',partner_id)]).id
            # print("candidate",candidate)
            registered_exams = request.env["ccmc.exam.schedule"].sudo().search([('ccmc_candidate','=',candidate)])
            print('registered_examsssssssssssssssssssssssssssss',registered_exams)
            candidate = registered_exams
            # import wdb; wdb.set_trace(); 
            show_certificate = candidate.certificate_criteria == 'passed' or False
            show_admit_card = candidate.state == '1-in_process'
            vals = {"registered_exams":registered_exams,"candidate":registered_exams.ccmc_candidate,"show_certificate":show_certificate,'show_admit_card':show_admit_card}
            return request.render("bes.ccmc_exam_candidate", vals)
        else:

            partner_id = request.env.user.partner_id.id
            registered_exams = request.env["survey.user_input"].sudo().search([('partner_id','=',partner_id)])
            # import wdb; wdb.set_trace(); 
            vals = {"registered_exams":registered_exams}
            return request.render("bes.ccmc_exam_list_view", vals)
    
    
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

    @http.route(['/my/ccmcexam/startexam'],type="http",auth="user",website=True)
    def VerifyTokenCcmc(self,**kw):
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
            
            return request.render("bes.ccmc_exam_list_view", vals)
            

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


    @http.route(['/my/ccmcexam/list/download_admit_card/<int:exam_id>'], method=["POST", "GET"], type="http", auth="user", website=True)
    def DownloadAdmitCardCCMC(self,exam_id,**kw ):
        # import wdb; wdb.set_trace()
        # exam_id = request.env['gp.exam.schedule'].sudo().search([('gp_candidate','=',candidate_id)])[-1]
        print("INSIDE DOWNLOAD ADMITCARD")
        report_action = request.env.ref('bes.candidate_ccmc_admit_card_action')
        pdf, _ = report_action.sudo()._render_qweb_pdf(int(exam_id))
        # print(pdf ,"Tbis is PDF")
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)
    


    @http.route(['/my/gpexam/list/download_certificate/<int:exam_id>'], method=["POST", "GET"], type="http", auth="user", website=True)
    def DownloadCertificateGP(self,exam_id,**kw ):
        # import wdb; wdb.set_trace()
        # exam_id = request.env['gp.exam.schedule'].sudo().search([('gp_candidate','=',candidate_id)])[-1]
        print("INSIDE DOWNLOAD Certificate")
        report_action = request.env.ref('bes.report_gp_certificate')
        # certificate_available = request.env['gp.exam.schedule'].sudo().search([('id','=',exam_id)]).certificate_criteria == 'passed'

        pdf, _ = report_action.sudo()._render_qweb_pdf(int(exam_id))
        # print(pdf ,"Tbis is PDF")
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)
    

    @http.route(['/my/ccmcexam/list/download_certificate/<int:exam_id>'], method=["POST", "GET"], type="http", auth="user", website=True)
    def DownloadCertificateCCMC(self,exam_id,**kw ):
        # import wdb; wdb.set_trace()
        # exam_id = request.env['gp.exam.schedule'].sudo().search([('gp_candidate','=',candidate_id)])[-1]
        print("INSIDE DOWNLOAD Certificate")
        report_action = request.env.ref('bes.report_ccmc_certificate')
        # certificate_available = request.env['ccmc.exam.schedule'].sudo().search([('id','=',exam_id)]).certificate_criteria == 'passed'

        pdf, _ = report_action.sudo()._render_qweb_pdf(int(exam_id))
        # print(pdf ,"Tbis is PDF")
        pdfhttpheaders = [('Content-Type', 'application/pdf'),('Content-Disposition', 'attachment; filename="Certificate.pdf"'), ('Content-Length', u'%s' % len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route(['/check_candidate_group'], method=["GET"], type="json", auth="user")
    def CheckCandidateGroup(self):
        
        group1_exists = request.env.user.has_group('bes.group_gp_candidates')
        group2_exists = request.env.user.has_group('bes.group_ccmc_candidates')

        if group1_exists or group2_exists:
            
            return {"valid_group":True}
        else:
            return {"valid_group":False}

    @http.route('/web/session/authenticate', type='json', auth="none")
    def authenticate(self, db, login, password, base_location=None):
        request.session.authenticate(db, login, password)
        result = request.env["ir.http"].session_info()
        _rotate_session(request)
        request.session.rotate = False
        expiration = datetime.datetime.utcnow() + datetime.timedelta(days=90)
        result["session"] = {
            "sid": request.session.sid,
            "expires_at": fields.Datetime.to_string(expiration),
        }
        print(result)
        return result
        
