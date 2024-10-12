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
from odoo.exceptions import ValidationError

name_ = 'bes.ship_visit'  # Example name for your logger
logger = logging.getLogger(name_)
_logger = logging.getLogger(__name__)

# Now you can use logger to log messages
logger.info("Logger initialized successfully.")
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

    # @http.route(['/my/ship_visits'], type='http', auth='user', website=True)
    # def portal_my_ship_visits(self, **kw):
       
    #     # Search for all ship visits associated with the user's batch ID
    #     ship_visits = request.env['gp.batches.ship.visit'].sudo().search([])

    #     vals = {'ship_visits': ship_visits, 'page_name': 'gp_ship_list'}
    #     return request.render('bes.portal_gp_ship_visits_po', vals)
  
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
        # import wdb;wdb.set_trace()
       
        vals = {
            'ship_visit': ship_visit,  # Pass the records to the template
            'page_name': 'gp_ship_list',
            'batch_id': batch_id
        }
        # return request.render('bes.portal_gp_ship_visits_po', vals)
        return request.redirect('/my/ship_visits')
    
 

 #   ccmc  ship visit
    # @http.route(['/my/ccmc_ship_visits/<int:batch_id>'], type='http', auth='user', website=True)
    # def portal_my_sccmchip_visit(self, batch_id, **kw):
    #     user_id = request.env.user.id

    #     ccmc_ship_batch_ids = request.env["bes.institute"].sudo().search(
    #         [('user_id', '=', user_id)]).id
    #     ship_visit = request.env['ccmc.batches.ship.visit'].sudo().search([('ccmc_ship_batch_ids', '=', batch_id)])
    #     vals = {'ship_visit': ship_visit, 'page_name': 'gp_ccmcship_list','batch_id':batch_id}
    #     return request.render('bes.portal_ccmc_ship_visits_po', vals)

    @http.route(['/my/ccmc_ship_visits/<int:batch_id>'], type='http', auth='user', website=True)
    def portal_my_sccmchip_visit(self, batch_id, **kw):
        user_id = request.env.user.id

        # Fetch institute based on the logged-in user
        ccmc_ship_batch_ids = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id

        # Fetch the ship visit records for the provided batch_id
        ship_visits = request.env['ccmc.batches.ship.visit'].sudo().search([('ccmc_ship_batch_ids', '=', batch_id)])

        vals = {
            'ship_visits': ship_visits,  # Pass the records to the template
            'page_name': 'gp_ccmcship_list',
            'batch_id': batch_id
        }

        # Render the template with the data
        # return request.render('bes.portal_ccmc_ship_visits_po', vals)
        return request.redirect('/my/ccmc_ship_visits')




    @http.route(['/my/ship_visits/create'], type='http', auth='user', website=True)
    def portal_gp_ship_visit_create(self, **kw):
        # Render the template for creating a new ship visit
        return request.render('bes.portal_gp_ship_visit_create', {'page_name': 'gp_ship_create'})

#    ccmc  ship visit
    @http.route(['/my/ccmc_ship_visits/create'], type='http', auth='user', website=True)
    def portal_ccmc_ship_visit_create(self, **kw):
        # Render the template for creating a new ship visit
        
        return request.render('bes.portal_ccmc_ship_visit_create', {'page_name': 'ccmcship_create'})

   

    @http.route(['/my/ship_visits/submit'], type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def portal_gp_ship_visit_submit(self, **post):
        if request.httprequest.method == 'POST':
            # import wdb;wdb.set_trace()
            batch_id = int(post.get("batch_id"))
            ship_name1 = post.get("ship_name1")
            port_name = post.get("port_name")
            course_gp = post.get("course_gp")
            imo_no = post.get("imo_no")
            time_spent = post.get("time_spent")
            date_of_visit_str = post.get("date_of_visit")
            no_of_candidate = post.get("no_of_candidate")
            gp_image = post.get("gp_image")
            candidate_ids = request.httprequest.form.getlist('candidate_ids')  # Fetch multiple candidate IDs

            # Process image file
            image_base64 = None
            if gp_image:
                file_content = gp_image.read()
                image_base64 = base64.b64encode(file_content).decode('utf-8')

            try:
                date_of_visit = datetime.strptime(date_of_visit_str, '%Y-%m-%dT%H:%M') if date_of_visit_str else False

                # Prepare the list of candidates for the Many2many field
                candidate_ids_list = [(6, 0, [int(candidate_id) for candidate_id in candidate_ids])] if candidate_ids else False

                # Data to create the ship visit record
                ship_data = {
                    "gp_ship_batch_id":batch_id,
                    "ship_name1": ship_name1,
                    "port_name": port_name,
                    "course_gp": course_gp,
                    "imo_no": imo_no,
                    "time_spent": time_spent,
                    "date_of_visit": date_of_visit,
                    "no_of_candidate": no_of_candidate,
                    "gp_image": image_base64 if gp_image else False,
                    "candidate_ids": candidate_ids_list,  # Assign the selected candidates to Many2many field
                }

                # Create the record in the model
                request.env['gp.batches.ship.visit'].sudo().create(ship_data)

            except Exception as e:
                _logger.error("Failed to create ship visit record: %s", e)
                request.session['error_message'] = "Failed to create ship visit record."

            return request.redirect('/my/ship_visits/'+str(batch_id))

 #   ccmc  ship visit

    @http.route(['/my/ccmc_ship_visits/submit'], type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def portal_ccmc_ship_visit_submit(self, **post):

        user_id = request.env.user.id

        # Fetch institute based on the logged-in user
        ccmc_ship_batch_ids = request.env["bes.institute"].sudo().search(
        [('user_id', '=', user_id)], limit=1).id  

        if request.httprequest.method == 'POST':
            ship_name2 = post.get("ship_name2")
            port_name = post.get("port_name")
            course_gp = post.get("course_gp")
            imo_no = post.get("imo_no")
            time_spent = post.get("time_spent")
            date_of_visit_str = post.get("date_of_visit")
            no_of_candidate = post.get("no_of_candidate")
            gp_image = post.get("gp_image")
            candidate_ids = request.httprequest.form.getlist('candidate_ids')  # Fetch multiple candidate IDs

            # Process image file
            image_base64 = None
            if gp_image:
                file_content = gp_image.read()
                image_base64 = base64.b64encode(file_content).decode('utf-8')

            try:
                date_of_visit = datetime.strptime(date_of_visit_str, '%Y-%m-%dT%H:%M') if date_of_visit_str else False

                # Prepare the list of candidates for the Many2many field
                candidate_ids_list = [(6, 0, [int(candidate_id) for candidate_id in candidate_ids])] if candidate_ids else False

                # Data to create the ship visit record
                ship_data = {
                    "ship_name2": ship_name2,
                    "port_name": port_name,
                    "course_gp": course_gp,
                    "imo_no": imo_no,
                    "time_spent": time_spent,
                    "date_of_visit": date_of_visit,
                    "no_of_candidate": no_of_candidate,
                    "gp_image": image_base64 if gp_image else False,
                    "candidate_ids": candidate_ids_list,  # Assign the selected candidates to Many2many field
                }

                # Create the record in the model
                request.env['ccmc.batches.ship.visit'].sudo().create(ship_data)

            except Exception as e:
                _logger.error("Failed to create ship visit record: %s", e)
                request.session['error_message'] = "Failed to create ship visit record."

            return request.redirect('/my/ccmc_ship_visits')

    # @http.route(['/my/ccmc_ship_visits/submit'], type='http', auth='user', website=True, methods=['POST'], csrf=True)
    # def portal_ccmc_ship_visit_submit(self, **post):
    #     if request.httprequest.method == 'POST':
    #         ship_name2 = post.get("ship_name2")
    #         port_name = post.get("port_name")
    #         course_gp = post.get("course_gp")
    #         imo_no = post.get("imo_no")
    #         date_of_visit_str = post.get("date_of_visit")
    #         no_of_candidate = post.get("no_of_candidate")
    #         gp_image = post.get("gp_image")
    #         candidate_ids = request.httprequest.form.getlist('candidate_ids')  # Fetch multiple candidate IDs

    #         # Process image file
    #         image_base64 = None
    #         if gp_image:
    #             file_content = gp_image.read()
    #             image_base64 = base64.b64encode(file_content).decode('utf-8')

    #         try:
    #             date_of_visit = datetime.strptime(date_of_visit_str, '%Y-%m-%dT%H:%M') if date_of_visit_str else False

    #             # Prepare the list of candidates for the Many2many field using indos_no
    #             candidate_ids_list = [(6, 0, [indos_no for indos_no in candidate_ids])] if candidate_ids else False

    #             # Data to create the ship visit record
    #             ship_data = {
    #                 "ship_name2": ship_name2,
    #                 "port_name": port_name,
    #                 "course_gp": course_gp,
    #                 "imo_no": imo_no,
    #                 "date_of_visit": date_of_visit,
    #                 "no_of_candidate": no_of_candidate,
    #                 "gp_image": image_base64 if gp_image else False,
    #                 "candidate_ids": candidate_ids_list,  # Assign the selected candidates to Many2many field
    #             }

    #             # Create the record in the model
    #             request.env['ccmc.batches.ship.visit'].sudo().create(ship_data)

    #             # Redirect to the appropriate page after submission
    #             return request.redirect('/my/ccmc_ship_visits')

    #         except Exception as e:
    #             _logger.error("Failed to create ship visit record: %s", e)
    #             request.session['error_message'] = "Failed to create ship visit record."

    #     # Handle GET request or return an error
    #     return request.redirect('/my/ccmc_ship_visits')


    
    
          

    @http.route(['/my/ship_visits/edit/<int:ship_visit_id>'], type='http', auth='user', website=True, methods=['GET'], csrf=False)
    def portal_gp_ship_visit_edit(self,ship_visit_id,**kw):
        visit = request.env['gp.batches.ship.visit'].sudo().browse(int(ship_visit_id))
        vals = {'visit': visit, 'page_name': 'gpship_edit'}
        if not visit.exists():
            return request.not_found()
        return request.render('bes.portal_gp_ship_visit_edit', vals)
 
  #   ccmc  ship visit
    @http.route(['/my/ccmc_ship_visits/edit'], type='http', auth='user', website=True, methods=['GET'], csrf=False)
    def portal_ccmc_ship_visit_edit(self, id, **kw):
        visit = request.env['ccmc.batches.ship.visit'].sudo().browse(int(id))

        vals = {'visit': visit, 'page_name': 'ccmcship_edit'}
        if not visit.exists():
            return request.not_found()
        return request.render('bes.portal_ccmc_ship_visit_edit', vals)

    
    @http.route(['/my/ship_visit/addcandidate'],type="json",auth='user', website=True, methods=['POST'])
    def portal_ship_visit_add_candidate(self, **post):
        
        
        ship_visit_id = int(request.jsonrequest["ship_vist_id"])
        candidate_ids =  [int(element) for element in request.jsonrequest["candidate_ids"]]
       
        # request.jsonrequest
        ship_visit = request.env['gp.batches.ship.visit'].sudo().browse(int(ship_visit_id))
        
        # for candidate in candidate_ids:
        #     import wdb;wdb.set_trace()
        
        for candidate in candidate_ids:
            ship_visit.write({'candidate_ids': [(4,candidate)]})
            request.env['gp.candidate.ship.visits'].sudo().create({
                "candidate_id":candidate,
                "ship_visit_id":ship_visit.id,
                "name_of_ships":ship_visit.ship_name1,
                "imo_no": ship_visit.imo_no,
                "name_of_ports_visited":ship_visit.port_name, 
                "date_of_visits":ship_visit.date_of_visit,
                "time_spent_on_ship":ship_visit.time_spent
            })
            
        

            

        # import wdb;wdb.set_trace()

            
            
            
        return {"status" : "success"}

    
    

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

        candidate_ids = request.httprequest.form.getlist('candidate_ids')
        new_candidate_ids = [int(candidate_id) for candidate_id in candidate_ids]

        # Get existing candidate IDs linked to other visits with the same ship_name2 and date_of_visit
        existing_visits = request.env['ccmc.batches.ship.visit'].sudo().search([
            ('ship_name2', '=', post.get('ship_name2')),
            ('date_of_visit', '=', date_of_visit),
            ('id', '!=', visit_id)  # Exclude the current visit from the search
        ])

        # Collect candidate IDs from existing visits with the same ship_name2 and date_of_visit
        existing_candidate_ids_in_same_visit = existing_visits.mapped('candidate_ids').ids

        # Get currently linked candidate IDs to the visit
        current_candidate_ids = visit.candidate_ids.ids

        # Create a set of candidate IDs to exclude (those already selected)
        excluded_candidate_ids = set(existing_candidate_ids_in_same_visit + current_candidate_ids)

        # Filter out excluded candidate IDs from new candidate IDs
        filtered_new_candidate_ids = [candidate_id for candidate_id in new_candidate_ids if candidate_id not in excluded_candidate_ids]

        # Merge old and new candidate IDs to keep both
        updated_candidate_ids = current_candidate_ids + filtered_new_candidate_ids
        
        # Update the record with the form data
        visit.write({
            'ship_name1': post.get('ship_name1'),
            'port_name': post.get('port_name'),
            'imo_no': post.get('imo_no'),
            'date_of_visit': date_of_visit,  # Use the formatted date
            'time_spent': post.get('time_spent'),
            'course_gp': post.get('course_gp'),
            'no_of_candidate': post.get('no_of_candidate'),
            'candidate_ids': [(6, 0, updated_candidate_ids)],  # Keep old candidates and add only new ones
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
            date_of_visit = date_of_visit.replace('T', ' ')  # Adjust the date format

        # Fetch candidate IDs from the POST request (new candidates being added)
        candidate_ids = request.httprequest.form.getlist('candidate_ids')
        new_candidate_ids = [int(candidate_id) for candidate_id in candidate_ids]

        # Get existing candidate IDs linked to other visits with the same ship_name2 and date_of_visit
        existing_visits = request.env['ccmc.batches.ship.visit'].sudo().search([
            ('ship_name2', '=', post.get('ship_name2')),
            ('date_of_visit', '=', date_of_visit),
            ('id', '!=', visit_id)  # Exclude the current visit from the search
        ])

        # Collect candidate IDs from existing visits with the same ship_name2 and date_of_visit
        existing_candidate_ids_in_same_visit = existing_visits.mapped('candidate_ids').ids

        # Get currently linked candidate IDs to the visit
        current_candidate_ids = visit.candidate_ids.ids

        # Create a set of candidate IDs to exclude (those already selected)
        excluded_candidate_ids = set(existing_candidate_ids_in_same_visit + current_candidate_ids)

        # Filter out excluded candidate IDs from new candidate IDs
        filtered_new_candidate_ids = [candidate_id for candidate_id in new_candidate_ids if candidate_id not in excluded_candidate_ids]

        # Merge old and new candidate IDs to keep both
        updated_candidate_ids = current_candidate_ids + filtered_new_candidate_ids

        # Update the visit with the new candidate IDs
        visit.write({
            'ship_name2': post.get('ship_name2'),
            'port_name': post.get('port_name'),
            'imo_no': post.get('imo_no'),
            'date_of_visit': date_of_visit,
            'time_spent': post.get('time_spent'),
            'course_gp': post.get('course_gp'),
            'no_of_candidate': post.get('no_of_candidate'),
            'candidate_ids': [(6, 0, updated_candidate_ids)],  # Keep old candidates and add only new ones
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

        candidates = ship_visit.candidate_ids  # Assuming candidate_ids is the field on the ship_visit model

        # Render the form view with candidates
        vals = {
            'ship_visit': ship_visit,
            'candidates': candidates,  # Pass candidates to the template
            'page_name': 'gp_ship_from'
        }

        # Render a form view or a detailed view of the record
        return request.render('bes.portal_gp_ship_visit_form', vals)

# ccmc ship visit
    # @http.route(['/my/ccmc_ship_visits/view'], type='http', auth='user', website=True)
    # def portal_ccmc_ship_visit_view(self, id):
    #     # Fetch the specific ship visit by ID
    #     ship_visit = request.env['ccmc.batches.ship.visit'].sudo().browse(int(id))
        
    #     # Ensure the record exists
    #     if not ship_visit.exists():
    #         return request.redirect('/my/ccmc_ship_visits')  # Redirect if record does not exist

    #     # Render a form view or a detailed view of the record
    #     vals = { 'ship_visit': ship_visit,'page_name': 'ccmc_ship_from'}
    #     return request.render('bes.portal_ccmc_ship_visit_form', vals)
    @http.route(['/my/ccmc_ship_visits/view'], type='http', auth='user', website=True)
    def portal_ccmc_ship_visit_view(self, id):
        # Fetch the specific ship visit by ID
        ship_visit = request.env['ccmc.batches.ship.visit'].sudo().browse(int(id))
        
        # Ensure the record exists
        if not ship_visit.exists():
            return request.redirect('/my/ccmc_ship_visits')  # Redirect if record does not exist

        # Fetch candidates related to the ship visit
        candidates = ship_visit.candidate_ids  # Assuming candidate_ids is the field on the ship_visit model

        # Render the form view with candidates
        vals = {
            'ship_visit': ship_visit,
            'candidates': candidates,  # Pass candidates to the template
            'page_name': 'ccmc_ship_from'
        }
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