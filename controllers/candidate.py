from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import db_monodb, request, root
from odoo import fields
from odoo import http
from werkzeug.utils import secure_filename
import base64
from datetime import datetime
from odoo.service import security
from odoo.exceptions import UserError,ValidationError
import json
import requests
from pytz import timezone
from functools import wraps
from odoo.exceptions import AccessError


def check_user_groups(group_xml_id):
    def decorator(func):
        @wraps(func)
        def wrapper(self,*args, **kwargs):
            if not request.env.user.has_group(group_xml_id):
                raise AccessError("You Do not have Access")
            return func(self,*args, **kwargs)
        return wrapper
    return decorator



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
        # print(parameter_value)
        session = request.session
        # print("Session")
        # print(session)
        if parameter_value:
            partner_id = request.env.user.id
            # print(partner_id)
            candidate = request.env["gp.candidate"].sudo().search([('user_id','=',partner_id)])
            exam_region = request.env["gp.candidate"].sudo().search([('user_id','=',partner_id)]).institute_id.exam_center.name
            institute_code = request.env["gp.candidate"].sudo().search([('user_id','=',partner_id)]).institute_id.code
            registered_exams = request.env["gp.exam.schedule"].sudo().search([('gp_candidate','=',candidate.id),('state','in',('1-in_process','3-certified'))])
            
            # print('registered_examsssssssssssssssssssssssssssss',registered_exams)
            # registered_exams
            # import wdb; wdb.set_trace(); 
            
            show_certificate = registered_exams.state == '3-certified' or False

            if registered_exams.state == '1-in_process':
                if not registered_exams.hold_admit_card and candidate.stcw_criteria == 'passed' and candidate.ship_visit_criteria == 'passed' and candidate.attendance_criteria == 'passed':
                    show_admit_card = True
                else:
                    show_admit_card = False
            else:
                show_admit_card = False

            vals = {"registered_exams":registered_exams,"candidate":registered_exams.gp_candidate,
                    "show_certificate":show_certificate,
                    'show_admit_card':show_admit_card,'exam_region':exam_region,'institute_code':institute_code}
            # print(vals)
            return request.render("bes.gp_exam_candidate", vals)
        else:
            # Ensure current time is timezone-aware (Odoo uses UTC)
            utc_now = fields.Datetime.now()  # Odoo gives naive datetime in UTC
            ist_timezone = timezone('Asia/Kolkata')
            ist_now = utc_now.replace(tzinfo=timezone('UTC')).astimezone(ist_timezone).replace(tzinfo=None)  # Convert to naive

            partner_id = request.env.user.id
            candidate = request.env["gp.candidate"].sudo().search([('user_id','=',partner_id)])
            registered_exams = request.env["survey.user_input"].sudo().search([('gp_candidate','=',candidate.id)])
            # Sort registered_exams so that 'GSK' subjects come first, 'MEK' subjects second, and others follow
            registered_exams = registered_exams.sorted(
                key=lambda exam: 0 if exam.survey_id.subject.name == 'GSK' else (1 if exam.survey_id.subject.name == 'MEK' else 2)
            )
            # import wdb; wdb.set_trace();

            vals = {
                "registered_exams": registered_exams,
                "ist_now": ist_now,  # Pass IST time to the template
            }
            return request.render("bes.gp_exam_list_view", vals)
        

    @http.route(['/my/ccmcexam/list'],type="http",auth="user",website=True)
    def CCMCExamListView(self,**kwargs):
        parameter_value = kwargs.get('ccmcexamcand')
        print(parameter_value)

        if parameter_value:
            partner_id = request.env.user.id
            candidate = request.env["ccmc.candidate"].sudo().search([('user_id','=',partner_id)])
            # print("candidate",candidate)
            registered_exams = request.env["ccmc.exam.schedule"].sudo().search([('ccmc_candidate','=',candidate.id),('state','in',('1-in_process','3-certified'))])
            print('registered_examsssssssssssssssssssssssssssss',registered_exams)
            # candidate = registered_exams
            # import wdb; wdb.set_trace(); 
            show_certificate = registered_exams.certificate_criteria == 'passed' or False
            if registered_exams.state == '1-in_process':
                if not registered_exams.hold_admit_card and candidate.stcw_criteria == 'passed' and candidate.ship_visit_criteria == 'passed' and candidate.attendance_criteria == 'passed':
                    show_admit_card = True
                else:
                    show_admit_card = False
            else:
                show_admit_card = False
            # show_admit_card = candidate.state == '1-in_process'
            vals = {"registered_exams":registered_exams,"candidate":registered_exams.ccmc_candidate,"show_certificate":show_certificate,'show_admit_card':show_admit_card}
            return request.render("bes.ccmc_exam_candidate", vals)
        else:
            # Ensure current time is timezone-aware (Odoo uses UTC)
            utc_now = fields.Datetime.now()  # Odoo gives naive datetime in UTC
            ist_timezone = timezone('Asia/Kolkata')
            ist_now = utc_now.replace(tzinfo=timezone('UTC')).astimezone(ist_timezone).replace(tzinfo=None)  # Convert to naive

            partner_id = request.env.user.id
            candidate = request.env["ccmc.candidate"].sudo().search([('user_id','=',partner_id)])
            registered_exams = request.env["survey.user_input"].sudo().search([('ccmc_candidate','=',candidate.id)])
            # registered_exams = request.env["survey.user_input"].sudo().search([('partner_id','=',partner_id)])
            # import wdb; wdb.set_trace(); 
            vals = {
                "registered_exams": registered_exams,
                "ist_now": ist_now,  # Pass IST time to the template
            }
            return request.render("bes.ccmc_exam_list_view", vals)
    
    
    # @http.route(['/my/gpexam/startexam'],type="http",auth="user",website=True)
    # def StartExam(self,**kw):
    #     partner_id = request.env.user.partner_id.id
    #     registered_exam = request.env["survey.user_input"].sudo().search([('id','=',kw.get("id"))])

    #     exam_url = registered_exam.survey_id.survey_start_url
    #     identification_token = registered_exam.access_token
    #     # vals = {}
    #     return request.redirect(exam_url+"?answer_token="+identification_token)
    
    
    
    
    @http.route(['/my/gpexam/startexam'],type="json",auth="user",website=True)
    def VerifyToken(self,**kw):
        # import wdb; wdb.set_trace()
        partner_id = request.env.user.partner_id.id
    
        
        survey_input_id = request.jsonrequest["survey_input_id"]
        examiner_token = request.jsonrequest["examiner_token"]
        online_subject = request.jsonrequest["online_subject"]
        ip = request.jsonrequest["ip"]
        
        # import wdb; wdb.set_trace()

        
        registered_exam = request.env["survey.user_input"].sudo().search([('id','=',survey_input_id)])
        
        # if registered_exam.gp_candidate:
        gp_exam = request.env["gp.exam.schedule"].sudo().search([('gp_candidate','=',registered_exam.gp_candidate.id),('dgs_batch','=',registered_exam.dgs_batch.id)],limit=1)
        
        gp_ip = gp_exam.ip_address.split(",")
        print(gp_exam)
        survey_examiner_token = gp_exam.token
        # elif registered_exam.ccmc_candidate:
        #     ccmc_exam = request.env["ccmc.exam.schedule"].sudo().search([('ccmc_candidate','=',registered_exam.gp_candidate.id),('dgs_batch','=',registered_exam.dgs_batch.id)],limit=1)
        #     survey_examiner_token = ccmc_exam.token
            
        # import wdb; wdb.set_trace()

        if ip in gp_ip:
        
            if survey_examiner_token == examiner_token:
                
                if gp_exam.attempting_gsk_online and gp_exam.attempting_mek_online:
                
                    if online_subject == "MEK":
                        if gp_exam.attempted_gsk_online:
                            print("Comingh Gere")
                            if gp_exam.mek_online_token_used:
                                registered_exams = request.env["survey.user_input"].sudo().search([('partner_id','=',partner_id)])
                                vals = {"registered_exams":registered_exams, "error":"Token Already Used"}                    
                                return json.dumps({"error":"Token Already Used"})
                            else:
                            
                                gp_exam.write({"attempted_mek_online":True,'mek_online_token_used':True})
                                exam_url = registered_exam.survey_id.survey_start_url
                                identification_token = registered_exam.access_token
                                url = exam_url+"?answer_token="+identification_token
                                
                                return json.dumps({"success":url})
                                # return request.redirect(exam_url+"?answer_token="+identification_token)
                                
                        else:
                                
                            # gp_exam.write({"attempted_gsk_online":True,'gsk_online_token_used':True})
                            registered_exams = request.env["survey.user_input"].sudo().search([('partner_id','=',partner_id)])
                            vals = {"registered_exams":registered_exams, "error":"GSK Exam Must be Attempted First"}                    
                            return json.dumps({"error":"GSK Exam Must be Attempted First"})
                        
                    else:
                        
                        if gp_exam.gsk_online_token_used:
                            registered_exams = request.env["survey.user_input"].sudo().search([('partner_id','=',partner_id)])
                            vals = {"registered_exams":registered_exams, "error":"Token Already Used"}                    
                            return json.dumps({"error":"Token Already Used"})
                        else:
                            gp_exam.write({"attempted_mek_online":True,"attempted_gsk_online":True ,'gsk_online_token_used':True, "mek_online_token_used":True})
                            exam_url = registered_exam.survey_id.survey_start_url
                            identification_token = registered_exam.access_token
                            # return request.redirect(exam_url+"?answer_token="+identification_token)
                            url = exam_url+"?answer_token="+identification_token    
                            return json.dumps({"success":url})

                elif gp_exam.attempting_mek_online:
                    
                    if gp_exam.mek_online_token_used:
                        registered_exams = request.env["survey.user_input"].sudo().search([('partner_id','=',partner_id)])
                        vals = {"registered_exams":registered_exams, "error":"Token Already Used"}                    
                        # return request.render("bes.gp_exam_list_view", vals)
                        return json.dumps({"error":"Token Already Used"})
                    else:    
                        gp_exam.write({"attempted_mek_online":True,'mek_online_token_used':True})
                        exam_url = registered_exam.survey_id.survey_start_url
                        identification_token = registered_exam.access_token
                        # return request.redirect(exam_url+"?answer_token="+identification_token)
                        url = exam_url+"?answer_token="+identification_token    
                        return json.dumps({"success":url})

                
                elif gp_exam.attempting_gsk_online:
                    print("Data")
                    print(gp_exam.mek_online_token_used)
                    if gp_exam.gsk_online_token_used:
                        registered_exams = request.env["survey.user_input"].sudo().search([('partner_id','=',partner_id)])
                        vals = {"registered_exams":registered_exams, "error":"Token Already Used"}                    
                        # return request.render("bes.gp_exam_list_view", vals)
                        return json.dumps({"error":"Token Already Used"})

                    else:
                        gp_exam.write({"attempted_gsk_online":True,'gsk_online_token_used':True})
                        exam_url = registered_exam.survey_id.survey_start_url
                        identification_token = registered_exam.access_token
                        # Assume exam_url and identification_token are set correctly
                        # full_exam_url = exam_url + "?answer_token=" + identification_token  # Example URL
                        # return request.redirect(exam_url+"?answer_token="+identification_token)
                        url = exam_url+"?answer_token="+identification_token    
                        return json.dumps({"success":url})
                        # print("Full Exam URL:", full_exam_url)  # Debugging line

                        # try:
                        #     import wdb; wdb.set_trace()
                        #     html_content = """
                        #                     <html>
                        #                         <head>
                        #                             <title>Test Page</title>
                        #                         </head>
                        #                         <body>
                        #                             <p>Redirecting...</p>
                        #                             <script type="text/javascript">
                        #                                 setTimeout(function() {
                        #                                     window.open("${full_exam_url}", "_blank");
                        #                                 }, 3000);
                        #                             </script>
                        #                         </body>
                        #                     </html>
                        #                     """.format(full_exam_url=full_exam_url)

                        #     print("About to send response...")  # Debugging line
                        #     return request.make_response(html_content, headers={'Content-Type': 'text/html'})

                        # except Exception as e:
                        #     print("Error occurred:", str(e))
                        #     return request.redirect('/error_page')  # Redirect to an error page or handle accordingly

                
            else:
                
                registered_exams = request.env["survey.user_input"].sudo().search([('partner_id','=',partner_id)])
                # import wdb; wdb.set_trace(); 
                vals = {"registered_exams":registered_exams, "error":"Invalid Examiner Token"}
                return json.dumps({"error":"Invalid Examiner Token"})
                # return request.render("bes.gp_exam_list_view", vals)

        return json.dumps({"error":"Invalid IP Address"})
            

    @http.route(['/my/ccmcexam/startexam'],type="json",auth="user",website=True)
    def VerifyTokenCcmc(self,**kw):
        partner_id = request.env.user.partner_id.id
        
        survey_input_id = request.jsonrequest["survey_input_id"]
        examiner_token = request.jsonrequest["examiner_token"]
        online_subject = request.jsonrequest["online_subject"]
        ip = request.jsonrequest["ip"]
        
        registered_exam = request.env["survey.user_input"].sudo().search([('id','=',survey_input_id)])
     
        # if registered_exam.ccmc_candidate:
        
        ccmc_exam = request.env["ccmc.exam.schedule"].sudo().search([('ccmc_candidate','=',registered_exam.ccmc_candidate.id),('dgs_batch','=',registered_exam.dgs_batch.id)],limit=1)
        print("ccmc_exam")
        print(ccmc_exam)
        print("ccmc_exam.token")
        print(ccmc_exam.token)
        survey_examiner_token = ccmc_exam.token

        ccmc_ip = ccmc_exam.ip_address.split(",")
        # import wdb; wdb.set_trace()
        if ip in ccmc_ip:
        
            if survey_examiner_token == examiner_token:
                if ccmc_exam.ccmc_online_token_used:
                    registered_exams = request.env["survey.user_input"].sudo().search([('partner_id','=',partner_id)])
                    # import wdb; wdb.set_trace(); 
                    vals = {"registered_exams":registered_exams, "error":"Token Already Used"}                
                    # return request.render("bes.ccmc_exam_list_view", vals)
                    return json.dumps({"error":"Token Already Used"})
                
                else:
                    ccmc_exam.write({'ccmc_online_token_used':True})
                    exam_url = registered_exam.survey_id.survey_start_url
                    identification_token = registered_exam.access_token
                    url = exam_url+"?answer_token="+identification_token
                    return json.dumps({"success":url})
                    # return request.redirect(exam_url+"?answer_token="+identification_token)
            else:
                
                registered_exams = request.env["survey.user_input"].sudo().search([('partner_id','=',partner_id)])
                # import wdb; wdb.set_trace(); 
                vals = {"registered_exams":registered_exams, "error":"Invalid Examiner Token"}
                
                # return request.render("bes.ccmc_exam_list_view", vals)
                return json.dumps({"error":"Token Already Used"})
        
        else :
            return json.dumps({"error":"Invalid IP Address"})
            

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
        exam_id = request.env['gp.exam.schedule'].sudo().search([('id','=',int(exam_id))])
        
        if exam_id.stcw_criterias == 'pending' or exam_id.attendance_criteria == 'pending' or exam_id.ship_visit_criteria == 'pending':
            raise ValidationError("Elligiblity Criteria Not Satisfied")
            
        print("INSIDE DOWNLOAD Certificate")
        
        print("Indos" + str(exam_id.indos_no))
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
    
    @http.route(['/gpcandidate/repeater/<int:batch_id>'], type="http", auth="user", website=True)
    @check_user_groups("bes.group_gp_candidates")
    def applyExam(self,batch_id, **kw):        
        # raise ValidationError("Not Allowed")
        batch = request.env["dgs.batches"].sudo().search([('id', '=', batch_id)])
        partner_id = request.env.user.id
        candidate = request.env["gp.candidate"].sudo().search([('user_id', '=', partner_id)])
        previous_exam = request.env['gp.exam.schedule'].sudo().search([('gp_candidate', '=', candidate.id)], order='attempt_number desc', limit=1)
        # if candidate.indos_no == "24GM0634":

        if previous_exam.attempt_number == 7:
            raise ValidationError("Max Exam Attempt Exceded")
        new_exam = request.env['gp.exam.schedule'].sudo().search([('gp_candidate', '=', candidate.id),('dgs_batch','=',batch.id)])
        # current_year = datetime.datetime.now().year
        
        invoice_exist = request.env['account.move'].sudo().search([('gp_candidate','=',candidate.id),('repeater_exam_batch','=',batch.id)])
        course = "GP"
        # import wdb; wdb.set_trace()

        if batch.form_deadline_start > datetime.today().date():
            raise ValidationError(f"Form Submission of Application for Repeater {batch.to_date.strftime('%B %Y')} examination is not Started Yet.")
        
        if batch.form_deadline < datetime.today().date():
            raise ValidationError(f"Last date of submission of Application for Repeater {batch.to_date.strftime('%B %Y')} examination is Over.")

        vals = {
            'candidate': candidate,
            'exam': previous_exam,
            'batch':batch,
            # 'year':current_year,
            'invoice_exist':invoice_exist,
            'course':course,
            'new_exam':new_exam
        }
        
        if previous_exam.state == '3-certified':
            return request.render("bes.application_status", vals)
        
        if not invoice_exist:
            return request.render("bes.exam_application_form_template", vals)
        else:
            return request.render("bes.application_status", vals)
        # else:
        #     raise ValidationError("Not allowed")
    
    @http.route(['/ccmccandidate/repeater/<int:batch_id>'], type="http", auth="user", website=True)
    @check_user_groups("bes.group_ccmc_candidates")
    def applyCCMCExam(self,batch_id, **kw):
        # raise ValidationError("Not Allowed")
        batch = request.env["dgs.batches"].sudo().search([('id', '=', batch_id)])
        
        partner_id = request.env.user.id
        candidate = request.env["ccmc.candidate"].sudo().search([('user_id', '=', partner_id)])
        previous_exam = request.env['ccmc.exam.schedule'].sudo().search([('ccmc_candidate', '=', candidate.id)], order='attempt_number desc', limit=1)
        if previous_exam.attempt_number == 7:
            raise ValidationError("Max Exam Attempt Exceded")
        # import wdb; wdb.set_trace()
        new_exam = request.env['ccmc.exam.schedule'].sudo().search([('ccmc_candidate', '=', candidate.id),('dgs_batch','=',batch.id)])
        invoice_exist = request.env['account.move'].sudo().search([('ccmc_candidate','=',candidate.id),('repeater_exam_batch','=',batch.id)])
        course = "CCMC"

        if batch.form_deadline_start > datetime.today().date():
            raise ValidationError(f"Form Submission of Application for Repeater {batch.to_date.strftime('%B %Y')} examination is not Started Yet.")
        
        if batch.form_deadline < datetime.today().date():
            raise ValidationError(f"Last date of submission of Application for Repeater {batch.to_date.strftime('%B %Y')} examination is Over.")

        vals = {
            'candidate': candidate,
            'exam': previous_exam,
            'batch':batch,
            'invoice_exist':invoice_exist,
            'course':course,
            'new_exam':new_exam
        }

        # if len(exam) <= 0:
        #     # raise ValidationError("No previous Exam Found .Candidate Must be registered through batches")
        #     return request.render("bes.no_previous_exam_found", vals)
        if previous_exam.state == '3-certified':
            return request.render("bes.application_status", vals)

        if not invoice_exist:
            return request.render("bes.ccmc_exam_application_form_template", vals)
        else:
            return request.render("bes.application_status", vals)

       
    @http.route('/my/ccmcapplication/view', type='http', auth="user", website=True, methods=['GET', 'POST'])
    def viewCCMCApplication(self, **kwargs):
        if request.httprequest.method == 'POST':
            
            # import wdb;wdb.set_trace()
            candidate_user_id = request.env.user.id
            candidate = request.env['ccmc.candidate'].sudo().search([('user_id', '=', candidate_user_id)], limit=1)
            
            if kwargs.get('stcw_table_data'):
                stcw_data = json.loads(kwargs.get('stcw_table_data'))

            if candidate.stcw_criteria == 'passed':
                print("Done")
            else:
                for stcw in stcw_data:
                    data = {
                    'candidate_id' : candidate.id,
                    'course_name' : stcw['course'].lower(),
                    'candidate_cert_no': stcw['candidate_certificate_no'],
                    'institute_name': int(stcw['institute_id']),
                    'other_institute': stcw['other_institute_name'],
                    'course_start_date': stcw['course_startdate'],
                    'course_end_date' : stcw['course_enddate']
                    }
                    request.env['ccmc.candidate.stcw.certificate'].sudo().create(data)
            
            
            
            if candidate.dgs_batch.id == 4:
                candidate.write({'previous_repeater':True})
            
            dgs_batch_id =int(kwargs.get('batch_id'))
            


            
            exam_region = request.env["exam.center"].sudo().search([('name','=',kwargs.get('exam_centre'))])            
            exam = request.env['ccmc.exam.schedule'].sudo().search([('ccmc_candidate', '=', candidate.id)], order='attempt_number desc', limit=1)
            
            if exam.attempt_number >= 7:
                raise ValidationError("Exam Attempt Limit Exceeds")
            
            invoice_exist = request.env['account.move'].sudo().search([('ccmc_candidate','=',candidate.id),('repeater_exam_batch','=',dgs_batch_id)])   
            
            if kwargs.get('gender'):
                gender = kwargs.get('gender')
            else:
                gender = candidate.gender
            if kwargs.get('mobile'):
                mobile = kwargs.get('mobile')
            else:
                mobile = candidate.mobile
            if kwargs.get('email'):
                email = kwargs.get('email')
            else:
                email = candidate.email
            if kwargs.get('ship_visit'):
                ship_visit = kwargs.get('ship_visit')

            if candidate:
                candidate.sudo().write({
                    'gender': gender,
                    'mobile': mobile,
                    'email': email,
                    'ship_visited': ship_visit
                })
            # Extracting data from the HTML form
            candidate_id = candidate.id
            name_of_ships = "Ship In Campus"
            imo_no = "Na"
            name_of_ports_visited = "Na"
            time_spent_on_ship = 8
            date_of_visits = datetime.today().date()  # Correct type for date fields
            bridge = True
            eng_room = True
            cargo_area = True


            # Assuming 'gp.candidate' is the model
            candidate_data = {
                "candidate_id":candidate_id,
                "name_of_ships": name_of_ships,
                "imo_no": imo_no,
                "name_of_ports_visited": name_of_ports_visited,
                "date_of_visits": date_of_visits,
                "time_spent_on_ship": time_spent_on_ship,
                "bridge": bridge,
                "eng_room": eng_room,
                "cargo_area": cargo_area,
            }
            
            request.env['ccmc.candidate.ship.visits'].sudo().create(candidate_data)

            candidate._check_ship_visit_criteria()
            candidate._check_attendance_criteria()
            candidate._check_stcw_certificate()


            if not invoice_exist:
                line_items = []
                cookery_prac = kwargs.get('cookery_practical')
                cookery_oral = kwargs.get('cookery_oral')
                cookery_gsk_online = kwargs.get('cookery_gsk_online')
                exam_region = request.env["exam.center"].sudo().search([('id','=',exam_center)])

                # exams_register = request.env['candidate.gp.register.exam.wizard'].sudo().search([('candidate_id','=',candidate.id)])
                dgs_batch_id = kwargs.get('batch_id')
                
                
                if cookery_gsk_online:
                    
                    product = request.env['product.template'].sudo().search([('default_code','=','ccmc_online_repeater')])
                    line_items.append((0, 0, {
                            'product_id': product.id,
                            'price_unit': product.list_price,
                            'quantity': 1
                        }))
                
                if cookery_oral:
                    
                    product = request.env['product.template'].sudo().search([('default_code','=','ccmc_oral_repeater')])
                    line_items.append((0, 0, {
                            'product_id': product.id,
                            'price_unit': product.list_price,
                            'quantity': 1
                        }))
                
                if cookery_prac:
                    product = request.env['product.template'].sudo().search([('default_code','=','ccmc_practical_repeater')])
                    line_items.append((0, 0, {
                            'product_id': product.id,
                            'price_unit': product.list_price,
                            'quantity': 1
                        }))
                    
                    
                
                if candidate:
                    transaction_id = kwargs.get('upi_utr_no')
                    transaction_date = kwargs.get('payment_date')
                    total_amount = int(kwargs.get('amount'))
                    file_content = kwargs.get("transaction_slip").read()
                    filename = kwargs.get('transaction_slip').filename
                    # import wdb;wdb.set_trace()
                    # import wdb; wdb.set_trace()
                    
                    invoice_vals = {
                        'transaction_id': transaction_id,
                        'transaction_date': transaction_date,
                        'total_amount':total_amount,
                        'partner_id': candidate.user_id.partner_id.id,  
                        'ccmc_candidate': candidate.id,
                        'move_type': 'out_invoice',
                        'invoice_line_ids':line_items,
                        'ccmc_repeater_candidate_ok':True,
                        'l10n_in_gst_treatment':'unregistered',
                        'preferred_exam_region':exam_region.id,
                        'repeater_exam_batch': int(dgs_batch_id),
                        'transaction_slip': base64.b64encode(file_content),
                        'file_name':filename
                    }
                    
                    new_invoice = request.env['account.move'].sudo().create(invoice_vals)
                    new_invoice.action_post()
                    
                    return request.redirect("/my/invoices")
            else:
                raise ValidationError("Application For Repeater Exam is already Submitted ONCE. \nKindly Check the Invoice for Further Status of Application")
        else:
            partner_id = request.env.user.id
            candidate = request.env["ccmc.candidate"].sudo().search([('user_id', '=', partner_id)], limit=1)
            courses = request.env['course.master'].sudo().search([])
            vals = {
                'candidate': candidate,
                'courses': courses
            }
            return request.render("bes.ccmc_exam_application_form_template", vals)


    @http.route('/my/application/view', type='http', auth="user", website=True, methods=['GET', 'POST'])
    def viewApplication(self, **kwargs):
        if request.httprequest.method == 'POST':
            # import wdb; wdb.set_trace()l
            candidate_user_id = request.env.user.id
            candidate = request.env['gp.candidate'].sudo().search([('user_id', '=', candidate_user_id)], limit=1)
            
            if kwargs.get('stcw_table_data'):
                stcw_data = json.loads(kwargs.get('stcw_table_data'))
            
            # document.getElementById("gpstcwlist")
            
            if candidate.stcw_criteria == 'passed':
                print("Done")
            else:
                for stcw in stcw_data:
                    data = {
                    'candidate_id' : candidate.id,
                    'course_name' : stcw['course'].lower(),
                    'candidate_cert_no': stcw['candidate_certificate_no'],
                    'institute_name': int(stcw['institute_id']),
                    'other_institute': stcw['other_institute_name'],
                    'course_start_date': stcw['course_startdate'],
                    'course_end_date' : stcw['course_enddate']
                    }
                    request.env['gp.candidate.stcw.certificate'].sudo().create(data)
            
            
            if candidate.dgs_batch.id == 4:
                candidate.write({'previous_repeater':True})
            
            
            dgs_batch_id = int(kwargs.get('batch_id'))
            
            print(kwargs)
            exam_center = int(kwargs.get('exam_centre'))
            
            exam = request.env['gp.exam.schedule'].sudo().search([('gp_candidate', '=', candidate.id)], order='attempt_number desc', limit=1)

            if exam.attempt_number >= 7:
                raise ValidationError("Exam Attempt Limit Exceeds")
            
            
            invoice_exist = request.env['account.move'].sudo().search([('gp_candidate','=',candidate.id),('repeater_exam_batch','=',dgs_batch_id)])

            if not invoice_exist:
            
                # import wdb; wdb.set_trace()
                

                
                
                line_items = []
                mek_practical_oral = kwargs.get('mek_practical_oral')
                gsk_practical_oral = kwargs.get('gsk_practical_oral')
                mek_online = kwargs.get('mek_online')
                gsk_online = kwargs.get('gsk_online')
                
                exam_region = request.env["exam.center"].sudo().search([('id','=',exam_center)])
                # import wdb; wdb.set_trace()
                
                if mek_practical_oral:
                    product = request.env['product.template'].sudo().search([('default_code','=','mek_po_repeater')])
                    line_items.append((0, 0, {
                            'product_id': product.id,
                            'price_unit': product.list_price,
                            'quantity': 1
                        }))
                
                if gsk_practical_oral:
                    product = request.env['product.template'].sudo().search([('default_code','=','gsk_po_repeater')])
                    line_items.append((0, 0, {
                            'product_id': product.id,
                            'price_unit': product.list_price,
                            'quantity': 1
                        }))
                
                if mek_online:
                    product = request.env['product.template'].sudo().search([('default_code','=','mek_online_repeater')])
                    line_items.append((0, 0, {
                            'product_id': product.id,
                            'price_unit': product.list_price,
                            'quantity': 1
                        }))
                
                if gsk_online:
                    product = request.env['product.template'].sudo().search([('default_code','=','gsk_online_repeater')])
                    line_items.append((0, 0, {
                            'product_id': product.id,
                            'price_unit': product.list_price,
                            'quantity': 1
                        }))
                    
                
            
                exam = request.env['gp.exam.schedule'].sudo().search([('gp_candidate', '=', candidate.id)], order='attempt_number desc', limit=1)
                # exams_register = request.env['candidate.gp.register.exam.wizard'].sudo().search([('candidate_id','=',candidate.id)])
                
                # import wdb; wdb.set_trace()
                
                # exams_register.register_exam_web(dgs_batch_id,candidate)
                if kwargs.get('gender'):
                    gender = kwargs.get('gender')
                else:
                    gender = candidate.gender
                if kwargs.get('mobile'):
                    mobile = kwargs.get('mobile')
                else:
                    mobile = candidate.mobile
                if kwargs.get('email'):
                    email = kwargs.get('email')
                else:
                    email = candidate.email
                if kwargs.get('ship_visit'):
                    ship_visit = kwargs.get('ship_visit')

                if candidate:
                    candidate.sudo().write({
                        'gender': gender,
                        'mobile': mobile,
                        'email': email,
                        'ship_visited': ship_visit
                    })

                # import wdb; wdb.set_trace()
                # Ensure correct types for dates and datetimes
                date_of_visits = datetime.today().date()  # Correct type for date fields


                candidate_data = {
                    "candidate_id": candidate.id,
                    "name_of_ships": "Ship In Campus",
                    "imo_no": "Na",
                    "name_of_ports_visited": "Na",
                    "date_of_visits": date_of_visits,  # Pass as datetime.date
                    "time_spent_on_ship": 8,  # Pass as datetime.datetime
                    "bridge": True,
                    "eng_room": True,
                    "cargo_area": True,
                }

                request.env['gp.candidate.ship.visits'].sudo().create(candidate_data)

                candidate._check_ship_visit_criteria()
                candidate._check_attendance_criteria()
                candidate._check_stcw_certificate()




                if candidate:
                    transaction_id = kwargs.get('upi_utr_no')
                    transaction_date = kwargs.get('payment_date')
                    total_amount = int(kwargs.get('amount'))
                    file_content = kwargs.get("transaction_slip").read()
                    filename = kwargs.get('transaction_slip').filename

                    
                    invoice_vals = {
                        'transaction_id': transaction_id,
                        'transaction_date': transaction_date,
                        'total_amount':total_amount,
                        'partner_id': candidate.user_id.partner_id.id,  
                        'gp_candidate': candidate.id,
                        'move_type': 'out_invoice',
                        'invoice_line_ids':line_items,
                        'gp_repeater_candidate_ok':True,
                        'l10n_in_gst_treatment':'unregistered',
                        'preferred_exam_region':exam_region.id,
                        'repeater_exam_batch': int(dgs_batch_id),
                        'transaction_slip': base64.b64encode(file_content),
                        'file_name':filename
                    }
                    
                    new_invoice = request.env['account.move'].sudo().create(invoice_vals)
                    new_invoice.action_post()
                    
                    return request.redirect("/my/invoices")
            else:
                raise ValidationError("Application For Repeater Exam is already Submitted ONCE. \nKindly Check the Invoice for Further Status of Application")
        else:
            partner_id = request.env.user.id
            candidate = request.env["gp.candidate"].sudo().search([('user_id', '=', partner_id)], limit=1)
            courses = request.env['course.master'].sudo().search([])
            vals = {
                'candidate': candidate,
                'courses': courses
            }
            return request.render("bes.exam_application_form_template", vals)
    
    def detect_current_month(self):
        # Get the current month as an integer (1 for January, 2 for February, etc.)
        current_month = datetime.datetime.now().month
        
        # Define the month ranges
        winter_months = [12, 1, 2]
        spring_months = [3, 4, 5, 6]
        summer_months = [7, 8]
        fall_months = [9, 10, 11]

        # Check which range the current month falls into
        if current_month in winter_months:
            return "dec_feb"
        elif current_month in spring_months:
            return "mar_jun"
        elif current_month in summer_months:
            return "jul_aug"
        elif current_month in fall_months:
            return "sep_nov"
        else:
            return "Invalid month."


    @http.route(['/my/getproductprice'], type='json', auth="user", methods=['GET', 'POST'])
    def GetProductPrice(self, **kwargs):
        default_code = request.jsonrequest['product_code']


        # import wdb; wdb.set_trace()
        amount = request.env["product.template"].sudo().search([('default_code', '=', default_code )]).list_price

        
        return json.dumps({"amount":amount})
    
    @http.route(['/my/gprepeatercandidate/addstcw'], type='http', auth="user", website=True, methods=['GET', 'POST'])
    def AddGPRepeaterSTCW(self, **kw):
        candidate_user_id = request.env.user.id
        candidate = request.env['gp.candidate'].sudo().search([('user_id', '=', candidate_user_id)], limit=1)
        
        if request.httprequest.method == 'POST':
            dgs_batch_id = int(kw.get('batch_id'))
            course_name = kw.get('course_name')
            institute_name = kw.get('institute_name')
            marine_training_inst_number = kw.get('marine_training_inst_number')
            candidate_cert_no = kw.get('candidate_cert_no')
            course_start_date = kw.get('course_start_date')
            course_end_date = kw.get('course_end_date')

            stcw_data = {
                'candidate_id' : candidate.id,
                'course_name': course_name,
                'institute_name': institute_name,
                'marine_training_inst_number': marine_training_inst_number,
                'candidate_cert_no': candidate_cert_no,
                'course_start_date': course_start_date,
                'course_end_date': course_end_date,
            }
            request.env["gp.candidate.stcw.certificate"].sudo().create(stcw_data)
            request.env.cr.commit()
        # candidate = request.env["gp.candidate"].sudo().search([('id','=',candidate.id)])
        candidate._check_sign()
        candidate._check_image()
        candidate._check_ship_visit_criteria()
        candidate._check_attendance_criteria()
        candidate._check_stcw_certificate()

        
    #     return request.redirect('/gpcandidate/repeater/'+str(dgs_batch_id))

    # @http.route('/my/gprepeatercandidate/addstcw', type='http', auth='user', methods=['POST'])
    # def AddGPRepeaterSTCW(self, **kw):
    #     candidate_user_id = request.env.user.id
    #     candidate = request.env['gp.candidate'].sudo().search([('user_id', '=', candidate_user_id)], limit=1)
        
    #     try:
    #         dgs_batch_id = int(kw.get('batch_id'))
    #         course_name = kw.get('course_name')
    #         institute_name = kw.get('institute_name')
    #         other_institute = kw.get('other_institute_name')
    #         marine_training_inst_number = kw.get('marine_training_inst_number')
    #         candidate_cert_no = kw.get('candidate_cert_no')
    #         course_start_date = kw.get('course_start_date')
    #         course_end_date = kw.get('course_end_date')

    #         stcw_data = {
    #             'candidate_id': candidate.id,
    #             'course_name': course_name,
    #             'institute_name': institute_name,
    #             'other_institute': other_institute,
    #             'marine_training_inst_number': marine_training_inst_number,
    #             'candidate_cert_no': candidate_cert_no,
    #             'course_start_date': course_start_date,
    #             'course_end_date': course_end_date,
    #         }
    #         request.env["gp.candidate.stcw.certificate"].sudo().create(stcw_data)
    #         request.env.cr.commit()
            
    #         candidate._check_sign()
    #         candidate._check_image()
    #         candidate._check_ship_visit_criteria()
    #         candidate._check_attendance_criteria()
    #         candidate._check_stcw_certificate()
            
    #     #     return {'success': True, 'message': 'STCW certificate added successfully.'}
    #     except Exception as e:
    #         pass
    #     #     return {'success': False, 'message': str(e)}
    
    @http.route(['/my/gprepeatercandidate/stcw/delete'], type='http', auth="user", website=True, methods=['GET', 'POST'])
    def DeleteGPRepeaterSTCW(self, **kw):
        # import wdb; wdb.set_trace();
        candidate_user_id = request.env.user.id
        candidate = request.env['gp.candidate'].sudo().search([('user_id', '=', candidate_user_id)], limit=1)
        dgs_batch_id = int(kw.get('batch_id'))
        stcw_id = kw.get("gp_stcw_id")
        request.env['gp.candidate.stcw.certificate'].sudo().search([('id','=',stcw_id)]).unlink()
        
        request.env.cr.commit()
        # candidate = request.env["gp.candidate"].sudo().search([('id','=',kw.get("candidate_id"))])
        candidate._check_sign()
        candidate._check_image()
        candidate._check_ship_visit_criteria()
        candidate._check_attendance_criteria()
        candidate._check_stcw_certificate()
        
        return request.redirect('/gpcandidate/repeater/'+str(dgs_batch_id))
    
    @http.route(['/my/ccmcrepeatercandidate/addstcw'], type='http', auth="user", website=True, methods=['GET', 'POST'])
    def AddCCMCRepeaterSTCW(self, **kw):
        candidate_user_id = request.env.user.id
        candidate = request.env['ccmc.candidate'].sudo().search([('user_id', '=', candidate_user_id)], limit=1)
        if request.httprequest.method == 'POST':
            dgs_batch_id = int(kw.get('batch_id'))
            course_name = kw.get('course_name')
            institute_name = kw.get('institute_name')
            other_institute = kw.get('other_institute_name')
            marine_training_inst_number = kw.get('marine_training_inst_number')
            candidate_cert_no = kw.get('candidate_cert_no')
            course_start_date = kw.get('course_start_date')
            course_end_date = kw.get('course_end_date')

            stcw_data = {
                'candidate_id' : candidate.id,
                'course_name': course_name,
                'institute_name': institute_name,
                'other_institute': other_institute,
                'marine_training_inst_number': marine_training_inst_number,
                'candidate_cert_no': candidate_cert_no,
                'course_start_date': course_start_date,
                'course_end_date': course_end_date,
            }
            request.env["ccmc.candidate.stcw.certificate"].sudo().create(stcw_data)
            request.env.cr.commit()
        # candidate = request.env["gp.candidate"].sudo().search([('id','=',candidate.id)])
        candidate._check_sign()
        candidate._check_image()
        candidate._check_ship_visit_criteria()
        candidate._check_attendance_criteria()
        candidate._check_stcw_certificate()

        
        return request.redirect('/ccmccandidate/repeater/'+str(dgs_batch_id))
    
    @http.route(['/my/ccmcrepeatercandidate/stcw/delete'], type='http', auth="user", website=True, methods=['GET', 'POST'])
    def DeleteCCCMCRepeaterSTCW(self, **kw):
        # import wdb; wdb.set_trace();
        candidate_user_id = request.env.user.id
        candidate = request.env['ccmc.candidate'].sudo().search([('user_id', '=', candidate_user_id)], limit=1)
        dgs_batch_id = int(kw.get('batch_id'))
        stcw_id = kw.get("ccmc_stcw_id")
        request.env['ccmc.candidate.stcw.certificate'].sudo().search([('id','=',stcw_id)]).unlink()
        
        request.env.cr.commit()
        # candidate = request.env["gp.candidate"].sudo().search([('id','=',kw.get("candidate_id"))])
        candidate._check_sign()
        candidate._check_image()
        candidate._check_ship_visit_criteria()
        candidate._check_attendance_criteria()
        candidate._check_stcw_certificate()
        
        return request.redirect('/ccmccandidate/repeater/'+str(dgs_batch_id))
    
    
    @http.route(['/my/checkotherinstitutegp'], type='http', auth="user", method=['GET'])
    def CheckOthersInstituteGP(self, **kwargs):
        candidate_user_id = request.env.user.id
        candidate = request.env['gp.candidate'].sudo().search([('user_id', '=', candidate_user_id)], limit=1)
        # Assuming 'candidate' is already defined as per your initial code
        stcw_certificates = candidate.stcw_certificate.filtered(lambda cert: cert.institute_name.id == 114 )
        print("Certificate")
        print(stcw_certificates)
        for certificate in stcw_certificates:
            if not certificate.other_institute:
                return json.dumps({"other_institute_name":False})
        return json.dumps({"other_institute_name":True})
    
    @http.route(['/my/checktransaction'], type='json', auth="user", method=['POST'])
    def CheckTransaction(self, **kw):
                    
        upi_utr_no = request.jsonrequest["upi_utr_no"]
        print(request.jsonrequest)
        print(upi_utr_no)
        invoice = request.env['account.move'].sudo().search([('transaction_id','=',upi_utr_no)], limit=1)
        if invoice:
            return json.dumps({"invoice_valid":True})
        else:
            return json.dumps({"invoice_valid":False})
        
    
    
    @http.route(['/my/checkotherinstituteccmc'], type='http', auth="user", method=['GET'])
    def CheckOthersInstituteCCMC(self, **kwargs):
        candidate_user_id = request.env.user.id
        candidate = request.env['ccmc.candidate'].sudo().search([('user_id', '=', candidate_user_id)], limit=1)
        stcw_certificates = candidate.stcw_certificate.filtered(lambda cert: cert.institute_name.id == 114 )

        for certificate in stcw_certificates:
            if not certificate.other_institute:
                return json.dumps({"other_institute_name":False})
        return json.dumps({"other_institute_name":True})
   
   
   
    @http.route(['/my/gp/update-inst'], type='http', auth="user", website=True, methods=['GET', 'POST'])
    def GPUpdateOtherInstitute(self, **kw):
        candidate_user_id = request.env.user.id
        if request.httprequest.method == 'POST':
            candidate = request.env['gp.candidate'].sudo().search([('user_id', '=', candidate_user_id)], limit=1)
            dgs_batch_id = int(kw.get('batch_id'))
            stcw_id = kw.get("gp_stcw_line_id")
            stcw = request.env['gp.candidate.stcw.certificate'].sudo().search([('id','=',stcw_id)])
            # import wdb; wdb.set_trace();
            stcw.sudo().write({'other_institute': kw.get('other_institute_name')})
        
        candidate._check_sign()
        candidate._check_image()
        candidate._check_ship_visit_criteria()
        candidate._check_attendance_criteria()
        candidate._check_stcw_certificate()
        
        return request.redirect('/gpcandidate/repeater/'+str(dgs_batch_id))

    @http.route(['/my/ccmc/update-inst'], type='http', auth="user", website=True, methods=['GET', 'POST'])
    def CCMCUpdateOtherInstitute(self, **kw):
        candidate_user_id = request.env.user.id
        if request.httprequest.method == 'POST':
            candidate = request.env['ccmc.candidate'].sudo().search([('user_id', '=', candidate_user_id)], limit=1)
            dgs_batch_id = int(kw.get('batch_id'))
            stcw_id = kw.get("ccmc_stcw_line_id")
            stcw = request.env['ccmc.candidate.stcw.certificate'].sudo().search([('id','=',stcw_id)])
            # import wdb; wdb.set_trace();
            stcw.sudo().write({'other_institute': kw.get('other_institute_name')})
        
        candidate._check_sign()
        candidate._check_image()
        candidate._check_ship_visit_criteria()
        candidate._check_attendance_criteria()
        candidate._check_stcw_certificate()
        
        return request.redirect('/ccmccandidate/repeater/'+str(dgs_batch_id))

    @http.route(['/my/download_instruction/<int:batch_id>'], method=["POST", "GET"], type="http", auth="user", website=True)
    def DownloadInstruction(self,batch_id,**kw ):
        
        batch = request.env["dgs.batches"].sudo().search([('id', '=', int(batch_id))])

        # import wdb; wdb.set_trace()
         # Check if batch and instruction document exist
        if batch and batch.instruction_document:
            instruction_pdf = base64.b64decode(batch.instruction_document)  # Assuming this is already in binary format
            # file_name = instruction_pdf.file_name
            pdfhttpheaders = [
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', 'attachment; filename="Instruction.pdf"'),
                ('Content-Length', u'%s' % len(instruction_pdf))
            ]
            return request.make_response(instruction_pdf, pdfhttpheaders)
        else:
            # Return a 404 error if batch or document not found
            return request.not_found()