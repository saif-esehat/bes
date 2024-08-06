from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import db_monodb, request, root
from odoo import fields
from odoo import http
from werkzeug.utils import secure_filename
import base64
import datetime
from odoo.service import security
from odoo.exceptions import UserError,ValidationError
import json



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
            print(partner_id)
            candidate = request.env["gp.candidate"].sudo().search([('user_id','=',partner_id)])
            exam_region = request.env["gp.candidate"].sudo().search([('user_id','=',partner_id)]).institute_id.exam_center.name
            institute_code = request.env["gp.candidate"].sudo().search([('user_id','=',partner_id)]).institute_id.code
            registered_exams = request.env["gp.exam.schedule"].sudo().search([('gp_candidate','=',candidate.id),('state','in',('1-in_process','3-certified'))])
            
            print('registered_examsssssssssssssssssssssssssssss',registered_exams)
            # registered_exams
            # import wdb; wdb.set_trace(); 
            
            show_certificate = registered_exams.state == '3-certified' or False

            if registered_exams.state == '1-in_process':
                if candidate.institute_batch_id.admit_card_status == 'issued' and candidate.stcw_criteria == 'passed' and candidate.ship_visit_criteria == 'passed' and candidate.attendance_criteria == 'passed':
                    show_admit_card = True
                else:
                    show_admit_card = False
            else:
                show_admit_card = False

            vals = {"registered_exams":registered_exams,"candidate":registered_exams.gp_candidate,
                    "show_certificate":show_certificate,
                    'show_admit_card':show_admit_card,'exam_region':exam_region,'institute_code':institute_code}
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
            candidate = request.env["ccmc.candidate"].sudo().search([('user_id','=',partner_id)])
            # print("candidate",candidate)
            registered_exams = request.env["ccmc.exam.schedule"].sudo().search([('ccmc_candidate','=',candidate.id),('state','in',('1-in_process','3-certified'))])
            print('registered_examsssssssssssssssssssssssssssss',registered_exams)
            # candidate = registered_exams
            # import wdb; wdb.set_trace(); 
            show_certificate = registered_exams.certificate_criteria == 'passed' or False
            if registered_exams.state == '1-in_process' and candidate.institute_batch_id.admit_card_status == 'issued' and candidate.stcw_criteria == 'passed' and candidate.ship_visit_criteria == 'passed' and candidate.attendance_criteria == 'passed':
                show_admit_card = True
            else:
                show_admit_card = False
            # show_admit_card = candidate.state == '1-in_process'
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
        
        registered_exam = request.env["survey.user_input"].sudo().search([('id','=',survey_input_id)])
        
        survey_examiner_token = registered_exam.examiner_token
        
        
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
        
        survey_examiner_token = registered_exam.examiner_token
        
        
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
    
    @http.route(['/gpcandidate/repeater/<int:batch_id>'], type="http", auth="user", website=True)
    def applyExam(self,batch_id, **kw):
        # import wdb; wdb.set_trace()
        # raise ValidationError("Not Allowed")
        batch = request.env["dgs.batches"].sudo().search([('id', '=', batch_id)])
        partner_id = request.env.user.id
        candidate = request.env["gp.candidate"].sudo().search([('user_id', '=', partner_id)])
        exam = request.env['gp.exam.schedule'].sudo().search([('gp_candidate', '=', candidate.id)], order='attempt_number desc', limit=1)
        current_year = datetime.datetime.now().year
        vals = {
            'candidate': candidate,
            'exam': exam,
            'batch':batch,
            'year':current_year
        }
        if exam.state == '1-in_process':
            return request.render("bes.exam_in_process", vals)
        else:
            return request.render("bes.exam_application_form_template", vals)
    
    @http.route(['/ccmccandidate/repeater/<int:batch_id>'], type="http", auth="user", website=True)
    def applyCCMCExam(self,batch_id, **kw):
        # raise ValidationError("Not Allowed")
        batch = request.env["dgs.batches"].sudo().search([('id', '=', batch_id)])
        
        partner_id = request.env.user.id
        candidate = request.env["ccmc.candidate"].sudo().search([('user_id', '=', partner_id)])
        exam = request.env['ccmc.exam.schedule'].sudo().search([('ccmc_candidate', '=', candidate.id)], order='attempt_number desc', limit=1)
        # import wdb; wdb.set_trace()
        # last_exam_record = self.env['ccmc.exam.schedule'].search([('ccmc_candidate','=',self.id)], order='attempt_number desc', limit=1)
        
        
        vals = {
            'candidate': candidate,
            'exam': exam,
            'batch':batch
        }

        # if len(exam) <= 0:
        #     # raise ValidationError("No previous Exam Found .Candidate Must be registered through batches")
        #     return request.render("bes.no_previous_exam_found", vals)
        
        if exam.state == '1-in_process':
            return request.render("bes.exam_in_process", vals)
        else:
            return request.render("bes.ccmc_exam_application_form_template", vals)

       
    @http.route('/my/ccmcapplication/view', type='http', auth="user", website=True, methods=['GET', 'POST'])
    def viewCCMCApplication(self, **kwargs):
        if request.httprequest.method == 'POST':
            
            
            candidate_user_id = request.env.user.id
            candidate = request.env['ccmc.candidate'].sudo().search([('user_id', '=', candidate_user_id)], limit=1)
            dgs_batch_id =int(kwargs.get('batch_id'))
            


            
            exam_region = request.env["exam.center"].sudo().search([('name','=',kwargs.get('exam_centre'))])            
            exam = request.env['ccmc.exam.schedule'].sudo().search([('ccmc_candidate', '=', candidate.id)], order='attempt_number desc', limit=1)
            
            if exam.attempt_number >= 7:
                raise ValidationError("Exam Attempt Limit Exceeds")
            
            invoice_exist = request.env['account.move'].sudo().search([('ccmc_candidate','=',candidate.id),('repeater_exam_batch','=',dgs_batch_id)])   
            
         
            if not invoice_exist:
                line_items = []
                cookery_prac = kwargs.get('cookery_practical')
                cookery_oral = kwargs.get('cookery_oral')
                cookery_gsk_online = kwargs.get('cookery_gsk_online')
                exam_region = request.env["exam.center"].sudo().search([('name','=','MUMBAI')])
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
            # import wdb; wdb.set_trace()
            candidate_user_id = request.env.user.id
            candidate = request.env['gp.candidate'].sudo().search([('user_id', '=', candidate_user_id)], limit=1)
            
            if candidate.dgs_batch.id == 4:
                candidate.write({'previous_repeater':True})
            
            dgs_batch_id = int(kwargs.get('batch_id'))
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