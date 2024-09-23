from odoo.addons.portal.controllers.portal import CustomerPortal , pager
from odoo.http import request
from odoo import http
from werkzeug.utils import secure_filename
import base64
import csv
import io
from io import StringIO
from datetime import datetime
import xlsxwriter
from odoo.exceptions import UserError,ValidationError




class PublicPortal(http.Controller):
    
    @http.route(['/register/repeater/candidate'],type="http", auth='none',website=True)
    def RegisterGPCandidateView(self,**kw ):
        # import wdb; wdb.set_trace();
        if request.httprequest.method == 'GET':
            return request.render("bes.gprepeaterregister", {})
        elif request.httprequest.method == 'POST':
            # import wdb; wdb.set_trace();
            
            candidate_image = kw.get("candidate_image").read()
            candidate_image_name = kw.get('candidate_image').filename
            
            signature_photo = kw.get("signature_image").read()
            signature_photo_name = kw.get('signature_image').filename
            
            vals = {
                'candidate_image_name': candidate_image_name,
                'candidate_image':  base64.b64encode(candidate_image),
                'candidate_signature_name': signature_photo_name,
                'candidate_signature': base64.b64encode(signature_photo),
                'name': kw.get('name'),
                'course': kw.get('course'),
                'indos_no': kw.get('indos'),
                'candidate_code': kw.get('candidate_code'),
                'institute_id': int(kw.get('institute_id')),
                'gender': kw.get('gender'),
                'email': kw.get('email'),
                'phone': kw.get('phone'),
                'state': 'pending'
            }
            
            
            
            request.env["repeater.candidate.approval"].sudo().create(vals)

            
            return request.render("bes.gprepeaterregister", {})
            
    



    @http.route(['/verification/gpadmitcard/<int:exam_id>'], type="http", auth='none')
    def VerifyGpAdmitCard(self,exam_id,**kw ):
        # import wdb; wdb.set_trace()
        try:
            exam_id = request.env['gp.exam.schedule'].sudo().search([('id','=',exam_id)]).id
        except:
            raise ValidationError("Admit Card Not Found or Not Generated")
        report_action = request.env.ref('bes.candidate_gp_admit_card_action')
        pdf, _ = report_action.sudo()._render_qweb_pdf(int(exam_id))
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)


    @http.route(['/verification/ccmcadmitcard/<int:exam_id>'], type="http", auth='none')
    def VerifyCcmcAdmitCard(self,exam_id,**kw ):
        # import wdb; wdb.set_trace()
        try:
            exam_id = request.env['ccmc.exam.schedule'].sudo().search([('id','=',exam_id)]).id
        except:
            raise ValidationError("Admit Card Not Found or Not Generated")
        report_action = request.env.ref('bes.candidate_ccmc_admit_card_action')
        pdf, _ = report_action.sudo()._render_qweb_pdf(int(exam_id))
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)
    
    @http.route(['/verification/gpcerificate/<int:certificate_id>'], type="http", auth='none')
    def VerifyGPCertificate(self,certificate_id,**kw ):
        try:
            certificate = request.env['gp.exam.schedule'].sudo().search([('id','=',certificate_id)])
            if certificate.state == "3-certified":
                certificate_id = certificate.id
            else:
                raise ValidationError("Certificate Not Found or Not Generated")
                
        except:
            raise ValidationError("Certificate Not Found or Not Generated")
        report_action = request.env.ref('bes.report_gp_certificate')
        pdf, _ = report_action.sudo()._render_qweb_pdf(int(certificate_id))
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)
    
    @http.route(['/verification/ccmccerificate/<int:certificate_id>'], type="http", auth='none')
    def VerifyCCMCCertificate(self,certificate_id,**kw ):
        try:
            certificate = request.env['ccmc.exam.schedule'].sudo().search([('id','=',certificate_id)])
            if certificate.state == "3-certified":
                certificate_id = certificate.id
            else:
                raise ValidationError("Certificate Not Found or Not Generated")
                
        except:
            raise ValidationError("Certificate Not Found or Not Generated")
        report_action = request.env.ref('bes.report_ccmc_certificate')
        pdf, _ = report_action.sudo()._render_qweb_pdf(int(certificate_id))
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)