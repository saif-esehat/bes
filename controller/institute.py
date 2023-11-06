from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request
from odoo import http

class InstitutePortal(CustomerPortal):
    
    
    
    @http.route(['/my/gpcandidate/list'],type="http",auth="user",website=True)
    def candidateListView(self,**kw):
        # import wdb; wdb.set_trace()

        user_id = request.env.user.id
        institute_id = request.env["bes.institute"].sudo().search([('user_id','=',user_id)]).id
        candidates =  request.env["gp.candidate"].sudo().search([('institute_id','=',institute_id)])
        vals = {'candidates':candidates , 'page_name': 'gp_candidate'}
        # self.env["gp.candidate"].sudo().search([('')])
        return request.render("bes.candidate_portal_list", vals)
    
    
    
    
    
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
    
        