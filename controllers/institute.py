from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request
from odoo import http
from werkzeug.utils import secure_filename
import base64
import csv
import io
from io import StringIO
from datetime import datetime
import xlsxwriter



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

    @http.route(['/my/uploadgpcandidatedata'], type="http", auth="user", website=True)
    def UploadGPCandidateData(self, **kw):
        user_id = request.env.user.id
        institute_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id

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
                # Include other fields here with their corresponding data
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

        return request.redirect("/my/gpcandidate/list")

    @http.route(['/my/gpcandidateprofile/<int:candidate_id>'], type="http", auth="user", website=True)
    def GPcandidateProfileView(self, candidate_id, **kw):
        # import wdb; wdb.set_trace()
        candidate = request.env["gp.candidate"].sudo().search(
            [('id', '=', candidate_id)])
        vals = {'candidate': candidate, "page_name": "gp_candidate_form"}
        return request.render("bes.gp_candidate_profile_view", vals)

    @http.route(['/my/gpcandidateform/view/<int:batch_id>'],method=["POST", "GET"], type="http", auth="user", website=True)
    def GPcandidateFormView(self,batch_id, **kw):
        states = request.env['res.country.state'].sudo().search(
                    [('country_id.code', '=', 'IN')])
        
        user_id = request.env.user.id
        
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
            
        
        
        vals = {"states" : states,"batch_id":batch_id}
        return request.render("bes.gp_candidate_form_view", vals)


    @http.route(['/my/gpfacultiesform/view/<int:batch_id>'],method=["POST", "GET"], type="http", auth="user", website=True)
    def GPFacultiesFormView(self,batch_id, **kw):

        states = request.env['res.country.state'].sudo().search(
                    [('country_id.code', '=', 'IN')])
        
        user_id = request.env.user.id
        
        print("BATCH id",batch_id)

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
                # "courses_taught": courses_taught,

            }
            # import wdb; wdb.set_trace();

            request.env['institute.faculty'].sudo().create(faculty_data)
            
            return request.redirect("/my/gpbatch/faculties/"+str(batch_id))
            
        
        
        vals = {"states" : states,"batch_id":batch_id}
        return request.render("bes.gp_faculty_form_view", vals)

    @http.route(['/my/gpbatch/candidates/<int:batch_id>'], type="http", auth="user", website=True)
    def GPcandidateListView(self, batch_id, **kw):
        # import wdb; wdb.set_trace()

        user_id = request.env.user.id
        institute_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id
        candidates = request.env["gp.candidate"].sudo().search(
            [('institute_id', '=', institute_id), ('institute_batch_id', '=', batch_id)])
        batches = request.env["institute.gp.batches"].sudo().search(
            [('id', '=', batch_id)])
        vals = {'candidates': candidates, 'page_name': 'gp_candidate','batch_id':batch_id,'batches':batches}
        # self.env["gp.candidate"].sudo().search([('')])
        return request.render("bes.gp_candidate_portal_list", vals)

    @http.route(['/my/gpbatch/faculties/<int:batch_id>'], type="http", auth="user", website=True)
    def GPFacultyListView(self, batch_id, **kw):
        # import wdb; wdb.set_trace()

        user_id = request.env.user.id
        gp_batches_id = request.env["bes.institute"].sudo().search(
            [('user_id', '=', user_id)]).id
        faculties = request.env["institute.faculty"].sudo().search(
            [('gp_batches_id', '=', batch_id)])
        vals = {'faculties': faculties, 'page_name': 'gp_faculty','batch_id':batch_id}
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
            indos_no = kw.get('indos_no')
            candidate.write({'candidate_image': base64.b64encode(candidate_image),
                             'candidate_image_name':  candidate_image_name,
                             'indos_no':indos_no})
            
            # import wdb; wdb.set_trace()
            
            return request.redirect('/my/gpcandidateprofile/'+str(kw.get("canidate_id")))
            
            
       
        vals = {}
        return request.render("bes.gp_candidate_profile_view", vals)
        
    
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
        # import wdb; wdb.set_trace()

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
                             "internet_strength": kw.get("internet_strength")
                             })

            vals = {'institutes': institute, 'page_name': 'institute_page'}

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
        
        
    @http.route(['/my/shipvisit/delete'], method=["POST", "GET"], type="http", auth="user", website=True)
    def DeleteShipVisits(self, **kw):
        
        visit_id = kw.get("visit_id")
        request.env['gp.candidate.ship.visits'].sudo().search([('id','=',visit_id)]).unlink()
        
        
        return request.redirect('/my/gpcandidateprofile/'+str(kw.get("candidate_id")))
    
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
    
    
    
    @http.route(['/my/gpcandidate/updatefees'], method=["POST", "GET"], type="http", auth="user", website=True)
    def UpdateFees(self, **kw):
        candidate_id = kw.get('candidate_id')
        fees_paid = kw.get('fees_paid')
        
        
        candidate = request.env["gp.candidate"].sudo().search(
            [('id', '=', int(candidate_id))])
        
        candidate.write({'fees_paid':fees_paid})
        
        return request.redirect('/my/gpcandidateprofile/'+str(kw.get("candidate_id")))
        
    
    @http.route('/my/batches/download_report/<int:batch_id>', type='http', auth='user',website=True)
    def generate_report(self,batch_id ):
        
        excel_buffer = io.BytesIO()

        # Create a new Excel workbook and add a worksheet
        workbook = xlsxwriter.Workbook(excel_buffer)
        
        gp_candidates = request.env["gp.candidate"].sudo().search([('institute_batch_id','=',batch_id)])
        faculties = request.env["institute.faculty"].sudo().search([('gp_batches_id','=',batch_id)])
        

        #Candidate
        
        candidate_worksheet = workbook.add_worksheet("Candidate")
        candidate_worksheet.write('A1', 'Candidate Name')


        row = 1
        
        for gp_candidate in gp_candidates:
            candidate_worksheet.write(row,0,gp_candidate.name)
            row += 1
        
        #Faculty
        
        faculty_worksheet = workbook.add_worksheet("Faculty")
        faculty_worksheet.write('A1', 'Faculty Name')
        row = 1
        for faculty in faculties:
            faculty_worksheet.write(row,0,faculty.faculty_name)
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
        return data