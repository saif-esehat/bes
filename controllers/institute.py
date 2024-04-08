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




class InstitutePortal(CustomerPortal):

    @http.route(['/my/gpbatch'], type="http", auth="user", website=True)
    def GPBatchList(self, **kw):
        user_id = request.env.user.id
        institute_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id
        batches = request.env["institute.gp.batches"].sudo().search(
            [('institute_id', '=', institute_id)])

        vals = {"batches": batches,'institute_id':institute_id, "page_name": "gp_batches"}
        return request.render("bes.institute_gp_batches", vals)

    @http.route(['/my/gpbatch/updatebatchcapacity'],method=['POST'], type="http", auth="user", website=True)
    def UpdateBatchApprovalCapacity(self, **kw):
        
        batch_id = int(kw.get('batch_id'))
        capacity = int(kw.get('capacity'))
        
        file_content = kw.get("approvaldocument").read()
        filename = kw.get('approvaldocument').filename
        batch = request.env["institute.gp.batches"].sudo().search([('id','=',batch_id)])
        batch.write({ "dgs_approved_capacity": capacity,
                     "dgs_approval_state":True,
                     "dgs_document":base64.b64encode(file_content)
                     })
        
        return request.redirect("/my/gpbatch")
    
    
    @http.route(['/my/ccmcbatchbatch/updatebatchcapacity'],method=['POST'], type="http", auth="user", website=True)
    def UpdateCCMCBatchApprovalCapacity(self, **kw):
        
        batch_id = int(kw.get('batch_id'))
        capacity = int(kw.get('capacity'))
        
        file_content = kw.get("approvaldocument").read()
        filename = kw.get('approvaldocument').filename
        batch = request.env["institute.ccmc.batches"].sudo().search([('id','=',batch_id)])
        batch.write({ "dgs_approved_capacity": capacity,
                     "dgs_approval_state":True,
                     "dgs_document":base64.b64encode(file_content)
                     })
        
        return request.redirect("/my/ccmcbatch")


    @http.route(['/my/ccmcbatch'], type="http", auth="user", website=True)
    def CCMCBatchList(self, **kw):
        user_id = request.env.user.id
        institute_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id
        batches = request.env["institute.ccmc.batches"].sudo().search(
            [('institute_id', '=', institute_id)])

        vals = {"batches": batches, 'institute_id':institute_id, "page_name": "ccmc_batches",}
        return request.render("bes.institute_ccmc_batches", vals)

    # @http.route(['/my/uploadgpcandidatedata'], type="http", auth="user", website=True)
    # def UploadGPCandidateData(self, **kw):
    #     user_id = request.env.user.id
    #     institute_id = request.env["bes.institute"].sudo().search(
    #         [('user_id', '=', user_id)]).id
        
    #     batch_id = int(kw.get("batch_id"))
    #     file_content = kw.get("fileUpload").read()
    #     filename = kw.get('fileUpload').filename
    #     file_content_str = file_content.decode('utf-8')

    #     if file_content_str.startswith('\ufeff'):
    #         file_content_str = file_content_str.lstrip('\ufeff')

    #     csv_file = StringIO(file_content_str)
    #     csv_reader = csv.DictReader(csv_file)

    #     for row in csv_reader:
    #         # import wdb; wdb.set_trace()
    #         full_name = row['Full Name of candidate as in INDOS']
    #         indos_no = row['Indos No.']
    #         dob = datetime.strptime(row['DOB'], '%d/%m/%y').date()
    #         address = row['Address']
    #         dist_city = row['Dist./City']
    #         if row['State (short)']:
    #             state = request.env['res.country.state'].sudo().search(
    #                 [('country_id.code', '=', 'IN'), ('code', '=', row['State (short)'])]).id
    #             # state = row['State (short)']
    #         pin_code = row['Pin code']
    #         roll_no = row['Roll No.']
    #         code_no = row['Code No.']
    #         xth_std_eng = float(row['%  Xth Std in Eng.'])

    #         if not row['%12th Std in Eng.']:
    #             twelfth_std_eng = 0
    #         else:
    #             twelfth_std_eng = float(row['%12th Std in Eng.'])

    #         if not row['%ITI ']:
    #             iti = 0
    #         else:
    #             iti = float(row['%ITI '])

    #         candidate_st = row['To be mentioned if Candidate SC/ST']

    #         if candidate_st == 'Yes':
    #             candidate_st = True
    #         else:
    #             candidate_st = False

    #         new_candidate = request.env['gp.candidate'].sudo().create({
    #             'name': full_name,
    #             'institute_id': institute_id,
    #             'indos_no': indos_no,
    #             'dob': dob,
    #             'roll_no':roll_no,
    #             'candidate_code':code_no,
    #             # Include other fields here with their corresponding data
    #             'institute_batch_id':batch_id,
    #             'street': address,
    #             'city': dist_city,
    #             'state_id': state,
    #             'zip': pin_code,
    #             'tenth_percent': xth_std_eng,
    #             'twelve_percent': twelfth_std_eng,
    #             'iti_percent': iti,
    #             'sc_st': candidate_st  # Assuming 'Yes' as value for SC/ST
    #             # Add other fields similarly
    #         })

    #         # import wdb; wdb.set_trace()

    #     return request.redirect("/my/gpbatch/candidates/"+str(batch_id))

    
    


    # @http.route(['/my/uploadccmccandidatedata'], type="http", auth="user", website=True)
    # def UploadCcmcCandidateData(self, **kw):
    #     user_id = request.env.user.id
    #     institute_id = request.env["bes.institute"].sudo().search(
    #         [('user_id', '=', user_id)]).id
        
    #     print("Batch id1",kw.get("ccmc_batch_id"))
    #     batch_id = int(kw.get("ccmc_batch_id"))
    #     file_content = kw.get("ccmcfileUpload").read()
    #     filename = kw.get('ccmcfileUpload').filename
    #     file_content_str = file_content.decode('utf-8')

    #     if file_content_str.startswith('\ufeff'):
    #         file_content_str = file_content_str.lstrip('\ufeff')

    #     csv_file = StringIO(file_content_str)
    #     csv_reader = csv.DictReader(csv_file)

    #     for row in csv_reader:
    #         # import wdb; wdb.set_trace()
    #         full_name = row['Full Name of candidate as in INDOS']
    #         indos_no = row['Indos No.']
    #         dob = datetime.strptime(row['DOB'], '%d/%m/%y').date()
    #         address = row['Address']
    #         dist_city = row['Dist./City']
    #         if row['State (short)']:
    #             state = request.env['res.country.state'].sudo().search(
    #                 [('country_id.code', '=', 'IN'), ('code', '=', row['State (short)'])]).id
    #             # state = row['State (short)']
    #         pin_code = row['Pin code']
    #         xth_std_eng = float(row['%  Xth Std in Eng.'])
    #         roll_no = row['Roll No.']
    #         code_no = row['Code No.']

    #         if not row['%12th Std in Eng.']:
    #             twelfth_std_eng = 0
    #         else:
    #             twelfth_std_eng = float(row['%12th Std in Eng.'])

    #         if not row['%ITI ']:
    #             iti = 0
    #         else:
    #             iti = float(row['%ITI '])

    #         candidate_st = row['To be mentioned if Candidate SC/ST']

    #         if candidate_st == 'Yes':
    #             candidate_st = True
    #         else:
    #             candidate_st = False

    #         new_candidate = request.env['ccmc.candidate'].sudo().create({
    #             'name': full_name,
    #             'institute_id': institute_id,
    #             'indos_no': indos_no,
    #             'dob': dob,
    #             # Include other fields here with their corresponding data
    #             'institute_batch_id':batch_id,
    #             'street': address,
    #             'roll_no':roll_no,
    #             'candidate_code':code_no,
    #             'city': dist_city,
    #             'state_id': state,
    #             'zip': pin_code,
    #             'tenth_percent': xth_std_eng,
    #             'twelve_percent': twelfth_std_eng,
    #             'iti_percent': iti,
    #             'sc_st': candidate_st  # Assuming 'Yes' as value for SC/ST
    #             # Add other fields similarly
    #         })

    #         # import wdb; wdb.set_trace()

    #     return request.redirect("/my/ccmcbatch/candidates/"+str(batch_id))

    @http.route(['/my/gpcandidateprofile/<int:candidate_id>'], type="http", auth="user", website=True)
    def GPcandidateProfileView(self, candidate_id, **kw):
        # import wdb; wdb.set_trace()
        candidate = request.env["gp.candidate"].sudo().search(
            [('id', '=', candidate_id)])
        batches = candidate.institute_batch_id
        
        vals = {'candidate': candidate, "page_name": "gp_candidate_form",'batches':batches}
        return request.render("bes.gp_candidate_profile_view", vals)

    @http.route(['/my/ccmccandidateprofile/<int:candidate_id>'], type="http", auth="user", website=True)
    def CcmcCandidateProfileView(self, candidate_id, **kw):
        # import wdb; wdb.set_trace()
        candidate = request.env["ccmc.candidate"].sudo().search(
            [('id', '=', candidate_id)])
        batches = candidate.institute_batch_id
        vals = {'candidate': candidate, "page_name": "ccmc_candidate_form",'batches':batches}
        return request.render("bes.ccmc_candidate_profile_view", vals)
    
    @http.route(['/getcountrystate'],method=["GET"], type="http", auth="user", website=True)
    def GetCountryState(self):
        states = request.env['res.country.state'].sudo().search(
                    [('country_id.code', '=', 'IN')])
        state_data = [{'id': state.id, 'name': state.name} for state in states]
        return json.dumps(state_data)

    @http.route(['/my/creategpinvoice'],method=["POST"], type="http", auth="user", website=True)
    def CreateGPinvoice(self, **kw):
        # import wdb; wdb.set_trace();
        user_id = request.env.user.id
        batch_id = kw.get("invoice_batch_id")
        batch = request.env['institute.gp.batches'].sudo().search([('id','=',batch_id)])
        institute_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)])
        
        partner_id = institute_id.user_id.partner_id.id
        product_id = batch.course.exam_fees.id
        product_price = batch.course.exam_fees.lst_price
        qty = request.env['gp.candidate'].sudo().search_count([('institute_batch_id','=',batch.id),('fees_paid','=','yes')])
        
        # qty = batch.candidate_count
        # import wdb; wdb.set_trace();
        line_items = [(0, 0, {
        'product_id': product_id,
        'price_unit':product_price,
        'quantity':qty
        })]
        
        # import wdb; wdb.set_trace();
        
        invoice_vals = {
            'partner_id': partner_id,  # Replace with the partner ID for the customer
            'move_type': 'out_invoice',
            'invoice_line_ids':line_items,
            'gp_batch_ok':True,
            'batch':batch.id,
            'l10n_in_gst_treatment':'unregistered'
            # Add other invoice fields as needed
        }
        
        
        
        new_invoice = request.env['account.move'].sudo().create(invoice_vals)
        new_invoice.action_post()
        # import wdb; wdb.set_trace();
        batch.write({"invoice_created":True,"account_move":new_invoice.id,'state': '3-pending_invoice'})
        
        return request.redirect("/my/invoices/")
    
    #CCMC Invoice  
    @http.route(['/my/createccmcinvoice'],method=["POST"], type="http", auth="user", website=True)
    def CreateCCMCinvoice(self, **kw):
        # import wdb; wdb.set_trace();
        user_id = request.env.user.id
        print(request.env.user)   
        batch_id = kw.get("ccmc_invoice_batch_id")   
        batch = request.env['institute.ccmc.batches'].sudo().search([('id','=',batch_id)])
        
        institute_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)])
        
        ccmc_partner_id = institute_id.user_id.partner_id.id
        product_id_ccmc = batch.ccmc_course.exam_fees.id
        
        product_price = batch.ccmc_course.exam_fees.lst_price
        
        qty = request.env['ccmc.candidate'].sudo().search_count([('institute_batch_id','=',batch.id),('fees_paid','=','yes')])
        
        # qty = batch.candidate_count
        # import wdb; wdb.set_trace();
        line_items = [(0, 0, {
        'product_id': product_id_ccmc,
        'price_unit':product_price,
        'quantity':qty
        })]
        
        # import wdb; wdb.set_trace();
        
        invoice_vals = {
            'partner_id': ccmc_partner_id,  # Replace with the partner ID for the customer
            'move_type': 'out_invoice',
            'invoice_line_ids':line_items,
            'ccmc_batch_ok':True,
            'ccmc_batch':batch.id,
            'l10n_in_gst_treatment':'unregistered'
            # Add other invoice fields as needed
        }
        
        
        
        new_invoice = request.env['account.move'].sudo().create(invoice_vals)
        new_invoice.action_post()
        # import wdb; wdb.set_trace();
        batch.write({"ccmc_invoice_created":True,"ccmc_account_move":new_invoice.id,'ccmc_state': '3-pending_invoice'})
        
        return request.redirect("/my/invoices/")
    # @http.route(['/my/deletegpcandidate'], type="http", auth="user", website=True)
    # def DeleteGPcandidate(self, **kw):


    @http.route(['/my/deletegpcandidate'], type="http", auth="user", website=True)
    def DeleteGPcandidate(self, **kw):

        user_id = request.env.user.id
        candidate_id = kw.get("candidate_id")
        
        batch = request.env['institute.gp.batches'].sudo().search([('id','=',kw.get("candidate_batch_id"))])
        candidate_user_id = request.env['gp.candidate'].sudo().search([('id','=',kw.get('candidate_id'))]).user_id
        if not candidate_user_id:
            request.env['gp.candidate'].sudo().search([('id','=',kw.get('candidate_id'))]).unlink()
            
            return request.redirect("/my/gpbatch/candidates/"+str(batch.id))
        else:
            raise ValidationError("Not Allowed")
        # import wdb; wdb.set_trace();
    
    
    
    @http.route(['/my/creategpcandidateform'],method=["POST"], type="http", auth="user", website=True)
    def CreateGPcandidate(self, **kw):

        user_id = request.env.user.id
        batch_id = kw.get("batch_id")

        
        batch_name = request.env['institute.gp.batches'].sudo().search([('id','=',batch_id)]).batch_name
        
        institute_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id
        
        if request.httprequest.method == 'POST':
            name = kw.get("name")
            dob = kw.get("dob")
            street = kw.get("street")
            street2 = kw.get("street2")
            city = kw.get("city")
            zip_code = kw.get("zip")
            state_id = kw.get("state_id")
            phone = kw.get("phone")
            mobile = kw.get("mobile")
            email = kw.get("email")
            tenth_percent = kw.get("tenth_percent")
            twelve_percent = kw.get("twelve_percent")
            iti_percent = kw.get("iti_percent")
            sc_st = kw.get("sc_st")
            
            candidate_data = {
                "name": name,
                "institute_batch_id":batch_id,
                "institute_id":institute_id,
                "dob": dob,
                "street": street,
                "street2": street2,
                "city": city,
                "zip": zip_code,
                "state_id": state_id,  # Assuming state_id is a Many2one field
                "phone": phone,
                "mobile": mobile,
                "email": email,
                "tenth_percent": tenth_percent,
                "twelve_percent": twelve_percent,
                "iti_percent": iti_percent,
                "sc_st": sc_st,
            }
            
            
            request.env['gp.candidate'].sudo().create(candidate_data)
            
            return request.redirect("/my/gpbatch/candidates/"+str(batch_id))
        
    @http.route(['/my/createccmccandidateform'],method=["POST"], type="http", auth="user", website=True)
    def CreateCCMCcandidate(self, **kw):
        user_id = request.env.user.id

        batch_id = kw.get("ccmc_candidate_batch_id")
        
        batch_name = request.env['institute.ccmc.batches'].sudo().search([('id','=',batch_id)]).ccmc_batch_name
        
        institute_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id
        
        if request.httprequest.method == 'POST':
            name = kw.get("name")
            dob = kw.get("dob")
            street = kw.get("street")
            street2 = kw.get("street2")
            city = kw.get("city")
            zip_code = kw.get("zip")
            state_id = kw.get("state_id")
            phone = kw.get("phone")
            mobile = kw.get("mobile")
            email = kw.get("email")
            tenth_percent = kw.get("tenth_percent")
            twelve_percent = kw.get("twelve_percent")
            iti_percent = kw.get("iti_percent")
            sc_st = kw.get("sc_st")
            
            candidate_data = {
                "name": name,
                "institute_batch_id":batch_id,
                "institute_id":institute_id,
                "dob": dob,
                "street": street,
                "street2": street2,
                "city": city,
                "zip": zip_code,
                "state_id": state_id,  # Assuming state_id is a Many2one field
                "phone": phone,
                "mobile": mobile,
                "email": email,
                "tenth_percent": tenth_percent,
                "twelve_percent": twelve_percent,
                "iti_percent": iti_percent,
                "sc_st": sc_st,
            }
            
            # import wdb; wdb.set_trace();
            request.env['ccmc.candidate'].sudo().create(candidate_data)
            
            
            return request.redirect("/my/ccmcbatch/candidates/"+str(batch_id))
    
    @http.route('/my/confirmccmcuser', type='http', auth="public", website=True)
    def CreateCCMCUser(self, **kw):

        batch = request.env['ccmc.candidate'].sudo().search([('id', '=', kw.get("confirm_ccmc_candidate_batch_id"))]) 

        batch_id = kw.get("confirm_ccmc_candidate_batch_id")
        candidate = request.env['ccmc.candidate'].sudo().search([('id', '=', kw.get("confirm_ccmc_candidate_id"))])
        
        
        if candidate.indos_no:
            if candidate.candidate_image and candidate.candidate_signature:
               # Create user based on candidate details
                user_values = {
                    'name': candidate.name,
                    'login': candidate.indos_no,  # You can set the login as the same as the user name
                    'password': str(candidate.indos_no) + "1",  # Generate a random password
                }
                portal_user = request.env['res.users'].sudo().create(user_values)
                # Assign the created user to the candidate
                candidate.write({'user_id': portal_user.id})
            else:
                raise ValidationError("Candidate Image or Candidate Signature Missing")
        else:
            raise ValidationError("Indos No. cannot be empty")

        return request.redirect("/my/ccmcbatch/candidates/"+str(batch_id))
    
    @http.route(['/my/deleteccmccandidate'], type="http", auth="user", website=True)
    def DeleteCCMCcandidate(self, **kw):
        
        user_id = request.env.user.id
        candidate_id = kw.get("ccmc_candidate_id")

        print(candidate_id)

        batch = request.env['institute.ccmc.batches'].sudo().search([('id','=',kw.get("delete_ccmc_candidate_batch_id"))])
        
        candidate_user_id = request.env['gp.candidate'].sudo().search([('id','=',kw.get('ccmc_candidate_id'))]).user_id
        if not candidate_user_id:
            request.env['ccmc.candidate'].sudo().search([('id','=',kw.get('ccmc_candidate_id'))]).unlink()
            
            return request.redirect("/my/ccmcbatch/candidates/"+str(batch.id))
        else:
            raise ValidationError("Not Allowed")
        # import wdb; wdb.set_trace();
        
    @http.route('/confirmgpuser', type='http', auth="public", website=True)
    def CreateGPUser(self, **kw):


        batch = request.env['gp.candidate'].sudo().search([('id', '=', kw.get("confirm_gp_candidate_batch_id"))])
        batch_id = kw.get("confirm_gp_candidate_batch_id")

        candidate = request.env['gp.candidate'].sudo().search([('id', '=', kw.get("confirm_gp_candidate_id"))])
        
        
        if candidate.indos_no:
            if candidate.candidate_image and candidate.candidate_signature:
               # Create user based on candidate details
                user_values = {
                    'name': candidate.name,
                    'login': candidate.indos_no,  # You can set the login as the same as the user name
                    'password': str(candidate.indos_no) + "1",  # Generate a random password
                }
                portal_user = request.env['res.users'].sudo().create(user_values)
                # Assign the created user to the candidate
                candidate.write({'user_id': portal_user.id})
            else:
                raise ValidationError("Candidate Image or Candidate Signature Missing")
        else:
            raise ValidationError("Indos No. cannot be empty")

        return request.redirect("/my/gpbatch/candidates/"+str(batch_id))

    @http.route(['/my/gpcandidateform/view/<int:batch_id>'],method=["POST", "GET"], type="http", auth="user", website=True)
    def GPcandidateFormView(self,batch_id, **kw):
        
        # import wdb; wdb.set_trace();
        
        states = request.env['res.country.state'].sudo().search(
                    [('country_id.code', '=', 'IN')])
        
        user_id = request.env.user.id

        batch_name = request.env['institute.gp.batches'].sudo().search([('id','=',batch_id)]).batch_name
        
        institute_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id
        

        if request.httprequest.method == 'POST':
            name = kw.get("name")
            dob = kw.get("dob")
            indos_no = kw.get("indos_no")
            candidate_code = kw.get("candidate_code")
            roll_no = kw.get("roll_no")
            street = kw.get("street")
            street2 = kw.get("street2")
            city = kw.get("city")
            zip_code = kw.get("zip")
            state_id = kw.get("state_id")
            phone = kw.get("phone")
            mobile = kw.get("mobile")
            email = kw.get("email")
            tenth_percent = kw.get("tenth_percent")
            twelve_percent = kw.get("twelve_percent")
            iti_percent = kw.get("iti_percent")
            sc_st = kw.get("sc_st")
            
            candidate_data = {
                "name": name,
                "institute_batch_id":batch_id,
                "institute_id":institute_id,
                "dob": dob,
                "indos_no": indos_no,
                "candidate_code": candidate_code,
                "roll_no": roll_no,
                "street": street,
                "street2": street2,
                "city": city,
                "zip": zip_code,
                "state_id": state_id,  # Assuming state_id is a Many2one field
                "phone": phone,
                "mobile": mobile,
                "email": email,
                "tenth_percent": tenth_percent,
                "twelve_percent": twelve_percent,
                "iti_percent": iti_percent,
                "sc_st": sc_st,
            }
            # import wdb; wdb.set_trace();

            request.env['gp.candidate'].sudo().create(candidate_data)
            
            return request.redirect("/my/gpbatch/candidates/"+str(batch_id))
            
        
        
        vals = {"states" : states,"batch_id":batch_id,"batch_name":batch_name,"page_name":"gp_candidate_form"}
        return request.render("bes.gp_candidate_form_view", vals)



    @http.route(['/my/ccmccandidateform/view/<int:batch_id>'],method=["POST", "GET"], type="http", auth="user", website=True)
    def CcmcCandidateFormView(self,batch_id, **kw):

        states = request.env['res.country.state'].sudo().search(
                    [('country_id.code', '=', 'IN')])
        
        user_id = request.env.user.id

        batch_name = request.env['institute.ccmc.batches'].sudo().search([('id','=',batch_id)]).ccmc_batch_name

        
        institute_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id

        if request.httprequest.method == 'POST':
            name = kw.get("name")
            dob = kw.get("dob")
            indos_no = kw.get("indos_no")
            candidate_code = kw.get("candidate_code")
            roll_no = kw.get("roll_no")
            street = kw.get("street")
            street2 = kw.get("street2")
            city = kw.get("city")
            zip_code = kw.get("zip")
            state_id = kw.get("state_id")
            phone = kw.get("phone")
            mobile = kw.get("mobile")
            email = kw.get("email")
            tenth_percent = kw.get("tenth_percent")
            twelve_percent = kw.get("twelve_percent")
            iti_percent = kw.get("iti_percent")
            sc_st = kw.get("sc_st")
            
            candidate_data = {
                "name": name,
                "institute_batch_id":batch_id,
                "institute_id":institute_id,
                "dob": dob,
                "indos_no": indos_no,
                "candidate_code": candidate_code,
                "roll_no": roll_no,
                "street": street,
                "street2": street2,
                "city": city,
                "zip": zip_code,
                "state_id": state_id,  # Assuming state_id is a Many2one field
                "phone": phone,
                "mobile": mobile,
                "email": email,
                "tenth_percent": tenth_percent,
                "twelve_percent": twelve_percent,
                "iti_percent": iti_percent,
                "sc_st": sc_st,
            }
            # import wdb; wdb.set_trace();

            request.env['ccmc.candidate'].sudo().create(candidate_data)
            
            return request.redirect("/my/ccmcbatch/candidates/"+str(batch_id))
            
        
        
        vals = {"states" : states,"batch_id":batch_id,"batch_name":batch_name,"page_name":"ccmc_candidate_form"}
        return request.render("bes.ccmc_candidate_form_view", vals)

        


    @http.route(['/my/gpfacultiesform/view/<int:batch_id>'],method=["POST", "GET"], type="http", auth="user", website=True)
    def GPFacultiesFormView(self,batch_id, **kw):
        # import wdb; wdb.set_trace();
        states = request.env['res.country.state'].sudo().search(
                    [('country_id.code', '=', 'IN')])
        
        user_id = request.env.user.id

        batch_name = request.env['institute.gp.batches'].sudo().search([('id','=',batch_id)]).batch_name

        
        print("BATCH id2",batch_id)

        if request.httprequest.method == 'POST':
            faculty_name = kw.get("faculty_name")
            # faculty_photo = kw.get('faculty_photo')
            dob = kw.get("dob")
            file_content = kw.get("faculty_photo").read()
            filename = kw.get('faculty_photo').filename
            designation = kw.get("designation")
            qualification = kw.get("qualification")
            contract_terms = kw.get("contract_terms")
            course_name = kw.get('course_name')
            courses_taught = kw.get("courses_taught")
            
            faculty_data = {
                "faculty_name": faculty_name,
                'gp_batches_id':batch_id,
                'faculty_photo':  base64.b64encode(file_content),
                'faculty_photo_name': filename,
                "dob": dob,
                "designation": designation,
                "qualification": qualification,
                "contract_terms": contract_terms,
                "course_name":course_name
                # "courses_taught": courses_taught

            }
            # import wdb; wdb.set_trace();

            request.env['institute.faculty'].sudo().create(faculty_data)
            
            return request.redirect("/my/gpbatch/faculties/"+str(batch_id))
            
        
        
        vals = {"states" : states,"batch_id":batch_id,"page_name":"gp_faculty_form","batch_name":batch_name}
        return request.render("bes.gp_faculty_form_view", vals)

    @http.route(['/my/ccmcfacultiesform/view/<int:batch_id>'],method=["POST", "GET"], type="http", auth="user", website=True)
    def CcmcFacultiesFormView(self,batch_id, **kw):

        states = request.env['res.country.state'].sudo().search(
                    [('country_id.code', '=', 'IN')])
        
        user_id = request.env.user.id
        batch_name = request.env['institute.ccmc.batches'].sudo().search([('id','=',batch_id)]).ccmc_batch_name

        
        print("BATCH id3",batch_id)

        if request.httprequest.method == 'POST':
            faculty_name = kw.get("faculty_name")
            # faculty_photo = kw.get('faculty_photo')
            dob = kw.get("dob")
            file_content = kw.get("faculty_photo").read()
            filename = kw.get('faculty_photo').filename
            designation = kw.get("designation")
            qualification = kw.get("qualification")
            contract_terms = kw.get("contract_terms")
            course_name = kw.get('course_name')
            # courses_taught = kw.get("courses_taught")

            
            faculty_data = {
                "faculty_name": faculty_name,
                'ccmc_batches_id':batch_id,
                'faculty_photo':  base64.b64encode(file_content),
                'faculty_photo_name': filename,
                "dob": dob,
                "designation": designation,
                "qualification": qualification,
                "contract_terms": contract_terms,
                "course_name":course_name
                # "courses_taught": courses_taught

            }
            # import wdb; wdb.set_trace();

            request.env['institute.faculty'].sudo().create(faculty_data)
            
            return request.redirect("/my/ccmcbatch/faculties/"+str(batch_id))
            
        
        
        vals = {"states" : states,"batch_id":batch_id,"page_name":"ccmc_faculty_form","batch_name":batch_name}
        return request.render("bes.gp_faculty_form_view", vals)

   

    @http.route(['/my/gpbatch/candidates/<int:batch_id>','/my/gpbatch/candidates/<int:batch_id>/page/<int:page>'], type="http", auth="user", website=True)
    def GPcandidateListView(self, batch_id,page=1,sortby="id",search="",search_in="All", **kw,):
        
        
        
        
        # sorted_list = {
        #     'id':{'label':'ID Desc', 'order':'id desc'},
        # }
        # search_domain_count = search_list[search_in]["domain"][0]
        # default_order_by = sorted_list[sortby]["order"]

        user_id = request.env.user.id
        institute_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id
        
        search_list = {
            'All':{'label':'All','input':'All','domain':[('institute_id', '=', institute_id),('institute_batch_id', '=', batch_id)]},
            'Name':{'label':'Candidate Name','input':'Name','domain':[('institute_id', '=', institute_id), ('institute_batch_id', '=', batch_id),('name','ilike',search)]},
            'Indos_No':{'label':'Indos No','input':'Indos_No','domain':[('institute_id', '=', institute_id), ('institute_batch_id', '=', batch_id),('indos_no','ilike',search)]},
            'Candidate_Code_No':{'label':'Candidate Code No','input':'Candidate_Code_No','domain':[('institute_id', '=', institute_id), ('institute_batch_id', '=', batch_id),('candidate_code','ilike',search)]},
            'Roll_No':{'label':'Roll No.','input':'Roll_No','domain':[('institute_id', '=', institute_id), ('institute_batch_id', '=', batch_id),('roll_no','ilike',search)]}

        }
        
        # import wdb; wdb.set_trace()
        
        search_domain = search_list[search_in]["domain"]

        
        candidates_count = request.env["gp.candidate"].sudo().search_count(search_domain)
        
        page_detail = pager(url="/my/gpbatch/candidates/"+str(batch_id),
                            total=candidates_count,
                            url_args={'search_in':search_in,'search':search},
                            page=page,
                            step=10
                            )
        candidates = request.env["gp.candidate"].sudo().search(
            search_domain, limit= 10,offset=page_detail['offset'])
        batches = request.env["institute.gp.batches"].sudo().search(
            [('id', '=', batch_id)])
        
        
        
        vals = {'candidates': candidates, 
                'page_name': 'gp_candidate',
                'batch_id':batch_id,
                'batches':batches,
                'pager':page_detail,
                'search_in':search_in,
                'search':search,
                'searchbar_inputs':search_list
                }
        # import wdb; wdb.set_trace()
        
        # self.env["gp.candidate"].sudo().search([('')])
        return request.render("bes.gp_candidate_portal_list", vals)

    

    @http.route(['/my/ccmcbatch/candidates/<int:batch_id>','/my/ccmcbatch/candidates/<int:batch_id>/page/<int:page>'], type="http", auth="user", website=True)
    def CcmcCandidateListView(self, batch_id,page=1, search="",search_in="All",**kw):
        # import wdb; wdb.set_trace()

        

        user_id = request.env.user.id
        institute_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id

        search_list = {
            'All':{'label':'All','input':'All','domain':[('institute_id', '=', institute_id),('institute_batch_id', '=', batch_id)]},
            'Name':{'label':'Candidate Name','input':'Name','domain':[('institute_id', '=', institute_id), ('institute_batch_id', '=', batch_id),('name','ilike',search)]},
            'Indos_No':{'label':'Indos No','input':'Indos_No','domain':[('institute_id', '=', institute_id), ('institute_batch_id', '=', batch_id),('indos_no','ilike',search)]},
            'Candidate_Code_No':{'label':'Candidate Code No','input':'Candidate_Code_No','domain':[('institute_id', '=', institute_id), ('institute_batch_id', '=', batch_id),('candidate_code','ilike',search)]},
            'Roll_No':{'label':'Roll No.','input':'Roll_No','domain':[('institute_id', '=', institute_id), ('institute_batch_id', '=', batch_id),('roll_no','ilike',search)]}

        }

        search_domain = search_list[search_in]["domain"]

        candidates_count = request.env["ccmc.candidate"].sudo().search_count(search_domain)
        page_detail = pager(url="/my/ccmcbatch/candidates/"+str(batch_id),
                            total=candidates_count,
                            url_args={'search_in':search_in,'search':search},
                            page=page,
                            step=10
                            )
        
        candidates = request.env["ccmc.candidate"].sudo().search(search_domain, limit= 10,offset=page_detail['offset'])
        batches = request.env["institute.ccmc.batches"].sudo().search(
            [('id', '=', batch_id)])
        vals = {'candidates': candidates,
                'page_name': 'ccmc_candidate',
                'batch_id':batch_id,
                'batches':batches,
                'pager':page_detail,
                'search_in':search_in,
                'search':search,
                'searchbar_inputs':search_list
                }
        print("Batch id4",batch_id)
        # import wdb; wdb.set_trace()
        return request.render("bes.ccmc_candidate_portal_list", vals)


    @http.route(['/my/gpbatch/faculties/<int:batch_id>'], type="http", auth="user", website=True)
    def GPFacultyListView(self, batch_id, **kw):
        user_id = request.env.user.id
        
        gp_batches_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id
        
        faculties = request.env["institute.faculty"].sudo().search(
            [('gp_batches_id', '=', batch_id)])
        # import wdb; wdb.set_trace()
        
        vals = {'faculties': faculties, 'page_name': 'gp_faculty_list','batch_id':batch_id}
        # self.env["gp.candidate"].sudo().search([('')])
        return request.render("bes.gp_faculty_portal_list", vals)


    @http.route(['/my/ccmcbatch/faculties/<int:batch_id>'], type="http", auth="user", website=True)
    def CcmcFacultyListView(self, batch_id, **kw):
        # import wdb; wdb.set_trace()

        user_id = request.env.user.id
        ccmc_batches_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id
        faculties = request.env["institute.faculty"].sudo().search(
            [('ccmc_batches_id', '=', batch_id)])
        vals = {'faculties': faculties, 'page_name': 'ccmc_faculty_list','batch_id':batch_id}
        # self.env["gp.candidate"].sudo().search([('')])
        return request.render("bes.gp_faculty_portal_list", vals)
   
    @http.route(['/my/institute_document/list'], type="http", auth="user", website=True)
    def InstituteDocumentList(self, **kw):
    
        user_id = request.env.user.id
    
        # institute_id = request.env["bes.institute"].sudo().search(
        #     [('user_id', '=', user_id)]).id

        institute = request.env["bes.institute"].sudo().search([('user_id', '=', user_id)])

        gp_batches = request.env['institute.gp.batches'].sudo().search([('institute_id','=',institute.id)])
        ccmc_batches = request.env['institute.ccmc.batches'].sudo().search([('institute_id','=',institute.id)])
            
        
        lod = request.env["lod.institute"].sudo().search(
            [('institute_id', '=', institute.id)])
        
        # import wdb; wdb.set_trace()
    
        
        vals = {'lods': lod, 'page_name': 'lod_list'}
    
        return request.render("bes.institute_document_list", vals)
    
    

    @http.route(['/my/updategpcandidate'], method=["POST", "GET"], type="http", auth="user", website=True)
    def UpdateCandidate(self, **kw):
        import wdb; wdb.set_trace()
        candidate = request.env["gp.candidate"].sudo().search(
            [('id', '=',int(kw.get("canidate_id")) )])
        
        
        
        if request.httprequest.method == 'POST':
            # import wdb; wdb.set_trace()
            candidate_image = kw.get("candidate_photo").read()
            candidate_image_name = kw.get('candidate_photo').filename
            
            if candidate_image and candidate_image_name:
                candidate.write({'candidate_image': base64.b64encode(candidate_image),
                             'candidate_image_name':  candidate_image_name,
                             })
                
            signature_photo = kw.get("signature_photo").read()
            signature_photo_name = kw.get('signature_photo').filename
            
            # print(signature_photo)
            # print(signature_photo_name)
            # # import wdb; wdb.set_trace()
            # print(signature_photo and signature_photo_name)
            if signature_photo and signature_photo_name:
                candidate.write({'candidate_signature': base64.b64encode(signature_photo),
                             'candidate_signature_name':  signature_photo_name,
                             })
            candidate_details = {
                'indos_no':kw.get('indos_no'),
                'name':kw.get('full_name'),
                'email':kw.get('e_mail'),
                'phone':kw.get('phone'),
                'mobile':kw.get('mobile'),
                'street':kw.get('street'),
                'street2':kw.get('street2'),
            }
            
            for key, value in candidate_details.items():
                if value:
                    candidate.write({key: value})
            
            # import wdb; wdb.set_trace()
            
            return request.redirect('/my/gpcandidateprofile/'+str(kw.get("canidate_id")))
            
        # import wdb; wdb.set_trace() 
        batches = request.env["institute.gp.batches"].sudo().search([('id', '=', batch_id)])
        vals = {'batches':batches}
        return request.render("bes.gp_candidate_profile_view", vals)




    @http.route(['/my/updateccmccandidate'], method=["POST", "GET"], type="http", auth="user", website=True)
    def UpdateCcmcCandidate(self, **kw):
        # import wdb; wdb.set_trace()
        candidate = request.env["ccmc.candidate"].sudo().search(
            [('id', '=',int(kw.get("canidate_id")) )])
        
        if request.httprequest.method == 'POST':
            # import wdb; wdb.set_trace()
            candidate_image = kw.get("candidate_photo").read()
            candidate_image_name = kw.get('candidate_photo').filename
            
            if candidate_image and candidate_image_name:
                candidate.write({'candidate_image': base64.b64encode(candidate_image),
                             'candidate_image_name':  candidate_image_name,
                             })
                
            signature_photo = kw.get("signature_photo").read()
            signature_photo_name = kw.get('signature_photo').filename
            
            # print(signature_photo)
            # print(signature_photo_name)
            # # import wdb; wdb.set_trace()
            # print(signature_photo and signature_photo_name)
            if signature_photo and signature_photo_name:
                candidate.write({'candidate_signature': base64.b64encode(signature_photo),
                             'candidate_signature_name':  signature_photo_name,
                             })
                
            indos_no = kw.get('indos_no')
            
            if indos_no:
                candidate.write({'indos_no':indos_no})
            
            # import wdb; wdb.set_trace()
            
            return request.redirect('/my/ccmccandidateprofile/'+str(kw.get("canidate_id")))
            
            
       
        vals = {}
        return request.render("bes.ccmc_candidate_profile_view", vals)




        
    
    @http.route(['/my/institute_document/download/<model("lod.institute"):document_id>'], type="http", auth="user", website=True)
    def InstituteDocumentDownload(self, document_id, **kw):
        # import wdb; wdb.set_trace()
        document = request.env['lod.institute'].sudo().browse(document_id.id)

        if document and document.document_file:  # Ensure the document and file data exist
            file_content = base64.b64decode(
                document.document_file)  # Decoding file data
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



    @http.route(['/my/institute_document'], type="http", method=["POST", "GET"], auth="user", website=True)
    def InstituteDocumentView(self, **kw):

        user_id = request.env.user.id
        institute_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id
        # import wdb; wdb.set_trace()

        if request.httprequest.method == 'POST':
            # import wdb; wdb.set_trace()
            file_content = kw.get("fileUpload").read()
            filename = kw.get('fileUpload').filename
            # attachment = uploaded_file.read()
            
            

            data = request.env["lod.institute"].sudo().create({'institute_id': institute_id,
                                                               'document_name': kw.get('documentName'),
                                                               'upload_date': kw.get('uploadDate'),
                                                               'document_file':  base64.b64encode(file_content),
                                                               'documents_name': filename
                                                               })
            # 'document_file': uploaded_file

            return request.redirect('/my/institute_document/list')
        else:
            vals = {}
            return request.render("bes.institute_documents_form", vals)

    @http.route(['/my/ccmccandidate/list'], type="http", auth="user", website=True)
    def CCMCcandidateListView(self, **kw):
        # import wdb; wdb.set_trace()

        user_id = request.env.user.id
        institute_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id
        candidates = request.env["ccmc.candidate"].sudo().search(
            [('institute_id', '=', institute_id)])
        vals = {'candidates': candidates, 'page_name': 'ccmc_candidate'}
        # self.env["gp.candidate"].sudo().search([('')])
        return request.render("bes.ccmc_candidate_portal_list", vals)

    @http.route(['/my/editinstitute'], method=["POST", "GET"], type="http", auth="user", website=True)
    def editInstituteView(self, **kw):
        

        user_id = request.env.user.id
        institute = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)])

        if request.httprequest.method == 'POST':
            
            
            institute.write({"email": kw.get("email"),
                             "street": kw.get("street"),
                             "street2": kw.get("street2"),
                             "city": kw.get("city"),
                             "zip": kw.get("zip"),
                             "principal_name": kw.get("principal_name"),
                             "principal_phone": kw.get("principal_phone"),
                             "principal_mobile": kw.get("principal_mobile"),
                             "principal_email": kw.get("principal_email"),
                             "admin_phone": kw.get("admin_phone"),
                             "admin_mobile": kw.get("admin_mobile"),
                             "admin_email": kw.get("admin_email"),
                             "name_of_second_authorized_person": kw.get("second_authorized_person"),
                             "computer_lab_pc_count": kw.get("computer_lab_pc_count"),
                             "internet_strength": kw.get("internet_strength"),
                             "ip_address": kw.get("ip_address")
                             })
            

            vals = {'institutes': institute, 'page_name': 'institute_page'}
            institute.user_id.write({'email': kw.get("email"),'login':kw.get("email")})

            return request.render("bes.institute_detail_form", vals)

        else:

            vals = {'institutes': institute, 'page_name': 'institute_page'}
            return request.render("bes.institute_detail_form", vals)




    @http.route(['/my/addshipvisit'], method=["POST", "GET"], type="http", auth="user", website=True)
    def AddShipVisits(self, **kw):
        
        # Extracting data from the HTML form
        candidate_id = kw.get("candidate_id")
        name_of_ships = kw.get("name_of_ships")
        imo_no = kw.get("imo_no")
        name_of_ports_visited = kw.get("name_of_ports_visited")
        date_of_visits = kw.get("date_of_visits")
        time_spent_on_ship = kw.get("time_spent_on_ship")
        bridge = kw.get("bridge")
        eng_room = kw.get("eng_room")
        cargo_area = kw.get("cargo_area")

        # Assuming 'gp.candidate' is the model
        candidate_data = {
            "candidate_id":candidate_id,
            "name_of_ships": name_of_ships,
            "imo_no": imo_no,
            "name_of_ports_visited": name_of_ports_visited,
            "date_of_visits": date_of_visits,
            "time_spent_on_ship": time_spent_on_ship,
            "bridge": bridge,
            "eng_room": eng_room,
            "cargo_area": cargo_area,
        }
        
        request.env['gp.candidate.ship.visits'].sudo().create(candidate_data)
        # import wdb; wdb.set_trace()

        # Create a record in the 'gp.candidate' model
        
        return request.redirect('/my/gpcandidateprofile/'+str(kw.get("candidate_id")))


    @http.route(['/my/addccmcshipvisit'], method=["POST", "GET"], type="http", auth="user", website=True)
    def AddCcmcShipVisits(self, **kw):
        
        # Extracting data from the HTML form
        candidate_id = kw.get("candidate_id")
        name_of_ships = kw.get("name_of_ships")
        imo_no = kw.get("imo_no")
        name_of_ports_visited = kw.get("name_of_ports_visited")
        date_of_visits = kw.get("date_of_visits")
        time_spent_on_ship = kw.get("time_spent_on_ship")
        bridge = kw.get("bridge")
        eng_room = kw.get("eng_room")
        cargo_area = kw.get("cargo_area")

        # Assuming 'gp.candidate' is the model
        candidate_data = {
            "candidate_id":candidate_id,
            "name_of_ships": name_of_ships,
            "imo_no": imo_no,
            "name_of_ports_visited": name_of_ports_visited,
            "date_of_visits": date_of_visits,
            "time_spent_on_ship": time_spent_on_ship,
            "bridge": bridge,
            "eng_room": eng_room,
            "cargo_area": cargo_area,
        }
        
        request.env['ccmc.candidate.ship.visits'].sudo().create(candidate_data)
        # import wdb; wdb.set_trace()

        # Create a record in the 'gp.candidate' model
        
        return request.redirect('/my/ccmccandidateprofile/'+str(kw.get("candidate_id")))
        
        
    @http.route(['/my/shipvisit/delete'], method=["POST", "GET"], type="http", auth="user", website=True)
    def DeleteShipVisits(self, **kw):
        
        visit_id = kw.get("visit_id")
        request.env['gp.candidate.ship.visits'].sudo().search([('id','=',visit_id)]).unlink()
        
        
        return request.redirect('/my/gpcandidateprofile/'+str(kw.get("candidate_id")))

    @http.route(['/my/ccmcshipvisit/delete'], method=["POST", "GET"], type="http", auth="user", website=True)
    def DeleteCcmcShipVisits(self, **kw):
        
        visit_id = kw.get("visit_id")
        request.env['ccmc.candidate.ship.visits'].sudo().search([('id','=',visit_id)]).unlink()
        print("Delete ccmc ship visit",str(kw.get("candidate_id")))
        
        
        return request.redirect('/my/ccmccandidateprofile/'+str(kw.get("candidate_id")))
    
    @http.route(['/my/gpcandidate/addstcw'], method=["POST", "GET"], type="http", auth="user", website=True)
    def AddSTCW(self, **kw):
        
        candidate_id = kw.get('candidate_id')
        course_name = kw.get('course_name')
        institute_name = kw.get('institute_name')
        marine_training_inst_number = kw.get('marine_training_inst_number')
        mti_indos_no = kw.get('mti_indos_no')
        candidate_cert_no = kw.get('candidate_cert_no')
        course_start_date = kw.get('course_start_date')
        course_end_date = kw.get('course_end_date')
        certificate_upload = kw.get('certificate_upload')
        
        file_content = certificate_upload.read()
        filename = certificate_upload.filename

        stcw_data = {
            'candidate_id' : candidate_id,
            'course_name': course_name,
            'institute_name': institute_name,
            'marine_training_inst_number': marine_training_inst_number,
            'mti_indos_no': mti_indos_no,
            'candidate_cert_no': candidate_cert_no,
            'course_start_date': course_start_date,
            'course_end_date': course_end_date,
            'file_name': filename,
            'certificate_upload': base64.b64encode(file_content)
        }
        request.env["gp.candidate.stcw.certificate"].sudo().create(stcw_data)

        
        return request.redirect('/my/gpcandidateprofile/'+str(kw.get("candidate_id")))


    
    @http.route(['/my/ccmccandidate/addstcw'], method=["POST", "GET"], type="http", auth="user", website=True)
    def AddCcmcSTCW(self, **kw):
        
        candidate_id = kw.get('candidate_id')
        course_name = kw.get('course_name')
        institute_name = kw.get('institute_name')
        marine_training_inst_number = kw.get('marine_training_inst_number')
        mti_indos_no = kw.get('mti_indos_no')
        candidate_cert_no = kw.get('candidate_cert_no')
        course_start_date = kw.get('course_start_date')
        course_end_date = kw.get('course_end_date')
        certificate_upload = kw.get('certificate_upload')
        
        file_content = certificate_upload.read()
        filename = certificate_upload.filename

        stcw_data = {
            'candidate_id' : candidate_id,
            'course_name': course_name,
            'institute_name': institute_name,
            'marine_training_inst_number': marine_training_inst_number,
            'mti_indos_no': mti_indos_no,
            'candidate_cert_no': candidate_cert_no,
            'course_start_date': course_start_date,
            'course_end_date': course_end_date,
            'file_name': filename,
            'certificate_upload': base64.b64encode(file_content)
        }
        request.env["ccmc.candidate.stcw.certificate"].sudo().create(stcw_data)

        
        return request.redirect('/my/ccmccandidateprofile/'+str(kw.get("candidate_id")))
    
    
    @http.route(['/my/gpcandidate/updatefees'], method=["POST", "GET"], type="http", auth="user", website=True)
    def UpdateFees(self, **kw):
        candidate_id = kw.get('candidate_id')
        fees_paid = kw.get('fees_paid')
        
        
        candidate = request.env["gp.candidate"].sudo().search(
            [('id', '=', int(candidate_id))])
        
        candidate.write({'fees_paid':fees_paid})
        
        return request.redirect('/my/gpcandidateprofile/'+str(kw.get("candidate_id")))


    @http.route(['/my/gpcandidate/addattendance'], method=["POST", "GET"], type="http", auth="user", website=True)
    def UpdateGpAttendance(self, **kw):
        candidate_id = kw.get('candidate_id')
        attendance1 = kw.get('attendance1')
        attendance2 = kw.get('attendance2')

        
        
        candidate = request.env["gp.candidate"].sudo().search(
            [('id', '=', int(candidate_id))])
        
        candidate.write({'attendance_compliance_1':attendance1})
        candidate.write({'attendance_compliance_2':attendance2})

        
        return request.redirect('/my/gpcandidateprofile/'+str(kw.get("candidate_id")))

    @http.route(['/my/ccmccandidate/addattendance'], method=["POST", "GET"], type="http", auth="user", website=True)
    def UpdateCcmcAttendance(self, **kw):
        candidate_id = kw.get('candidate_id')
        attendance1 = kw.get('attendance1')
        attendance2 = kw.get('attendance2')

        
        
        candidate = request.env["ccmc.candidate"].sudo().search(
            [('id', '=', int(candidate_id))])
        
        candidate.write({'attendance_compliance_1':attendance1})
        candidate.write({'attendance_compliance_2':attendance2})

        
        return request.redirect('/my/ccmccandidateprofile/'+str(kw.get("candidate_id")))

    @http.route(['/my/ccmccandidate/updatefees'], method=["POST", "GET"], type="http", auth="user", website=True)
    def UpdateCcmcFees(self, **kw):
        candidate_id = kw.get('candidate_id')
        fees_paid = kw.get('fees_paid')
        
        
        candidate = request.env["ccmc.candidate"].sudo().search(
            [('id', '=', int(candidate_id))])
        
        candidate.write({'fees_paid':fees_paid})
        
        return request.redirect('/my/ccmccandidateprofile/'+str(kw.get("candidate_id")))
    
    @http.route('/my/batches/download_report/<int:batch_id>', type='http', auth='user',website=True)
    def generate_report(self,batch_id ):
        
        excel_buffer = io.BytesIO()

        # Create a new Excel workbook and add a worksheet
        workbook = xlsxwriter.Workbook(excel_buffer)
        
        gp_candidates = request.env["gp.candidate"].sudo().search([('institute_batch_id','=',batch_id)])
        faculties = request.env["institute.faculty"].sudo().search([('gp_batches_id','=',batch_id)])
        institutes = request.env["institute.gp.batches"].sudo().search([('id','=',batch_id)])
        
        # print(institutes.dgs_approved_capacity)
        
        
        institute_worksheet = workbook.add_worksheet("Institute")
        institute_worksheet.set_column('A:B', 60)
        date_format = workbook.add_format({'num_format': 'dd-mmm-yy'})
        bold_format = workbook.add_format({'bold': True, 'border': 1,'font_size': 16})  # 'border': 1 adds a thin border

        # Create a format with borders.
        border_format = workbook.add_format({'border': 1,'font_size': 14}) 

        # bold_format = workbook.add_format({'bold': True})
        
        # border_format = workbook.add_format({'border': 1})  # 'border': 1 adds a thin border

        
        headers = ['', '']
        for col_num, header in enumerate(headers):
            institute_worksheet.write(0, col_num, header)

        # Add data to the worksheet.
        data = [
            ['Name of the Institute', institutes.institute_id.name],
            ['MTI No. of institute', institutes.institute_id.mti],
            ['Approved Capacity', institutes.dgs_approved_capacity],
            ['Course Title', institutes.course.name],
            ['Batch No.', institutes.batch_name],
            # ['DOB.',gp_candidate.dob],
            ['Date of commencement and ending of the course', str(institutes.from_date) + ' to ' + str(institutes.to_date)],
        ]
        
        for row_num, row_data in enumerate(data, start=1):
            for col_num, cell_data in enumerate(row_data):
                if col_num == 0:  # Check if it's column A
                    institute_worksheet.write(row_num, col_num, cell_data, bold_format)
                else:
                    institute_worksheet.write(row_num, col_num, cell_data, border_format)

        
        # table_range = 'A1:B{}'.format(len(data))  # No +1 for header row.

        # Add a table to the worksheet.
        # institute_worksheet.add_table(table_range, {'columns': [{'header': header} for header in headers]})


        # institute_worksheet.write('A1','Information of Institute',bold_format)
        # institute_worksheet.write('A2','Name of the Institute',bold_format)
        # institute_worksheet.write('A3','MTI No. of institute',bold_format)
        # institute_worksheet.write('A4','Approved Capacity',bold_format)
        # institute_worksheet.write('A5','Course Title',bold_format)
        # institute_worksheet.write('A6','Batch No.',bold_format)
        # institute_worksheet.write('A7','Date of commencement and ending of the course',bold_format)
        

        # institute_worksheet.write(1,1,institutes.institute_id.name)
        # institute_worksheet.write(2,1,institutes.institute_id.mti)
        # institute_worksheet.write(3,1,institutes.institute_id.computer_lab_pc_count)
        # institute_worksheet.write(4,1,institutes.course.name)
        # institute_worksheet.write(5,1,institutes.batch_name)
        # institute_worksheet.write(6,1,str(institutes.from_date) + ' to ' + str(institutes.to_date))
        

        #Candidate
        
        candidate_worksheet = workbook.add_worksheet("Candidate")
        # candidate_worksheet.write('A1', 'Candidate Name')

        candidate_worksheet.write('A1', 'SR. NO.')
        candidate_worksheet.write('B1', 'ROLL NO')
        candidate_worksheet.write('C1', 'NAME')
        candidate_worksheet.write('D1', 'DOB')
        candidate_worksheet.write('E1', 'Xth')
        candidate_worksheet.write('F1', 'XIIth')


        row = 1
        
        for gp_candidate in gp_candidates:
            candidate_worksheet.write(row,0,row)
            candidate_worksheet.write(row,1,gp_candidate.roll_no)
            candidate_worksheet.write(row,2,gp_candidate.name)
            candidate_worksheet.write(row,3,gp_candidate.dob,date_format)
            candidate_worksheet.write(row,4,gp_candidate.tenth_percent)
            candidate_worksheet.write(row,5,gp_candidate.twelve_percent)
            row += 1
        
        #Faculty
        
        faculty_worksheet = workbook.add_worksheet("Faculty")
        

        faculty_worksheet.write('A1', 'Qualification')
        faculty_worksheet.write('B1', 'Faculty Name')
        faculty_worksheet.write('C1', 'Specialization')
        faculty_worksheet.write('D1', 'DOB')
        faculty_worksheet.write('E1', 'FT or PT')




        
        row = 1
        for faculty in faculties:
            faculty_worksheet.write(row,0,faculty.qualification)
            faculty_worksheet.write(row,1,faculty.faculty_name)
            faculty_worksheet.write(row,2,faculty.designation)
            faculty_worksheet.write(row,3,faculty.dob,date_format)
            row += 1

        

        
    

        # Close the workbook to save the data to the buffer
        workbook.close()

        # Set the buffer position to the beginning
        excel_buffer.seek(0)

        # Generate a response with the Excel file
        response = request.make_response(
            excel_buffer.getvalue(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', 'attachment; filename=my_excel_file.xlsx')
            ]
        )

        # Clean up the buffer
        excel_buffer.close()

        return response
        

    @http.route('/my/ccmc_batches/download_report/<int:batch_id>', type='http', auth='user',website=True)
    def generate_ccmc_report(self,batch_id ):
        
        excel_buffer = io.BytesIO()

        # Create a new Excel workbook and add a worksheet
        workbook = xlsxwriter.Workbook(excel_buffer)
        
        ccmc_candidates = request.env["ccmc.candidate"].sudo().search([('institute_batch_id','=',batch_id)])
        faculties = request.env["institute.faculty"].sudo().search([('ccmc_batches_id','=',batch_id)])
        institutes = request.env["institute.ccmc.batches"].sudo().search([('id','=',batch_id)])
        
        
        
        institute_worksheet = workbook.add_worksheet("Institute")
        institute_worksheet.set_column('A:B', 60)
        date_format = workbook.add_format({'num_format': 'dd-mmm-yy'})
        bold_format = workbook.add_format({'bold': True, 'border': 1,'font_size': 16})  # 'border': 1 adds a thin border

        # Create a format with borders.
        border_format = workbook.add_format({'border': 1,'font_size': 14}) 

        # bold_format = workbook.add_format({'bold': True})
        
        # border_format = workbook.add_format({'border': 1})  # 'border': 1 adds a thin border

        
        headers = ['', '']
        for col_num, header in enumerate(headers):
            institute_worksheet.write(0, col_num, header)

        # Add data to the worksheet.
        data = [
            ['Name of the Institute', institutes.institute_id.name],
            ['MTI No. of institute', institutes.institute_id.mti],
            ['Approved Capacity', institutes.dgs_approved_capacity],
            ['Course Title', institutes.ccmc_course.name],
            ['Batch No.', institutes.ccmc_batch_name],
            ['Date of commencement and ending of the course', str(institutes.ccmc_from_date) + ' to ' + str(institutes.ccmc_to_date)],
        ]
        
        for row_num, row_data in enumerate(data, start=1):
            for col_num, cell_data in enumerate(row_data):
                if col_num == 0:  # Check if it's column A
                    institute_worksheet.write(row_num, col_num, cell_data, bold_format)
                else:
                    institute_worksheet.write(row_num, col_num, cell_data, border_format)

        
        # table_range = 'A1:B{}'.format(len(data))  # No +1 for header row.

        # Add a table to the worksheet.
        # institute_worksheet.add_table(table_range, {'columns': [{'header': header} for header in headers]})


        # institute_worksheet.write('A1','Information of Institute',bold_format)
        # institute_worksheet.write('A2','Name of the Institute',bold_format)
        # institute_worksheet.write('A3','MTI No. of institute',bold_format)
        # institute_worksheet.write('A4','Approved Capacity',bold_format)
        # institute_worksheet.write('A5','Course Title',bold_format)
        # institute_worksheet.write('A6','Batch No.',bold_format)
        # institute_worksheet.write('A7','Date of commencement and ending of the course',bold_format)
        

        # institute_worksheet.write(1,1,institutes.institute_id.name)
        # institute_worksheet.write(2,1,institutes.institute_id.mti)
        # institute_worksheet.write(3,1,institutes.institute_id.computer_lab_pc_count)
        # institute_worksheet.write(4,1,institutes.course.name)
        # institute_worksheet.write(5,1,institutes.batch_name)
        # institute_worksheet.write(6,1,str(institutes.from_date) + ' to ' + str(institutes.to_date))
        

        #Candidate
        
        candidate_worksheet = workbook.add_worksheet("Candidate")
        # candidate_worksheet.write('A1', 'Candidate Name')

        candidate_worksheet.write('A1', 'SR. NO.')
        candidate_worksheet.write('B1', 'ROLL NO')
        candidate_worksheet.write('C1', 'NAME')
        candidate_worksheet.write('D1', 'DOB')
        candidate_worksheet.write('E1', 'Xth')
        candidate_worksheet.write('F1', 'XIIth')


        row = 1
        
        for ccmc_candidate in ccmc_candidates:
            candidate_worksheet.write(row,0,row)
            candidate_worksheet.write(row,1,ccmc_candidate.roll_no)
            candidate_worksheet.write(row,2,ccmc_candidate.name)
            candidate_worksheet.write(row,3,ccmc_candidate.dob,date_format)
            candidate_worksheet.write(row,4,ccmc_candidate.tenth_percent)
            candidate_worksheet.write(row,5,ccmc_candidate.twelve_percent)
            row += 1
        
        #Faculty
        
        faculty_worksheet = workbook.add_worksheet("Faculty")
        faculty_worksheet.write('A1', 'Qualification')
        faculty_worksheet.write('B1', 'Faculty Name')
        faculty_worksheet.write('C1', 'Specialization')
        faculty_worksheet.write('D1', 'DOB')
        faculty_worksheet.write('E1', 'FT or PT')




        
        row = 1
        for faculty in faculties:
            faculty_worksheet.write(row,0,faculty.qualification)
            faculty_worksheet.write(row,1,faculty.faculty_name)
            faculty_worksheet.write(row,2,faculty.designation)
            faculty_worksheet.write(row,3,faculty.dob,date_format)
            row += 1

        

        
    

        # Close the workbook to save the data to the buffer
        workbook.close()

        # Set the buffer position to the beginning
        excel_buffer.seek(0)

        # Generate a response with the Excel file
        response = request.make_response(
            excel_buffer.getvalue(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', 'attachment; filename=my_excel_file.xlsx')
            ]
        )

        # Clean up the buffer
        excel_buffer.close()

        return response
        
    
    def _get_report_data(self):
        # Your logic to fetch data for the report
        data = request.env['res.partner'].search([])
        return 
    
    
    @http.route(['/my/gpcandidates/download_admit_card/<int:candidate_id>'], method=["POST", "GET"], type="http", auth="user", website=True)
    def DownloadsAdmitCard(self,candidate_id,**kw ):
        # import wdb; wdb.set_trace()
        try:
            exam_id = request.env['gp.exam.schedule'].sudo().search([('gp_candidate','=',candidate_id)])[-1]
        except:
            raise ValidationError("Admit Card Not Found or Not Generated")
        report_action = request.env.ref('bes.candidate_gp_admit_card_action')
        pdf, _ = report_action.sudo()._render_qweb_pdf(int(exam_id))
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)
    

    @http.route(['/my/gpcandidates/download_gp_certificate/<int:candidate_id>'], method=["POST", "GET"], type="http", auth="user", website=True)
    def DownloadGPCertificate(self,candidate_id,**kw ):
        # import wdb; wdb.set_trace()
        try:
            exam_id = request.env['gp.exam.schedule'].sudo().search([('gp_candidate','=',candidate_id),('certificate_criteria','=','passed')])
        except:
            raise ValidationError("Certificate Not Generated")
        report_action = request.env.ref('bes.report_gp_certificate')
        pdf, _ = report_action.sudo()._render_qweb_pdf(int(exam_id.id))
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route(['/my/gpcandidates/download_admit_card_from_url/<int:rec_id>'], type='http', auth="user", website=True)
    def download_admit_card_from_url(self, rec_id, **kw):
        # Retrieve the record
        report_action = request.env.ref('bes.candidate_gp_admit_card_action')

        # Check if the user has access to the record
        if report_action.check_access_rights('read', raise_exception=False):
            # Perform operations
            pdf_content, _ = report_action.sudo()._render_qweb_pdf(rec_id)

            # Set PDF headers
            pdf_http_headers = [('Content-Type', 'application/pdf'), ('Content-Length', str(len(pdf_content)))]

    
 
         
    

    @http.route(['/my/ccmccandidates/download_admit_card/<int:candidate_id>'], method=["POST", "GET"], type="http", auth="user", website=True)
    def DownloadCcmcAdmitCard(self,candidate_id,**kw ):
        # import wdb; wdb.set_trace()
        try:
            exam_id = request.env['ccmc.exam.schedule'].sudo().search([('ccmc_candidate','=',candidate_id)])[-1]
        except:
            raise ValidationError("Admit Card Not Found or Not Generated")
        
        report_action = request.env.ref('bes.candidate_ccmc_admit_card_action')
        pdf, _ = report_action.sudo()._render_qweb_pdf(int(exam_id))
        # print(pdf ,"Tbis is PDF")
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)
    
    
    
    @http.route(['/my/ccmccandidates/download_ccmc_certificate/<int:candidate_id>'], method=["POST", "GET"], type="http", auth="user", website=True)
    def DownloadCCMCCertificate(self,candidate_id,**kw ):
        # import wdb; wdb.set_trace()
        try:
            exam_id = request.env['ccmc.exam.schedule'].sudo().search([('ccmc_candidate','=',candidate_id),('certificate_criteria','=','passed')])
        except:
            raise ValidationError("Certificate Not Generated")
        report_action = request.env.ref('bes.report_ccmc_certificate')
        pdf, _ = report_action.sudo()._render_qweb_pdf(int(exam_id.id))
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)
    

    


    @http.route('/my/ccmcbatch/candidates/download_format', type='http', auth='user',website=True)
    def generate_ccmc_student_format(self ):
        excel_buffer = io.BytesIO()

        # Create a new Excel workbook and add a worksheet
        workbook = xlsxwriter.Workbook(excel_buffer)
        candidate_worksheet = workbook.add_worksheet("Candidates")
        
        
        locked = workbook.add_format({'locked':True})
        unlocked = workbook.add_format({'locked':False})
        candidate_worksheet.set_column('A:XDF', None, unlocked)

        candidate_worksheet.set_column('A:A',15,unlocked)
        candidate_worksheet.set_column('B:B',30,unlocked)
        candidate_worksheet.set_column('D:D',30,unlocked)
        candidate_worksheet.set_column('E:E',30,unlocked)
        candidate_worksheet.set_column('F:F',20,unlocked)
        candidate_worksheet.set_column('G:G',15,unlocked)
        candidate_worksheet.set_column('H:H',10,unlocked)
        candidate_worksheet.set_column('I:I',20,unlocked)
        candidate_worksheet.set_column('J:J',20,unlocked)
        candidate_worksheet.set_column('K:K',20,unlocked)
        candidate_worksheet.set_column('L:L',10,unlocked)
        candidate_worksheet.set_column('M:M',10,unlocked)
        candidate_worksheet.set_column('N:N',10,unlocked)
        candidate_worksheet.set_column('O:O',10,unlocked)
        candidate_worksheet.protect()
        date_format = workbook.add_format({'num_format': 'dd-mmm-yy','locked':False})
        # number_format = workbook.add_format({'num_format': '0000000000', 'locked': False})
        # zip_format = workbook.add_format({'num_format': '000000', 'locked': False})

        # bold_format = workbook.add_format({'bold': True, 'border': 1,'font_size': 16})


        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': 'white',
            'bg_color': '#336699',  # Blue color for the background
            'locked':True
        })
        
        header = ['INDOS NO', 'NAME', 'DOB', 'STREET', 'STREET2', 'CITY', 'ZIP', 'STATE', 'PHONE', 'MOBILE', 'EMAIL', 'Xth', 'XIIth', 'ITI', 'SC/ST/OBC']
        for col, value in enumerate(header):
            candidate_worksheet.write(0, col, value, header_format)

        # Set date format for DOB column
        candidate_worksheet.set_column('C:C', 20, date_format)
        # candidate_worksheet.set_column('J:J', None, number_format)
        # candidate_worksheet.set_column('G:G', None, zip_format)



        dropdown_values = ['Yes', 'No']

        state_values = ['JK','MH', 'AP', 'AR', 'AS', 'BR', 'CT', 'GA', 'GJ', 'HR', 'HP', 'JH', 'KA', 'KL', 'MP', 'MN', 'ML', 'MZ', 'NL', 'OD', 'PB', 'RJ', 'SK', 'TN', 'TG', 'TR', 'UP', 'UK', 'WB', 'CH', 'LD', 'DL', 'PY', 'AN', 'DH']


        # Add data validation for SC/ST column
        candidate_worksheet.data_validation('O2:O1048576', {'validate': 'list',
                                                'source': dropdown_values })
        
        candidate_worksheet.data_validation('H2:H1048576', {'validate': 'list',
                                        'source': state_values })
        

        state_cheatsheet = workbook.add_worksheet("States")
        state_cheatsheet.write('A1','Code')
        state_cheatsheet.write('B1','State')

        state_values = {
                'JK': 'Jammu and Kashmir',
                'MH': 'Maharashtra',
                'AP': 'Andhra Pradesh',
                'AR': 'Arunachal Pradesh',
                'AS': 'Assam',
                'BR': 'Bihar',
                'CT': 'Chhattisgarh',
                'GA': 'Goa',
                'GJ': 'Gujarat',
                'HR': 'Haryana',
                'HP': 'Himachal Pradesh',
                'JH': 'Jharkhand',
                'KA': 'Karnataka',
                'KL': 'Kerala',
                'MP': 'Madhya Pradesh',
                'MN': 'Manipur',
                'ML': 'Meghalaya',
                'MZ': 'Mizoram',
                'NL': 'Nagaland',
                'OD': 'Odisha',
                'PB': 'Punjab',
                'RJ': 'Rajasthan',
                'SK': 'Sikkim',
                'TN': 'Tamil Nadu',
                'TG': 'Telangana',
                'TR': 'Tripura',
                'UP': 'Uttar Pradesh',
                'UK': 'Uttarakhand',
                'WB': 'West Bengal',
                'AN': 'Andaman and Nicobar Islands',
                'CH': 'Chandigarh',
                'DH': 'Dadra and Nagar Haveli and Daman and Diu',
                'LD': 'Lakshadweep',
                'DL': 'Delhi',
                'PY': 'Puducherry'
            }
        
        row = 1
        for state, code in state_values.items():
            state_cheatsheet.write(row, 0, state)
            state_cheatsheet.write(row, 1, code)
            row += 1
        

        
        
        
        # candidate_worksheet.protect()
        # candidate_worksheet.write(1, None, None, {'locked': False})
        # candidate_worksheet.set_row(0, None, None)


        workbook.close()

        # Set the buffer position to the beginning
        excel_buffer.seek(0)

        # Generate a response with the Excel file
        response = request.make_response(
            excel_buffer.getvalue(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', 'attachment; filename=candidate_format_file.xlsx')
            ]
        )

        # Clean up the buffer
        excel_buffer.close()

        return response
    

    @http.route('/my/gpbatch/candidates/download_format', type='http', auth='user',website=True)
    def generate_gp_student_format(self ):
        excel_buffer = io.BytesIO()

        # Create a new Excel workbook and add a worksheet
        workbook = xlsxwriter.Workbook(excel_buffer)
        candidate_worksheet = workbook.add_worksheet("Candidates")
        
        
        locked = workbook.add_format({'locked':True})
        unlocked = workbook.add_format({'locked':False})
        candidate_worksheet.set_column('A:XDF', None, unlocked)
        
        candidate_worksheet.set_column('A:A',15,unlocked)
        candidate_worksheet.set_column('B:B',30,unlocked)
        candidate_worksheet.set_column('D:D',30,unlocked)
        candidate_worksheet.set_column('E:E',30,unlocked)
        candidate_worksheet.set_column('F:F',20,unlocked)
        candidate_worksheet.set_column('G:G',15,unlocked)
        candidate_worksheet.set_column('H:H',10,unlocked)
        candidate_worksheet.set_column('I:I',20,unlocked)
        candidate_worksheet.set_column('J:J',20,unlocked)
        candidate_worksheet.set_column('K:K',20,unlocked)
        candidate_worksheet.set_column('L:L',10,unlocked)
        candidate_worksheet.set_column('M:M',10,unlocked)
        candidate_worksheet.set_column('N:N',10,unlocked)
        candidate_worksheet.set_column('O:O',10,unlocked)
        
        candidate_worksheet.protect()
        date_format = workbook.add_format({'num_format': 'dd-mmm-yy','locked':False})
        # number_format = workbook.add_format({'num_format': '0000000000', 'locked': False})
        # zip_format = workbook.add_format({'num_format': '000000', 'locked': False})

        # bold_format = workbook.add_format({'bold': True, 'border': 1,'font_size': 16})
        candidate_worksheet.write_comment('L2', 'In the columns Xth, XIIth, ITI , Please enter only number or grade (a,"a+,b,b+,c,c+,d,d+)')

        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': 'white',
            'bg_color': '#336699',  # Blue color for the background
            'locked':True
        })
        
        header = ['INDOS NO', 'NAME', 'DOB', 'STREET', 'STREET2', 'CITY', 'ZIP', 'STATE', 'PHONE', 'MOBILE', 'EMAIL', 'Xth', 'XIIth', 'ITI', 'SC/ST/OBC']
        for col, value in enumerate(header):
            candidate_worksheet.write(0, col, value, header_format)
            # candidate_worksheet.set_column('J:J', None, number_format)
            # candidate_worksheet.set_column('G:G', None, zip_format)


        # Set date format for DOB column
        candidate_worksheet.set_column('C:C', 20, date_format)

        dropdown_values = ['Yes', 'No']
        # import wdb; wdb.set_trace()


        state_values = ['JK','MH', 'AP', 'AR', 'AS', 'BR', 'CT', 'GA', 'GJ', 'HR', 'HP', 'JH', 'KA', 'KL', 'MP', 'MN', 'ML', 'MZ', 'NL', 'OD', 'PB', 'RJ', 'SK', 'TN', 'TG', 'TR', 'UP', 'UK', 'WB', 'CH', 'LD', 'DL', 'PY', 'AN', 'DH']

        state_values2 = ['Jammu and Kashmir','Maharashtra','Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh','Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka','Kerala', 'Madhya Pradesh', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland','Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana','Tripura','Uttar Pradesh','Uttarakhand','West Bengal','Chandigarh','Lakshadweep', 'Delhi', 'Puducherry','Andaman and Nicobar Islands','Dadra and Nagar Haveli and Daman and Diu']

        # Add data validation for SC/ST column
        candidate_worksheet.data_validation('O2:O1048576', {'validate': 'list',
                                                'source': dropdown_values })
        

        candidate_worksheet.data_validation('H2:H1048576', {'validate': 'list', 'source': state_values})
        


        state_cheatsheet = workbook.add_worksheet("States")
        state_cheatsheet.write('A1','Code')
        state_cheatsheet.write('B1','State')

        state_values = {
                'JK': 'Jammu and Kashmir',
                'MH': 'Maharashtra',
                'AP': 'Andhra Pradesh',
                'AR': 'Arunachal Pradesh',
                'AS': 'Assam',
                'BR': 'Bihar',
                'CT': 'Chhattisgarh',
                'GA': 'Goa',
                'GJ': 'Gujarat',
                'HR': 'Haryana',
                'HP': 'Himachal Pradesh',
                'JH': 'Jharkhand',
                'KA': 'Karnataka',
                'KL': 'Kerala',
                'MP': 'Madhya Pradesh',
                'MN': 'Manipur',
                'ML': 'Meghalaya',
                'MZ': 'Mizoram',
                'NL': 'Nagaland',
                'OD': 'Odisha',
                'PB': 'Punjab',
                'RJ': 'Rajasthan',
                'SK': 'Sikkim',
                'TN': 'Tamil Nadu',
                'TG': 'Telangana',
                'TR': 'Tripura',
                'UP': 'Uttar Pradesh',
                'UK': 'Uttarakhand',
                'WB': 'West Bengal',
                'AN': 'Andaman and Nicobar Islands',
                'CH': 'Chandigarh',
                'DH': 'Dadra and Nagar Haveli and Daman and Diu',
                'LD': 'Lakshadweep',
                'DL': 'Delhi',
                'PY': 'Puducherry'
            }
        
        row = 1
        for state, code in state_values.items():
            state_cheatsheet.write(row, 0, state)
            state_cheatsheet.write(row, 1, code)
            row += 1


        # state_cheatsheet.protect()
        # state_cheatsheet.write(1, None, None, {'locked': False})
        # state_cheatsheet.set_row(0, None, None)
      
        

        
        
        


        workbook.close()

        # Set the buffer position to the beginning
        excel_buffer.seek(0)

        # Generate a response with the Excel file
        response = request.make_response(
            excel_buffer.getvalue(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', 'attachment; filename=candidate_format_file.xlsx')
            ]
        )

        # Clean up the buffer
        excel_buffer.close()

        return response
    
    def remove_after_dot_in_phone_number(self,phone_number):
        if '.' in phone_number:
            return phone_number.split('.')[0]  # Split the phone number by dot and return the first part
        else:
            return phone_number  # If there's 
    

    @http.route(['/my/uploadgpcandidatedata'], type="http", auth="user", website=True)
    def UploadGPCandidateData(self, **kw):
        try:
            user_id = request.env.user.id
            institute_id = request.env["bes.institute"].sudo().search(
                [('user_id', '=', user_id)]).id
            
            batch_id = int(kw.get("batch_id"))
            file_content = kw.get("fileUpload").read()
            filename = kw.get('fileUpload').filename

            # workbook = xlsxwriter.Workbook(BytesIO(file_content))
            workbook = xlrd.open_workbook(file_contents=file_content)
            # worksheet = workbook.sheet_by_index(0)

            # worksheet = workbook.get_worksheet_by_name('Candidates')
            worksheet = workbook.sheet_by_index(0)
            for row_num in range(1, worksheet.nrows):  # Assuming first row contains headers
                row = worksheet.row_values(row_num)
                
                
                dob = date_value
                street1 = row[3]
                street2 = row[4]  
                dist_city = row[5]  # Assuming Dist./City is the fifth column

                pin_code = int(row[6])  # Assuming Pin code is the seventh column
                state_value = row[7]  # Assuming State (short) is the sixth column


                state_values = {
                    'JK': 'Jammu and Kashmir',
                    'MH': 'Maharashtra',
                    'AP': 'Andhra Pradesh',
                    'AR': 'Arunachal Pradesh',
                    'AS': 'Assam',
                    'BR': 'Bihar',
                    'CT': 'Chhattisgarh',
                    'GA': 'Goa',
                    'GJ': 'Gujarat',
                    'HR': 'Haryana',
                    'HP': 'Himachal Pradesh',
                    'JH': 'Jharkhand',
                    'KA': 'Karnataka',
                    'KL': 'Kerala',
                    'MP': 'Madhya Pradesh',
                    'MN': 'Manipur',
                    'ML': 'Meghalaya',
                    'MZ': 'Mizoram',
                    'NL': 'Nagaland',
                    'OD': 'Odisha',
                    'PB': 'Punjab',
                    'RJ': 'Rajasthan',
                    'SK': 'Sikkim',
                    'TN': 'Tamil Nadu',
                    'TG': 'Telangana',
                    'TR': 'Tripura',
                    'UP': 'Uttar Pradesh',
                    'UK': 'Uttarakhand',
                    'WB': 'West Bengal',
                    'AN': 'Andaman and Nicobar Islands',
                    'CH': 'Chandigarh',
                    'DH': 'Dadra and Nagar Haveli and Daman and Diu',
                    'LD': 'Lakshadweep',
                    'DL': 'Delhi',
                    'PY': 'Puducherry'
                }

                # state = False
                # for code, name in state_values.items():
                #     if name.lower() == state_value.lower():
                #         state = code
                #     else:
                #         state = False

                    # state = False
                    # for code, name in state_values.items():
                    #     if name.lower() == state_value.lower():
                    #         state = code
                    #     else:
                    #         state = False

                    # print("Stateeeeee",state)
                            
                data_xth_std_eng = 0
                data_twelfth_std_eng = 0
                data_iti = 0
                state = request.env['res.country.state'].sudo().search(
                    [('country_id.code', '=', 'IN'), ('code', '=', state_value)]).id if state_value else False

                # phone = str((row[8]))
                # print("Phone ",str(row[8] ))
                if row[8]:
                    phone = self.remove_after_dot_in_phone_number(str(row[8]))
                else:
                    phone = ""
                
                if row[9]:
                    mobile = self.remove_after_dot_in_phone_number(str(row[9]))
                else:
                    mobile = ""

                # mobile = str(row[9]) 
                email = row[10] 

                
                xth_std_eng = row[11]  # Assuming %  Xth Std in Eng. is the tenth column
                
                
                if type(xth_std_eng) in [int, float]:
                    data_xth_std_eng = float(xth_std_eng)
                # import wdb; wdb.set_trace()
                elif type(xth_std_eng) == str:
                    
                    if xth_std_eng.lower() == 'a+':
                        data_xth_std_eng = 90
                    if xth_std_eng.lower() == 'a':
                        data_xth_std_eng = 80
                    if xth_std_eng.lower() == 'b+':
                        data_xth_std_eng = 70
                    if xth_std_eng.lower() == 'b':
                        data_xth_std_eng = 60
                    if xth_std_eng.lower() == 'c+':
                        data_xth_std_eng = 50
                    if xth_std_eng.lower() == 'c':
                        data_xth_std_eng = 40
                    if xth_std_eng.lower() == 'd+':
                        data_xth_std_eng = 30
                    if xth_std_eng.lower() == 'd':
                        data_xth_std_eng = 20
                    if xth_std_eng.lower() == 'e':
                        data_xth_std_eng = 19
                
                else:
                    # import wdb; wdb.set_trace()
                    raise ValidationError("Invalid marks/percentage")

                twelfth_std_eng = row[12]  # Assuming %12th Std in Eng. is the eleventh column
                if type(twelfth_std_eng) in [int, float]:
                    data_twelfth_std_eng = float(twelfth_std_eng)
                elif type(twelfth_std_eng) == str:
                    if twelfth_std_eng.lower() == 'a+':
                        data_twelfth_std_eng = 90
                    if twelfth_std_eng.lower() == 'a':
                        data_twelfth_std_eng = 80
                    if twelfth_std_eng.lower() == 'b+':
                        data_twelfth_std_eng = 70
                    if twelfth_std_eng.lower() == 'b':
                        data_twelfth_std_eng = 60
                    if twelfth_std_eng.lower() == 'c+':
                        data_twelfth_std_eng = 50
                    if twelfth_std_eng.lower() == 'c':
                        data_twelfth_std_eng = 40
                    if twelfth_std_eng.lower() == 'd+':
                        data_twelfth_std_eng = 30
                    if twelfth_std_eng.lower() == 'd':
                        data_twelfth_std_eng = 20
                    if twelfth_std_eng.lower() == 'e':
                        data_twelfth_std_eng = 19
                    else:
                        data_twelfth_std_eng = 0
                else:
                    raise ValidationError("Invalid marks/percentage")

                iti = row[13] # Assuming %ITI is the twelfth column
                if type(iti) in [int, float]:
                    data_iti = float(iti)
                elif type(iti) == str:
                    if iti.lower() == 'a+':
                        data_iti = 90
                    if iti.lower() == 'a':
                        data_iti = 80
                    if iti.lower() == 'b+':
                        data_iti = 70
                    if iti.lower() == 'b':
                        data_iti = 60
                    if iti.lower() == 'c+':
                        data_iti = 50
                    if iti.lower() == 'c':
                        data_iti = 40
                    if iti.lower() == 'd+':
                        data_iti = 30
                    if iti.lower() == 'd':
                        data_iti = 20
                    if iti.lower() == 'e':
                        data_iti = 19
                    else:
                        data_iti = 0
                else:
                    raise ValidationError("Invalid marks/percentage")

                candidate_st = True if row[14] == 'Yes' else False  # Assuming To be mentioned if Candidate SC/ST is the thirteenth column

                new_candidate = request.env['gp.candidate'].sudo().create({
                    'name': full_name,
                    'institute_id': institute_id,
                    'indos_no': indos_no,
                    'dob': dob,
                    # 'roll_no': roll_no,
                    # 'candidate_code': code_no,
                    'institute_batch_id': batch_id,
                    'street': street1,
                    'street2': street2,
                    'phone': phone,
                    'mobile': mobile,
                    'email': email,

                    'city': dist_city,
                    'state_id': state,
                    'zip': pin_code,
                    'tenth_percent': data_xth_std_eng,
                    'twelve_percent': data_twelfth_std_eng,
                    'iti_percent': data_iti,
                    'sc_st': candidate_st
                })
        except:
            error_val = "Excel Sheet format incorrect\n"+"There is problem in row no " + str(row_num)
            raise ValidationError(error_val)

        # workbook.close()

        return request.redirect("/my/gpbatch/candidates/"+str(batch_id))


    def convert_to_dd_mmm_yy(self,date_str):
        try:
            # Parse the input date string to datetime object
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')  # Assuming input format is YYYY-MM-DD
        except ValueError:
            try:
                date_obj = datetime.strptime(date_str, '%m/%d/%Y')  # Assuming input format is MM/DD/YYYY
            except ValueError:
                try:
                    date_obj = datetime.strptime(date_str, '%d-%m-%Y')  # Assuming input format is DD-MM-YYYY
                except ValueError:
                    try:
                        date_obj = datetime.strptime(date_str, '%d %b %Y')  # Assuming input format is DD MMM YYYY
                    except ValueError:
                        return "Invalid date format"
        
        # Format the date object to "dd/mmm/yy" format
        formatted_date = date_obj.strftime('%d/%b/%y').replace('/', '')  # Removing the slashes
        
        return formatted_date



    @http.route(['/my/uploadccmccandidatedata'], type="http", auth="user", website=True)
    def UploadCCMCCandidateData(self, **kw):
        user_id = request.env.user.id
        institute_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id
        
        
        batch_id = int(kw.get("batch_ccmc_id"))
        
        # import wdb; wdb.set_trace()
        
        file_content = kw.get("ccmcfileUpload").read()
        filename = kw.get('ccmcfileUpload').filename

        # workbook = xlsxwriter.Workbook(BytesIO(file_content))
        workbook = xlrd.open_workbook(file_contents=file_content)
        # worksheet = workbook.sheet_by_index(0)

        # worksheet = workbook.get_worksheet_by_name('Candidates')
        worksheet = workbook.sheet_by_index(0)

        for row_num in range(1, worksheet.nrows):  # Assuming first row contains headers
            row = worksheet.row_values(row_num)
            
            # import wdb; wdb.set_trace()
            
            try: 
                indos_no = row[0]  
                full_name = row[1] 

                
                date_value = xlrd.xldate_as_datetime(row[2], workbook.datemode)
                # formatted_date = self.convert_to_dd_mmm_yy(date_value)
                # print("Formatted date:", formatted_date)
                date_string = date_value.strftime('%d-%b-%y') 
                dob = date_value

                street1 = row[3]
                street2 = row[4]  
                dist_city = row[5]  # Assuming Dist./City is the fifth column
                pin_code = int(row[6])  # Assuming Pin code is the seventh column
                state_value = row[7]  # Assuming State (short) is the sixth column

                state_values = {
                        'MH': 'Maharashtra',
                        'AP': 'Andhra Pradesh',
                        'AR': 'Arunachal Pradesh',
                        'AS': 'Assam',
                        'BR': 'Bihar',
                        'CT': 'Chhattisgarh',
                        'GA': 'Goa',
                        'GJ': 'Gujarat',
                        'HR': 'Haryana',
                        'HP': 'Himachal Pradesh',
                        'JH': 'Jharkhand',
                        'KA': 'Karnataka',
                        'KL': 'Kerala',
                        'MP': 'Madhya Pradesh',
                        'MN': 'Manipur',
                        'ML': 'Meghalaya',
                        'MZ': 'Mizoram',
                        'NL': 'Nagaland',
                        'OD': 'Odisha',
                        'PB': 'Punjab',
                        'RJ': 'Rajasthan',
                        'SK': 'Sikkim',
                        'TN': 'Tamil Nadu',
                        'TG': 'Telangana',
                        'TR': 'Tripura',
                        'UP': 'Uttar Pradesh',
                        'UK': 'Uttarakhand',
                        'WB': 'West Bengal',
                        'AN': 'Andaman and Nicobar Islands',
                        'CH': 'Chandigarh',
                        'DH': 'Dadra and Nagar Haveli and Daman and Diu',
                        'LD': 'Lakshadweep',
                        'DL': 'Delhi',
                        'PY': 'Puducherry'
                    }
            
            
                    
                data_xth_std_eng = 0
                data_twelfth_std_eng = 0
                data_iti = 0


                if row[8]:
                    phone = self.remove_after_dot_in_phone_number(str(row[8]))
                else:
                    phone = ""
                
                if row[9]:
                    mobile = self.remove_after_dot_in_phone_number(str(row[9]))
                else:
                    mobile = ""
                    
                email = row[10] 

                xth_std_eng = row[11]  # Assuming %  Xth Std in Eng. is the tenth column
                
                if type(xth_std_eng) in [int, float]:
                    data_xth_std_eng = float(xth_std_eng)
                elif type(xth_std_eng) == str:
                    if xth_std_eng.lower() == 'a+':
                        data_xth_std_eng = 90
                    if xth_std_eng.lower() == 'a':
                        data_xth_std_eng = 80
                    if xth_std_eng.lower() == 'b+':
                        data_xth_std_eng = 70
                    if xth_std_eng.lower() == 'b':
                        data_xth_std_eng = 60
                    if xth_std_eng.lower() == 'c+':
                        data_xth_std_eng = 50
                    if xth_std_eng.lower() == 'c':
                        data_xth_std_eng = 40
                    if xth_std_eng.lower() == 'd+':
                        data_xth_std_eng = 30
                    if xth_std_eng.lower() == 'd':
                        data_xth_std_eng = 20
                    if xth_std_eng.lower() == 'e':
                        data_xth_std_eng = 19
                    else:
                        data_xth_std_eng = 0
                else:
                    raise ValidationError("Invalid marks/percentage")

                twelfth_std_eng = row[12]  # Assuming %12th Std in Eng. is the eleventh column
                if type(twelfth_std_eng) in [int, float]:
                    data_twelfth_std_eng = float(twelfth_std_eng)
                elif type(twelfth_std_eng) == str:
                    if twelfth_std_eng.lower() == 'a+':
                        data_twelfth_std_eng = 90
                    if twelfth_std_eng.lower() == 'a':
                        data_twelfth_std_eng = 80
                    if twelfth_std_eng.lower() == 'b+':
                        data_twelfth_std_eng = 70
                    if twelfth_std_eng.lower() == 'b':
                        data_twelfth_std_eng = 60
                    if twelfth_std_eng.lower() == 'c+':
                        data_twelfth_std_eng = 50
                    if twelfth_std_eng.lower() == 'c':
                        data_twelfth_std_eng = 40
                    if twelfth_std_eng.lower() == 'd+':
                        data_twelfth_std_eng = 30
                    if twelfth_std_eng.lower() == 'd':
                        data_twelfth_std_eng = 20
                    if twelfth_std_eng.lower() == 'e':
                        data_twelfth_std_eng = 19
                    else:
                        data_twelfth_std_eng = 0
                else:
                    raise ValidationError("Invalid marks/percentage")

                iti = row[13] # Assuming %ITI is the twelfth column
                if type(iti) in [int, float]:
                    data_iti = float(iti)
                elif type(iti) == str:
                    if iti.lower() == 'a+':
                        data_iti = 90
                    if iti.lower() == 'a':
                        data_iti = 80
                    if iti.lower() == 'b+':
                        data_iti = 70
                    if iti.lower() == 'b':
                        data_iti = 60
                    if iti.lower() == 'c+':
                        data_iti = 50
                    if iti.lower() == 'c':
                        data_iti = 40
                    if iti.lower() == 'd+':
                        data_iti = 30
                    if iti.lower() == 'd':
                        data_iti = 20
                    if iti.lower() == 'e':
                        data_iti = 19
                    else:
                        data_iti = 0
                else:
                    raise ValidationError("Invalid marks/percentage")

                candidate_st = True if row[14] == 'Yes' else False  # Assuming To be mentioned if Candidate SC/ST is the thirteenth column

                new_candidate = request.env['ccmc.candidate'].sudo().create({
                    'name': full_name,
                    'institute_id': institute_id,
                    'indos_no': indos_no,
                    'dob': dob,
                    # 'roll_no': roll_no,
                    # 'candidate_code': code_no,
                    'institute_batch_id': batch_id,
                    'street': street1,
                    'street2': street2,
                    'phone': phone,
                    'mobile': mobile,
                    'email': email,

                    'city': dist_city,
                    'state_id': state,
                    'zip': pin_code,
                    'tenth_percent': data_xth_std_eng,
                    'twelve_percent': data_twelfth_std_eng,
                    'iti_percent': data_iti,
                    'sc_st': candidate_st
                })
                
            except:
                error_val = "Excel Sheet format incorrect \n "+" There is problem in row no " + str(row_num)
                print(row,"errrrrrrrrrrrrrrrrrrrrrrrrrrror")
                raise ValidationError(error_val)
            
        # workbook.close()

        return request.redirect("/my/ccmcbatch/candidates/"+str(batch_id))


    @http.route(['/my/gpcandidates/download_dgs_capacity/<int:batch_id>/<int:institute_id>'], method=["POST", "GET"], type="http", auth="user", website=True)
    def DownloadsGgsCapacityCard(self,batch_id,institute_id,**kw ):
        
        batch = request.env['institute.gp.batches'].sudo().search([('id','=',batch_id)])
        institute = request.env['bes.institute'].sudo().search([('id','=',institute_id)])
        
        # import wdb; wdb.set_trace()
        
        if batch.dgs_document:
            pdf_data = base64.b64decode(batch.dgs_document)  # Decoding file data
            file_name = institute.name + "-" + batch.batch_name + "-" + "DGS Document" + ".pdf"

            headers = [('Content-Type', 'application/octet-stream'), ('Content-Disposition', f'attachment; filename="{file_name}"')]
            return request.make_response(pdf_data, headers)
        else:
            return request.not_found()
   
    @http.route(['/my/ccmccandidates/download_dgs_capacity/<int:batch_id>/<int:institute_id>'], method=["POST", "GET"], type="http", auth="user", website=True)
    def DownloadsGgsCapacity(self,batch_id,institute_id,**kw ):
        
        batch = request.env['institute.ccmc.batches'].sudo().search([('id','=',batch_id)])
        institute = request.env['bes.institute'].sudo().search([('id','=',institute_id)])
        
        # import wdb; wdb.set_trace()
        
        if batch.dgs_document:
            pdf_data = base64.b64decode(batch.dgs_document)  # Decoding file data
            file_name = institute.name + "-" + batch.ccmc_batch_name + "-" + "DGS Document" + ".pdf"

            headers = [('Content-Type', 'application/octet-stream'), ('Content-Disposition', f'attachment; filename="{file_name}"')]
            return request.make_response(pdf_data, headers)
        else:
            return request.not_found()
        
