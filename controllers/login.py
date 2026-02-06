from odoo import http
from odoo.http import request
import base64
import logging

from odoo.addons.auth_signup.controllers.main import AuthSignupHome

_logger = logging.getLogger(__name__)


class BesAuthSignupHome(AuthSignupHome):
    """Override AuthSignupHome to add password decryption for encrypted login."""
    
    @http.route('/web/login', type='http', auth='public', website=True, sitemap=False)
    def web_login(self, *args, **kw):
        """Override login to handle encrypted password and login parameters."""
        
        # Get encrypted parameters from request
        enc_pwd = request.params.get('encrypted_password')
        enc_login = request.params.get('encrypted_login')
        
        if enc_pwd and enc_login:
            try:
                decoded_pwd = base64.b64decode(enc_pwd).decode('utf-8')
                # Replace password param so Odoo works normally
                request.params['password'] = decoded_pwd
                
                decoded_login = base64.b64decode(enc_login).decode('utf-8')
                # Replace login param so Odoo works normally
                request.params['login'] = decoded_login
                
            except Exception as e:
                _logger.warning("Password decode failed: %s", e)
        
        # Call parent method
        return super(BesAuthSignupHome, self).web_login(*args, **kw)