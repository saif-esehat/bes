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





class InstitutePortal(CustomerPortal):

    @http.route(['/my/gpbatch'], type="http", auth="user", website=True)
    def GPBatchList(self, **kw):
        user_id = request.env.user.id
        institute_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id
        batches = request.env["institute.gp.batches"].sudo().search(
            [('institute_id', '=', institute_id)])

        vals = {"batches": batches, "page_name": "gp_batches"}
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

        vals = {"batches": batches, "page_name": "ccmc_batches"}
        return request.render("bes.institute_ccmc_batches", vals)

    @http.route(['/my/uploadgpcandidatedata'], type="http", auth="user", website=True)
    def UploadGPCandidateData(self, **kw):
        user_id = request.env.user.id
        institute_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id
        
        batch_id = int(kw.get("batch_id"))
        file_content = kw.get("fileUpload").read()
        filename = kw.get('fileUpload').filename
        file_content_str = file_content.decode('utf-8')

        if file_content_str.startswith('\ufeff'):
            file_content_str = file_content_str.lstrip('\ufeff')

        csv_file = StringIO(file_content_str)
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            # import wdb; wdb.set_trace()
            full_name = row['Full Name of candidate as in INDOS']
            indos_no = row['Indos No.']
            dob = datetime.strptime(row['DOB'], '%d/%m/%y').date()
            address = row['Address']
            dist_city = row['Dist./City']
            if row['State (short)']:
                state = request.env['res.country.state'].sudo().search(
                    [('country_id.code', '=', 'IN'), ('code', '=', row['State (short)'])]).id
                # state = row['State (short)']
            pin_code = row['Pin code']
            roll_no = row['Roll No.']
            code_no = row['Code No.']
            xth_std_eng = float(row['%  Xth Std in Eng.'])

            if not row['%12th Std in Eng.']:
                twelfth_std_eng = 0
            else:
                twelfth_std_eng = float(row['%12th Std in Eng.'])

            if not row['%ITI ']:
                iti = 0
            else:
                iti = float(row['%ITI '])

            candidate_st = row['To be mentioned if Candidate SC/ST']

            if candidate_st == 'Yes':
                candidate_st = True
            else:
                candidate_st = False

            new_candidate = request.env['gp.candidate'].sudo().create({
                'name': full_name,
                'institute_id': institute_id,
                'indos_no': indos_no,
                'dob': dob,
                'roll_no':roll_no,
                'candidate_code':code_no,
                # Include other fields here with their corresponding data
                'institute_batch_id':batch_id,
                'street': address,
                'city': dist_city,
                'state_id': state,
                'zip': pin_code,
                'tenth_percent': xth_std_eng,
                'twelve_percent': twelfth_std_eng,
                'iti_percent': iti,
                'sc_st': candidate_st  # Assuming 'Yes' as value for SC/ST
                # Add other fields similarly
            })

            # import wdb; wdb.set_trace()

        return request.redirect("/my/gpbatch/candidates/"+str(batch_id))

    
    


    @http.route(['/my/uploadccmccandidatedata'], type="http", auth="user", website=True)
    def UploadCcmcCandidateData(self, **kw):
        user_id = request.env.user.id
        institute_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id
        
        print("Batch id1",kw.get("ccmc_batch_id"))
        batch_id = int(kw.get("ccmc_batch_id"))
        file_content = kw.get("ccmcfileUpload").read()
        filename = kw.get('ccmcfileUpload').filename
        file_content_str = file_content.decode('utf-8')

        if file_content_str.startswith('\ufeff'):
            file_content_str = file_content_str.lstrip('\ufeff')

        csv_file = StringIO(file_content_str)
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            # import wdb; wdb.set_trace()
            full_name = row['Full Name of candidate as in INDOS']
            indos_no = row['Indos No.']
            dob = datetime.strptime(row['DOB'], '%d/%m/%y').date()
            address = row['Address']
            dist_city = row['Dist./City']
            if row['State (short)']:
                state = request.env['res.country.state'].sudo().search(
                    [('country_id.code', '=', 'IN'), ('code', '=', row['State (short)'])]).id
                # state = row['State (short)']
            pin_code = row['Pin code']
            xth_std_eng = float(row['%  Xth Std in Eng.'])
            roll_no = row['Roll No.']
            code_no = row['Code No.']

            if not row['%12th Std in Eng.']:
                twelfth_std_eng = 0
            else:
                twelfth_std_eng = float(row['%12th Std in Eng.'])

            if not row['%ITI ']:
                iti = 0
            else:
                iti = float(row['%ITI '])

            candidate_st = row['To be mentioned if Candidate SC/ST']

            if candidate_st == 'Yes':
                candidate_st = True
            else:
                candidate_st = False

            new_candidate = request.env['ccmc.candidate'].sudo().create({
                'name': full_name,
                'institute_id': institute_id,
                'indos_no': indos_no,
                'dob': dob,
                # Include other fields here with their corresponding data
                'institute_batch_id':batch_id,
                'street': address,
                'roll_no':roll_no,
                'candidate_code':code_no,
                'city': dist_city,
                'state_id': state,
                'zip': pin_code,
                'tenth_percent': xth_std_eng,
                'twelve_percent': twelfth_std_eng,
                'iti_percent': iti,
                'sc_st': candidate_st  # Assuming 'Yes' as value for SC/ST
                # Add other fields similarly
            })

            # import wdb; wdb.set_trace()

        return request.redirect("/my/ccmcbatch/candidates/"+str(batch_id))

    @http.route(['/my/gpcandidateprofile/<int:candidate_id>'], type="http", auth="user", website=True)
    def GPcandidateProfileView(self, candidate_id, **kw):
        # import wdb; wdb.set_trace()
        candidate = request.env["gp.candidate"].sudo().search(
            [('id', '=', candidate_id)])
        batches = candidate.institute_batch_id
        print(batches.id,"keeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
        vals = {'candidate': candidate, "page_name": "gp_candidate_form",'batches':batches}
        return request.render("bes.gp_candidate_profile_view", vals)

    @http.route(['/my/ccmccandidateprofile/<int:candidate_id>'], type="http", auth="user", website=True)
    def CcmcCandidateProfileView(self, candidate_id, **kw):
        # import wdb; wdb.set_trace()
        candidate = request.env["ccmc.candidate"].sudo().search(
            [('id', '=', candidate_id)])
        vals = {'candidate': candidate, "page_name": "ccmc_candidate_form"}
        return request.render("bes.ccmc_candidate_profile_view", vals)
    
    @http.route(['/getcountrystate'],method=["GET"], type="http", auth="user", website=True)
    def GetCountryState(self):
        states = request.env['res.country.state'].sudo().search(
                    [('country_id.code', '=', 'IN')])
        state_data = [{'id': state.id, 'name': state.name} for state in states]
        return json.dumps(state_data)

    @http.route(['/my/creategpinvoice'],method=["POST"], type="http", auth="user", website=True)
    def CreateGPinvoice(self, **kw):
        print(kw,"kwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
        # import wdb; wdb.set_trace();
        user_id = request.env.user.id
        print(request.env.user)
        print(user_id,"userrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
        
        batch_id = kw.get("invoice_batch_id")
        print(batch_id,"battttch idddddddddddddd")
        
        batch = request.env['institute.gp.batches'].sudo().search([('id','=',batch_id)])
        print(request.env['institute.gp.batches'].sudo().search([('id','=',batch_id)]))
        print(batch,"batcheeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
        
        institute_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)])
        print(request.env["bes.institute"].sudo().search([('user_id', '=', user_id)]))
        print(institute_id,"institttttttttttttttttttttttttttttttttttt")
        
        partner_id = institute_id.user_id.partner_id.id
        print(partner_id,"Partnerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
        
        product_id = batch.course.exam_fees.id
        print(batch.course)
        print(product_id,"prooooooooooooooooooooooooooooooooooooooooooo")
        
        product_price = batch.course.exam_fees.lst_price
        print(product_price,"priceeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
        
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
        print(kw,"keyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy")
        # import wdb; wdb.set_trace();
        user_id = request.env.user.id
        print(request.env.user)
        print(user_id,"userrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
        
        batch_id = kw.get("ccmc_invoice_batch_id")
        print(batch_id,"battttch idddddddddddddd")
        
        batch = request.env['institute.ccmc.batches'].sudo().search([('id','=',batch_id)])
        print(request.env['institute.ccmc.batches'].sudo().search([('id','=',batch_id)]))
        
        print(batch,"batcheeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
        
        institute_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)])
        
        print(request.env["bes.institute"].sudo().search([('user_id', '=', user_id)]))
        print(user_id)
        
        print(institute_id,"institttttttttttttttttttttttttttttttttttt")
        
        ccmc_partner_id = institute_id.user_id.partner_id.id
        
        print(ccmc_partner_id,"Partnerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
        
        product_id_ccmc = batch.ccmc_course.exam_fees.id
        print(batch.ccmc_course)
        print(product_id_ccmc,"prooooooooooooooooooooooooooooooooooooooooooo")
        
        product_price = batch.ccmc_course.exam_fees.lst_price
        print(product_price,"priceeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
        
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
        print(kw,"keeeewwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
        user_id = request.env.user.id
        candidate_id = kw.get("candidate_id")
        
        batch = request.env['institute.gp.batches'].sudo().search([('id','=',kw.get("candidate_batch_id"))])
        print(batch,"batchhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
       
        print(batch.state,"state=======================================================================================================")
        candidate_user_id = request.env['gp.candidate'].sudo().search([('id','=',kw.get('candidate_id'))]).user_id
        if not candidate_user_id:
            request.env['gp.candidate'].sudo().search([('id','=',kw.get('candidate_id'))]).unlink()
            
            return request.redirect("/my/gpbatch/candidates/"+str(batch.id))
        else:
            raise ValidationError("Not Allowed")
        # import wdb; wdb.set_trace();
    
    
    
    @http.route(['/my/creategpcandidateform'],method=["POST"], type="http", auth="user", website=True)
    def CreateGPcandidate(self, **kw):
        print(kw,"kwwwwwwwwwwwwwwwwwwwwwwwww")
        user_id = request.env.user.id
        batch_id = kw.get("batch_id")
        print(batch_id,"batch_idddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd")
        
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
            # print(request.env['gp.candidate'].sudo().create(candidate_data),"DATA_CHECK================================================================================================")
            
            return request.redirect("/my/gpbatch/candidates/"+str(batch_id))
        
    @http.route(['/my/createccmccandidateform'],method=["POST"], type="http", auth="user", website=True)
    def CreateCCMCcandidate(self, **kw):
        user_id = request.env.user.id

        batch_id = kw.get("ccmc_candidate_batch_id")
        
        batch_name = request.env['institute.ccmc.batches'].sudo().search([('id','=',batch_id)]).ccmc_batch_name
        
        institute_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id
        print("")
        # candidate_count = request.env['institute.ccmc.batches'].sudo().search([('id', '=',batch_id)]).candidate_count
        print(request.env['institute.ccmc.batches'].sudo().search([('id', '=',batch_id)]).candidate_count,"countt")
        print(request.env['institute.ccmc.batches'].sudo().search([('id', '=',batch_id)]).ccmc_candidate_count,"ccmc_conttttttttttttttttt")
        
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
            # print(candidate_data,"candidate data=======================================================================================")
            # print(request.env['ccmc.candidate'].sudo().create(candidate_data),"================================================================================")
            request.env['ccmc.candidate'].sudo().create(candidate_data)
            
            
            return request.redirect("/my/ccmcbatch/candidates/"+str(batch_id))
    
    @http.route('/my/confirmccmcuser', type='http', auth="public", website=True)
    def CreateCCMCUser(self, **kw):

        print(kw,"kwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")

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
        print(kw,"kwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
        
        user_id = request.env.user.id
        candidate_id = kw.get("ccmc_candidate_id")

        print(candidate_id)

        batch = request.env['institute.ccmc.batches'].sudo().search([('id','=',kw.get("delete_ccmc_candidate_batch_id"))])
        
        print(batch,"hellowwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
        
        candidate_user_id = request.env['gp.candidate'].sudo().search([('id','=',kw.get('ccmc_candidate_id'))]).user_id
        if not candidate_user_id:
            request.env['ccmc.candidate'].sudo().search([('id','=',kw.get('ccmc_candidate_id'))]).unlink()
            
            return request.redirect("/my/ccmcbatch/candidates/"+str(batch.id))
        else:
            raise ValidationError("Not Allowed")
        # import wdb; wdb.set_trace();
        
    @http.route('/confirmgpuser', type='http', auth="public", website=True)
    def CreateGPUser(self, **kw):

        print(kw,"kwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")

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
            # courses_taught = kw.get("courses_taught")

            
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
        # import wdb; wdb.set_trace()
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
        # self.env["gp.candidate"].sudo().search([('')])
        return request.render("bes.ccmc_candidate_portal_list", vals)


    @http.route(['/my/gpbatch/faculties/<int:batch_id>'], type="http", auth="user", website=True)
    def GPFacultyListView(self, batch_id, **kw):
        # import wdb; wdb.set_trace()

        user_id = request.env.user.id
        gp_batches_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id
        faculties = request.env["institute.faculty"].sudo().search(
            [('gp_batches_id', '=', batch_id)])
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
        institute_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id
        lod = request.env["lod.institute"].sudo().search(
            [('institute_id', '=', institute_id)])
        vals = {'lods': lod, 'page_name': 'lod_list'}
        return request.render("bes.institute_document_list", vals)

    @http.route(['/my/updategpcandidate'], method=["POST", "GET"], type="http", auth="user", website=True)
    def UpdateCandidate(self, **kw):
        # import wdb; wdb.set_trace()
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
                
            indos_no = kw.get('indos_no')
            
            if indos_no:
                candidate.write({'indos_no':indos_no})
            
            # import wdb; wdb.set_trace()
            
            return request.redirect('/my/gpcandidateprofile/'+str(kw.get("canidate_id")))
            
            
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


        
        
        
        

    

