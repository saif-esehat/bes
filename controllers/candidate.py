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
        batch = request.env["dgs.batches"].sudo().search([('id', '=', batch_id)])
        
        partner_id = request.env.user.id
        candidate = request.env["gp.candidate"].sudo().search([('user_id', '=', partner_id)])
        exam = request.env['gp.exam.schedule'].sudo().search([('gp_candidate', '=', candidate.id)], order='attempt_number desc', limit=1)
        vals = {
            'candidate': candidate,
            'exam': exam,
            'batch':batch
        }
        if exam.state == '1-in_process':
            return request.render("bes.exam_in_process", vals)
        else:
            return request.render("bes.exam_application_form_template", vals)
    
    @http.route(['/ccmccandidate/repeater/<int:batch_id>'], type="http", auth="user", website=True)
    def applyCCMCExam(self,batch_id, **kw):
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
            cookery_prac = kwargs.get('cookery_practical')
            cookery_oral = kwargs.get('cookery_oral')
            cookery_gsk_online = kwargs.get('cookery_gsk_online')
            exam_region = request.env["exam.center"].sudo().search([('name','=',kwargs.get('exam_centre'))])
            import wdb; wdb.set_trace()

            candidate_code = kwargs.get('candidate_code')
            candidate = request.env['ccmc.candidate'].sudo().search([('candidate_code', '=', candidate_code)], limit=1)
            exam = request.env['ccmc.exam.schedule'].sudo().search([('ccmc_candidate', '=', candidate.id)], order='attempt_number desc', limit=1)

            cookery_bakery_qb = request.env['survey.survey'].sudo().search([('title','=','CCMC Master Q')])
            # exams_register = request.env['candidate.gp.register.exam.wizard'].sudo().search([('candidate_id','=',candidate.id)])
            dgs_batch_id = kwargs.get('batch_id')
            if candidate:
                candidate.dgs_batch = request.env['dgs.batches'].sudo().search([('id', '=', kwargs.get('batch_id'))], limit=1)
                dgs_exam = candidate.dgs_batch.id

                exam_id  = request.env['ir.sequence'].sudo().next_by_code("ccmc.exam.schedule")

                ccmc_exam_schedule = request.env["ccmc.exam.schedule"].sudo().create({'ccmc_candidate':candidate.id , "dgs_batch": dgs_exam  , "exam_id":exam_id })

                # Marks
                # cookery_practical = exam.cookery_practical
                # cookery_oral = exam.cookery_oral
                # cookery_gsk_online = exam.cookery_gsk_online
                # overall_marks = exam.overall_marks
                
                # #Mark Percentage
                # cookery_bakery_percentage = exam.cookery_bakery_percentage
                # ccmc_oral_percentage = exam.ccmc_oral_percentage
                # cookery_gsk_online_percentage = exam.cookery_gsk_online_percentage
                # overall_percentage = exam.overall_percentage
                
                if exam.cookery_bakery_prac_status == 'failed' and kwargs.get('cookery_practical'):
                    cookery_practical = exam.env["ccmc.cookery.bakery.line"].sudo().create({"exam_id":ccmc_exam_schedule.id,'cookery_parent':candidate.id,'institute_id': candidate.institute_id.id})
                    # gsk_oral = exam.env["gp.gsk.oral.line"].sudo().create({"exam_id":gp_exam_schedule.id,'gsk_oral_parent':candidate.id,'institute_id': candidate.institute_id.id})
                
                    cookery_practical = exam.cookery_practical
                    cookery_bakery = exam.cookery_bakery
                    cookery_bakery_percentage = exam.cookery_bakery_percentage
                    cookery_prac_carry_forward = False
                    cookery_bakery_prac_status = 'pending'                
                else:
                    cookery_practical = exam.cookery_practical
                    cookery_bakery = exam.cookery_bakery
                    cookery_bakery_percentage = exam.cookery_bakery_percentage
                    cookery_prac_carry_forward = True
                    cookery_bakery_prac_status = exam.cookery_bakery_prac_status

                
                
                if exam.ccmc_oral_prac_status == 'failed' and kwargs.get('cookery_oral'):
                    ccmc_oral = exam.env["ccmc.oral.line"].sudo().create({"exam_id":ccmc_exam_schedule.id,'ccmc_oral_parent':candidate.id,'institute_id': candidate.institute_id.id})
                    ccmc_gsk_oral = exam.env["ccmc.gsk.oral.line"].sudo().create({"exam_id":ccmc_exam_schedule.id,'ccmc_oral_parent':candidate.id,'institute_id': candidate.institute_id.id})
                    
                    cookery_oral = exam.cookery_oral
                    ccmc_oral = exam.ccmc_oral
                    ccmc_oral_percentage = exam.ccmc_oral_percentage
                    cookery_oral_carry_forward = False
                    ccmc_oral_prac_status = 'pending'      
                else:
                    cookery_oral = exam.cookery_oral
                    ccmc_oral = exam.ccmc_oral
                    ccmc_oral_percentage = exam.ccmc_oral_percentage
                    cookery_oral_carry_forward = True
                    ccmc_oral_prac_status = exam.ccmc_oral_prac_status     
                
                
                if exam.ccmc_online_status == 'failed' and kwargs.get('cookery_gsk_online'):
                    cookery_bakery_qb_input = cookery_bakery_qb._create_answer(user=candidate.user_id)
                    cookery_bakery_qb_input.write({'ccmc_candidate':candidate.id})
                    
                    cookery_gsk_online = exam.cookery_gsk_online
                    cookery_gsk_online_percentage = exam.cookery_gsk_online_percentage
                    cookery_gsk_online_carry_forward = False
                    ccmc_online_status = 'pending'
                else:
                    cookery_bakery_qb_input = exam.ccmc_online
                    cookery_gsk_online = exam.cookery_gsk_online
                    cookery_gsk_online_percentage = exam.cookery_gsk_online_percentage
                    cookery_gsk_online_carry_forward = True
                    ccmc_online_status = exam.ccmc_online_status

                overall_marks = exam.overall_marks
                overall_percentage = exam.overall_percentage
                ccmc_exam_schedule.write({
                    'registered_institute':candidate.institute_id.id,
                    'ccmc_candidate':candidate.id,
                    'exam_id':exam_id,
                    'exam_region':exam_region.id,
                    'dgs_batch':dgs_exam,
                    'cookery_practical':cookery_practical,
                    'cookery_oral':cookery_oral,
                    'cookery_gsk_online':cookery_gsk_online,
                    'overall_marks':overall_marks,
                    'cookery_bakery_percentage':cookery_bakery_percentage,
                    'ccmc_oral_percentage':ccmc_oral_percentage,
                    'cookery_gsk_online_percentage':cookery_gsk_online_percentage,
                    'overall_percentage':overall_percentage,
                    'cookery_bakery_prac_status':exam.cookery_bakery_prac_status,
                    'ccmc_oral_prac_status':exam.ccmc_oral_prac_status,
                    'cookery_prac_carry_forward':exam.cookery_prac_carry_forward,
                    'cookery_oral_carry_forward':exam.cookery_oral_carry_forward,
                    'cookery_gsk_online_carry_forward':exam.cookery_gsk_online_carry_forward,
                    "cookery_bakery":cookery_bakery.id,
                    "ccmc_oral":ccmc_oral.id,
                    "ccmc_online":cookery_bakery_qb_input.id
                    
                    })
                # ccmc_exam_schedule.write({"cookery_bakery":cookery_bakery.id,"ccmc_oral":ccmc_oral.id,"ccmc_online":cookery_bakery_qb_input.id})
                return request.redirect("/my/home")
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
            mek_practical_oral = kwargs.get('mek_practical_oral')
            gsk_practical_oral = kwargs.get('gsk_practical_oral')
            mek_online = kwargs.get('mek_online')
            gsk_online = kwargs.get('gsk_online')
            exam_region = request.env["exam.center"].sudo().search([('name','=',kwargs.get('exam_centre'))])
            # import wdb; wdb.set_trace()

            candidate_code = kwargs.get('candidate_code')
            candidate = request.env['gp.candidate'].sudo().search([('candidate_code', '=', candidate_code)], limit=1)
            exam = request.env['gp.exam.schedule'].sudo().search([('gp_candidate', '=', candidate.id)], order='attempt_number desc', limit=1)
            # exams_register = request.env['candidate.gp.register.exam.wizard'].sudo().search([('candidate_id','=',candidate.id)])
            dgs_batch_id = kwargs.get('batch_id')
            # exams_register.register_exam_web(dgs_batch_id,candidate)
            if candidate:
                candidate.dgs_batch = request.env['dgs.batches'].sudo().search([('id', '=', kwargs.get('batch_id'))], limit=1)
                dgs_exam = candidate.dgs_batch.id
        
                exam_id = request.env['ir.sequence'].sudo().next_by_code("gp.exam.sequence")

                
                gp_exam_schedule = request.env["gp.exam.schedule"].sudo().create({'gp_candidate':candidate.id , "dgs_batch": dgs_exam  , "exam_id":exam_id })

                
                if exam.gsk_oral_prac_status == 'failed' and kwargs.get('gsk_practical_oral'):
                    gsk_practical = exam.env["gp.gsk.practical.line"].sudo().create({"exam_id":gp_exam_schedule.id,'gsk_practical_parent':candidate.id,'institute_id': candidate.institute_id.id})
                    gsk_oral = exam.env["gp.gsk.oral.line"].sudo().create({"exam_id":gp_exam_schedule.id,'gsk_oral_parent':candidate.id,'institute_id': candidate.institute_id.id})
                
                    gsk_practical_marks = exam.gsk_practical_marks
                    gsk_oral_marks = exam.gsk_oral_marks
                    gsk_total = exam.gsk_total
                    gsk_percentage = exam.gsk_percentage
                    gsk_oral_prac_carry_forward = False
                    gsk_oral_prac_status = 'pending'
                
                else:
                    gsk_practical = exam.gsk_prac
                    gsk_oral =exam.gsk_oral
                    
                    gsk_oral_prac_status = exam.gsk_oral_prac_status
                    gsk_practical_marks = exam.gsk_practical_marks
                    gsk_oral_marks = exam.gsk_oral_marks
                    gsk_total = exam.gsk_total
                    gsk_percentage = exam.gsk_percentage
                    gsk_oral_prac_carry_forward = True

                
                
                if exam.mek_oral_prac_status == 'failed' and kwargs.get('mek_practical_oral'):
                    mek_practical = request.env["gp.mek.practical.line"].sudo().create({"exam_id":gp_exam_schedule.id,'mek_parent':candidate.id,'institute_id': candidate.institute_id.id})
                    mek_oral = request.env["gp.mek.oral.line"].sudo().create({"exam_id":gp_exam_schedule.id,'mek_oral_parent':candidate.id,'institute_id': candidate.institute_id.id})
                    mek_practical_marks = exam.mek_practical_marks
                    mek_oral_marks = exam.mek_oral_marks
                    mek_total = exam.mek_total
                    mek_percentage = exam.mek_percentage
                    mek_oral_prac_carry_forward = False
                    mek_oral_prac_status = 'pending'
                    
                else:
                    mek_practical = exam.mek_prac
                    mek_oral =exam.mek_oral
                    mek_oral_prac_carry_forward = True
                    mek_practical_marks = exam.mek_practical_marks
                    mek_oral_marks = exam.mek_oral_marks
                    mek_total = exam.mek_total
                    mek_percentage = exam.mek_percentage
                    mek_oral_prac_status = exam.mek_oral_prac_status
                
                # if self.mek_online_status == 'failed' and  self.gsk_online_status == 'failed':
            
                #     ## MEK QB Assigning
                #     mek_survey_qb_input = self.mek_survey_qb._create_answer(user=self.candidate_id.user_id)
                #     token = mek_survey_qb_input.generate_unique_string()
                #     mek_survey_qb_input.write({'gp_candidate':self.candidate_id.id ,'dgs_batch':dgs_exam  })
                #     mek_online_carry_forward = False
                #     mek_online_marks = self.gp_exam.mek_online_marks
                #     mek_online_percentage = self.gp_exam.mek_online_percentage
                    
                #     ## GSK QB Assigning
                #     gsk_survey_qb_input = self.gsk_survey_qb._create_answer(user=self.candidate_id.user_id)
                #     token = gsk_survey_qb_input.generate_unique_string()
                #     gsk_survey_qb_input.write({'gp_candidate':self.candidate_id.id , 'dgs_batch':dgs_exam})
                #     gsk_online_carry_forward = False
                #     gsk_online_marks = self.gp_exam.gsk_online_marks
                #     gsk_online_percentage = self.gp_exam.gsk_online_percentage

                if exam.mek_online_status == 'failed' and kwargs.get('mek_online'):
                    mek_survey_qb_input = exam.mek_survey_qb._create_answer(user=candidate.user_id)
                    token = mek_survey_qb_input.generate_unique_string()
                    mek_survey_qb_input.write({'gp_candidate':candidate.id ,'dgs_batch':dgs_exam  })
                    mek_online_carry_forward = False
                    mek_online_marks = exam.mek_online_marks
                    mek_online_percentage = exam.mek_online_percentage
                    mek_online_status = 'pending'
                else:
                    mek_survey_qb_input = exam.mek_online
                    mek_online_carry_forward = True
                    mek_online_marks = exam.mek_online_marks
                    mek_online_percentage = exam.mek_online_percentage
                    mek_online_status = exam.mek_online_status
                
                
                if exam.gsk_online_status == 'failed' and kwargs.get('gsk_online'):
                    gsk_survey_qb_input = exam.gsk_survey_qb._create_answer(user=candidate.user_id)
                    token = gsk_survey_qb_input.generate_unique_string()
                    gsk_survey_qb_input.write({'gp_candidate':candidate.id , 'dgs_batch':dgs_exam})
                    gsk_online_carry_forward = False
                    gsk_online_marks = exam.gsk_online_marks
                    gsk_online_percentage = exam.gsk_online_percentage
                    gsk_online_status = 'pending'
                else:
                    gsk_survey_qb_input = exam.gsk_online
                    gsk_online_marks = exam.gsk_online_marks
                    gsk_online_percentage = exam.gsk_online_percentage
                    gsk_online_carry_forward = True
                    gsk_online_status = exam.gsk_online_status
                    
                overall_marks = exam.overall_marks
                
                overall_percentage = exam.overall_percentage
                
                    
                
                gp_exam_schedule.write({
                                        # "registered_institute":candidate.institute_id.id,
                                        "mek_oral":mek_oral.id,
                                        "mek_prac":mek_practical.id,
                                        "gsk_oral":gsk_oral.id,
                                        'exam_region':exam_region.id,
                                        "gsk_prac":gsk_practical.id , 
                                        "gsk_online":gsk_survey_qb_input.id, 
                                        "mek_online":mek_survey_qb_input.id,
                                        "gsk_practical_marks":gsk_practical_marks,
                                        "gsk_oral_marks":gsk_oral_marks,
                                        "gsk_total":gsk_total,
                                        "gsk_percentage":gsk_percentage,
                                        "mek_practical_marks":mek_practical_marks,
                                        "mek_oral_marks":mek_oral_marks,
                                        "mek_total":mek_total,
                                        "mek_percentage":mek_percentage,
                                        "mek_online_marks":mek_online_marks,
                                        "mek_online_percentage":mek_online_percentage,
                                        "gsk_online_marks":gsk_online_marks,
                                        "gsk_online_percentage":gsk_online_percentage,
                                        "overall_marks":overall_marks,
                                        "overall_percentage":overall_percentage,
                                        "gsk_oral_prac_carry_forward":gsk_oral_prac_carry_forward,
                                        "mek_oral_prac_carry_forward":mek_oral_prac_carry_forward,
                                        "mek_online_carry_forward":mek_online_carry_forward,
                                        "gsk_online_carry_forward":gsk_online_carry_forward,
                                        "gsk_oral_prac_status":gsk_oral_prac_status,
                                        "mek_oral_prac_status":mek_oral_prac_status,
                                        "mek_online_status":mek_online_status,
                                        "gsk_online_status":gsk_online_status
                                        
                                        })

            return request.redirect("/my/home")
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
