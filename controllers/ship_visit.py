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
import json
from io import BytesIO
import xlrd
import logging

_logger = logging.getLogger(__name__)

class GPShipVisitPortalController(http.Controller):
    
    # @http.route('/gp/ship/visit', auth='public', type='http', website=True)
    # def ship_visit_list(self, **kwargs):
    #     visits = request.env['gp.batches.ship.visit'].search([])
    #     return request.render('bes.portal_gp_ship_visits', {
    #         'visits': visits,
    #     })
    def _prepare_home_portal_values(self, counters):
        # Call the super method to get the existing return values
        rtn = super(WeblearnsPortal, self)._prepare_home_portal_values(counters)

        # Calculate the count of gp.batches.ship.visit records
        ship_visit_count = request.env['gp.batches.ship.visit'].sudo().search_count([])

        # Add the count to the return dictionary
        rtn['gp_counts'] = ship_visit_count
        return rtn

    # @http.route(['/my/ship_visitss'], type='http', auth='user', website=True)
    # def portal_my_ship_visits(self, **kw):
    #     # Fetch the ship visits records
    #     ship_visits = request.env['gp.batches.ship.visit'].sudo().search([])
        
    #     vals = {'ship_visits': ship_visits, 'page_name': 'gp_ship_list'}
    #     return request.render('bes.portal_gp_ship_visits',vals )
     # 2
  

    # @http.route(['/my/ship_visits'], type='http', auth='user', website=True)
    # def portal_my_ship_visits(self ,**kw):
    #     ship_visits = request.env['gp.batches.ship.visit'].sudo().search([])
    #     vals = {'ship_visits': ship_visits, 'page_name': 'gp_ship_list'}
    #     return request.render('bes.portal_gp_ship_visits_po', vals)

    @http.route(['/my/ship_visits'], type='http', auth='user', website=True)
    def portal_my_ship_visits(self, **kw):
       
        # Search for all ship visits associated with the user's batch ID
        ship_visits = request.env['gp.batches.ship.visit'].sudo().search([])

        vals = {'ship_visits': ship_visits, 'page_name': 'gp_ship_list'}
        return request.render('bes.portal_gp_ship_visits_po', vals)
  
#   ccmc  ship visit
    @http.route(['/my/ccmc_ship_visits'], type='http', auth='user', website=True)
    def portal_ccmcmy_ship_visits(self, **kw):
       
        # Search for all ship visits associated with the user's batch ID
        ship_visits = request.env['ccmc.batches.ship.visit'].sudo().search([])

        vals = {'ship_visits': ship_visits, 'page_name': 'gp_ccmcship_list'}
        return request.render('bes.portal_ccmc_ship_visits_po', vals)

    @http.route(['/my/ship_visits/<int:batch_id>'], type='http', auth='user', website=True)
    def portal_my_ship_visit(self, batch_id, **kw):
        user_id = request.env.user.id

        gp_ship_batch_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id
        ship_visit = request.env['gp.batches.ship.visit'].sudo().search([('gp_ship_batch_id', '=', batch_id)])
        vals = {'ship_visit': ship_visit, 'page_name': 'gp_ship_list','batch_id':batch_id}
        return request.render('bes.portal_gp_ship_visits_po', vals)
 

 #   ccmc  ship visit
    @http.route(['/my/ccmc_ship_visits/<int:batch_id>'], type='http', auth='user', website=True)
    def portal_my_sccmchip_visit(self, batch_id, **kw):
        user_id = request.env.user.id

        ccmc_ship_batch_ids = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id
        ship_visit = request.env['ccmc.batches.ship.visit'].sudo().search([('ccmc_ship_batch_ids', '=', batch_id)])
        vals = {'ship_visit': ship_visit, 'page_name': 'gp_ccmcship_list','batch_id':batch_id}
        return request.render('bes.portal_ccmc_ship_visits_po', vals)




    @http.route(['/my/ship_visits/create'], type='http', auth='user', website=True)
    def portal_gp_ship_visit_create(self, **kw):
        # Render the template for creating a new ship visit
        return request.render('bes.portal_gp_ship_visit_create', {'page_name': 'gp_ship_create'})

 #   ccmc  ship visit
    @http.route(['/my/ccmc_ship_visits/create'], type='http', auth='user', website=True)
    def portal_ccmc_ship_visit_create(self, **kw):
        # Render the template for creating a new ship visit
        return request.render('bes.portal_ccmc_ship_visit_create', {'page_name': 'ccmcship_create'})



    @http.route(['/my/ship_visits/submit'], type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def portal_gp_ship_visit_submit(self, **post):
        # Process POST data
        if request.httprequest.method == 'POST':
            ship_name1 = post.get("ship_name1")
            port_name = post.get("port_name")
            course_gp = post.get("course_gp")
            imo_no = post.get("imo_no")
            date_of_visit = post.get("date_of_visit")
            no_of_candidate = post.get("no_of_candidate")
            gp_image = post.get("gp_image")

            # Process image file
            if gp_image:
                file_content = gp_image.read()
                filename = gp_image.filename
                image_base64 = base64.b64encode(file_content).decode('utf-8')  # Encode the image and decode to string

            try:
                date_of_visit_str = post.get('date_of_visit')
                date_of_visit = datetime.strptime(date_of_visit_str, '%Y-%m-%dT%H:%M') if date_of_visit_str else False

                # Data to create the ship visit record
                ship_data = {
                    "ship_name1": ship_name1,
                    'gp_image': image_base64 if gp_image else False,
                    'gp_image': filename if gp_image else False,  # Correct field name for storing filename
                    "port_name": port_name,
                    "course_gp": course_gp,
                    "imo_no": imo_no,  # Ensure you add imo_no to the dictionary
                    "date_of_visit": date_of_visit,  # Add date_of_visit
                    "no_of_candidate": no_of_candidate,
                }

                # Create the record in the model
                ship_visit_record = request.env['gp.batches.ship.visit'].sudo().create(ship_data)
            
            except Exception as e:
                _logger.error("Failed to create ship visit record: %s", e)
                request.session['error_message'] = "Failed to create ship visit record."

            return request.redirect('/my/ship_visits')

 #   ccmc  ship visit
    @http.route(['/my/ccmc_ship_visits/submit'], type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def portal_ccmc_ship_visit_submit(self, **post):
        # Process POST data
        if request.httprequest.method == 'POST':
            ship_name2 = post.get("ship_name2")
            port_name = post.get("port_name")
            course_gp = post.get("course_gp")
            imo_no = post.get("imo_no")
            date_of_visit = post.get("date_of_visit")
            no_of_candidate = post.get("no_of_candidate")
            gp_image = post.get("gp_image")

            # Process image file
            if gp_image:
                file_content = gp_image.read()
                filename = gp_image.filename
                image_base64 = base64.b64encode(file_content).decode('utf-8')  # Encode the image and decode to string

            try:
                date_of_visit_str = post.get('date_of_visit')
                date_of_visit = datetime.strptime(date_of_visit_str, '%Y-%m-%dT%H:%M') if date_of_visit_str else False

                # Data to create the ship visit record
                ship_data = {
                    "ship_name2": ship_name2,
                    'gp_image': image_base64 if gp_image else False,
                    'gp_image': filename if gp_image else False,  # Correct field name for storing filename
                    "port_name": port_name,
                    "course_gp": course_gp,
                    "imo_no": imo_no,  # Ensure you add imo_no to the dictionary
                    "date_of_visit": date_of_visit,  # Add date_of_visit
                    "no_of_candidate": no_of_candidate,
                }

                # Create the record in the model
                ship_visit_record = request.env['ccmc.batches.ship.visit'].sudo().create(ship_data)
            
            except Exception as e:
                _logger.error("Failed to create ship visit record: %s", e)
                request.session['error_message'] = "Failed to create ship visit record."

            return request.redirect('/my/ccmc_ship_visits')

          

    @http.route(['/my/ship_visits/edit'], type='http', auth='user', website=True, methods=['GET'], csrf=False)
    def portal_gp_ship_visit_edit(self, id, **kw):
        visit = request.env['gp.batches.ship.visit'].sudo().browse(int(id))
        if not visit.exists():
            return request.not_found()
        return request.render('bes.portal_gp_ship_visit_edit', {'visit': visit})
 
  #   ccmc  ship visit
    @http.route(['/my/ccmc_ship_visits/edit'], type='http', auth='user', website=True, methods=['GET'], csrf=False)
    def portal_ccmc_ship_visit_edit(self, id, **kw):
        visit = request.env['ccmc.batches.ship.visit'].sudo().browse(int(id))
        if not visit.exists():
            return request.not_found()
        return request.render('bes.portal_ccmc_ship_visit_edit', {'visit': visit})


    @http.route(['/my/ship_visits/update'], type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def portal_gp_ship_visit_update(self, **post):
        visit_id = post.get('id')

        if not visit_id:
            return request.not_found()
        
        visit = request.env['gp.batches.ship.visit'].sudo().browse(int(visit_id))
        if not visit.exists():
            return request.not_found()
        
        # Convert the date format to match Odoo's expected format
        date_of_visit = post.get('date_of_visit')
        if date_of_visit:
            # Replace 'T' with a space to match the expected format
            date_of_visit = date_of_visit.replace('T', ' ')
        
        # Update the record with the form data
        visit.write({
            'ship_name1': post.get('ship_name1'),
            'port_name': post.get('port_name'),
            'imo_no': post.get('imo_no'),
            'date_of_visit': date_of_visit,  # Use the formatted date
            'time_spent': post.get('time_spent'),
            'course_gp': post.get('course_gp'),
            'no_of_candidate': post.get('no_of_candidate'),
        })

        request.session['success_message'] = "Ship visit record updated successfully."
        return request.redirect('/my/ship_visits')


# ccmc ship visit
    @http.route(['/my/ccmc_ship_visits/update'], type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def portal_ccmc_ship_visit_update(self, **post):
        visit_id = post.get('id')

        if not visit_id:
            return request.not_found()
        
        visit = request.env['ccmc.batches.ship.visit'].sudo().browse(int(visit_id))
        if not visit.exists():
            return request.not_found()
        
        # Convert the date format to match Odoo's expected format
        date_of_visit = post.get('date_of_visit')
        if date_of_visit:
            # Replace 'T' with a space to match the expected format
            date_of_visit = date_of_visit.replace('T', ' ')
        
        # Update the record with the form data
        visit.write({
            'ship_name2': post.get('ship_name2'),
            'port_name': post.get('port_name'),
            'imo_no': post.get('imo_no'),
            'date_of_visit': date_of_visit,  # Use the formatted date
            'time_spent': post.get('time_spent'),
            'course_gp': post.get('course_gp'),
            'no_of_candidate': post.get('no_of_candidate'),
        })

        request.session['success_message'] = "Ship visit record updated successfully."
        return request.redirect('/my/ccmc_ship_visits')

    @http.route(['/my/ship_visits/view'], type='http', auth='user', website=True)
    def portal_gp_ship_visit_view(self, id):
        # Fetch the specific ship visit by ID
        ship_visit = request.env['gp.batches.ship.visit'].sudo().browse(int(id))
        
        # Ensure the record exists
        if not ship_visit.exists():
            return request.redirect('/my/ship_visits')  # Redirect if record does not exist

        # Render a form view or a detailed view of the record
        vals = { 'ship_visit': ship_visit,'page_name': 'gp_ship_from'}
        return request.render('bes.portal_gp_ship_visit_form', vals)

# ccmc ship visit
    @http.route(['/my/ccmc_ship_visits/view'], type='http', auth='user', website=True)
    def portal_ccmc_ship_visit_view(self, id):
        # Fetch the specific ship visit by ID
        ship_visit = request.env['ccmc.batches.ship.visit'].sudo().browse(int(id))
        
        # Ensure the record exists
        if not ship_visit.exists():
            return request.redirect('/my/ccmc_ship_visits')  # Redirect if record does not exist

        # Render a form view or a detailed view of the record
        vals = { 'ship_visit': ship_visit,'page_name': 'ccmc_ship_from'}
        return request.render('bes.portal_ccmc_ship_visit_form', vals)

    @http.route(['/my/ship_visits/delete'], type='http', auth='user', website=True)
    def portal_gp_ship_visit_delete(self, id):
        ship_visit = request.env['gp.batches.ship.visit'].sudo().browse(int(id))
        if ship_visit.exists():
            ship_visit.unlink()
        return request.redirect('/my/ship_visits')

# ccmc ship visit
    @http.route(['/my/ccmc_ship_visits/delete'], type='http', auth='user', website=True)
    def portal_ccmc_ship_visit_delete(self, id):
        ship_visit = request.env['ccmc.batches.ship.visit'].sudo().browse(int(id))
        if ship_visit.exists():
            ship_visit.unlink()
        return request.redirect('/my/ccmc_ship_visits')

  