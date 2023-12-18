from odoo.addons.portal.controllers.portal import CustomerPortal

from odoo.http import request
from odoo import http

class Portals(CustomerPortal):
    
    def _prepare_home_portal_values(self, counters):
        rtn = super(Portals, self)._prepare_home_portal_values(counters)
        rtn['student_counts'] = request.env['bes'].search_count([])
        return rtn
    
    @http.route(['/my/student'], type='http', website=True)
    def PortalListView(self,**kw):
        print()
        print("======================================================================================")
        print()

        student_obj = request.env['school.student']
        students = student_obj.search([])
        return request.render("students_list_view_ports",{'students':students})