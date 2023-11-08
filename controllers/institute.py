from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request
from odoo import http
from werkzeug.utils import secure_filename
import base64


class InstitutePortal(CustomerPortal):
    
    
    
    @http.route(['/my/gpcandidate/list'],type="http",auth="user",website=True)
    def GPcandidateListView(self,**kw):
        # import wdb; wdb.set_trace()

        user_id = request.env.user.id
        institute_id = request.env["bes.institute"].sudo().search([('user_id','=',user_id)]).id
        candidates =  request.env["gp.candidate"].sudo().search([('institute_id','=',institute_id)])
        vals = {'candidates':candidates , 'page_name': 'gp_candidate'}
        # self.env["gp.candidate"].sudo().search([('')])
        return request.render("bes.gp_candidate_portal_list", vals)
    
    
    
    @http.route(['/my/institute_document/list'],type="http",auth="user",website=True)
    def InstituteDocumentList(self,**kw):
        user_id = request.env.user.id
        institute_id = request.env["bes.institute"].sudo().search([('user_id','=',user_id)]).id
        lod = request.env["lod.institute"].sudo().search([('institute_id','=',institute_id)])
        vals = {'lods':lod , 'page_name': 'lod_list'}
        return request.render("bes.institute_document_list", vals)
    
    @http.route(['/my/institute_document/download/<model("lod.institute"):document_id>'],type="http",auth="user",website=True)
    def InstituteDocumentDownload(self,document_id,**kw):
        # import wdb; wdb.set_trace()
        document = request.env['lod.institute'].sudo().browse(document_id.id)
        
        if document and document.document_file:  # Ensure the document and file data exist
            file_content = base64.b64decode(document.document_file)  # Decoding file data
            file_name = document.documents_name  # File name
            file_name = secure_filename(file_name)  # Secure file name
            
            # Return the file as a download attachment
            headers = [
                ('Content-Type', 'application/octet-stream'),
                ('Content-Disposition', f'attachment; filename="{file_name}"'),
            ]
            return request.make_response(file_content, headers)
        else:
            return "File not found or empty."


        
    @http.route(['/my/institute_document'],type="http",method=["POST","GET"],auth="user",website=True)
    def InstituteDocumentView(self,**kw):
        
        user_id = request.env.user.id
        institute_id = request.env["bes.institute"].sudo().search([('user_id','=',user_id)]).id
        # import wdb; wdb.set_trace()

        if request.httprequest.method == 'POST':
            # import wdb; wdb.set_trace()
            file_content = kw.get("fileUpload").read()
            filename = kw.get('fileUpload').filename
            # attachment = uploaded_file.read()

            data = request.env["lod.institute"].sudo().create({'institute_id':institute_id,
                                                        'document_name':kw.get('documentName'),
                                                        'upload_date': kw.get('uploadDate'),
                                                        'document_file':file_content,
                                                        'documents_name':filename
                                                        })
                                                        # 'document_file': uploaded_file

            return request.redirect('/my/institute_document/list')
        else:
            vals={}
            return request.render("bes.institute_documents_form", vals)


    
    
    @http.route(['/my/ccmccandidate/list'],type="http",auth="user",website=True)
    def CCMCcandidateListView(self,**kw):
        # import wdb; wdb.set_trace()

        user_id = request.env.user.id
        institute_id = request.env["bes.institute"].sudo().search([('user_id','=',user_id)]).id
        candidates =  request.env["ccmc.candidate"].sudo().search([('institute_id','=',institute_id)])
        vals = {'candidates':candidates , 'page_name': 'ccmc_candidate'}
        # self.env["gp.candidate"].sudo().search([('')])
        return request.render("bes.ccmc_candidate_portal_list", vals)
    
    
    
    
    @http.route(['/my/editinstitute'],method=["POST","GET"],type="http",auth="user",website=True)
    def editInstituteView(self,**kw):
        # import wdb; wdb.set_trace()

        user_id = request.env.user.id
        institute = request.env["bes.institute"].sudo().search([('user_id','=',user_id)])
        
        if request.httprequest.method == 'POST':
            institute.write({"email":kw.get("email"),
                             "street":kw.get("street"),
                             "street2":kw.get("street2"),
                             "city":kw.get("city"),
                             "zip":kw.get("zip")})
            
            vals = {'institutes':institute , 'page_name': 'institute_page'}
            
            return request.render("bes.institute_detail_form", vals)
   
        else:

            vals = {'institutes':institute , 'page_name': 'institute_page'}
            return request.render("bes.institute_detail_form", vals)
    
        