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