import base64
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal



class CustomerPortalInherit(CustomerPortal):

    @http.route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):

        # 🔐 Decode Base64 fields BEFORE Odoo validation
        
        print(post)
        if post and request.httprequest.method == 'POST':
            post = post.copy()  # IMPORTANT: avoid mutating request.params

            fields_to_decode = [
                'name', 'email', 'phone',
                'street', 'city', 'zipcode','vat','company_name'
            ]

            for field in fields_to_decode:
                if post.get(field):
                    try:
                        post[field] = base64.b64decode(post[field]).decode('utf-8')
                    except Exception as e:
                        print("Base64 decode failed for " + field)

        # 🔁 Call original Odoo logic
        return super(CustomerPortalInherit, self).account(
            redirect=redirect,
            **post
        )
