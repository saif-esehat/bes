from odoo import http
from odoo.http import request


class CandidateController(http.Controller):

	@http.route('/candidate',type='http', website=True, csrf=False, auth='public')
	def candidate(self, **rec):
		print('wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww')
		candidate = request.env['gp.candidate'].sudo()
		if not rec:
			return request.render("bes.candidate_entry_page", {})

		if rec:
			
			code = rec['candidate_code']
			roll_no = rec['roll_no']
			name = rec['full_name_of_candidate']
			indos_no = rec['indos_no']
			dob = rec['dob']
			age = rec['age']
			phone = rec['phone']
			mobile = rec['mobile']
			email = rec['email']
			tenth_percent = rec['tenth_percent']
			twelfth_percent = rec['twelfth_percent']
			iti_percent = rec['iti_percent']
		

			rec_dict = {
				'candidate_code': code,
				'roll_no': roll_no,
				'name': name,
				'indos_no': indos_no,
				'dob': dob,
				'age': age,
				'phone': phone,
				'mobile': mobile,
				'email': email,
				'tenth_percent': tenth_percent,
				'twelve_percent': twelfth_percent,
				'iti_percent': iti_percent,
			}

			record = candidate.create(rec_dict)
			return request.render("bes.candidate_thankyou", {})
		

		
# class ExaminationReportController(http.Controller):
#     @http.route('/web/content', type='http', auth='user')
#     def download_combined_pdf(self, model, id, field, filename=None, **kwargs):
#         record = request.env[model].browse(int(id))
#         if record:
#             pdf_data = getattr(record, field)
#             if pdf_data:
#                 response = request.make_response(
#                     pdf_data,
#                     headers=[
#                         ('Content-Type', 'application/pdf'),
#                         ('Content-Disposition', f'attachment; filename={filename}')
#                     ]
#                 )
#                 return response
#         return request.not_found()