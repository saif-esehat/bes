from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import UserError, AccessDenied
import re



class PortalSecurityPasswordPolicy(CustomerPortal):

    def _check_password_policy(self, password):
        if len(password) < 12:
            return _("Password must be at least 12 characters long.")
        if not re.search(r'[A-Z]', password):
            return _("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password):
            return _("Password must contain at least one lowercase letter.")
        if not re.search(r'[0-9]', password):
            return _("Password must contain at least one number.")
        if not re.search(r'[\W_]', password):
            return _("Password must contain at least one special character.")
        return None
    
    
    def _update_password(self, old, new1, new2):
        # Empty check (same as core)
        for k, v in [('old', old), ('new1', new1), ('new2', new2)]:
            if not v:
                return {'errors': {'password': {k: _("You cannot leave any password empty.")}}}

        # Match check
        if new1 != new2:
            return {'errors': {'password': {'new2': _("The new password and its confirmation must be identical.")}}}

        # 🔒 Password policy enforcement
        policy_error = self._check_password_policy(new1)
        if policy_error:
            return {'errors': {'password': {'new1': policy_error}}}

        try:
            request.env['res.users'].change_password(old, new1)
        except UserError as e:
            return {'errors': {'password': e.name}}
        except AccessDenied as e:
            msg = e.args[0]
            if msg == AccessDenied().args[0]:
                msg = _('The old password you provided is incorrect, your password was not changed.')
            return {'errors': {'password': {'old': msg}}}

        # Prevent logout after password change
        new_token = request.env.user._compute_session_token(request.session.sid)
        request.session.session_token = new_token

        return {'success': {'password': True}}
    
    @staticmethod
    def get_error(e, path=''):
        """ Recursively dereferences `path` (a period-separated sequence of dict
        keys) in `e` (an error dict or value), returns the final resolution IIF it's
        an str, otherwise returns None
        """
        for k in (path.split('.') if path else []):
            if not isinstance(e, dict):
                return None
            e = e.get(k)

        return e if isinstance(e, str) else None
    
    
    @http.route('/my/security', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def security(self, **post):
        values = self._prepare_portal_layout_values()
        values['get_error'] = self.get_error
        values['allow_api_keys'] = bool(
            request.env['ir.config_parameter'].sudo().get_param('portal.allow_api_keys')
        )

        if request.httprequest.method == 'POST':
            values.update(self._update_password(
                post.get('old', '').strip(),
                post.get('new1', '').strip(),
                post.get('new2', '').strip()
            ))

        return request.render(
            'portal.portal_my_security',
            values,
            headers={'X-Frame-Options': 'DENY'}
        )
    
    





    # @http.route('/my/security', type='http', auth='user', website=True, methods=['GET', 'POST'])
    # def security(self, **post):
    #     values = self._prepare_portal_layout_values()
    #     values['get_error'] = request.env['portal.mixin']._get_error if hasattr(request.env['portal.mixin'], '_get_error') else lambda e, k=None: e
    #     values['allow_api_keys'] = bool(
    #         request.env['ir.config_parameter'].sudo().get_param('portal.allow_api_keys')
    #     )

    #     if request.httprequest.method == 'POST':
    #         old = post.get('old', '').strip()
    #         new1 = post.get('new1', '').strip()
    #         new2 = post.get('new2', '').strip()

    #         # 🔒 Password policy enforcement
    #         policy_error = self._validate_password_policy(new1)
    #         if policy_error:
    #             values['errors'] = {
    #                 'password.new1': policy_error
    #             }
    #             return request.render('portal.portal_my_security', values)

    #         # Continue with original logic
    #         values.update(self._update_password(old, new1, new2))

    #     return request.render(
    #         'portal.portal_my_security',
    #         values,
    #         headers={'X-Frame-Options': 'DENY'}
    #     )
