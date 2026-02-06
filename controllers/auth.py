from odoo import http
from odoo.http import request
import json
from odoo.exceptions import AccessDenied
import logging

_logger = logging.getLogger(__name__)

class ReactAuthController(http.Controller):
    """
    Authentication controller for React app integration
    Provides API endpoints for React frontend authentication
    Specifically for DGS Portal users
    """
    
    @http.route('/api/auth/login', type='json', auth='none', methods=['POST'], csrf=False)
    def api_login(self, **kwargs):
        """
        Authenticate user via API for React app
        Returns session info and user data
        Only allows users with DGS Portal group
        CSRF is disabled for login endpoint since we need to authenticate first
        """
        try:
            # Get JSON data from request
            data = request.jsonrequest
            
            if not data:
                return {
                    'success': False,
                    'error': 'No data provided'
                }
            
            db = data.get('db')
            login = data.get('login')
            password = data.get('password')
            
            if not all([db, login, password]):
                return {
                    'success': False,
                    'error': 'Missing required fields: db, login, password'
                }
            
            # Authenticate user
            try:
                request.session.authenticate(db, login, password)
            except AccessDenied:
                return {
                    'success': False,
                    'error': 'Invalid credentials'
                }
            
            # Check if user has DGS Portal group
            user = request.env.user
            if not user.has_group('bes.group_dgs_portal'):
                request.session.logout()
                return {
                    'success': False,
                    'error': 'Access denied. User does not have DGS Portal permissions.'
                }
            
            # Get session info
            session_info = request.env['ir.http'].session_info()
            
            # Get user data
            user_data = {
                'id': user.id,
                'name': user.name,
                'login': user.login,
                'email': user.email,
                'groups': [group.name for group in user.groups_id],
                'is_admin': user.has_group('base.group_system'),
                'has_dgs_portal': user.has_group('bes.group_dgs_portal'),
                'authenticated': True
            }
            
            # Add session data
            session_info.update({
                'user': user_data,
                'success': True
            })
            
            _logger.info(f"DGS Portal user {login} authenticated successfully via API")
            
            return session_info
            
        except Exception as e:
            _logger.error(f"Authentication error: {str(e)}")
            return {
                'success': False,
                'error': f'Authentication failed: {str(e)}'
            }
    
    @http.route('/api/auth/logout', type='http', auth='user', methods=['POST'], csrf=True)
    def api_logout(self, **kwargs):
        """
        Logout user and clear session
        """
        try:
            user_login = request.env.user.login
            request.session.logout()
            
            _logger.info(f"DGS Portal user {user_login} logged out via API")
            
            return request.make_response(
                json.dumps({
                    'success': True,
                    'message': 'Logged out successfully'
                }),
                headers={'Content-Type': 'application/json'}
            )
            
        except Exception as e:
            _logger.error(f"Logout error: {str(e)}")
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': f'Logout failed: {str(e)}'
                }),
                headers={'Content-Type': 'application/json'}
            )
    
    @http.route('/api/auth/check', type='http', auth='none', methods=['GET'], csrf=True)
    def api_check_auth(self, **kwargs):
        """
        Check if user is authenticated and return user info
        Only for DGS Portal users
        """
        try:
            # Check if user is authenticated by checking session
            if not request.session.uid:
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'User not authenticated',
                        'authenticated': False
                    }),
                    headers={'Content-Type': 'application/json'}
                )
            
            # Get user from session
            user = request.env['res.users'].sudo().browse(request.session.uid)
            
            # Check if user has DGS Portal group
            if not user.has_group('bes.group_dgs_portal'):
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Access denied. User does not have DGS Portal permissions.',
                        'authenticated': False
                    }),
                    headers={'Content-Type': 'application/json'}
                )
            
            user_data = {
                'id': user.id,
                'name': user.name,
                'login': user.login,
                'email': user.email,
                'groups': [group.name for group in user.groups_id],
                'is_admin': user.has_group('base.group_system'),
                'has_dgs_portal': user.has_group('bes.group_dgs_portal'),
                'authenticated': True
            }
            
            return request.make_response(
                json.dumps({
                    'success': True,
                    'user': user_data
                }),
                headers={'Content-Type': 'application/json'}
            )
            
        except Exception as e:
            
            _logger.error(f"Auth check error: {str(e)}")
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': f'Authentication check failed: {str(e)}',
                    'authenticated': False
                }),
                headers={'Content-Type': 'application/json'}
            )
                
    @http.route('/api/auth/refresh', type='http', auth='user', methods=['POST'], csrf=True)
    def api_refresh_token(self, **kwargs):
        """
        Refresh session token (if needed)
        Only for DGS Portal users
        """
        try:
            user = request.env.user
            
            # Check if user has DGS Portal group
            if not user.has_group('bes.group_dgs_portal'):
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Access denied. User does not have DGS Portal permissions.'
                    }),
                    headers={'Content-Type': 'application/json'}
                )
            
            return request.make_response(
                json.dumps({
                    'success': True,
                    'message': 'Session is valid',
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'login': user.login
                    }
                }),
                headers={'Content-Type': 'application/json'}
            )
            
        except Exception as e:
            _logger.error(f"Token refresh error: {str(e)}")
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': f'Token refresh failed: {str(e)}'
                }),
                headers={'Content-Type': 'application/json'}
            )
    
    @http.route('/api/auth/change_password', type='json', auth='user', methods=['POST'], csrf=True)
    def api_change_password(self, **kwargs):
        """
        Change user password by confirming old password
        Only for DGS Portal users
        """
        try:
            # Get JSON data from request
            data = request.jsonrequest
            
            if not data:
                return {
                    'success': False,
                    'error': 'No data provided'
                }
            
            old_password = data.get('old_password')
            new_password = data.get('new_password')
            confirm_password = data.get('confirm_password')
            
            if not all([old_password, new_password, confirm_password]):
                return {
                    'success': False,
                    'error': 'Missing required fields: old_password, new_password, confirm_password'
                }
            
            # Check if new passwords match
            if new_password != confirm_password:
                return {
                    'success': False,
                    'error': 'New password and confirmation password do not match'
                }
            
            # Check password strength (basic validation)
            if len(new_password) < 8:
                return {
                    'success': False,
                    'error': 'New password must be at least 8 characters long'
                }
            
            user = request.env.user
            
            # Check if user has DGS Portal group
            if not user.has_group('bes.group_dgs_portal'):
                return {
                    'success': False,
                    'error': 'Access denied. User does not have DGS Portal permissions.'
                }
            
            # Verify old password by attempting to authenticate
            try:
                # Create a temporary session to verify old password
                temp_session = request.session
                temp_session.authenticate(request.session.db, user.login, old_password)
                
                # If authentication succeeds, old password is correct
                # Now change the password
                user.sudo().write({
                    'password': new_password
                })
                
                _logger.info(f"DGS Portal user {user.login} changed password successfully")
                
                return {
                    'success': True,
                    'message': 'Password changed successfully'
                }
                
            except AccessDenied:
                return {
                    'success': False,
                    'error': 'Old password is incorrect'
                }
            
        except Exception as e:
            _logger.error(f"Password change error: {str(e)}")
            return {
                'success': False,
                'error': f'Password change failed: {str(e)}'
            }
    
    @http.route('/api/auth/csrf_token', type='http', auth='none', methods=['GET'], csrf=False)
    def api_get_csrf_token(self, **kwargs):
        """
        Get CSRF token for the current session
        This endpoint doesn't require CSRF protection since it's used to get the token
        Returns the CSRF token in a JSON response
        """
        try:
            
            
            
            # Ensure we have a valid session
            if not request.session.sid:
                request.session.ensure_valid()
            
            _logger.info(f"Generating CSRF token for session: {request.session.sid}")
            csrf_token = request.csrf_token()
            _logger.info(f"Generated CSRF token: {csrf_token}")
            
            # Return JSON response with CSRF token
            return request.make_response(
                json.dumps({
                    'success': True,
                    'csrf_token': csrf_token
                }),
                headers={
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true'
                }
            )
        except Exception as e:
            # import wdb; wdb.set_trace(); 
            _logger.error(f"CSRF token generation error: {str(e)}")
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': f'Failed to generate CSRF token: {str(e)}'
                }),
                headers={'Content-Type': 'application/json'}
            )