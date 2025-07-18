from odoo.addons.portal.controllers.portal import CustomerPortal, pager
from odoo.http import request
from odoo import http
from werkzeug.utils import secure_filename
import base64
import csv
import io
from io import StringIO
from datetime import datetime
import xlsxwriter
from odoo.exceptions import UserError, ValidationError
import json
from io import BytesIO
import xlrd
import re


class InstitutePortal(CustomerPortal):

    @http.route(["/my/gpbatch"], type="http", auth="user", website=True)
    def GPBatchList(self, **kw):
        user_id = request.env.user.id
        institute_id = (
            request.env["bes.institute"].sudo().search([("user_id", "=", user_id)]).id
        )
        batches = (
            request.env["institute.gp.batches"]
            .sudo()
            .search([("institute_id", "=", institute_id)])
        )

        vals = {
            "batches": batches,
            "institute_id": institute_id,
            "page_name": "gp_batches",
        }
        return request.render("bes.institute_gp_batches", vals)

    @http.route(
        ["/my/gpbatch/updatebatchcapacity"],
        method=["POST"],
        type="http",
        auth="user",
        website=True,
    )
    def UpdateBatchApprovalCapacity(self, **kw):

        batch_id = int(kw.get("batch_id"))
        capacity = int(kw.get("capacity"))

        # file_content = kw.get("approvaldocument").read()
        # filename = kw.get('approvaldocument').filename
        batch = (
            request.env["institute.gp.batches"].sudo().search([("id", "=", batch_id)])
        )
        batch.write(
            {
                "dgs_approved_capacity": capacity,
                "dgs_approval_state": True,
                #  "dgs_document":base64.b64encode(file_content)
            }
        )
        batch.update_dgs_capacity()

        return request.redirect("/my/gpbatch/candidates/" + str(batch_id))

    @http.route(
        ["/my/ccmcbatchbatch/updatebatchcapacity"],
        method=["POST"],
        type="http",
        auth="user",
        website=True,
    )
    def UpdateCCMCBatchApprovalCapacity(self, **kw):

        batch_id = int(kw.get("batch_id"))
        capacity = int(kw.get("capacity"))

        # file_content = kw.get("approvaldocument").read()
        # filename = kw.get('approvaldocument').filename
        batch = (
            request.env["institute.ccmc.batches"].sudo().search([("id", "=", batch_id)])
        )
        batch.write(
            {
                "dgs_approved_capacity": capacity,
                "dgs_approval_state": True,
                #  "dgs_document":base64.b64encode(file_content)
            }
        )
        batch.update_dgs_capacity()

        return request.redirect("/my/ccmcbatch/candidates/" + str(batch_id))

    @http.route(["/my/ccmcbatch"], type="http", auth="user", website=True)
    def CCMCBatchList(self, **kw):
        user_id = request.env.user.id
        institute_id = (
            request.env["bes.institute"].sudo().search([("user_id", "=", user_id)]).id
        )
        batches = (
            request.env["institute.ccmc.batches"]
            .sudo()
            .search([("institute_id", "=", institute_id)])
        )

        vals = {
            "batches": batches,
            "institute_id": institute_id,
            "page_name": "ccmc_batches",
        }
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

    @http.route(
        ["/my/gpcandidateprofile/<int:candidate_id>"],
        type="http",
        auth="user",
        website=True,
    )
    def GPcandidateProfileView(self, candidate_id, **kw):
        # import wdb; wdb.set_trace()
        candidate = (
            request.env["gp.candidate"].sudo().search([("id", "=", candidate_id)])
        )
        states = (
            request.env["res.country.state"]
            .sudo()
            .search([("country_id.code", "=", "IN")])
        )
        batches = candidate.institute_batch_id

        candidate._check_sign()
        candidate._check_image()
        candidate._check_ship_visit_criteria()
        candidate._check_attendance_criteria()
        candidate._check_stcw_certificate()

        vals = {
            "candidate": candidate,
            "page_name": "gp_candidate_form",
            "batches": batches,
            "states": states,
        }
        return request.render("bes.gp_candidate_profile_view", vals)

    @http.route(
        ["/my/ccmccandidateprofile/<int:candidate_id>"],
        type="http",
        auth="user",
        website=True,
    )
    def CcmcCandidateProfileView(self, candidate_id, **kw):
        # import wdb; wdb.set_trace()
        candidate = (
            request.env["ccmc.candidate"].sudo().search([("id", "=", candidate_id)])
        )
        states = (
            request.env["res.country.state"]
            .sudo()
            .search([("country_id.code", "=", "IN")])
        )
        batches = candidate.institute_batch_id

        candidate._check_sign()
        candidate._check_image()
        candidate._check_ship_visit_criteria()
        candidate._check_attendance_criteria()
        candidate._check_stcw_certificate()

        vals = {
            "candidate": candidate,
            "page_name": "ccmc_candidate_form",
            "batches": batches,
            "states": states,
        }
        return request.render("bes.ccmc_candidate_profile_view", vals)

    @http.route(
        ["/getcountrystate"], method=["GET"], type="http", auth="user", website=True
    )
    def GetCountryState(self):
        states = (
            request.env["res.country.state"]
            .sudo()
            .search([("country_id.code", "=", "IN")])
        )
        state_data = [{"id": state.id, "name": state.name} for state in states]
        return json.dumps(state_data)

    @http.route(
        ["/my/downloadtransactionslip/<int:invoice_id>"],
        method=["POST"],
        type="http",
        auth="user",
        website=True,
    )
    def DownloadTransactionSlip(self, invoice_id, **kw):
        invoice = request.env["account.move"].sudo().search([("id", "=", invoice_id)])
        transaction_slip = base64.b64decode(
            invoice.transaction_slip
        )  # Decoding file data
        file_name = invoice.file_name
        headers = [
            ("Content-Type", "application/octet-stream"),
            ("Content-Disposition", f'attachment; filename="{file_name}"'),
        ]
        return request.make_response(transaction_slip, headers)

    @http.route(
        ["/my/updatetransaction"],
        method=["POST"],
        type="http",
        auth="user",
        website=True,
    )
    def UpdateTransaction(self, **kw):

        invoice_id = kw.get("invoice_id")
        transaction_id = kw.get("transaction_id")
        transaction_date = kw.get("transaction_date")
        bank_name = kw.get("bank_name")
        total_amount = int(kw.get("total_amount"))
        file_content = kw.get("transaction_slip").read()
        filename = kw.get("transaction_slip").filename

        invoice = request.env["account.move"].sudo().search([("id", "=", invoice_id)])
        invoice.write(
            {
                "transaction_id": transaction_id,
                "transaction_date": transaction_date,
                "bank_name": bank_name,
                "total_amount": total_amount,
                "transaction_slip": base64.b64encode(file_content),
                "file_name": filename,
            }
        )
        # import wdb; wdb.set_trace();

        return request.redirect("/my/invoices/" + str(invoice_id))

    @http.route(
        ["/getinvoiceqty"], method=["POST"], type="json", auth="user", website=True
    )
    def getqty(self, **kw):
        data = request.jsonrequest
        print(request.jsonrequest)
        user_id = request.env.user.id
        batch_id = data["invoice_batch_id"]
        batch = (
            request.env["institute.gp.batches"].sudo().search([("id", "=", batch_id)])
        )

        product_price = batch.course.exam_fees.lst_price
        qty = (
            request.env["gp.candidate"]
            .sudo()
            .search_count(
                [
                    ("institute_batch_id", "=", batch.id),
                    ("fees_paid", "=", "yes"),
                    ("invoice_generated", "=", False),
                ]
            )
        )
        print("Qty", batch)
        total_price = product_price * qty
        return json.dumps({"candidate_qty": qty, "total_price": total_price})

    @http.route(
        ["/my/creategpinvoice"], method=["POST"], type="http", auth="user", website=True
    )
    def CreateGPinvoice(self, **kw):

        user_id = request.env.user.id
        batch_id = kw.get("invoice_batch_id")
        batch = (
            request.env["institute.gp.batches"].sudo().search([("id", "=", batch_id)])
        )
        institute_id = (
            request.env["bes.institute"].sudo().search([("user_id", "=", user_id)])
        )

        transaction_date = kw.get("transaction_date")
        transaction_id = kw.get("transaction_id")
        bank_name = kw.get("bank_name")
        transaction_amount = kw.get("transaction_amount")
        transaction_slip = request.httprequest.files.get("transaction_slip")

        transaction_slip_file = base64.b64encode(transaction_slip.read())
 
        transaction_slip_filename = transaction_slip.filename

        # import wdb; wdb.set_trace();

        partner_id = institute_id.user_id.partner_id.id
        product_id = batch.course.exam_fees.id
        product_price = batch.course.exam_fees.lst_price
        candidates = (
            request.env["gp.candidate"]
            .sudo()
            .search(
                [
                    ("institute_batch_id", "=", batch.id),
                    ("fees_paid", "=", "yes"),
                    ("invoice_generated", "=", False),
                ]
            )
        )
        qty = (
            request.env["gp.candidate"]
            .sudo()
            .search_count(
                [
                    ("institute_batch_id", "=", batch.id),
                    ("fees_paid", "=", "yes"),
                    ("invoice_generated", "=", False),
                ]
            )
        )

        if qty == 0:
            raise ValidationError(
                "No Candidate Found for Registration. Please Select Fees Paid as Yes in Candidate Profile for the elligible Candidate"
            )
        # qty = batch.candidate_count
        # import wdb; wdb.set_trace();
        line_items = [
            (
                0,
                0,
                {
                    "product_id": product_id,
                    "price_unit": product_price,
                    "quantity": qty,
                },
            )
        ]

        # import wdb; wdb.set_trace();

        invoice_vals = {
            "gp_candidates": candidates.ids,
            "partner_id": partner_id,  # Replace with the partner ID for the customer
            "move_type": "out_invoice",
            "invoice_line_ids": line_items,
            "gp_batch_ok": True,
            "batch": batch.id,
            "l10n_in_gst_treatment": "unregistered",
            # Add other invoice fields as needed
        }

        new_invoice = request.env["account.move"].sudo().create(invoice_vals)
        candidates.write({"invoice_generated": True})
        new_invoice.action_post()

        new_invoice.write(
            {
                "transaction_id": transaction_id,
                "bank_name": bank_name,
                "transaction_slip": transaction_slip_file,
                "file_name": transaction_slip_filename,
                "transaction_date": transaction_date,
                "total_amount": transaction_amount,
            }
        )
        # import wdb; wdb.set_trace();
        batch.write(
            {
                "invoice_created": True,
                "account_move": new_invoice.id,
                "state": "3-pending_invoice",
            }
        )

        return request.redirect("/my/invoices/")

    # CCMC Invoice

    @http.route(
        ["/getccmcinvoiceqty"], method=["POST"], type="json", auth="user", website=True
    )
    def getccmcqty(self, **kw):
        data = request.jsonrequest
        # import wdb; wdb.set_trace()
        print(request.jsonrequest)
        user_id = request.env.user.id
        batch_id = data["ccmc_invoice_batch_id"]
        batch = (
            request.env["institute.ccmc.batches"].sudo().search([("id", "=", batch_id)])
        )

        product_price = batch.ccmc_course.exam_fees.lst_price
        qty = (
            request.env["ccmc.candidate"]
            .sudo()
            .search_count(
                [
                    ("institute_batch_id", "=", batch.id),
                    ("fees_paid", "=", "yes"),
                    ("invoice_generated", "=", False),
                ]
            )
        )
        print("Qty", batch)
        total_price = product_price * qty
        return json.dumps({"candidate_qty": qty, "total_price": total_price})

    @http.route(
        ["/my/createccmcinvoice"],method=["POST"],type="http",auth="user",website=True,
    )
    def CreateCCMCinvoice(self, **kw):
        # import wdb; wdb.set_trace();
        user_id = request.env.user.id
        print(request.env.user)
        batch_id = kw.get("ccmc_invoice_batch_id")
        batch = (
            request.env["institute.ccmc.batches"].sudo().search([("id", "=", batch_id)])
        )

        institute_id = (
            request.env["bes.institute"].sudo().search([("user_id", "=", user_id)])
        )

        transaction_date = kw.get("transaction_date")
        transaction_id = kw.get("transaction_id")
        bank_name = kw.get("bank_name")
        transaction_amount = kw.get("transaction_amount")
        transaction_slip = request.httprequest.files.get("transaction_slip")

        transaction_slip_file = base64.b64encode(transaction_slip.read())
        transaction_slip_filename = transaction_slip.filename

        ccmc_partner_id = institute_id.user_id.partner_id.id
        product_id_ccmc = batch.ccmc_course.exam_fees.id

        product_price = batch.ccmc_course.exam_fees.lst_price

        candidates = (
            request.env["ccmc.candidate"]
            .sudo()
            .search(
                [
                    ("institute_batch_id", "=", batch.id),
                    ("fees_paid", "=", "yes"),
                    ("invoice_generated", "=", False),
                ]
            )
        )
        qty = (
            request.env["ccmc.candidate"]
            .sudo()
            .search_count(
                [
                    ("institute_batch_id", "=", batch.id),
                    ("fees_paid", "=", "yes"),
                    ("invoice_generated", "=", False),
                ]
            )
        )

        if qty == 0:
            raise ValidationError(
                "No Candidate Found for Registration. Please Select Fees Paid as Yes in Candidate Profile for the elligible Candidate"
            )

        # qty = request.env['ccmc.candidate'].sudo().search_count([('institute_batch_id','=',batch.id),('fees_paid','=','yes')])

        # qty = batch.candidate_count
        # import wdb; wdb.set_trace();
        line_items = [
            (
                0,
                0,
                {
                    "product_id": product_id_ccmc,
                    "price_unit": product_price,
                    "quantity": qty,
                },
            )
        ]

        # import wdb; wdb.set_trace();

        invoice_vals = {
            "ccmc_candidates": candidates.ids,
            "partner_id": ccmc_partner_id,  # Replace with the partner ID for the customer
            "move_type": "out_invoice",
            "invoice_line_ids": line_items,
            "ccmc_batch_ok": True,
            "ccmc_batch": batch.id,
            "l10n_in_gst_treatment": "unregistered",
            # Add other invoice fields as needed
        }

        new_invoice = request.env["account.move"].sudo().create(invoice_vals)
        candidates.write({"invoice_generated": True})
        new_invoice.action_post()
        # import wdb; wdb.set_trace();

        new_invoice.write(
            {
                "transaction_id": transaction_id,
                "bank_name": bank_name,
                "transaction_slip": transaction_slip_file,
                "file_name": transaction_slip_filename,
                "transaction_date": transaction_date,
                "total_amount": transaction_amount,
            }
        )
        batch.write(
            {
                "ccmc_invoice_created": True,
                "ccmc_account_move": new_invoice.id,
                "ccmc_state": "3-pending_invoice",
            }
        )

        return request.redirect("/my/invoices/")

    # @http.route(['/my/deletegpcandidate'], type="http", auth="user", website=True)
    # def DeleteGPcandidate(self, **kw):

    @http.route(["/my/deletegpcandidate"], type="http", auth="user", website=True)
    def DeleteGPcandidate(self, **kw):

        user_id = request.env.user.id
        candidate_id = kw.get("candidate_id")

        batch = (
            request.env["institute.gp.batches"]
            .sudo()
            .search([("id", "=", kw.get("candidate_batch_id"))])
        )
        candidate_user_id = (
            request.env["gp.candidate"]
            .sudo()
            .search([("id", "=", kw.get("candidate_id"))])
            .user_id
        )
        if not candidate_user_id:
            request.env["gp.candidate"].sudo().search(
                [("id", "=", kw.get("candidate_id"))]
            ).unlink()

            return request.redirect("/my/gpbatch/candidates/" + str(batch.id))
        else:
            raise ValidationError("Not Allowed")
        # import wdb; wdb.set_trace();

    @http.route(
        ["/my/creategpcandidateform"],
        method=["POST"],
        type="http",
        auth="user",
        website=True,
    )
    def CreateGPcandidate(self, **kw):

        user_id = request.env.user.id
        batch_id = int(kw.get("batch_id"))

        batch_name = (
            request.env["institute.gp.batches"]
            .sudo()
            .search([("id", "=", batch_id)])
            .batch_name
        )

        institute_id = (
            request.env["bes.institute"].sudo().search([("user_id", "=", user_id)]).id
        )

        # import wdb; wdb.set_trace();

        if request.httprequest.method == "POST":
            name = kw.get("name")
            # indos_no = kw.get("indos_no").strip()
            indos_no = kw.get("indos_no","").strip()  # Ensure default empty string if key not present
            
            if re.fullmatch(r'^[0-9]{2}[a-zA-Z]{2}[0-9]{4}$', indos_no):
                pass  # Valid format; proceed
            else:
                raise ValidationError(
                    "INDOS No. must be 8 characters long: 2 digits, 2 letters, 4 digits (e.g., 12AB3456). No spaces allowed."
                )
            
            gender = "male" if kw.get("gender") == "male" else "female"
            date_str = kw.get("dob")
            try:
                dob = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                raise ValidationError(
                    "Invalid Date of Birth format. Please use YYYY-MM-DD."
                )
            street = kw.get("street")
            street2 = kw.get("street2")
            city = kw.get("city")
            zip_code = kw.get("zip")
            state_id = kw.get("state_id")
            phone = kw.get("phone")
            mobile = kw.get("mobile")
            email = kw.get("email")
            eighth_percent = kw.get("eighth_percent")
            tenth_percent = kw.get("tenth_percent")
            twelve_percent = kw.get("twelve_percent")
            iti_percent = kw.get("iti_percent")
            sc_st = kw.get("sc_st")

            if kw.get("minicoy") and sc_st == "st" and not eighth_percent:
                error = f"{name} is not eligible for GP. \n Candidate should be at minimum 8th Passed to be eligible"
                return request.render("bes.not_eligible", {"error": error})

            today = datetime.now().date()
            delta = today - dob
            age = delta.days // 365

            candidate_data = {
                "name": name,
                "indos_no": indos_no,
                "gender": gender,
                "institute_batch_id": batch_id,
                "institute_id": institute_id,
                "dob": dob,
                "age": age,
                "street": street,
                "street2": street2,
                "city": city,
                "zip": zip_code,
                "state_id": state_id,  # Assuming state_id is a Many2one field
                "phone": phone,
                "mobile": mobile,
                "email": email,
                "eighth_percent": eighth_percent,
                "tenth_percent": tenth_percent,
                "twelve_percent": twelve_percent,
                "iti_percent": iti_percent,
                "sc_st": sc_st,
            }

            request.env["gp.candidate"].sudo().create(candidate_data)

            return request.redirect("/my/gpbatch/candidates/" + str(batch_id))

    @http.route(
        ["/my/createccmccandidateform"],
        method=["POST"],
        type="http",
        auth="user",
        website=True,
    )
    def CreateCCMCcandidate(self, **kw):
        user_id = request.env.user.id

        batch_id = int(kw.get("ccmc_candidate_batch_id"))

        batch_name = (
            request.env["institute.ccmc.batches"]
            .sudo()
            .search([("id", "=", batch_id)])
            .ccmc_batch_name
        )

        institute_id = (
            request.env["bes.institute"].sudo().search([("user_id", "=", user_id)]).id
        )

        if request.httprequest.method == "POST":
            name = kw.get("name")
            indos_no = kw.get("indos_no","").strip()  # Ensure default empty string if key not present
            if re.fullmatch(r'^[0-9]{2}[a-zA-Z]{2}[0-9]{4}$', indos_no):
                pass  # Valid format; proceed
            else:
                raise ValidationError(
                    "INDOS No. must be 8 characters long: 2 digits, 2 letters, 4 digits (e.g., 12AB3456). No spaces allowed."
                )
            gender = "male" if kw.get("gender") == "male" else "female"
            date_str = kw.get("dob")
            try:
                dob = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                raise ValidationError(
                    "Invalid Date of Birth format. Please use YYYY-MM-DD."
                )
            street = kw.get("street")
            street2 = kw.get("street2")
            city = kw.get("city")
            zip_code = kw.get("zip")
            state_id = kw.get("state_id")
            phone = kw.get("phone")
            mobile = kw.get("mobile")
            email = kw.get("email")
            eighth_percent = kw.get("eighth_percent")
            tenth_percent = kw.get("tenth_percent")
            twelve_percent = kw.get("twelve_percent")
            iti_percent = kw.get("iti_percent")
            sc_st = kw.get("sc_st")

            if kw.get("minicoy") and sc_st == "st" and not eighth_percent:
                error = f"{name} is not eligible for CCMC. \n Candidate should be at minimum 8th Passed to be eligible"
                return request.render("bes.not_eligible", {"error": error})

            today = datetime.now().date()
            delta = today - dob
            age = delta.days // 365

            candidate_data = {
                "name": name,
                "indos_no": indos_no,
                "gender": gender,
                "institute_batch_id": batch_id,
                "institute_id": institute_id,
                "dob": dob,
                "age": age,
                "street": street,
                "street2": street2,
                "city": city,
                "zip": zip_code,
                "state_id": state_id,  # Assuming state_id is a Many2one field
                "phone": phone,
                "mobile": mobile,
                "email": email,
                "eighth_percent": eighth_percent,
                "tenth_percent": tenth_percent,
                "twelve_percent": twelve_percent,
                "iti_percent": iti_percent,
                "sc_st": sc_st,
            }

            # import wdb; wdb.set_trace();
            request.env["ccmc.candidate"].sudo().create(candidate_data)

            return request.redirect("/my/ccmcbatch/candidates/" + str(batch_id))

    @http.route("/my/confirmccmcuser", type="http", auth="public", website=True)
    def CreateCCMCUser(self, **kw):

        batch = (
            request.env["ccmc.candidate"]
            .sudo()
            .search([("id", "=", kw.get("confirm_ccmc_candidate_batch_id"))])
        )

        batch_id = kw.get("confirm_ccmc_candidate_batch_id")
        candidate = (
            request.env["ccmc.candidate"]
            .sudo()
            .search([("id", "=", kw.get("confirm_ccmc_candidate_id"))])
        )

        if candidate.indos_no:
            if candidate.candidate_image and candidate.candidate_signature:
                # Create user based on candidate details
                user_values = {
                    "name": candidate.name,
                    "login": candidate.indos_no,  # You can set the login as the same as the user name
                    "password": str(candidate.indos_no)
                    + "1",  # Generate a random password
                }
                portal_user = request.env["res.users"].sudo().create(user_values)
                # Assign the created user to the candidate
                candidate.write({"user_id": portal_user.id})
            else:
                raise ValidationError("Candidate Image or Candidate Signature Missing")
        else:
            raise ValidationError("Indos No. cannot be empty")

        return request.redirect("/my/ccmcbatch/candidates/" + str(batch_id))

    @http.route(["/my/deleteccmccandidate"], type="http", auth="user", website=True)
    def DeleteCCMCcandidate(self, **kw):

        user_id = request.env.user.id
        candidate_id = kw.get("ccmc_candidate_id")

        print(candidate_id)

        batch = (
            request.env["institute.ccmc.batches"]
            .sudo()
            .search([("id", "=", kw.get("delete_ccmc_candidate_batch_id"))])
        )

        candidate_user_id = (
            request.env["ccmc.candidate"]
            .sudo()
            .search([("id", "=", kw.get("ccmc_candidate_id"))])
            .user_id
        )
        if not candidate_user_id:
            request.env["ccmc.candidate"].sudo().search(
                [("id", "=", kw.get("ccmc_candidate_id"))]
            ).unlink()

            return request.redirect("/my/ccmcbatch/candidates/" + str(batch.id))
        else:
            raise ValidationError("Not Allowed")
        # import wdb; wdb.set_trace();

    @http.route("/confirmgpuser", type="http", auth="public", website=True)
    def CreateGPUser(self, **kw):

        batch = (
            request.env["gp.candidate"]
            .sudo()
            .search([("id", "=", kw.get("confirm_gp_candidate_batch_id"))])
        )
        batch_id = kw.get("confirm_gp_candidate_batch_id")

        candidate = (
            request.env["gp.candidate"]
            .sudo()
            .search([("id", "=", kw.get("confirm_gp_candidate_id"))])
        )

        if candidate.indos_no:
            if candidate.candidate_image and candidate.candidate_signature:
                # Create user based on candidate details
                user_values = {
                    "name": candidate.name,
                    "login": candidate.indos_no,  # You can set the login as the same as the user name
                    "password": str(candidate.indos_no)
                    + "1",  # Generate a random password
                }
                portal_user = request.env["res.users"].sudo().create(user_values)
                # Assign the created user to the candidate
                candidate.write({"user_id": portal_user.id})
            else:
                raise ValidationError("Candidate Image or Candidate Signature Missing")
        else:
            raise ValidationError("Indos No. cannot be empty")

        return request.redirect("/my/gpbatch/candidates/" + str(batch_id))

    @http.route(
        ["/my/gpcandidateform/view/<int:batch_id>"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def GPcandidateFormView(self, batch_id, **kw):

        # import wdb; wdb.set_trace();

        states = (
            request.env["res.country.state"]
            .sudo()
            .search([("country_id.code", "=", "IN")])
        )

        user_id = request.env.user.id

        batch_name = (
            request.env["institute.gp.batches"]
            .sudo()
            .search([("id", "=", batch_id)])
            .batch_name
        )

        institute_id = (
            request.env["bes.institute"].sudo().search([("user_id", "=", user_id)]).id
        )

        if request.httprequest.method == "POST":
            name = kw.get("name")
            dob = kw.get("dob")
            indos_no = kw.get("indos_no").strip()
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
                "institute_batch_id": batch_id,
                "institute_id": institute_id,
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

            request.env["gp.candidate"].sudo().create(candidate_data)

            return request.redirect("/my/gpbatch/candidates/" + str(batch_id))

        vals = {
            "states": states,
            "batch_id": batch_id,
            "batch_name": batch_name,
            "page_name": "gp_candidate_form",
        }
        return request.render("bes.gp_candidate_form_view", vals)

    @http.route(
        ["/my/ccmccandidateform/view/<int:batch_id>"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def CcmcCandidateFormView(self, batch_id, **kw):

        states = (
            request.env["res.country.state"]
            .sudo()
            .search([("country_id.code", "=", "IN")])
        )

        user_id = request.env.user.id

        batch_name = (
            request.env["institute.ccmc.batches"]
            .sudo()
            .search([("id", "=", batch_id)])
            .ccmc_batch_name
        )

        institute_id = (
            request.env["bes.institute"].sudo().search([("user_id", "=", user_id)]).id
        )

        if request.httprequest.method == "POST":
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
                "institute_batch_id": batch_id,
                "institute_id": institute_id,
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

            request.env["ccmc.candidate"].sudo().create(candidate_data)

            return request.redirect("/my/ccmcbatch/candidates/" + str(batch_id))

        vals = {
            "states": states,
            "batch_id": batch_id,
            "batch_name": batch_name,
            "page_name": "ccmc_candidate_form",
        }
        return request.render("bes.ccmc_candidate_form_view", vals)

    @http.route(
        ["/my/gpfacultiesform/view/<int:batch_id>"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def GPFacultiesFormView(self, batch_id, **kw):
        # import wdb; wdb.set_trace();
        states = (
            request.env["res.country.state"]
            .sudo()
            .search([("country_id.code", "=", "IN")])
        )

        user_id = request.env.user.id

        batch_name = (
            request.env["institute.gp.batches"]
            .sudo()
            .search([("id", "=", batch_id)])
            .batch_name
        )

        # print("BATCH id2",batch_id)

        if request.httprequest.method == "POST":
            faculty_name = kw.get("faculty_name")
            # faculty_photo = kw.get('faculty_photo')
            dob = kw.get("dob")
            file_content = kw.get("faculty_photo").read()
            filename = kw.get("faculty_photo").filename
            designation = kw.get("designation")
            qualification = kw.get("qualification")
            contract_terms = kw.get("contract_terms")
            course_name = kw.get("course_name")
            courses_id = kw.get("courses_taught")
            courses_taught = (
                request.env["course.master"]
                .sudo()
                .search([("id", "=", int(courses_id))])
            )
            # import wdb; wdb.set_trace();

            faculty_data = {
                "faculty_name": faculty_name,
                "gp_batches_id": batch_id,
                "faculty_photo": base64.b64encode(file_content),
                "faculty_photo_name": filename,
                "dob": dob,
                "designation": designation,
                "qualification": qualification,
                "contract_terms": contract_terms,
                "course_name": course_name,
                "courses_taught": courses_taught,
            }
            # import wdb; wdb.set_trace();

            request.env["institute.faculty"].sudo().create(faculty_data)

            return request.redirect("/my/gpbatch/faculties/" + str(batch_id))

        vals = {
            "states": states,
            "batch_id": batch_id,
            "page_name": "gp_faculty_form",
            "batch_name": batch_name,
        }
        return request.render("bes.gp_faculty_form_view", vals)

    @http.route(
        ["/my/ccmcfacultiesform/view/<int:batch_id>"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def CcmcFacultiesFormView(self, batch_id, **kw):

        states = (
            request.env["res.country.state"]
            .sudo()
            .search([("country_id.code", "=", "IN")])
        )

        user_id = request.env.user.id
        batch_name = (
            request.env["institute.ccmc.batches"]
            .sudo()
            .search([("id", "=", batch_id)])
            .ccmc_batch_name
        )

        print("BATCH id3", batch_id)

        if request.httprequest.method == "POST":
            faculty_name = kw.get("faculty_name")
            # faculty_photo = kw.get('faculty_photo')
            dob = kw.get("dob")
            file_content = kw.get("faculty_photo").read()
            filename = kw.get("faculty_photo").filename
            designation = kw.get("designation")
            qualification = kw.get("qualification")
            contract_terms = kw.get("contract_terms")
            course_name = kw.get("course_name")
            # courses_taught = kw.get("courses_taught")
            courses_id = kw.get("courses_taught")
            courses_taught = (
                request.env["course.master"]
                .sudo()
                .search([("id", "=", int(courses_id))])
            )

            faculty_data = {
                "faculty_name": faculty_name,
                "ccmc_batches_id": batch_id,
                "faculty_photo": base64.b64encode(file_content),
                "faculty_photo_name": filename,
                "dob": dob,
                "designation": designation,
                "qualification": qualification,
                "contract_terms": contract_terms,
                "course_name": course_name,
                "courses_taught": courses_taught,
            }
            # import wdb; wdb.set_trace();

            request.env["institute.faculty"].sudo().create(faculty_data)

            return request.redirect("/my/ccmcbatch/faculties/" + str(batch_id))

        vals = {
            "states": states,
            "batch_id": batch_id,
            "page_name": "ccmc_faculty_form",
            "batch_name": batch_name,
        }
        return request.render("bes.ccmc_faculty_form_view", vals)

    @http.route(
        [
            "/my/gpbatch/candidates/<int:batch_id>",
            "/my/gpbatch/candidates/<int:batch_id>/page/<int:page>",
        ],
        type="http",
        auth="user",
        website=True,
    )
    def GPcandidateListView(
        self,
        batch_id,
        page=1,
        sortby="id",
        search="",
        search_in="All",
        **kw,
    ):

        # sorted_list = {
        #     'id':{'label':'ID Desc', 'order':'id desc'},
        # }
        # search_domain_count = search_list[search_in]["domain"][0]
        # default_order_by = sorted_list[sortby]["order"]

        user_id = request.env.user.id
        institute_id = (
            request.env["bes.institute"].sudo().search([("user_id", "=", user_id)]).id
        )

        search_list = {
            "All": {
                "label": "All",
                "input": "All",
                "domain": [
                    ("institute_id", "=", institute_id),
                    ("institute_batch_id", "=", batch_id),
                ],
            },
            "Name": {
                "label": "Candidate Name",
                "input": "Name",
                "domain": [
                    ("institute_id", "=", institute_id),
                    ("institute_batch_id", "=", batch_id),
                    ("name", "ilike", search),
                ],
            },
            "Indos_No": {
                "label": "Indos No",
                "input": "Indos_No",
                "domain": [
                    ("institute_id", "=", institute_id),
                    ("institute_batch_id", "=", batch_id),
                    ("indos_no", "ilike", search),
                ],
            },
            "Candidate_Code_No": {
                "label": "Candidate Code No",
                "input": "Candidate_Code_No",
                "domain": [
                    ("institute_id", "=", institute_id),
                    ("institute_batch_id", "=", batch_id),
                    ("candidate_code", "ilike", search),
                ],
            },
            "Roll_No": {
                "label": "Roll No.",
                "input": "Roll_No",
                "domain": [
                    ("institute_id", "=", institute_id),
                    ("institute_batch_id", "=", batch_id),
                    ("roll_no", "ilike", search),
                ],
            },
        }

        # import wdb; wdb.set_trace()

        search_domain = search_list[search_in]["domain"]

        candidates_count = (
            request.env["gp.candidate"].sudo().search_count(search_domain)
        )

        page_detail = pager(
            url="/my/gpbatch/candidates/" + str(batch_id),
            total=candidates_count,
            url_args={"search_in": search_in, "search": search},
            page=page,
            step=40,
        )
        candidates = (
            request.env["gp.candidate"]
            .sudo()
            .search(search_domain, limit=40, offset=page_detail["offset"])
        )
        batches = (
            request.env["institute.gp.batches"].sudo().search([("id", "=", batch_id)])
        )
        batches._compute_all_candidates_have_indos()

        states = (
            request.env["res.country.state"]
            .sudo()
            .search([("country_id.code", "=", "IN")])
        )

        vals = {
            "candidates": candidates,
            "page_name": "gp_candidate",
            "batch_id": batch_id,
            "batches": batches,
            "states": states,
            "pager": page_detail,
            "search_in": search_in,
            "search": search,
            "searchbar_inputs": search_list,
        }
        # import wdb; wdb.set_trace()
        # self.env["gp.candidate"].sudo().search([('')])
        return request.render("bes.gp_candidate_portal_list", vals)

    @http.route(
        [
            "/my/ccmcbatch/candidates/<int:batch_id>",
            "/my/ccmcbatch/candidates/<int:batch_id>/page/<int:page>",
        ],
        type="http",
        auth="user",
        website=True,
    )
    def CcmcCandidateListView(self, batch_id, page=1, search="", search_in="All", **kw):
        # import wdb; wdb.set_trace()

        user_id = request.env.user.id
        institute_id = (
            request.env["bes.institute"].sudo().search([("user_id", "=", user_id)]).id
        )

        search_list = {
            "All": {
                "label": "All",
                "input": "All",
                "domain": [
                    ("institute_id", "=", institute_id),
                    ("institute_batch_id", "=", batch_id),
                ],
            },
            "Name": {
                "label": "Candidate Name",
                "input": "Name",
                "domain": [
                    ("institute_id", "=", institute_id),
                    ("institute_batch_id", "=", batch_id),
                    ("name", "ilike", search),
                ],
            },
            "Indos_No": {
                "label": "Indos No",
                "input": "Indos_No",
                "domain": [
                    ("institute_id", "=", institute_id),
                    ("institute_batch_id", "=", batch_id),
                    ("indos_no", "ilike", search),
                ],
            },
            "Candidate_Code_No": {
                "label": "Candidate Code No",
                "input": "Candidate_Code_No",
                "domain": [
                    ("institute_id", "=", institute_id),
                    ("institute_batch_id", "=", batch_id),
                    ("candidate_code", "ilike", search),
                ],
            },
            "Roll_No": {
                "label": "Roll No.",
                "input": "Roll_No",
                "domain": [
                    ("institute_id", "=", institute_id),
                    ("institute_batch_id", "=", batch_id),
                    ("roll_no", "ilike", search),
                ],
            },
        }

        search_domain = search_list[search_in]["domain"]

        candidates_count = (
            request.env["ccmc.candidate"].sudo().search_count(search_domain)
        )
        page_detail = pager(
            url="/my/ccmcbatch/candidates/" + str(batch_id),
            total=candidates_count,
            url_args={"search_in": search_in, "search": search},
            page=page,
            step=40,
        )

        candidates = (
            request.env["ccmc.candidate"]
            .sudo()
            .search(search_domain, limit=40, offset=page_detail["offset"])
        )
        batches = (
            request.env["institute.ccmc.batches"].sudo().search([("id", "=", batch_id)])
        )

        states = (
            request.env["res.country.state"]
            .sudo()
            .search([("country_id.code", "=", "IN")])
        )
        vals = {
            "candidates": candidates,
            "page_name": "ccmc_candidate",
            "batch_id": batch_id,
            "batches": batches,
            "states": states,
            "pager": page_detail,
            "search_in": search_in,
            "search": search,
            "searchbar_inputs": search_list,
        }
        print("Batch id4", batch_id)
        batches._compute_all_candidates_have_indos()
        # import wdb; wdb.set_trace()
        return request.render("bes.ccmc_candidate_portal_list", vals)

    @http.route(
        ["/my/gpbatch/faculties/<int:batch_id>"], type="http", auth="user", website=True
    )
    def GPFacultyListView(self, batch_id, **kw):
        user_id = request.env.user.id

        gp_batches_id = (
            request.env["bes.institute"].sudo().search([("user_id", "=", user_id)]).id
        )

        faculties = (
            request.env["institute.faculty"]
            .sudo()
            .search([("gp_batches_id", "=", batch_id)])
        )
        # import wdb; wdb.set_trace()

        vals = {
            "faculties": faculties,
            "page_name": "gp_faculty_list",
            "batch_id": batch_id,
        }
        # self.env["gp.candidate"].sudo().search([('')])
        return request.render("bes.gp_faculty_portal_list", vals)

    @http.route(
        ["/my/ccmcbatch/faculties/<int:batch_id>"],
        type="http",
        auth="user",
        website=True,
    )
    def CcmcFacultyListView(self, batch_id, **kw):
        # import wdb; wdb.set_trace()

        user_id = request.env.user.id
        ccmc_batches_id = (
            request.env["bes.institute"].sudo().search([("user_id", "=", user_id)]).id
        )
        faculties = (
            request.env["institute.faculty"]
            .sudo()
            .search([("ccmc_batches_id", "=", batch_id)])
        )
        vals = {
            "faculties": faculties,
            "page_name": "ccmc_faculty_list",
            "batch_id": batch_id,
        }
        # self.env["gp.candidate"].sudo().search([('')])
        return request.render("bes.ccmc_faculty_portal_list", vals)

    @http.route(
        ["/my/gpbatch/faculties/profile/<int:batch_id>/<int:faculties_id>"],
        type="http",
        auth="user",
        website=True,
    )
    def GPFacultyProfileView(self, batch_id, faculties_id, **kw):
        # import  wdb; wdb.set_trace()
        user_id = request.env.user.id

        institute = (
            request.env["bes.institute"].sudo().search([("user_id", "=", user_id)])
        )

        batches = (
            request.env["institute.gp.batches"].sudo().search([("id", "=", batch_id)])
        )

        # import wdb; wdb.set_trace()

        faculties = (
            request.env["institute.faculty"].sudo().search([("id", "=", faculties_id)])
        )

        vals = {
            "faculties": faculties,
            "page_name": "gp_faculty_list",
            "batch_id": batch_id,
            "batches": batches,
        }

        return request.render("bes.gp_faculty_profile_view", vals)

    @http.route(
        ["/my/ccmcbatch/faculties/profile/<int:batch_id>/<int:faculties_id>"],
        type="http",
        auth="user",
        website=True,
    )
    def CCMCFacultyProfileView(self, batch_id, faculties_id, **kw):
        user_id = request.env.user.id

        institute = (
            request.env["bes.institute"].sudo().search([("user_id", "=", user_id)])
        )

        batches = (
            request.env["institute.ccmc.batches"].sudo().search([("id", "=", batch_id)])
        )

        # import wdb; wdb.set_trace()

        faculties = (
            request.env["institute.faculty"].sudo().search([("id", "=", faculties_id)])
        )

        vals = {
            "faculties": faculties,
            "page_name": "ccmc_faculty_list",
            "batch_id": batch_id,
            "batches": batches,
        }

        return request.render("bes.ccmc_faculty_profile_view", vals)

    @http.route(["/my/institute_document/list"], type="http", auth="user", website=True)
    def InstituteDocumentList(self, **kw):

        user_id = request.env.user.id

        # institute_id = request.env["bes.institute"].sudo().search(
        #     [('user_id', '=', user_id)]).id

        institute = (
            request.env["bes.institute"].sudo().search([("user_id", "=", user_id)])
        )

        gp_batches = (
            request.env["institute.gp.batches"]
            .sudo()
            .search([("institute_id", "=", institute.id)])
        )
        ccmc_batches = (
            request.env["institute.ccmc.batches"]
            .sudo()
            .search([("institute_id", "=", institute.id)])
        )

        lod = (
            request.env["lod.institute"]
            .sudo()
            .search([("institute_id", "=", institute.id)])
        )

        # import wdb; wdb.set_trace()

        vals = {"lods": lod, "page_name": "lod_list"}

        return request.render("bes.institute_document_list", vals)

    @http.route(
        ["/my/updategpcandidate"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def UpdateCandidate(self, **kw):
        # import wdb; wdb.set_trace()
        candidate = (
            request.env["gp.candidate"]
            .sudo()
            .search([("id", "=", int(kw.get("canidate_id")))])
        )

        states = (
            request.env["res.country.state"]
            .sudo()
            .search([("country_id.code", "=", "IN")])
        )

        if request.httprequest.method == "POST":
            # import wdb; wdb.set_trace()
            candidate_image = kw.get("candidate_photo").read()
            candidate_image_name = kw.get("candidate_photo").filename

            if candidate_image and candidate_image_name:
                candidate.write(
                    {
                        "candidate_image": base64.b64encode(candidate_image),
                        "candidate_image_name": candidate_image_name,
                    }
                )

            signature_photo = kw.get("signature_photo").read()
            signature_photo_name = kw.get("signature_photo").filename

            # print(signature_photo)
            # print(signature_photo_name)
            # # import wdb; wdb.set_trace()
            # print(signature_photo and signature_photo_name)
            if signature_photo and signature_photo_name:
                candidate.write(
                    {
                        "candidate_signature": base64.b64encode(signature_photo),
                        "candidate_signature_name": signature_photo_name,
                    }
                )
            state = (
                request.env["res.country.state"]
                .sudo()
                .search(
                    [("country_id.code", "=", "IN"), ("id", "=", kw.get("state_id"))]
                )
                .id
                if kw.get("state_id")
                else False
            )
            candidate_details = {
                "indos_no": kw.get("indos_no"),
                "name": kw.get("full_name"),
                "gender": kw.get("gender"),
                "dob": kw.get("dob"),
                "email": kw.get("e_mail"),
                "phone": kw.get("phone"),
                "mobile": kw.get("mobile"),
                "street": kw.get("street"),
                "street2": kw.get("street2"),
                "city": kw.get("city"),
                "zip": kw.get("zip"),
                "state_id": state,
                "sc_st": kw.get("sc_st"),
            }

            for key, value in candidate_details.items():
                if value:
                    candidate.write({key: value})

            # import wdb; wdb.set_trace()

            return request.redirect(
                "/my/gpcandidateprofile/" + str(kw.get("canidate_id"))
            )

        # import wdb; wdb.set_trace()
        # batches = request.env["institute.gp.batches"].sudo().search([('id', '=', batch_id)])
        vals = {}
        return request.render("bes.gp_candidate_profile_view", vals)

    @http.route(
        ["/my/updateccmccandidate"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def UpdateCcmcCandidate(self, **kw):
        # import wdb; wdb.set_trace()
        candidate = (
            request.env["ccmc.candidate"]
            .sudo()
            .search([("id", "=", int(kw.get("canidate_id")))])
        )

        states = (
            request.env["res.country.state"]
            .sudo()
            .search([("country_id.code", "=", "IN")])
        )

        if request.httprequest.method == "POST":
            # import wdb; wdb.set_trace()
            candidate_image = kw.get("candidate_photo").read()
            candidate_image_name = kw.get("candidate_photo").filename

            if candidate_image and candidate_image_name:
                candidate.write(
                    {
                        "candidate_image": base64.b64encode(candidate_image),
                        "candidate_image_name": candidate_image_name,
                    }
                )

            signature_photo = kw.get("signature_photo").read()
            signature_photo_name = kw.get("signature_photo").filename

            # print(signature_photo)
            # print(signature_photo_name)
            # # import wdb; wdb.set_trace()
            # print(signature_photo and signature_photo_name)
            if signature_photo and signature_photo_name:
                candidate.write(
                    {
                        "candidate_signature": base64.b64encode(signature_photo),
                        "candidate_signature_name": signature_photo_name,
                    }
                )

            state = (
                request.env["res.country.state"]
                .sudo()
                .search(
                    [("country_id.code", "=", "IN"), ("id", "=", kw.get("state_id"))]
                )
                .id
                if kw.get("state_id")
                else False
            )

            candidate_details = {
                "indos_no": kw.get("indos_no"),
                "name": kw.get("full_name"),
                "gender": kw.get("gender"),
                "dob": kw.get("dob"),
                "email": kw.get("e_mail"),
                "phone": kw.get("phone"),
                "mobile": kw.get("mobile"),
                "street": kw.get("street"),
                "street2": kw.get("street2"),
                "city": kw.get("city"),
                "zip": kw.get("zip"),
                "state_id": state,
                "sc_st": kw.get("sc_st"),
            }

            for key, value in candidate_details.items():
                if value:
                    candidate.write({key: value})

            # import wdb; wdb.set_trace()

            return request.redirect(
                "/my/ccmccandidateprofile/" + str(kw.get("canidate_id"))
            )

        vals = {}
        return request.render("bes.ccmc_candidate_profile_view", vals)

    @http.route(
        ['/my/institute_document/download/<model("lod.institute"):document_id>'],
        type="http",
        auth="user",
        website=True,
    )
    def InstituteDocumentDownload(self, document_id, **kw):
        # import wdb; wdb.set_trace()
        document = request.env["lod.institute"].sudo().browse(document_id.id)

        if (
            document and document.document_file
        ):  # Ensure the document and file data exist
            file_content = base64.b64decode(
                document.document_file
            )  # Decoding file data
            file_name = document.documents_name  # File name
            file_name = secure_filename(file_name)  # Secure file name

            # Return the file as a download attachment
            headers = [
                ("Content-Type", "application/octet-stream"),
                ("Content-Disposition", f'attachment; filename="{file_name}"'),
            ]
            return request.make_response(file_content, headers)
        else:
            return "File not found or empty."

    @http.route(
        ["/my/institute_document"],
        type="http",
        method=["POST", "GET"],
        auth="user",
        website=True,
    )
    def InstituteDocumentView(self, **kw):

        user_id = request.env.user.id
        institute_id = (
            request.env["bes.institute"].sudo().search([("user_id", "=", user_id)]).id
        )
        # import wdb; wdb.set_trace()

        if request.httprequest.method == "POST":
            # import wdb; wdb.set_trace()
            file_content = kw.get("fileUpload").read()
            filename = kw.get("fileUpload").filename
            # attachment = uploaded_file.read()

            data = (
                request.env["lod.institute"]
                .sudo()
                .create(
                    {
                        "institute_id": institute_id,
                        "document_name": kw.get("documentName"),
                        "upload_date": kw.get("uploadDate"),
                        "document_file": base64.b64encode(file_content),
                        "documents_name": filename,
                    }
                )
            )
            # 'document_file': uploaded_file

            return request.redirect("/my/institute_document/list")
        else:
            vals = {}
            return request.render("bes.institute_documents_form", vals)

    @http.route(["/my/ccmccandidate/list"], type="http", auth="user", website=True)
    def CCMCcandidateListView(self, **kw):
        # import wdb; wdb.set_trace()

        user_id = request.env.user.id
        institute_id = (
            request.env["bes.institute"].sudo().search([("user_id", "=", user_id)]).id
        )
        candidates = (
            request.env["ccmc.candidate"]
            .sudo()
            .search([("institute_id", "=", institute_id)])
        )
        vals = {"candidates": candidates, "page_name": "ccmc_candidate"}
        # self.env["gp.candidate"].sudo().search([('')])
        return request.render("bes.ccmc_candidate_portal_list", vals)

    @http.route(
        ["/my/editinstitute"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def editInstituteView(self, **kw):

        user_id = request.env.user.id
        institute = (
            request.env["bes.institute"].sudo().search([("user_id", "=", user_id)])
        )

        if request.httprequest.method == "POST":

            institute.write(
                {
                    "email": kw.get("email"),
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
                    "name_of_second_authorized_person": kw.get(
                        "second_authorized_person"
                    ),
                    "computer_lab_pc_count": kw.get("computer_lab_pc_count"),
                    "internet_strength": kw.get("internet_strength"),
                    "ip_address": kw.get("ip_address"),
                }
            )

            vals = {"institutes": institute, "page_name": "institute_page"}
            institute.user_id.write(
                {"email": kw.get("email"), "login": kw.get("email")}
            )

            return request.render("bes.institute_detail_form", vals)

        else:

            vals = {"institutes": institute, "page_name": "institute_page"}
            return request.render("bes.institute_detail_form", vals)

    @http.route(
        ["/my/addshipvisit"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def AddShipVisits(self, **kw):

        # Extracting data from the HTML form
        candidate_id = int(kw.get("candidate_id"))
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
            "candidate_id": candidate_id,
            "name_of_ships": name_of_ships,
            "imo_no": imo_no,
            "name_of_ports_visited": name_of_ports_visited,
            "date_of_visits": date_of_visits,
            "time_spent_on_ship": time_spent_on_ship,
            "bridge": bridge,
            "eng_room": eng_room,
            "cargo_area": cargo_area,
        }

        request.env["gp.candidate.ship.visits"].sudo().create(candidate_data)

        # request.env.cr.commit()
        candidate = (
            request.env["gp.candidate"].sudo().search([("id", "=", candidate_id)])
        )
        candidate._check_sign()
        candidate._check_image()
        candidate._check_ship_visit_criteria()
        candidate._check_attendance_criteria()
        candidate._check_stcw_certificate()
        # import wdb; wdb.set_trace()

        # Create a record in the 'gp.candidate' model

        return request.redirect("/my/gpcandidateprofile/" + str(candidate_id))

    @http.route(
        ["/my/addccmcshipvisit"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def AddCcmcShipVisits(self, **kw):

        # Extracting data from the HTML form
        candidate_id = int(kw.get("candidate_id"))
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
            "candidate_id": candidate_id,
            "name_of_ships": name_of_ships,
            "imo_no": imo_no,
            "name_of_ports_visited": name_of_ports_visited,
            "date_of_visits": date_of_visits,
            "time_spent_on_ship": time_spent_on_ship,
            "bridge": bridge,
            "eng_room": eng_room,
            "cargo_area": cargo_area,
        }

        request.env["ccmc.candidate.ship.visits"].sudo().create(candidate_data)
        # import wdb; wdb.set_trace()
        candidate = (
            request.env["ccmc.candidate"].sudo().search([("id", "=", candidate_id)])
        )
        candidate._check_ship_visit_criteria()

        return request.redirect("/my/ccmccandidateprofile/" + str(candidate_id))

    @http.route(
        ["/my/shipvisit/delete"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def DeleteShipVisits(self, **kw):

        visit_id = kw.get("visit_id")
        request.env["gp.candidate.ship.visits"].sudo().search(
            [("id", "=", visit_id)]
        ).unlink()

        request.env.cr.commit()
        candidate = (
            request.env["gp.candidate"]
            .sudo()
            .search([("id", "=", kw.get("candidate_id"))])
        )
        candidate._check_sign()
        candidate._check_image()
        candidate._check_ship_visit_criteria()
        candidate._check_attendance_criteria()
        candidate._check_stcw_certificate()

        return request.redirect("/my/gpcandidateprofile/" + str(kw.get("candidate_id")))

    @http.route(
        ["/my/stcw/delete"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def DeleteStcw(self, **kw):
        # import wdb; wdb.set_trace();
        stcw_id = kw.get("stcw_id")
        request.env["gp.candidate.stcw.certificate"].sudo().search(
            [("id", "=", stcw_id)]
        ).unlink()

        request.env.cr.commit()
        candidate = (
            request.env["gp.candidate"]
            .sudo()
            .search([("id", "=", kw.get("candidate_id"))])
        )
        candidate._check_sign()
        candidate._check_image()
        candidate._check_ship_visit_criteria()
        candidate._check_attendance_criteria()
        candidate._check_stcw_certificate()

        return request.redirect("/my/gpcandidateprofile/" + str(kw.get("candidate_id")))

    @http.route(
        ["/my/ccmcstcw/delete"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def DeleteccmcStcw(self, **kw):
        print(kw)
        # import wdb; wdb.set_trace();
        stcw_id = kw.get("stcw_ccmc_id")
        request.env["ccmc.candidate.stcw.certificate"].sudo().search(
            [("id", "=", stcw_id)]
        ).unlink()

        request.env.cr.commit()
        candidate = (
            request.env["ccmc.candidate"]
            .sudo()
            .search([("id", "=", kw.get("candidate_ccmc_id"))])
        )
        candidate._check_sign()
        candidate._check_image()
        candidate._check_ship_visit_criteria()
        candidate._check_attendance_criteria()
        candidate._check_stcw_certificate()

        return request.redirect(
            "/my/ccmccandidateprofile/" + str(kw.get("candidate_ccmc_id"))
        )

    @http.route(
        ["/my/ccmcshipvisit/delete"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def DeleteCcmcShipVisits(self, **kw):

        visit_id = kw.get("visit_id")
        request.env["ccmc.candidate.ship.visits"].sudo().search(
            [("id", "=", visit_id)]
        ).unlink()
        print("Delete ccmc ship visit", str(kw.get("candidate_id")))

        candidate = (
            request.env["ccmc.candidate"]
            .sudo()
            .search([("id", "=", kw.get("candidate_id"))])
        )
        candidate._check_ship_visit_criteria()
        return request.redirect(
            "/my/ccmccandidateprofile/" + str(kw.get("candidate_id"))
        )

    @http.route(
        ["/my/gpcandidate/addstcw"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def AddSTCW(self, **kw):

        candidate_id = kw.get("candidate_id")
        course_name = kw.get("course_name")
        institute_name = kw.get("institute_name")
        other_institute = kw.get("other_institute_name")
        marine_training_inst_number = kw.get("marine_training_inst_number")
        # mti_indos_no = kw.get('mti_indos_no')
        candidate_cert_no = kw.get("candidate_cert_no")
        course_start_date = kw.get("course_start_date")
        course_end_date = kw.get("course_end_date")
        certificate_upload = kw.get("certificate_upload")

        file_content = certificate_upload.read()
        filename = certificate_upload.filename

        stcw_data = {
            "candidate_id": candidate_id,
            "course_name": course_name,
            "institute_name": institute_name,
            "other_institute": other_institute,
            "marine_training_inst_number": marine_training_inst_number,
            # 'mti_indos_no': mti_indos_no,
            "candidate_cert_no": candidate_cert_no,
            "course_start_date": course_start_date,
            "course_end_date": course_end_date,
            "file_name": filename,
            "certificate_upload": base64.b64encode(file_content),
        }
        request.env["gp.candidate.stcw.certificate"].sudo().create(stcw_data)
        request.env.cr.commit()
        candidate = (
            request.env["gp.candidate"].sudo().search([("id", "=", candidate_id)])
        )
        candidate._check_sign()
        candidate._check_image()
        candidate._check_ship_visit_criteria()
        candidate._check_attendance_criteria()
        candidate._check_stcw_certificate()

        return request.redirect("/my/gpcandidateprofile/" + str(kw.get("candidate_id")))

    @http.route(
        ["/my/ccmccandidate/addstcw"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def AddCcmcSTCW(self, **kw):

        candidate_id = kw.get("candidate_id")
        course_name = kw.get("course_name")
        institute_name = kw.get("institute_name")
        other_institute = kw.get("other_institute_name")
        marine_training_inst_number = kw.get("marine_training_inst_number")
        # mti_indos_no = kw.get('mti_indos_no')
        candidate_cert_no = kw.get("candidate_cert_no")
        course_start_date = kw.get("course_start_date")
        course_end_date = kw.get("course_end_date")
        certificate_upload = kw.get("certificate_upload")

        file_content = certificate_upload.read()
        filename = certificate_upload.filename

        stcw_data = {
            "candidate_id": candidate_id,
            "course_name": course_name,
            "institute_name": institute_name,
            "other_institute": other_institute,
            "marine_training_inst_number": marine_training_inst_number,
            # 'mti_indos_no': mti_indos_no,
            "candidate_cert_no": candidate_cert_no,
            "course_start_date": course_start_date,
            "course_end_date": course_end_date,
            "file_name": filename,
            "certificate_upload": base64.b64encode(file_content),
        }
        request.env["ccmc.candidate.stcw.certificate"].sudo().create(stcw_data)
        candidate = (
            request.env["ccmc.candidate"].sudo().search([("id", "=", candidate_id)])
        )
        candidate._check_sign()
        candidate._check_image()
        candidate._check_ship_visit_criteria()
        candidate._check_attendance_criteria()
        candidate._check_stcw_certificate()

        return request.redirect(
            "/my/ccmccandidateprofile/" + str(kw.get("candidate_id"))
        )

    @http.route(
        ["/my/gpcandidate/updatefees"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def UpdateFees(self, **kw):
        # import wdb; wdb.set_trace();
        candidate_id = kw.get("candidate_id")
        fees_paid = kw.get("fees_paid")

        candidate = (
            request.env["gp.candidate"].sudo().search([("id", "=", int(candidate_id))])
        )

        candidate.write({"fees_paid": fees_paid})

        return request.redirect("/my/gpcandidateprofile/" + str(kw.get("candidate_id")))

    @http.route(
        ["/my/gpcandidate/updatefeesall"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def UpdateFeesGPAll(self, **kw):
        # import wdb; wdb.set_trace();
        batch_id = int(kw.get("confirm_gp_candidate_batch_id"))

        candidate = (
            request.env["gp.candidate"]
            .sudo()
            .search([("institute_batch_id", "=", int(batch_id))])
        )

        candidate.write({"fees_paid": "yes"})

        return request.redirect("/my/gpbatch/candidates/" + str(batch_id))

    @http.route(
        ["/my/ccmccandidate/updatefeesall"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def UpdateFeesCCMCAll(self, **kw):
        batch_id = int(kw.get("ccmc_batch_id"))

        candidate = (
            request.env["ccmc.candidate"]
            .sudo()
            .search([("institute_batch_id", "=", int(batch_id))])
        )

        candidate.write({"fees_paid": "yes"})

        return request.redirect("/my/ccmcbatch/candidates/" + str(batch_id))

    @http.route(
        ["/my/gpcandidate/updatefees2"],
        method=["POST", "GET"],
        type="json",
        auth="user",
    )
    def UpdateFeesGP(self, **kw):
        # import wdb; wdb.set_trace();
        data = request.jsonrequest
        candidate_id = data["candidate_id"]
        fees_paid = data["fees_paid"]

        candidate = (
            request.env["gp.candidate"].sudo().search([("id", "=", int(candidate_id))])
        )

        candidate.write({"fees_paid": fees_paid})

        return json.dumps({"status": "success"})

    @http.route(
        ["/my/ccmccandidate/updatefees2"],
        method=["POST", "GET"],
        type="json",
        auth="user",
    )
    def UpdateFeesccmc(self, **kw):
        # import wdb; wdb.set_trace();
        data = request.jsonrequest
        candidate_id = data["candidate_id"]
        fees_paid = data["fees_paid"]

        candidate = (
            request.env["ccmc.candidate"]
            .sudo()
            .search([("id", "=", int(candidate_id))])
        )

        candidate.write({"fees_paid": fees_paid})

        return json.dumps({"status": "success"})

    @http.route(
        ["/my/gpcandidate/attendance_compliance_1"],
        method=["POST", "GET"],
        type="json",
        auth="user",
    )
    def GPAttendanceCompliance1(self, **kw):
        # import wdb; wdb.set_trace();
        data = request.jsonrequest
        candidate_id = data["candidate_id"]
        attendance_compliance_1 = data["attendance_compliance_1"]
        candidate = (
            request.env["gp.candidate"].sudo().search([("id", "=", int(candidate_id))])
        )

        # import wdb; wdb.set_trace();
        if attendance_compliance_1 == "yes":
            candidate.write(
                {
                    "attendance_compliance_1": attendance_compliance_1,
                    "attendance_compliance_2": "na",
                }
            )
            candidate._check_attendance_criteria()
            return json.dumps(
                {
                    "status": "success",
                    "candidate_id": candidate_id,
                    "attendance_compliance_1": attendance_compliance_1,
                }
            )
        elif attendance_compliance_1 == "no":
            candidate.write(
                {
                    "attendance_compliance_1": attendance_compliance_1,
                    "attendance_compliance_2": "no",
                }
            )
            candidate._check_attendance_criteria()
            return json.dumps(
                {
                    "status": "success",
                    "candidate_id": candidate_id,
                    "attendance_compliance_1": attendance_compliance_1,
                }
            )

    @http.route(
        ["/my/gpcandidate/attendance_compliance_2"],
        method=["POST", "GET"],
        type="json",
        auth="user",
    )
    def GPAttendanceCompliance2(self, **kw):
        # import wdb; wdb.set_trace();
        data = request.jsonrequest
        candidate_id = data["candidate_id"]
        attendance_compliance_2 = data["attendance_compliance_2"]

        candidate = (
            request.env["gp.candidate"].sudo().search([("id", "=", int(candidate_id))])
        )

        candidate.write({"attendance_compliance_2": attendance_compliance_2})
        candidate._check_attendance_criteria()

        return json.dumps({"status": "success"})

    @http.route(
        ["/my/ccmccandidate/attendance_compliance_1"],
        method=["POST", "GET"],
        type="json",
        auth="user",
    )
    def CCMCAttendanceCompliance1(self, **kw):
        # import wdb; wdb.set_trace();
        data = request.jsonrequest
        candidate_id = data["candidate_id"]
        attendance_compliance_1 = data["attendance_compliance_1"]

        candidate = (
            request.env["ccmc.candidate"]
            .sudo()
            .search([("id", "=", int(candidate_id))])
        )

        if attendance_compliance_1 == "yes":
            candidate.write(
                {
                    "attendance_compliance_1": attendance_compliance_1,
                    "attendance_compliance_2": "na",
                }
            )
            candidate._check_attendance_criteria()
            return json.dumps(
                {
                    "status": "success",
                    "candidate_id": candidate_id,
                    "attendance_compliance_1": attendance_compliance_1,
                }
            )
        elif attendance_compliance_1 == "no":
            candidate.write(
                {
                    "attendance_compliance_1": attendance_compliance_1,
                    "attendance_compliance_2": "no",
                }
            )
            candidate._check_attendance_criteria()
            return json.dumps(
                {
                    "status": "success",
                    "candidate_id": candidate_id,
                    "attendance_compliance_1": attendance_compliance_1,
                }
            )

    @http.route(
        ["/my/ccmccandidate/attendance_compliance_2"],
        method=["POST", "GET"],
        type="json",
        auth="user",
    )
    def CCMCAttendanceCompliance2(self, **kw):
        # import wdb; wdb.set_trace();
        data = request.jsonrequest
        candidate_id = data["candidate_id"]
        attendance_compliance_2 = data["attendance_compliance_2"]

        candidate = (
            request.env["ccmc.candidate"]
            .sudo()
            .search([("id", "=", int(candidate_id))])
        )

        candidate.write({"attendance_compliance_2": attendance_compliance_2})
        candidate._check_attendance_criteria()

        return json.dumps({"status": "success"})

    @http.route(
        ["/my/gpcandidate/addattendance"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def UpdateGpAttendance(self, **kw):
        candidate_id = kw.get("candidate_id")
        attendance1 = kw.get("attendance1")
        attendance2 = kw.get("attendance2")

        candidate = (
            request.env["gp.candidate"].sudo().search([("id", "=", int(candidate_id))])
        )

        candidate.write({"attendance_compliance_1": attendance1})
        candidate.write({"attendance_compliance_2": attendance2})

        request.env.cr.commit()
        candidate = (
            request.env["gp.candidate"].sudo().search([("id", "=", candidate_id)])
        )
        candidate._check_sign()
        candidate._check_image()
        candidate._check_ship_visit_criteria()
        candidate._check_attendance_criteria()
        candidate._check_stcw_certificate()

        return request.redirect("/my/gpcandidateprofile/" + str(kw.get("candidate_id")))

    @http.route(
        ["/my/ccmccandidate/addattendance"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def UpdateCcmcAttendance(self, **kw):
        candidate_id = kw.get("candidate_id")
        attendance1 = kw.get("attendance1")
        attendance2 = kw.get("attendance2")

        candidate = (
            request.env["ccmc.candidate"]
            .sudo()
            .search([("id", "=", int(candidate_id))])
        )

        candidate.write({"attendance_compliance_1": attendance1})
        candidate.write({"attendance_compliance_2": attendance2})
        candidate._check_attendance_criteria()

        return request.redirect(
            "/my/ccmccandidateprofile/" + str(kw.get("candidate_id"))
        )

    @http.route(
        ["/my/ccmccandidate/updatefees"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def UpdateCcmcFees(self, **kw):
        candidate_id = kw.get("candidate_id")
        fees_paid = kw.get("fees_paid")

        candidate = (
            request.env["ccmc.candidate"]
            .sudo()
            .search([("id", "=", int(candidate_id))])
        )

        candidate.write({"fees_paid": fees_paid})

        return request.redirect(
            "/my/ccmccandidateprofile/" + str(kw.get("candidate_id"))
        )

    @http.route(
        "/my/batches/download_report/<int:batch_id>",
        type="http",
        auth="user",
        website=True,
    )
    def generate_report(self, batch_id):

        excel_buffer = io.BytesIO()

        # Create a new Excel workbook and add a worksheet
        workbook = xlsxwriter.Workbook(excel_buffer)

        gp_candidates = (
            request.env["gp.candidate"]
            .sudo()
            .search([("institute_batch_id", "=", batch_id)])
        )
        faculties = (
            request.env["institute.faculty"]
            .sudo()
            .search([("gp_batches_id", "=", batch_id)])
        )
        institutes = (
            request.env["institute.gp.batches"].sudo().search([("id", "=", batch_id)])
        )

        # print(institutes.dgs_approved_capacity)

        institute_worksheet = workbook.add_worksheet("Institute")
        institute_worksheet.set_column("A:B", 60)
        date_format = workbook.add_format({"num_format": "dd-mmm-yy"})
        bold_format = workbook.add_format(
            {"bold": True, "border": 1, "font_size": 16}
        )  # 'border': 1 adds a thin border

        # Create a format with borders.
        border_format = workbook.add_format({"border": 1, "font_size": 14})

        # bold_format = workbook.add_format({'bold': True})

        # border_format = workbook.add_format({'border': 1})  # 'border': 1 adds a thin border

        headers = ["", ""]
        for col_num, header in enumerate(headers):
            institute_worksheet.write(0, col_num, header)

        # Add data to the worksheet.
        data = [
            ["Name of the Institute", institutes.institute_id.name],
            ["MTI No. of institute", institutes.institute_id.mti],
            ["Approved Capacity", institutes.dgs_approved_capacity],
            ["Course Title", institutes.course.name],
            ["Batch No.", institutes.batch_name],
            # ['DOB.',gp_candidate.dob],
            [
                "Date of commencement and ending of the course",
                str(institutes.from_date) + " to " + str(institutes.to_date),
            ],
        ]

        for row_num, row_data in enumerate(data, start=1):
            for col_num, cell_data in enumerate(row_data):
                if col_num == 0:  # Check if it's column A
                    institute_worksheet.write(row_num, col_num, cell_data, bold_format)
                else:
                    institute_worksheet.write(
                        row_num, col_num, cell_data, border_format
                    )

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

        # Candidate

        candidate_worksheet = workbook.add_worksheet("Candidate")
        # candidate_worksheet.write('A1', 'Candidate Name')

        candidate_worksheet.write("A1", "SR. NO.")
        candidate_worksheet.write("B1", "ROLL NO")
        candidate_worksheet.write("C1", "NAME")
        candidate_worksheet.write("D1", "DOB")
        candidate_worksheet.write("E1", "Indos No.")
        candidate_worksheet.write("F1", "Candidate Code")

        row = 1

        for gp_candidate in gp_candidates:
            candidate_worksheet.write(row, 0, row)
            candidate_worksheet.write(row, 1, gp_candidate.roll_no)
            candidate_worksheet.write(row, 2, gp_candidate.name)
            candidate_worksheet.write(row, 3, gp_candidate.dob, date_format)
            candidate_worksheet.write(row, 4, gp_candidate.indos_no)
            candidate_worksheet.write(row, 5, gp_candidate.candidate_code)
            row += 1

        # Faculty

        faculty_worksheet = workbook.add_worksheet("Faculty")

        faculty_worksheet.write("A1", "Qualification")
        faculty_worksheet.write("B1", "Faculty Name")
        faculty_worksheet.write("C1", "Specialization")
        faculty_worksheet.write("D1", "DOB")
        faculty_worksheet.write("E1", "FT or PT")

        row = 1
        for faculty in faculties:
            faculty_worksheet.write(row, 0, faculty.qualification)
            faculty_worksheet.write(row, 1, faculty.faculty_name)
            faculty_worksheet.write(row, 2, faculty.designation)
            faculty_worksheet.write(row, 3, faculty.dob, date_format)
            row += 1

        # Close the workbook to save the data to the buffer
        workbook.close()

        # Set the buffer position to the beginning
        excel_buffer.seek(0)

        # Generate a response with the Excel file
        response = request.make_response(
            excel_buffer.getvalue(),
            headers=[
                (
                    "Content-Type",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ),
                ("Content-Disposition", "attachment; filename=my_excel_file.xlsx"),
            ],
        )

        # Clean up the buffer
        excel_buffer.close()

        return response

    @http.route(
        "/my/ccmc_batches/download_report/<int:batch_id>",
        type="http",
        auth="user",
        website=True,
    )
    def generate_ccmc_report(self, batch_id):

        excel_buffer = io.BytesIO()

        # Create a new Excel workbook and add a worksheet
        workbook = xlsxwriter.Workbook(excel_buffer)

        ccmc_candidates = (
            request.env["ccmc.candidate"]
            .sudo()
            .search([("institute_batch_id", "=", batch_id)])
        )
        faculties = (
            request.env["institute.faculty"]
            .sudo()
            .search([("ccmc_batches_id", "=", batch_id)])
        )
        institutes = (
            request.env["institute.ccmc.batches"].sudo().search([("id", "=", batch_id)])
        )

        institute_worksheet = workbook.add_worksheet("Institute")
        institute_worksheet.set_column("A:B", 60)
        date_format = workbook.add_format({"num_format": "dd-mmm-yy"})
        bold_format = workbook.add_format(
            {"bold": True, "border": 1, "font_size": 16}
        )  # 'border': 1 adds a thin border

        # Create a format with borders.
        border_format = workbook.add_format({"border": 1, "font_size": 14})

        # bold_format = workbook.add_format({'bold': True})

        # border_format = workbook.add_format({'border': 1})  # 'border': 1 adds a thin border

        headers = ["", ""]
        for col_num, header in enumerate(headers):
            institute_worksheet.write(0, col_num, header)

        # Add data to the worksheet.
        data = [
            ["Name of the Institute", institutes.institute_id.name],
            ["MTI No. of institute", institutes.institute_id.mti],
            ["Approved Capacity", institutes.dgs_approved_capacity],
            ["Course Title", institutes.ccmc_course.name],
            ["Batch No.", institutes.ccmc_batch_name],
            [
                "Date of commencement and ending of the course",
                str(institutes.ccmc_from_date) + " to " + str(institutes.ccmc_to_date),
            ],
        ]

        for row_num, row_data in enumerate(data, start=1):
            for col_num, cell_data in enumerate(row_data):
                if col_num == 0:  # Check if it's column A
                    institute_worksheet.write(row_num, col_num, cell_data, bold_format)
                else:
                    institute_worksheet.write(
                        row_num, col_num, cell_data, border_format
                    )

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

        # Candidate

        candidate_worksheet = workbook.add_worksheet("Candidate")
        # candidate_worksheet.write('A1', 'Candidate Name')

        candidate_worksheet.write("A1", "SR. NO.")
        candidate_worksheet.write("B1", "ROLL NO")
        candidate_worksheet.write("C1", "NAME")
        candidate_worksheet.write("D1", "DOB")
        candidate_worksheet.write("E1", "Xth")
        candidate_worksheet.write("F1", "XIIth")

        row = 1

        for ccmc_candidate in ccmc_candidates:
            candidate_worksheet.write(row, 0, row)
            candidate_worksheet.write(row, 1, ccmc_candidate.roll_no)
            candidate_worksheet.write(row, 2, ccmc_candidate.name)
            candidate_worksheet.write(row, 3, ccmc_candidate.dob, date_format)
            candidate_worksheet.write(row, 4, ccmc_candidate.tenth_percent)
            candidate_worksheet.write(row, 5, ccmc_candidate.twelve_percent)
            row += 1

        # Faculty

        faculty_worksheet = workbook.add_worksheet("Faculty")
        faculty_worksheet.write("A1", "Qualification")
        faculty_worksheet.write("B1", "Faculty Name")
        faculty_worksheet.write("C1", "Specialization")
        faculty_worksheet.write("D1", "DOB")
        faculty_worksheet.write("E1", "FT or PT")

        row = 1
        for faculty in faculties:
            faculty_worksheet.write(row, 0, faculty.qualification)
            faculty_worksheet.write(row, 1, faculty.faculty_name)
            faculty_worksheet.write(row, 2, faculty.designation)
            faculty_worksheet.write(row, 3, faculty.dob, date_format)
            row += 1

        # Close the workbook to save the data to the buffer
        workbook.close()

        # Set the buffer position to the beginning
        excel_buffer.seek(0)

        # Generate a response with the Excel file
        response = request.make_response(
            excel_buffer.getvalue(),
            headers=[
                (
                    "Content-Type",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ),
                ("Content-Disposition", "attachment; filename=my_excel_file.xlsx"),
            ],
        )

        # Clean up the buffer
        excel_buffer.close()

        return response

    def _get_report_data(self):
        # Your logic to fetch data for the report
        data = request.env["res.partner"].search([])
        return

    @http.route(
        ["/my/gpcandidates/download_admit_card/<int:candidate_id>"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def DownloadsAdmitCard(self, candidate_id, **kw):
        
        user_id = request.env.user
        # import wdb; wdb.set_trace()
        if user_id.has_group('bes.download_not_allowed'):
            # User is in the group
            raise ValidationError("Please Contact Administrator")

        try:
            exam_id = (
                request.env["gp.exam.schedule"]
                .sudo()
                .search([("gp_candidate", "=", candidate_id)])[-1]
            )
        except:
            raise ValidationError("Admit Card Not Found or Not Generated")
        report_action = request.env.ref("bes.candidate_gp_admit_card_action")
        pdf, _ = report_action.sudo()._render_qweb_pdf(int(exam_id))
        pdfhttpheaders = [
            ("Content-Type", "application/pdf"),
            ("Content-Length", "%s" % len(pdf)),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route(
        ["/my/gpcandidates/download_gp_certificate/<int:candidate_id>"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def DownloadGPCertificate(self, candidate_id, **kw):
        # import wdb; wdb.set_trace()
                
        user_id = request.env.user
        # import wdb; wdb.set_trace()
        if user_id.has_group('bes.download_not_allowed'):
            # User is in the group
            raise ValidationError("Please Contact Administrator")

        try:
            exam_id = (
                request.env["gp.exam.schedule"]
                .sudo()
                .search(
                    [
                        ("gp_candidate", "=", candidate_id),
                        ("certificate_criteria", "=", "passed"),
                    ]
                )
            )
        except:
            raise ValidationError("Certificate Not Generated")
        report_action = request.env.ref("bes.report_gp_certificate")
        pdf, _ = report_action.sudo()._render_qweb_pdf(int(exam_id.id))
        pdfhttpheaders = [
            ("Content-Type", "application/pdf"),
            ("Content-Length", "%s" % len(pdf)),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route(
        ["/my/gpcandidates/download_admit_card_from_url/<int:rec_id>"],
        type="http",
        auth="user",
        website=True,
    )
    def download_admit_card_from_url(self, rec_id, **kw):
                
        user_id = request.env.user
        # import wdb; wdb.set_trace()
        if user_id.has_group('bes.download_not_allowed'):
            # User is in the group
            raise ValidationError("Please Contact Administrator")

        # Retrieve the record
        report_action = request.env.ref("bes.candidate_gp_admit_card_action")

        # Check if the user has access to the record
        if report_action.check_access_rights("read", raise_exception=False):
            # Perform operations
            pdf_content, _ = report_action.sudo()._render_qweb_pdf(rec_id)

            # Set PDF headers
            pdf_http_headers = [
                ("Content-Type", "application/pdf"),
                ("Content-Length", str(len(pdf_content))),
            ]

    @http.route(
        ["/my/ccmccandidates/download_admit_card/<int:candidate_id>"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def DownloadCcmcAdmitCard(self, candidate_id, **kw):
        # import wdb; wdb.set_trace()
                
        user_id = request.env.user
        # import wdb; wdb.set_trace()
        if user_id.has_group('bes.download_not_allowed'):
            # User is in the group
            raise ValidationError("Please Contact Administrator")

        try:
            exam_id = (
                request.env["ccmc.exam.schedule"]
                .sudo()
                .search([("ccmc_candidate", "=", candidate_id)])[-1]
            )
        except:
            raise ValidationError("Admit Card Not Found or Not Generated")

        report_action = request.env.ref("bes.candidate_ccmc_admit_card_action")
        pdf, _ = report_action.sudo()._render_qweb_pdf(int(exam_id))
        # print(pdf ,"Tbis is PDF")
        pdfhttpheaders = [
            ("Content-Type", "application/pdf"),
            ("Content-Length", "%s" % len(pdf)),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route(
        ["/my/ccmccandidates/download_ccmc_certificate/<int:candidate_id>"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def DownloadCCMCCertificate(self, candidate_id, **kw):
        # import wdb; wdb.set_trace()
                
        user_id = request.env.user
        # # import wdb; wdb.set_trace()
        if user_id.has_group('bes.download_not_allowed'):
            # User is in the group
            raise ValidationError("Please Contact Administrator")

        try:
            exam_id = (
                request.env["ccmc.exam.schedule"]
                .sudo()
                .search(
                    [
                        ("ccmc_candidate", "=", candidate_id),
                        ("certificate_criteria", "=", "passed"),
                    ]
                )
            )
        except:
            raise ValidationError("Certificate Not Generated")
        report_action = request.env.ref("bes.report_ccmc_certificate")
        pdf, _ = report_action.sudo()._render_qweb_pdf(int(exam_id.id))
        pdfhttpheaders = [
            ("Content-Type", "application/pdf"),
            ("Content-Length", "%s" % len(pdf)),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route(
        "/my/ccmcbatch/candidates/download_format",
        type="http",
        auth="user",
        website=True,
    )
    def generate_ccmc_student_format(self):
        excel_buffer = io.BytesIO()

        # Create a new Excel workbook and add a worksheet
        workbook = xlsxwriter.Workbook(excel_buffer)
        candidate_worksheet = workbook.add_worksheet("Candidates")

        locked = workbook.add_format({"locked": True})
        unlocked = workbook.add_format({"locked": False})
        candidate_worksheet.set_column("A:XDF", None, unlocked)

        candidate_worksheet.set_column("A:A", 15, unlocked)  # indos
        candidate_worksheet.set_column("B:B", 30, unlocked)  # name
        candidate_worksheet.set_column("C:C", 10, unlocked)  # gender
        candidate_worksheet.set_column("D:D", 15, unlocked)  # dob
        candidate_worksheet.set_column("E:E", 35, unlocked)  # line 1
        candidate_worksheet.set_column("F:F", 35, unlocked)  # line2
        candidate_worksheet.set_column("G:G", 20, unlocked)  # city
        candidate_worksheet.set_column("H:H", 10, unlocked)  # state
        candidate_worksheet.set_column("I:I", 15, unlocked)  # pin
        candidate_worksheet.set_column("J:J", 20, unlocked)  # mobile
        candidate_worksheet.set_column("K:K", 20, unlocked)  # email
        candidate_worksheet.set_column("L:L", 10, unlocked)  # Xth
        candidate_worksheet.set_column("M:M", 10, unlocked)  # XIIth
        candidate_worksheet.set_column("N:N", 10, unlocked)  # ITI
        candidate_worksheet.set_column("O:O", 25, unlocked)  # category

        candidate_worksheet.protect()
        date_format = workbook.add_format(
            {"num_format": "dd-mmm-yyyy", "locked": False}
        )
        # number_format = workbook.add_format({'num_format': '0000000000', 'locked': False})
        # zip_format = workbook.add_format({'num_format': '000000', 'locked': False})

        # bold_format = workbook.add_format({'bold': True, 'border': 1,'font_size': 16})

        header_format = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_color": "white",
                "bg_color": "#336699",  # Blue color for the background
                "locked": True,
            }
        )

        header = [
            "INDOS NO",
            "NAME",
            "Gender",
            "DOB DD-MMM-YYYY",
            "Address Line 1",
            "Address Line 2",
            "DIST/CITY",
            "STATE",
            "PINCODE",
            "MOBILE",
            "EMAIL",
            "Xth",
            "XIIth",
            "ITI",
            "To be mentioned if SC /ST /OBC",
        ]
        for col, value in enumerate(header):
            candidate_worksheet.write(0, col, value, header_format)

        # Set date format for DOB column
        candidate_worksheet.set_column("D:D", 20, date_format)
        # candidate_worksheet.set_column('J:J', None, number_format)
        # candidate_worksheet.set_column('G:G', None, zip_format)

        category_values = ["General", "SC", "ST", "OBC"]
        gender_values = ["Male", "Female"]
        state_values = [
            "JK",
            "MH",
            "AP",
            "AR",
            "AS",
            "BR",
            "CG",
            "GA",
            "GJ",
            "HR",
            "HP",
            "JH",
            "KA",
            "KL",
            "MP",
            "MN",
            "ML",
            "MZ",
            "NL",
            "OR",
            "PB",
            "RJ",
            "SK",
            "TN",
            "TG",
            "TR",
            "UP",
            "UK",
            "WB",
            "CH",
            "LD",
            "DL",
            "PY",
            "AN",
            "DH",
        ]

        # Add data validation for SC/ST column
        # candidate_worksheet.data_validation('O2:O1048576', {'validate': 'list',
        #                                         'source': dropdown_values })

        candidate_worksheet.data_validation(
            "H2:H1048576", {"validate": "list", "source": state_values}
        )

        candidate_worksheet.data_validation(
            "O2:O1048576", {"validate": "list", "source": category_values}
        )

        candidate_worksheet.data_validation(
            "C2:C1048576", {"validate": "list", "source": gender_values}
        )

        # Add data validation to enforce 6-digit PIN codes
        candidate_worksheet.data_validation(
            "I2:I1048576",  # Apply to all rows in column I (starting from row 2)
            {
                "validate": "length",  # Validate based on length
                "criteria": "==",      # Ensure the length is exactly equal to
                "value": 6,            # 6 characters
                "input_title": "PIN Code",  # Input prompt title
                "input_message": "Please enter a 6-digit PIN code.",  # Input prompt message
                "error_title": "Invalid PIN Code",  # Error message title
                "error_message": "The PIN code must be exactly 6 digits.",  # Error message
            }
        )

        state_cheatsheet = workbook.add_worksheet("States")
        state_cheatsheet.write("A1", "Code")
        state_cheatsheet.write("B1", "State")

        state_values = {
            "JK": "Jammu and Kashmir",
            "MH": "Maharashtra",
            "AP": "Andhra Pradesh",
            "AR": "Arunachal Pradesh",
            "AS": "Assam",
            "BR": "Bihar",
            "CG": "Chhattisgarh",
            "GA": "Goa",
            "GJ": "Gujarat",
            "HR": "Haryana",
            "HP": "Himachal Pradesh",
            "JH": "Jharkhand",
            "KA": "Karnataka",
            "KL": "Kerala",
            "MP": "Madhya Pradesh",
            "MN": "Manipur",
            "ML": "Meghalaya",
            "MZ": "Mizoram",
            "NL": "Nagaland",
            "OR": "Orissa",
            "PB": "Punjab",
            "RJ": "Rajasthan",
            "SK": "Sikkim",
            "TN": "Tamil Nadu",
            "TG": "Telangana",
            "TR": "Tripura",
            "UP": "Uttar Pradesh",
            "UK": "Uttarakhand",
            "WB": "West Bengal",
            "AN": "Andaman and Nicobar Islands",
            "CH": "Chandigarh",
            "DH": "Dadra and Nagar Haveli and Daman and Diu",
            "LD": "Lakshadweep",
            "DL": "Delhi",
            "PY": "Puducherry",
        }

        row = 1
        for state, code in state_values.items():
            state_cheatsheet.write(row, 0, state)
            state_cheatsheet.write(row, 1, code)
            row += 1

        # candidate_worksheet.protect()
        # candidate_worksheet.write(1, None, None, {'locked': False})
        # candidate_worksheet.set_row(0, None, None)
        instruction_worksheet = workbook.add_worksheet("Instructions")

        instruction_worksheet.set_column("A:P", 20, unlocked)

        # instruction_worksheet.protect()
        date_format = workbook.add_format(
            {"num_format": "dd-mmm-yyyy", "locked": False}
        )
        # number_format = workbook.add_format({'num_format': '0000000000', 'locked': False})
        # zip_format = workbook.add_format({'num_format': '000000', 'locked': False})

        # bold_format = workbook.add_format({'bold': True, 'border': 1,'font_size': 16})

        instruction_worksheet.write_comment(
            "M2",
            'In the columns Xth, XIIth, ITI , Please enter only number or grade (a,"a+,b,b+,c,c+,d,d+)',
        )

        header_format = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_color": "white",
                "bg_color": "#336699",  # Blue color for the background
                "locked": True,
            }
        )

        header = [
            "SR No",
            "INDOS NO",
            "NAME",
            "DOB DD-MMM-YYYY",
            "Address Line 1",
            "Address Line 2",
            "CITY",
            "STATE",
            "PINCODE",
            "MOBILE",
            "EMAIL",
            "Xth",
            "XIIth",
            "ITI",
        ]
        for col, value in enumerate(header):
            instruction_worksheet.write(0, col, value, header_format)

        # Set date format for DOB column
        instruction_worksheet.set_column("C:C", 20, date_format)

        cell_format = workbook.add_format()
        cell_format.set_text_wrap()

        mandatory_format = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_color": "red",
                "text_wrap": True,
            }
        )

        instruction_worksheet.write("A3", "1) Description")
        instruction_worksheet.write("A4", "2) Format")
        instruction_worksheet.write("A5", "3) Mandatory")

        instruction_worksheet.write("B2", "23GM1234")
        instruction_worksheet.write(
            "B3",
            "This field contains the student's Indos number to be used as the student's login in the future",
            cell_format,
        )
        instruction_worksheet.write(
            "B4",
            "The format should be adhered to; wrong Indos or duplicate Indos numbers should be avoided at all costs",
            cell_format,
        )
        instruction_worksheet.write("B5", "Mandatory Field", mandatory_format)

        instruction_worksheet.write("C2", "Lokesh Dalvi")
        instruction_worksheet.write("C3", "Name As per Indos Number", cell_format)
        instruction_worksheet.write(
            "C4",
            "The format of the name to be used should be as needed in certificates and future records",
            cell_format,
        )
        instruction_worksheet.write("C5", "Mandatory Field", mandatory_format)

        instruction_worksheet.write("D2", "14-Apr-02")
        instruction_worksheet.write(
            "D3",
            "This is the date of birth field for students; it should be as per records",
            cell_format,
        )
        instruction_worksheet.write(
            "D4",
            'The date format to be followed strictly is DD-MMM-YY; do not use "/" or any other special character except as per the format',
            cell_format,
        )
        instruction_worksheet.write("D5", "Mandatory Field", mandatory_format)

        instruction_worksheet.write("E2", "Street1")
        instruction_worksheet.write("E3", "This is address line 1")
        instruction_worksheet.write(
            "E4", "No format is needed; it can be blank as well", cell_format
        )
        instruction_worksheet.write(
            "E5", "Not mandatory but advisable to have", cell_format
        )

        instruction_worksheet.write("F2", "Street2")
        instruction_worksheet.write("F3", "This is address line 2")
        instruction_worksheet.write(
            "F4", "No format is needed; it can be blank as well", cell_format
        )
        instruction_worksheet.write(
            "F5", "Not mandatory but advisable to have", cell_format
        )

        instruction_worksheet.write("G2", "City")
        instruction_worksheet.write("G3", "City name as per address", cell_format)
        instruction_worksheet.write("G4", "No format")
        instruction_worksheet.write("G5", "Mandatory Field", mandatory_format)

        instruction_worksheet.write("H2", "MH")
        instruction_worksheet.write(
            "H3",
            "This field is the state code to be selected from dropdown only",
            cell_format,
        )
        instruction_worksheet.write(
            "H4",
            'Use only the drop-downs to select the state code; please do not enter data manually in this field. Refer to the worksheet "State" for the list',
            cell_format,
        )
        instruction_worksheet.write("H5", "Mandatory Field", mandatory_format)

        instruction_worksheet.write("I2", 123456)
        instruction_worksheet.write(
            "I3", "This field is the PIN code of the candidate's address", cell_format
        )
        instruction_worksheet.write(
            "I4",
            "The PIN code should be exactly 6 digits; only numbers are accepted",
            cell_format,
        )
        instruction_worksheet.write("I5", "Mandatory Field", mandatory_format)

        instruction_worksheet.write("J2", 1234567890)
        instruction_worksheet.write(
            "J3", "This field is the mobile number of the candidate", cell_format
        )
        instruction_worksheet.write(
            "J4", "Only numbers accepted; should be 10 digits", cell_format
        )
        instruction_worksheet.write(
            "J5", "Not mandatory but advisable to have", cell_format
        )

        instruction_worksheet.write("K2", "abc@gmail.com")
        instruction_worksheet.write(
            "K3", "This field is the email ID of the candidate", cell_format
        )
        instruction_worksheet.write("K4", 'Must contain a "@" and ".com"', cell_format)
        instruction_worksheet.write("K5", "Mandatory Field", mandatory_format)

        instruction_worksheet.write("L2", 61)
        instruction_worksheet.write(
            "L3",
            "This field should contain marks or grade of English subject",
            cell_format,
        )
        instruction_worksheet.write(
            "L4",
            'Only numbers and grades (a, a+, b, b+, c, c+, d, d+) are accepted ,symbols like "%" are not allowed',
            cell_format,
        )
        instruction_worksheet.write("L5", "Mandatory Field", mandatory_format)

        instruction_worksheet.write("M2", 61)
        instruction_worksheet.write(
            "M3",
            "This field should contain marks or grade of English subject",
            cell_format,
        )
        instruction_worksheet.write(
            "M4",
            'Only numbers and grades (a, a+, b, b+, c, c+, d, d+) are accepted ,symbols like "%" are not allowed',
            cell_format,
        )
        instruction_worksheet.write(
            "M5", "Not mandatory but advisable to have", cell_format
        )

        instruction_worksheet.write("N2", 61)
        instruction_worksheet.write("N3", "Enter marks or grades")
        instruction_worksheet.write(
            "N4",
            'Only numbers and grades (a, a+, b, b+, c, c+, d, d+) are accepted ,symbols like "%" are not allowed',
            cell_format,
        )
        instruction_worksheet.write(
            "N5", "Not mandatory but advisable to have", cell_format
        )

        # Instruction Description
        merge_format = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_size": 15,
                "font_color": "black",
            }
        )

        instruction_worksheet.merge_range(
            "A13:B13", "General Instructions:", merge_format
        )
        instruction_worksheet.write("A14", 1)
        instruction_worksheet.write(
            "B14", "Download this template and use the same to fill data", cell_format
        )
        instruction_worksheet.write("A15", 2)
        instruction_worksheet.write(
            "B15", "Do not upload your own Excel file", cell_format
        )
        instruction_worksheet.write("A16", 3)
        instruction_worksheet.write(
            "B16", "Data will be captured from Sheet 1 (Candidates)", cell_format
        )
        instruction_worksheet.write("A17", 4)
        instruction_worksheet.write(
            "B17", "Do not change the name of the sheet", cell_format
        )
        instruction_worksheet.write("A18", 5)
        instruction_worksheet.write(
            "B18",
            "If you are copying and pasting data from some other Excel, please ensure the format of this template is followed",
            mandatory_format,
        )
        instruction_worksheet.write("A19", 6)
        instruction_worksheet.write(
            "B19", "No rows or columns to be deleted or shifted", mandatory_format
        )

        instruction_worksheet.protect()

        workbook.close()

        # Set the buffer position to the beginning
        excel_buffer.seek(0)

        # Generate a response with the Excel file
        response = request.make_response(
            excel_buffer.getvalue(),
            headers=[
                (
                    "Content-Type",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ),
                (
                    "Content-Disposition",
                    "attachment; filename=candidate_format_file.xlsx",
                ),
            ],
        )

        # Clean up the buffer
        excel_buffer.close()

        return response

    @http.route(
        "/my/gpbatch/candidates/download_format", type="http", auth="user", website=True
    )
    def generate_gp_student_format(self):
        excel_buffer = io.BytesIO()

        # Create a new Excel workbook and add a worksheet
        workbook = xlsxwriter.Workbook(excel_buffer)
        candidate_worksheet = workbook.add_worksheet("Candidates")

        locked = workbook.add_format({"locked": True})
        unlocked = workbook.add_format({"locked": False})
        candidate_worksheet.set_column("A:XDF", None, unlocked)

        candidate_worksheet.set_column("A:A", 15, unlocked)  # indos
        candidate_worksheet.set_column("B:B", 30, unlocked)  # name
        candidate_worksheet.set_column("C:C", 10, unlocked)  # gender
        candidate_worksheet.set_column("D:D", 15, unlocked)  # dob
        candidate_worksheet.set_column("E:E", 35, unlocked)  # line 1
        candidate_worksheet.set_column("F:F", 35, unlocked)  # line2
        candidate_worksheet.set_column("G:G", 20, unlocked)  # city
        candidate_worksheet.set_column("H:H", 10, unlocked)  # state
        candidate_worksheet.set_column("I:I", 15, unlocked)  # pin
        candidate_worksheet.set_column("J:J", 20, unlocked)  # mobile
        candidate_worksheet.set_column("K:K", 20, unlocked)  # email
        candidate_worksheet.set_column("L:L", 10, unlocked)  # Xth
        candidate_worksheet.set_column("M:M", 10, unlocked)  # XIIth
        candidate_worksheet.set_column("N:N", 10, unlocked)  # ITI
        candidate_worksheet.set_column("O:O", 25, unlocked)  # category

        candidate_worksheet.protect()
        date_format = workbook.add_format(
            {"num_format": "dd-mmm-yyyy", "locked": False}
        )
        # number_format = workbook.add_format({'num_format': '0000000000', 'locked': False})
        # zip_format = workbook.add_format({'num_format': '000000', 'locked': False})

        # bold_format = workbook.add_format({'bold': True, 'border': 1,'font_size': 16})
        candidate_worksheet.write_comment(
            "K2",
            'In the columns Xth, XIIth, ITI , Please enter only number or grade (a,"a+,b,b+,c,c+,d,d+)',
        )

        header_format = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_color": "white",
                "bg_color": "#336699",  # Blue color for the background
                "locked": True,
            }
        )

        header = [
            "INDOS NO",
            "NAME",
            "Gender",
            "DOB DD-MMM-YYYY",
            "Address Line 1",
            "Address Line 2",
            "DIST/CITY",
            "STATE",
            "PINCODE",
            "MOBILE",
            "EMAIL",
            "Xth",
            "XIIth",
            "ITI",
            "To be mentioned if SC /ST /OBC",
        ]
        for col, value in enumerate(header):
            candidate_worksheet.write(0, col, value, header_format)
            # candidate_worksheet.set_column('J:J', None, number_format)
            # candidate_worksheet.set_column('G:G', None, zip_format)

        # Set date format for DOB column
        candidate_worksheet.set_column("D:D", 20, date_format)

        category_values = ["General", "SC", "ST", "OBC"]
        gender_values = ["Male", "Female"]
        # import wdb; wdb.set_trace()

        state_values = [
            "JK",
            "MH",
            "AP",
            "AR",
            "AS",
            "BR",
            "CG",
            "GA",
            "GJ",
            "HR",
            "HP",
            "JH",
            "KA",
            "KL",
            "MP",
            "MN",
            "ML",
            "MZ",
            "NL",
            "OR",
            "PB",
            "RJ",
            "SK",
            "TN",
            "TG",
            "TR",
            "UP",
            "UK",
            "WB",
            "CH",
            "LD",
            "DL",
            "PY",
            "AN",
            "DH",
        ]

        state_values2 = [
            "Jammu and Kashmir",
            "Maharashtra",
            "Andhra Pradesh",
            "Arunachal Pradesh",
            "Assam",
            "Bihar",
            "Chhattisgarh",
            "Goa",
            "Gujarat",
            "Haryana",
            "Himachal Pradesh",
            "Jharkhand",
            "Karnataka",
            "Kerala",
            "Madhya Pradesh",
            "Manipur",
            "Meghalaya",
            "Mizoram",
            "Nagaland",
            "Odisha",
            "Punjab",
            "Rajasthan",
            "Sikkim",
            "Tamil Nadu",
            "Telangana",
            "Tripura",
            "Uttar Pradesh",
            "Uttarakhand",
            "West Bengal",
            "Chandigarh",
            "Lakshadweep",
            "Delhi",
            "Puducherry",
            "Andaman and Nicobar Islands",
            "Dadra and Nagar Haveli and Daman and Diu",
        ]

        # Add data validation for SC/ST column
        # candidate_worksheet.data_validation('O2:O1048576', {'validate': 'list',
        #                                         'source': dropdown_values })

        candidate_worksheet.data_validation(
            "H2:H1048576", {"validate": "list", "source": state_values}
        )

        candidate_worksheet.data_validation(
            "O2:O1048576", {"validate": "list", "source": category_values}
        )

        candidate_worksheet.data_validation(
            "C2:C1048576", {"validate": "list", "source": gender_values}
        )
        # Add data validation to enforce 6-digit PIN codes
        candidate_worksheet.data_validation(
            "I2:I1048576",  # Apply to all rows in column I (starting from row 2)
            {
                "validate": "length",  # Validate based on length
                "criteria": "==",      # Ensure the length is exactly equal to
                "value": 6,            # 6 characters
                "input_title": "PIN Code",  # Input prompt title
                "input_message": "Please enter a 6-digit PIN code.",  # Input prompt message
                "error_title": "Invalid PIN Code",  # Error message title
                "error_message": "The PIN code must be exactly 6 digits.",  # Error message
            }
        )

        state_cheatsheet = workbook.add_worksheet("States")
        state_cheatsheet.write("A1", "Code")
        state_cheatsheet.write("B1", "State")

        state_values = {
            "JK": "Jammu and Kashmir",
            "MH": "Maharashtra",
            "AP": "Andhra Pradesh",
            "AR": "Arunachal Pradesh",
            "AS": "Assam",
            "BR": "Bihar",
            "CG": "Chhattisgarh",
            "GA": "Goa",
            "GJ": "Gujarat",
            "HR": "Haryana",
            "HP": "Himachal Pradesh",
            "JH": "Jharkhand",
            "KA": "Karnataka",
            "KL": "Kerala",
            "MP": "Madhya Pradesh",
            "MN": "Manipur",
            "ML": "Meghalaya",
            "MZ": "Mizoram",
            "NL": "Nagaland",
            "OR": "Orissa",
            "PB": "Punjab",
            "RJ": "Rajasthan",
            "SK": "Sikkim",
            "TN": "Tamil Nadu",
            "TG": "Telangana",
            "TR": "Tripura",
            "UP": "Uttar Pradesh",
            "UK": "Uttarakhand",
            "WB": "West Bengal",
            "AN": "Andaman and Nicobar Islands",
            "CH": "Chandigarh",
            "DH": "Dadra and Nagar Haveli and Daman and Diu",
            "LD": "Lakshadweep",
            "DL": "Delhi",
            "PY": "Puducherry",
        }

        row = 1
        for state, code in state_values.items():
            state_cheatsheet.write(row, 0, state)
            state_cheatsheet.write(row, 1, code)
            row += 1

        # state_cheatsheet.protect()
        # state_cheatsheet.write(1, None, None, {'locked': False})
        # state_cheatsheet.set_row(0, None, None)

        instruction_worksheet = workbook.add_worksheet("Instructions")

        instruction_worksheet.set_column("A:P", 20, unlocked)

        # instruction_worksheet.protect()
        date_format = workbook.add_format(
            {"num_format": "dd-mmm-yyyy", "locked": False}
        )
        # number_format = workbook.add_format({'num_format': '0000000000', 'locked': False})
        # zip_format = workbook.add_format({'num_format': '000000', 'locked': False})

        # bold_format = workbook.add_format({'bold': True, 'border': 1,'font_size': 16})

        instruction_worksheet.write_comment(
            "M2",
            'In the columns Xth, XIIth, ITI , Please enter only number or grade (a,"a+,b,b+,c,c+,d,d+)',
        )

        header_format = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_color": "white",
                "bg_color": "#336699",  # Blue color for the background
                "locked": True,
            }
        )

        header = [
            "SR No",
            "INDOS NO",
            "NAME",
            "DOB DD-MMM-YYYY",
            "Address Line 1",
            "Address Line 2",
            "CITY",
            "STATE",
            "PINCODE",
            "MOBILE",
            "EMAIL",
            "Xth",
            "XIIth",
            "ITI",
        ]
        for col, value in enumerate(header):
            instruction_worksheet.write(0, col, value, header_format)

        # Set date format for DOB column
        instruction_worksheet.set_column("C:C", 20, date_format)

        cell_format = workbook.add_format()
        cell_format.set_text_wrap()

        mandatory_format = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_color": "red",
                "text_wrap": True,
            }
        )

        instruction_worksheet.write("A3", "1) Description")
        instruction_worksheet.write("A4", "2) Format")
        instruction_worksheet.write("A5", "3) Mandatory")

        instruction_worksheet.write("B2", "23GM1234")
        instruction_worksheet.write(
            "B3",
            "This field contains the student's Indos number to be used as the student's login in the future",
            cell_format,
        )
        instruction_worksheet.write(
            "B4",
            "The format should be adhered to; wrong Indos or duplicate Indos numbers should be avoided at all costs",
            cell_format,
        )
        instruction_worksheet.write("B5", "Mandatory Field", mandatory_format)

        instruction_worksheet.write("C2", "Lokesh Dalvi")
        instruction_worksheet.write("C3", "Name As per Indos Number", cell_format)
        instruction_worksheet.write(
            "C4",
            "The format of the name to be used should be as needed in certificates and future records",
            cell_format,
        )
        instruction_worksheet.write("C5", "Mandatory Field", mandatory_format)

        instruction_worksheet.write("D2", "14-Apr-02")
        instruction_worksheet.write(
            "D3",
            "This is the date of birth field for students; it should be as per records",
            cell_format,
        )
        instruction_worksheet.write(
            "D4",
            'The date format to be followed strictly is DD-MMM-YY; do not use "/" or any other special character except as per the format',
            cell_format,
        )
        instruction_worksheet.write("D5", "Mandatory Field", mandatory_format)

        instruction_worksheet.write("E2", "Street1")
        instruction_worksheet.write("E3", "This is address line 1")
        instruction_worksheet.write(
            "E4", "No format is needed; it can be blank as well", cell_format
        )
        instruction_worksheet.write(
            "E5", "Not mandatory but advisable to have", cell_format
        )

        instruction_worksheet.write("F2", "Street2")
        instruction_worksheet.write("F3", "This is address line 2")
        instruction_worksheet.write(
            "F4", "No format is needed; it can be blank as well", cell_format
        )
        instruction_worksheet.write(
            "F5", "Not mandatory but advisable to have", cell_format
        )

        instruction_worksheet.write("G2", "City")
        instruction_worksheet.write("G3", "City name as per address", cell_format)
        instruction_worksheet.write("G4", "No format")
        instruction_worksheet.write("G5", "Mandatory Field", mandatory_format)

        instruction_worksheet.write("H2", "MH")
        instruction_worksheet.write(
            "H3",
            "This field is the state code to be selected from dropdown only",
            cell_format,
        )
        instruction_worksheet.write(
            "H4",
            'Use only the drop-downs to select the state code; please do not enter data manually in this field. Refer to the worksheet "State" for the list',
            cell_format,
        )
        instruction_worksheet.write("H5", "Mandatory Field", mandatory_format)

        instruction_worksheet.write("I2", 123456)
        instruction_worksheet.write(
            "I3", "This field is the PIN code of the candidate's address", cell_format
        )
        instruction_worksheet.write(
            "I4",
            "The PIN code should be exactly 6 digits; only numbers are accepted",
            cell_format,
        )
        instruction_worksheet.write("I5", "Mandatory Field", mandatory_format)

        instruction_worksheet.write("J2", 1234567890)
        instruction_worksheet.write(
            "J3", "This field is the mobile number of the candidate", cell_format
        )
        instruction_worksheet.write(
            "J4", "Only numbers accepted; should be 10 digits", cell_format
        )
        instruction_worksheet.write(
            "J5", "Not mandatory but advisable to have", cell_format
        )

        instruction_worksheet.write("K2", "abc@gmail.com")
        instruction_worksheet.write(
            "K3", "This field is the email ID of the candidate", cell_format
        )
        instruction_worksheet.write("K4", 'Must contain a "@" and ".com"', cell_format)
        instruction_worksheet.write("K5", "Mandatory Field", mandatory_format)

        instruction_worksheet.write("L2", 61)
        instruction_worksheet.write(
            "L3",
            "This field should contain marks or grade of English subject",
            cell_format,
        )
        instruction_worksheet.write(
            "L4",
            'Only numbers and grades (a, a+, b, b+, c, c+, d, d+) are accepted ,symbols like "%" are not allowed',
            cell_format,
        )
        instruction_worksheet.write("L5", "Mandatory Field", mandatory_format)

        instruction_worksheet.write("M2", 61)
        instruction_worksheet.write(
            "M3",
            "This field should contain marks or grade of English subject",
            cell_format,
        )
        instruction_worksheet.write(
            "M4",
            'Only numbers and grades (a, a+, b, b+, c, c+, d, d+) are accepted ,symbols like "%" are not allowed',
            cell_format,
        )
        instruction_worksheet.write(
            "M5", "Not mandatory but advisable to have", cell_format
        )

        instruction_worksheet.write("N2", 61)
        instruction_worksheet.write("N3", "Enter marks or grades")
        instruction_worksheet.write(
            "N4",
            'Only numbers and grades (a, a+, b, b+, c, c+, d, d+) are accepted ,symbols like "%" are not allowed',
            cell_format,
        )
        instruction_worksheet.write(
            "N5", "Not mandatory but advisable to have", cell_format
        )

        # Instruction Description
        merge_format = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_size": 15,
                "font_color": "black",
            }
        )

        instruction_worksheet.merge_range(
            "A13:B13", "General Instructions:", merge_format
        )
        instruction_worksheet.write("A14", 1)
        instruction_worksheet.write(
            "B14", "Download this template and use the same to fill data", cell_format
        )
        instruction_worksheet.write("A15", 2)
        instruction_worksheet.write(
            "B15", "Do not upload your own Excel file", cell_format
        )
        instruction_worksheet.write("A16", 3)
        instruction_worksheet.write(
            "B16", "Data will be captured from Sheet 1 (Candidates)", cell_format
        )
        instruction_worksheet.write("A17", 4)
        instruction_worksheet.write(
            "B17", "Do not change the name of the sheet", cell_format
        )
        instruction_worksheet.write("A18", 5)
        instruction_worksheet.write(
            "B18",
            "If you are copying and pasting data from some other Excel, please ensure the format of this template is followed",
            mandatory_format,
        )
        instruction_worksheet.write("A19", 6)
        instruction_worksheet.write(
            "B19", "No rows or columns to be deleted or shifted", mandatory_format
        )

        instruction_worksheet.protect()

        workbook.close()

        # Set the buffer position to the beginning
        excel_buffer.seek(0)

        # Generate a response with the Excel file
        response = request.make_response(
            excel_buffer.getvalue(),
            headers=[
                (
                    "Content-Type",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ),
                (
                    "Content-Disposition",
                    "attachment; filename=candidate_format_file.xlsx",
                ),
            ],
        )

        # Clean up the buffer
        excel_buffer.close()

        return response

    def remove_after_dot_in_phone_number(self, phone_number):
        if "." in phone_number:
            return phone_number.split(".")[
                0
            ]  # Split the phone number by dot and return the first part
        else:
            return phone_number  # If there's

    @http.route(["/my/uploadgpcandidatedata"], type="http", auth="user", website=True)
    def UploadGPCandidateData(self, **kw):
        # import wdb; wdb.set_trace()
        user_id = request.env.user.id
        institute_id = (
            request.env["bes.institute"].sudo().search([("user_id", "=", user_id)]).id
        )

        batch_id = int(kw.get("upload_batch_id"))
        file_content = kw.get("fileUpload").read()
        filename = kw.get("fileUpload").filename

        # workbook = xlsxwriter.Workbook(BytesIO(file_content))
        workbook = xlrd.open_workbook(file_contents=file_content)
        # worksheet = workbook.sheet_by_index(0)
        state_values = {
            "JK": "Jammu and Kashmir",
            "MH": "Maharashtra",
            "AP": "Andhra Pradesh",
            "AR": "Arunachal Pradesh",
            "AS": "Assam",
            "BR": "Bihar",
            "CG": "Chhattisgarh",
            "GA": "Goa",
            "GJ": "Gujarat",
            "HR": "Haryana",
            "HP": "Himachal Pradesh",
            "JH": "Jharkhand",
            "KA": "Karnataka",
            "KL": "Kerala",
            "MP": "Madhya Pradesh",
            "MN": "Manipur",
            "ML": "Meghalaya",
            "MZ": "Mizoram",
            "NL": "Nagaland",
            "OR": "Orissa",
            "PB": "Punjab",
            "RJ": "Rajasthan",
            "SK": "Sikkim",
            "TN": "Tamil Nadu",
            "TG": "Telangana",
            "TR": "Tripura",
            "UP": "Uttar Pradesh",
            "UK": "Uttarakhand",
            "WB": "West Bengal",
            "AN": "Andaman and Nicobar Islands",
            "CH": "Chandigarh",
            "DH": "Dadra and Nagar Haveli and Daman and Diu",
            "LD": "Lakshadweep",
            "DL": "Delhi",
            "PY": "Puducherry",
        }

        # worksheet = workbook.get_worksheet_by_name('Candidates')
        worksheet = workbook.sheet_by_index(0)
        for row_num in range(1, worksheet.nrows):  # Assuming first row contains headers
            row = worksheet.row_values(row_num)
            # import wdb; wdb.set_trace()
            # try:
            try:
                indos_no = row[0].strip()

                # Check if Indos No is missing or empty
                if not indos_no:
                    raise ValidationError(
                        f"Missing Indos No in row {row_num + 1}, Please use the given format and check for unwanted spaces"
                    )

                # Validate the format
                if not re.fullmatch(r'^[0-9]{2}[a-zA-Z]{2}[0-9]{4}$', indos_no):
                    raise ValidationError(
                        f"Invalid Indos No format in row {row_num + 1}: '{indos_no}'. "
                        "Must be exactly 8 characters: 2 digits, 2 letters, 4 digits (no spaces). "
                        "Example: '12AB3456'"
                    )

                # Search for duplicates in three different models
                gp_candidate = (
                    request.env["gp.candidate"]
                    .sudo()
                    .search([("indos_no", "=", indos_no)], limit=1)
                )
                ccmc_candidate = (
                    request.env["ccmc.candidate"]
                    .sudo()
                    .search([("indos_no", "=", indos_no)], limit=1)
                )
                login = (
                    request.env["res.users"]
                    .sudo()
                    .search([("login", "=", indos_no)], limit=1)
                )

                # Check if any of the searches return a result (i.e., duplicate found)
                if gp_candidate or ccmc_candidate or login:
                    duplicate = f"Duplicate Indos No '{indos_no}' in row {row_num + 1}. This indos no is already exists."
                    raise ValidationError(duplicate)

            except ValidationError as e:
                # Reraise the validation error with a specific message
                raise e
            except Exception as e:
                # Handle unexpected errors with a generic error message
                raise ValidationError(
                    f"An unexpected error occurred in row {row_num + 1}: {str(e)}"
                )

            try:
                full_name = row[1]
            except:
                raise ValidationError(f"Missing Full Name in row {row_num + 1}")

            try:
                gender = "male" if row[2].lower() == "male" else "female"
            except:
                raise ValidationError(
                    f"Missing Gender in row {row_num + 1}, Please use the given format and check for unwanted spaces"
                )

            try:
                date_value = row[3]
                if isinstance(date_value, float):
                    date_value = xlrd.xldate_as_datetime(date_value, workbook.datemode)
                else:
                    date_value = datetime.strptime(date_value, "%d-%b-%Y")
                dob = date_value.date()
            except:
                raise ValidationError(
                    f"Invalid or Missing Date of Birth in row {row_num + 1}, Please use the given format and check for unwanted spaces"
                )

            try:
                street1 = row[4]
            except:
                raise ValidationError(f"Missing Street 1 in row {row_num + 1}")

            try:
                street2 = row[5]
            except:
                raise ValidationError(f"Missing Street 2 in row {row_num + 1}")

            try:
                dist_city = row[6]
            except:
                raise ValidationError(f"Missing District/City in row {row_num + 1}")

            try:
                state_value = row[7]
                state = (
                    request.env["res.country.state"]
                    .sudo()
                    .search(
                        [("country_id.code", "=", "IN"), ("code", "=", state_value)]
                    )
                    .id
                    if state_value
                    else False
                )
            except:
                raise ValidationError(
                    f"Missing State in row {row_num + 1}, Please use the given format and check for unwanted spaces"
                )

            try:
                pin_code = int(row[8])
            except:
                raise ValidationError(
                    f"Invalid or Missing Pin Code in row {row_num + 1}, Please use the given format and check for unwanted spaces, Pin Code must be 6 digits"
                )

            try:
                if row[9]:
                    mobile = self.remove_after_dot_in_phone_number(str(row[9]))
                else:
                    mobile = ""
            except:
                raise ValidationError(
                    f"Missing Mobile in row {row_num + 1}, Please use the given format and check for unwanted spaces"
                )

            try:
                email = row[10]
            except:
                raise ValidationError(
                    f"Missing Email in row {row_num + 1}, Please use the given format and check for unwanted spaces"
                )

            def convert_grade_to_percentage(grade):
                if grade.lower() == "a+":
                    return 90
                if grade.lower() == "a":
                    return 80
                if grade.lower() == "b+":
                    return 70
                if grade.lower() == "b":
                    return 60
                if grade.lower() == "c+":
                    return 50
                if grade.lower() == "c":
                    return 40
                if grade.lower() == "d+":
                    return 30
                if grade.lower() == "d":
                    return 20
                if grade.lower() == "e":
                    return 19
                return 0

            try:
                xth_std_eng = row[11]
                if type(xth_std_eng) in [int, float]:
                    data_xth_std_eng = float(xth_std_eng)
                elif type(xth_std_eng) == str:
                    data_xth_std_eng = convert_grade_to_percentage(xth_std_eng)
                else:
                    raise ValidationError(
                        f"Invalid marks/percentage for Xth Std in row {row_num + 1}"
                    )
            except:
                raise ValidationError(
                    f"Missing Xth Std in row {row_num + 1}, Please use the given format and check for unwanted spaces"
                )

            try:
                twelfth_std_eng = row[12]
                if type(twelfth_std_eng) in [int, float]:
                    data_twelfth_std_eng = float(twelfth_std_eng)
                elif type(twelfth_std_eng) == str:
                    data_twelfth_std_eng = convert_grade_to_percentage(twelfth_std_eng)
                else:
                    raise ValidationError(
                        f"Invalid marks/percentage for XIIth Std in row {row_num + 1}"
                    )
            except:
                raise ValidationError(
                    f"Missing XIIth Std in row {row_num + 1}, Please use the given format and check for unwanted spaces"
                )

            try:
                iti = row[13]
                if type(iti) in [int, float]:
                    data_iti = float(iti)
                elif type(iti) == str:
                    data_iti = convert_grade_to_percentage(iti)
                else:
                    raise ValidationError(
                        f"Invalid marks/percentage for ITI in row {row_num + 1}"
                    )
            except:
                raise ValidationError(
                    f"Missing ITI in row {row_num + 1}, Please use the given format and check for unwanted spaces"
                )

            try:
                if row[14] == "General":
                    candidate_st = "general"
                elif row[14] == "SC":
                    candidate_st = "sc"
                elif row[14] == "ST":
                    candidate_st = "st"
                elif row[14] == "OBC":
                    candidate_st = "obc"
                else:
                    raise ValidationError(
                        f"Please Mention if candidate belong to SC/ ST/ OBC or General in row {row_num + 1}"
                    )
            except:
                raise ValidationError(
                    f"Please Mention if candidate belong to SC/ ST/ OBC or General in row {row_num + 1}"
                )

            today = datetime.now().date()
            delta = today - dob
            age = delta.days // 365

            try:
                new_candidate = (
                    request.env["gp.candidate"]
                    .sudo()
                    .create(
                        {
                            "name": full_name,
                            "gender": gender,
                            "institute_id": institute_id,
                            "indos_no": indos_no,
                            "dob": dob,
                            "age": age,
                            "institute_batch_id": batch_id,
                            "street": street1,
                            "street2": street2,
                            "mobile": mobile,
                            "email": email,
                            "city": dist_city,
                            "state_id": state,
                            "zip": pin_code,
                            "tenth_percent": data_xth_std_eng,
                            "twelve_percent": data_twelfth_std_eng,
                            "iti_percent": data_iti,
                            "sc_st": candidate_st,
                        }
                    )
                )
            except Exception as e:
                raise ValidationError(
                    f"Error creating candidate, Incorrect format for row {row_num + 1}"
                )
            # except ValidationError as e:
            #     raise ValidationError(f"Incorrect Excel format please check {row_num + 1}")

            # workbook.close()
        batches = (
            request.env["institute.gp.batches"].sudo().search([("id", "=", batch_id)])
        )
        batches._compute_all_candidates_have_indos()
        return request.redirect("/my/gpbatch/candidates/" + str(batch_id))

    def convert_to_dd_mmm_yy(self, date_str):
        try:
            # Parse the input date string to datetime object
            date_obj = datetime.strptime(
                date_str, "%Y-%m-%d"
            )  # Assuming input format is YYYY-MM-DD
        except ValueError:
            try:
                date_obj = datetime.strptime(
                    date_str, "%m/%d/%Y"
                )  # Assuming input format is MM/DD/YYYY
            except ValueError:
                try:
                    date_obj = datetime.strptime(
                        date_str, "%d-%m-%Y"
                    )  # Assuming input format is DD-MM-YYYY
                except ValueError:
                    try:
                        date_obj = datetime.strptime(
                            date_str, "%d %b %Y"
                        )  # Assuming input format is DD MMM YYYY
                    except ValueError:
                        return "Invalid date format"

        # Format the date object to "dd/mmm/yy" format
        formatted_date = date_obj.strftime("%d/%b/%y").replace(
            "/", ""
        )  # Removing the slashes

        return formatted_date

    @http.route(["/my/uploadccmccandidatedata"], type="http", auth="user", website=True)
    def UploadCCMCCandidateData(self, **kw):
        user_id = request.env.user.id
        institute_id = (
            request.env["bes.institute"].sudo().search([("user_id", "=", user_id)]).id
        )

        batch_id = int(kw.get("batch_ccmc_id"))

        # import wdb; wdb.set_trace()

        file_content = kw.get("ccmcfileUpload").read()
        filename = kw.get("ccmcfileUpload").filename

        # workbook = xlsxwriter.Workbook(BytesIO(file_content))
        workbook = xlrd.open_workbook(file_contents=file_content)
        # worksheet = workbook.sheet_by_index(0)
        state_values = {
            "MH": "Maharashtra",
            "AP": "Andhra Pradesh",
            "AR": "Arunachal Pradesh",
            "AS": "Assam",
            "BR": "Bihar",
            "CT": "Chhattisgarh",
            "GA": "Goa",
            "GJ": "Gujarat",
            "HR": "Haryana",
            "HP": "Himachal Pradesh",
            "JH": "Jharkhand",
            "KA": "Karnataka",
            "KL": "Kerala",
            "MP": "Madhya Pradesh",
            "MN": "Manipur",
            "ML": "Meghalaya",
            "MZ": "Mizoram",
            "NL": "Nagaland",
            "OR": "Orissa",
            "PB": "Punjab",
            "RJ": "Rajasthan",
            "SK": "Sikkim",
            "TN": "Tamil Nadu",
            "TG": "Telangana",
            "TR": "Tripura",
            "UP": "Uttar Pradesh",
            "UK": "Uttarakhand",
            "WB": "West Bengal",
            "AN": "Andaman and Nicobar Islands",
            "CH": "Chandigarh",
            "DH": "Dadra and Nagar Haveli and Daman and Diu",
            "LD": "Lakshadweep",
            "DL": "Delhi",
            "PY": "Puducherry",
        }
        # worksheet = workbook.get_worksheet_by_name('Candidates')
        worksheet = workbook.sheet_by_index(0)

        for row_num in range(1, worksheet.nrows):  # Assuming first row contains headers
            row = worksheet.row_values(row_num)

            # import wdb; wdb.set_trace()
            # try:
            try:
                indos_no = row[0].strip()

                # Check if Indos No is missing or empty
                if not indos_no:
                    raise ValidationError(
                        f"Missing Indos No in row {row_num + 1}, Please use the given format and check for unwanted spaces"
                    )
                # Validate the format
                if not re.fullmatch(r'^[0-9]{2}[a-zA-Z]{2}[0-9]{4}$', indos_no):
                    raise ValidationError(
                        f"Invalid Indos No format in row {row_num + 1}: '{indos_no}'. "
                        "Must be exactly 8 characters: 2 digits, 2 letters, 4 digits (no spaces). "
                        "Example: '12AB3456'"
                    )

                # Search for duplicates in three different models
                gp_candidate = (
                    request.env["gp.candidate"]
                    .sudo()
                    .search([("indos_no", "=", indos_no)], limit=1)
                )
                ccmc_candidate = (
                    request.env["ccmc.candidate"]
                    .sudo()
                    .search([("indos_no", "=", indos_no)], limit=1)
                )
                login = (
                    request.env["res.users"]
                    .sudo()
                    .search([("login", "=", indos_no)], limit=1)
                )

                # Check if any of the searches return a result (i.e., duplicate found)
                if gp_candidate or ccmc_candidate or login:
                    duplicate = f"Duplicate Indos No '{indos_no}' in row {row_num + 1}. This indos no is already exists."
                    raise ValidationError(duplicate)

            except ValidationError as e:
                # Reraise the validation error with a specific message
                raise e
            except Exception as e:
                # Handle unexpected errors with a generic error message
                raise ValidationError(
                    f"An unexpected error occurred in row {row_num + 1}: {str(e)}"
                )

            try:
                full_name = row[1]
            except:
                raise ValidationError(f"Missing Full Name in row {row_num + 1}")

            try:
                gender = "male" if row[2].lower() == "male" else "female"
            except:
                raise ValidationError(
                    f"Missing Gender in row {row_num + 1}, Please use the given format and check for unwanted spaces"
                )

            try:
                date_value = row[3]
                if isinstance(date_value, float):
                    date_value = xlrd.xldate_as_datetime(date_value, workbook.datemode)
                else:
                    date_value = datetime.strptime(date_value, "%d-%b-%Y")
                dob = date_value.date()
            except:
                raise ValidationError(
                    f"Invalid or Missing Date of Birth in row {row_num + 1}, Please use the given format and check for unwanted spaces"
                )

            try:
                street1 = row[4]
            except:
                raise ValidationError(f"Missing Street 1 in row {row_num + 1}")

            try:
                street2 = row[5]
            except:
                raise ValidationError(f"Missing Street 2 in row {row_num + 1}")

            try:
                dist_city = row[6]
            except:
                raise ValidationError(f"Missing District/City in row {row_num + 1}")

            try:
                state_value = row[7]
                state = (
                    request.env["res.country.state"]
                    .sudo()
                    .search(
                        [("country_id.code", "=", "IN"), ("code", "=", state_value)]
                    )
                    .id
                )
                # if state_value else False
            except:
                raise ValidationError(
                    f"Missing State in row {row_num + 1}, Please use the given format and check for unwanted spaces"
                )

            try:
                pin_code = int(row[8])
            except:
                raise ValidationError(
                    f"Invalid or Missing Pin Code in row {row_num + 1}, Please use the given format and check for unwanted spaces, Pin Code must be 6 digits"
                )

            try:
                if row[9]:
                    mobile = self.remove_after_dot_in_phone_number(str(row[9]))
                else:
                    mobile = ""
            except:
                raise ValidationError(
                    f"Missing Mobile in row {row_num + 1}, Please use the given format and check for unwanted spaces"
                )

            try:
                email = row[10]
            except:
                raise ValidationError(
                    f"Missing Email in row {row_num + 1}, Please use the given format and check for unwanted spaces"
                )

            def convert_grade_to_percentage(grade):
                if grade.lower() == "a+":
                    return 90
                if grade.lower() == "a":
                    return 80
                if grade.lower() == "b+":
                    return 70
                if grade.lower() == "b":
                    return 60
                if grade.lower() == "c+":
                    return 50
                if grade.lower() == "c":
                    return 40
                if grade.lower() == "d+":
                    return 30
                if grade.lower() == "d":
                    return 20
                if grade.lower() == "e":
                    return 19
                return 0

            try:
                xth_std_eng = row[11]
                if type(xth_std_eng) in [int, float]:
                    data_xth_std_eng = float(xth_std_eng)
                elif type(xth_std_eng) == str:
                    data_xth_std_eng = convert_grade_to_percentage(xth_std_eng)
                else:
                    raise ValidationError(
                        f"Invalid marks/percentage for Xth Std in row {row_num + 1}"
                    )
            except:
                raise ValidationError(
                    f"Missing Xth Std in row {row_num + 1}, Please use the given format and check for unwanted spaces"
                )

            try:
                twelfth_std_eng = row[12]
                if type(twelfth_std_eng) in [int, float]:
                    data_twelfth_std_eng = float(twelfth_std_eng)
                elif type(twelfth_std_eng) == str:
                    data_twelfth_std_eng = convert_grade_to_percentage(twelfth_std_eng)
                else:
                    raise ValidationError(
                        f"Invalid marks/percentage for XIIth Std in row {row_num + 1}"
                    )
            except:
                raise ValidationError(
                    f"Missing XIIth Std in row {row_num + 1}, Please use the given format and check for unwanted spaces"
                )

            try:
                iti = row[13]
                if type(iti) in [int, float]:
                    data_iti = float(iti)
                elif type(iti) == str:
                    data_iti = convert_grade_to_percentage(iti)
                else:
                    raise ValidationError(
                        f"Invalid marks/percentage for ITI in row {row_num + 1}"
                    )
            except:
                raise ValidationError(
                    f"Missing ITI in row {row_num + 1}, Please use the given format and check for unwanted spaces"
                )

            try:
                if row[14] == "General":
                    candidate_st = "general"
                elif row[14] == "SC":
                    candidate_st = "sc"
                elif row[14] == "ST":
                    candidate_st = "st"
                elif row[14] == "OBC":
                    candidate_st = "obc"
                else:
                    raise ValidationError(
                        f"Please Mention if candidate belong to SC/ ST/ OBC or General in row {row_num + 1}"
                    )
            except:
                raise ValidationError(
                    f"Please Mention if candidate belong to SC/ ST/ OBC or General in row {row_num + 1}"
                )

            today = datetime.now().date()
            delta = today - dob
            age = delta.days // 365

            try:
                new_candidate = (
                    request.env["ccmc.candidate"]
                    .sudo()
                    .create(
                        {
                            "name": full_name,
                            "gender": gender,
                            "institute_id": institute_id,
                            "indos_no": indos_no,
                            "dob": dob,
                            "age": age,
                            "institute_batch_id": batch_id,
                            "street": street1,
                            "street2": street2,
                            "mobile": mobile,
                            "email": email,
                            "city": dist_city,
                            "state_id": state,
                            "zip": pin_code,
                            "tenth_percent": data_xth_std_eng,
                            "twelve_percent": data_twelfth_std_eng,
                            "iti_percent": data_iti,
                            "sc_st": candidate_st,
                        }
                    )
                )
            except:
                raise ValidationError(
                    f"Error creating candidate, Incorrect format for row {row_num + 1}"
                )

        # workbook.close()
        batches = (
            request.env["institute.ccmc.batches"].sudo().search([("id", "=", batch_id)])
        )
        batches._compute_all_candidates_have_indos()
        return request.redirect("/my/ccmcbatch/candidates/" + str(batch_id))

    @http.route(
        ["/my/gp/download_dgs_capacity/<int:cousre_id>/<int:institute_id>"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def DownloadsGgsCapacityCard(self, cousre_id, institute_id, **kw):
        # import wdb; wdb.set_trace()

        # batch = request.env['institute.gp.batches'].sudo().search([('id','=',batch_id)])

        cousre = request.env["course.master"].sudo().search([("id", "=", cousre_id)])
        institute = (
            request.env["bes.institute"].sudo().search([("id", "=", institute_id)])
        )

        # import wdb; wdb.set_trace()

        # institute.courses[0].course.name
        if institute.courses[0].dgs_document:
            pdf_data = base64.b64decode(
                institute.courses[0].dgs_document
            )  # Decoding file data
            file_name = institute.courses[0].dgs_document_name + ".pdf"

            headers = [
                ("Content-Type", "application/octet-stream"),
                ("Content-Disposition", f'attachment; filename="{file_name}"'),
            ]
            return request.make_response(pdf_data, headers)
        else:
            return request.not_found()

    @http.route(
        ["/my/ccmc/download_dgs_capacity/<int:cousre_id>/<int:institute_id>"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def DownloadsGgsCapacity(self, cousre_id, institute_id, **kw):

        cousre = request.env["course.master"].sudo().search([("id", "=", cousre_id)])
        institute = (
            request.env["bes.institute"].sudo().search([("id", "=", institute_id)])
        )

        # import wdb; wdb.set_trace()
        # institute.courses[0].course.name
        if institute.courses[1].dgs_document:
            pdf_data = base64.b64decode(
                institute.courses[1].dgs_document
            )  # Decoding file data
            file_name = institute.courses[1].dgs_document_name + ".pdf"

            headers = [
                ("Content-Type", "application/octet-stream"),
                ("Content-Disposition", f'attachment; filename="{file_name}"'),
            ]
            return request.make_response(pdf_data, headers)
        else:
            return request.not_found()

    @http.route(
        ["/my/updatefacultydetails"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def UpdateFacultyDetails(self, **kw):

        # import wdb; wdb.set_trace()

        faculties = (
            request.env["institute.faculty"]
            .sudo()
            .search([("id", "=", kw.get("faculty_id"))])
        )
        # import wdb; wdb.set_trace()
        if request.httprequest.method == "POST":

            faculty_details = {
                "faculty_name": kw.get("full_name"),
                "dob": kw.get("dob"),
                "designation": kw.get("designation"),
                "qualification": kw.get("qualification"),
                "contract_terms": kw.get("contract"),
                "courses_taught": kw.get("courses_taught"),
            }

            for key, value in faculty_details.items():
                if value:
                    faculties.write({key: value})

            # return request.render("bes.gp_faculty_profile_view")
            return request.redirect(
                "/my/gpbatch/faculties/profile/"
                + str(kw.get("batch_id") + "/" + str(kw.get("faculty_id")))
            )

        # batches = request.env["institute.gp.batches"].sudo().search([('id', '=', batch_id)])
        vals = {}
        return request.render("bes.gp_faculty_profile_view", vals)

    @http.route(
        ["/my/ccmcupdatefacultydetails"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def UpdateCCMCFacultyDetails(self, **kw):

        # import wdb; wdb.set_trace()

        faculties = (
            request.env["institute.faculty"]
            .sudo()
            .search([("id", "=", kw.get("faculty_id"))])
        )
        # import wdb; wdb.set_trace()
        if request.httprequest.method == "POST":

            faculty_details = {
                "faculty_name": kw.get("full_name"),
                "dob": kw.get("dob"),
                "designation": kw.get("designation"),
                "qualification": kw.get("qualification"),
                "contract_terms": kw.get("contract"),
                "courses_taught": kw.get("courses_taught"),
            }

            for key, value in faculty_details.items():
                if value:
                    faculties.write({key: value})

            # return request.render("bes.gp_faculty_profile_view")
            return request.redirect(
                "/my/ccmcbatch/faculties/profile/"
                + str(kw.get("batch_id") + "/" + str(kw.get("faculty_id")))
            )

        # batches = request.env["institute.gp.batches"].sudo().search([('id', '=', batch_id)])
        vals = {}
        return request.render("bes.ccmc_faculty_profile_view", vals)

    @http.route(["/my/deletefaculty"], type="http", auth="user", website=True)
    def DeleteFaculty(self, **kw):

        user_id = request.env.user.id
        # import wdb; wdb.set_trace();

        batch = (
            request.env["institute.gp.batches"]
            .sudo()
            .search([("id", "=", kw.get("candidate_batch_id"))])
        )
        candidate_user_id = (
            request.env["gp.candidate"]
            .sudo()
            .search([("id", "=", kw.get("candidate_id"))])
            .user_id
        )
        if not candidate_user_id:
            request.env["gp.candidate"].sudo().search(
                [("id", "=", kw.get("candidate_id"))]
            ).unlink()

            return request.redirect("/my/gpbatch/candidates/" + str(batch.id))
        else:
            raise ValidationError("Not Allowed")

    @http.route(["/my/upload_instructions"], type="http", auth="user", website=True)
    def UploadInstruction(self, **kw):
        excel_buffer = io.BytesIO()

        # Create a new Excel workbook and add a worksheet
        workbook = xlsxwriter.Workbook(excel_buffer)
        instruction_worksheet = workbook.add_worksheet("Uploading Instructions")

        unlocked = workbook.add_format({"locked": False})

        instruction_worksheet.set_column("A:P", 20, unlocked)
        # instruction_worksheet.protect()
        date_format = workbook.add_format({"num_format": "dd-mmm-yy", "locked": False})

        instruction_worksheet.write_comment(
            "M2",
            'In the columns Xth, XIIth, ITI , Please enter only number or grade (a,"a+,b,b+,c,c+,d,d+)',
        )

        header_format = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_color": "white",
                "bg_color": "#336699",  # Blue color for the background
                "locked": True,
            }
        )

        header = [
            "Sr No",
            "INDOS NO",
            "NAME",
            "DOB",
            "STREET",
            "STREET2",
            "CITY",
            "ZIP",
            "STATE",
            "PHONE",
            "MOBILE",
            "EMAIL",
            "Xth",
            "XIIth",
            "ITI",
            "SC/ST/OBC",
        ]
        for col, value in enumerate(header):
            instruction_worksheet.write(0, col, value, header_format)

        # Set date format for DOB column
        instruction_worksheet.set_column("C:C", 20, date_format)

        cell_format = workbook.add_format()
        cell_format.set_text_wrap()

        mandatory_format = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_color": "red",
                "text_wrap": True,
            }
        )

        instruction_worksheet.write("A3", "1) Description")
        instruction_worksheet.write("A4", "2) Format")
        instruction_worksheet.write("A5", "3) Mandatory")

        instruction_worksheet.write("B2", "23GM1234")
        instruction_worksheet.write(
            "B3",
            "This field contains the student's Indos number to be used as the student's login in the future",
            cell_format,
        )
        instruction_worksheet.write(
            "B4",
            "The format should be adhered to; wrong Indos or duplicate Indos numbers should be avoided at all costs",
            cell_format,
        )
        instruction_worksheet.write("B5", "Mandatory Field", mandatory_format)

        instruction_worksheet.write("C2", "Lokesh Dalvi")
        instruction_worksheet.write("C3", "Name As per Indos Number", cell_format)
        instruction_worksheet.write(
            "C4",
            "The format of the name to be used should be as needed in certificates and future records",
            cell_format,
        )
        instruction_worksheet.write("C5", "Mandatory Field", mandatory_format)

        instruction_worksheet.write("D2", "14-Apr-02")
        instruction_worksheet.write(
            "D3",
            "This is the date of birth field for students; it should be as per records",
            cell_format,
        )
        instruction_worksheet.write(
            "D4",
            'The date format to be followed strictly is DD-MMM-YY; do not use "/" or any other special character except as per the format',
            cell_format,
        )
        instruction_worksheet.write("D5", "Mandatory Field", mandatory_format)

        instruction_worksheet.write("E2", "Street1")
        instruction_worksheet.write("E3", "This is address line 1")
        instruction_worksheet.write(
            "E4", "No format is needed; it can be blank as well", cell_format
        )
        instruction_worksheet.write(
            "E5", "Not mandatory but advisable to have", cell_format
        )

        instruction_worksheet.write("F2", "Street2")
        instruction_worksheet.write("F3", "This is address line 2")
        instruction_worksheet.write(
            "F4", "No format is needed; it can be blank as well", cell_format
        )
        instruction_worksheet.write(
            "F5", "Not mandatory but advisable to have", cell_format
        )

        instruction_worksheet.write("G2", "City")
        instruction_worksheet.write("G3", "City name as per address", cell_format)
        instruction_worksheet.write("G4", "No format")
        instruction_worksheet.write("G5", "Mandatory Field", mandatory_format)

        instruction_worksheet.write("H2", 123456)
        instruction_worksheet.write(
            "H3", "This field is the PIN code of the candidate's address", cell_format
        )
        instruction_worksheet.write(
            "H4",
            "The PIN code should be exactly 6 digits; only numbers are accepted",
            cell_format,
        )
        instruction_worksheet.write("H5", "Mandatory Field", mandatory_format)

        instruction_worksheet.write("I2", "MH")
        instruction_worksheet.write(
            "I3",
            "This field is the state code to be selected from dropdown only",
            cell_format,
        )
        instruction_worksheet.write(
            "I4",
            'Use only the drop-downs to select the state code; please do not enter data manually in this field. Refer to the worksheet "State" for the list',
            cell_format,
        )
        instruction_worksheet.write("I5", "Mandatory Field", mandatory_format)

        instruction_worksheet.write("J2", 12345678)
        instruction_worksheet.write(
            "J3", "This field is the phone number of the candidate", cell_format
        )
        instruction_worksheet.write(
            "J4", "Only numbers accepted; should be 8 digits", cell_format
        )
        instruction_worksheet.write(
            "J5", "Not mandatory but advisable to have", cell_format
        )

        instruction_worksheet.write("K2", 1234567890)
        instruction_worksheet.write(
            "K3", "This field is the mobile number of the candidate", cell_format
        )
        instruction_worksheet.write(
            "K4", "Only numbers accepted; should be 10 digits", cell_format
        )
        instruction_worksheet.write(
            "K5", "Not mandatory but advisable to have", cell_format
        )

        instruction_worksheet.write("L2", "abc@gmail.com")
        instruction_worksheet.write(
            "L3", "This field is the email ID of the candidate", cell_format
        )
        instruction_worksheet.write("L4", 'Must contain a "@" and ".com"', cell_format)
        instruction_worksheet.write("L5", "Mandatory Field", mandatory_format)

        instruction_worksheet.write("M2", 61)
        instruction_worksheet.write(
            "M3",
            "This field should contain marks or grade of English subject",
            cell_format,
        )
        instruction_worksheet.write(
            "M4",
            'Only numbers and grades (a, a+, b, b+, c, c+, d, d+) are accepted ,symbols like "%" are not allowed',
            cell_format,
        )
        instruction_worksheet.write("M5", "Mandatory Field", mandatory_format)

        instruction_worksheet.write("N2", 61)
        instruction_worksheet.write(
            "N3",
            "This field should contain marks or grade of English subject",
            cell_format,
        )
        instruction_worksheet.write(
            "N4",
            'Only numbers and grades (a, a+, b, b+, c, c+, d, d+) are accepted ,symbols like "%" are not allowed',
            cell_format,
        )
        instruction_worksheet.write(
            "N5", "Not mandatory but advisable to have", cell_format
        )

        instruction_worksheet.write("O2", 61)
        instruction_worksheet.write("O3", "Enter marks or grades")
        instruction_worksheet.write(
            "O4",
            'Only numbers and grades (a, a+, b, b+, c, c+, d, d+) are accepted ,symbols like "%" are not allowed',
            cell_format,
        )
        instruction_worksheet.write(
            "O5", "Not mandatory but advisable to have", cell_format
        )

        instruction_worksheet.write("P2", "Yes")
        instruction_worksheet.write(
            "P3",
            "This field is to mention if the candidate is from SC/ST/OBC",
            cell_format,
        )
        instruction_worksheet.write(
            "P4",
            "Use the dropdown to select yes or no; do not enter anything else in this field",
            cell_format,
        )
        instruction_worksheet.write("P5", "Mandatory Field", mandatory_format)

        # Instruction Description
        merge_format = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_size": 15,
                "font_color": "black",
            }
        )

        instruction_worksheet.merge_range(
            "A13:B13", "General Instructions:", merge_format
        )
        instruction_worksheet.write("A14", 1)
        instruction_worksheet.write(
            "B14", "Download this template and use the same to fill data", cell_format
        )
        instruction_worksheet.write("A15", 2)
        instruction_worksheet.write(
            "B15", "Do not upload your own Excel file", cell_format
        )
        instruction_worksheet.write("A16", 3)
        instruction_worksheet.write(
            "B16", "Data will be captured from Sheet 1 (Candidates)", cell_format
        )
        instruction_worksheet.write("A17", 4)
        instruction_worksheet.write(
            "B17", "Do not change the name of the sheet", cell_format
        )
        instruction_worksheet.write("A18", 5)
        instruction_worksheet.write(
            "B18",
            "If you are copying and pasting data from some other Excel, please ensure the format of this template is followed",
            mandatory_format,
        )
        instruction_worksheet.write("A19", 6)
        instruction_worksheet.write(
            "B19", "No rows or columns to be deleted or shifted", mandatory_format
        )

        instruction_worksheet.protect()

        workbook.close()

        # Set the buffer position to the beginning
        excel_buffer.seek(0)

        # Generate a response with the Excel file
        response = request.make_response(
            excel_buffer.getvalue(),
            headers=[
                (
                    "Content-Type",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ),
                (
                    "Content-Disposition",
                    "attachment; filename=candidate_uploading_instructions.xlsx",
                ),
            ],
        )

        # Clean up the buffer
        excel_buffer.close()

        return response

    # method=["POST", "GET"]

    @http.route(
        ["/my/update/inscap"], method=["POST"], type="http", auth="user", website=True
    )
    def UpdateInstituteCapacits(self, **kw):
        batch_per_year = kw.get("batch_per_year")
        candidate_per_batch = kw.get("candidate_per_batch")
        file_content = kw.get("approvaldocument").read()

        filename = kw.get("approvaldocument").filename

        # approvaldocument = kw.get('approvaldocument')
        course_id = kw.get("course_id")
        # import wdb; wdb.set_trace();
        course = (
            request.env["institute.courses"].sudo().search([("id", "=", course_id)])
        )
        course.write(
            {
                "batcher_per_year": batch_per_year,
                "intake_capacity": candidate_per_batch,
                "batcher_per_year": batch_per_year,
                "dgs_document_name": filename,
                "dgs_document": base64.b64encode(file_content),
            }
        )

        return request.redirect("/my/editinstitute")

    @http.route(
        ["/my/download/<int:course_id>"], type="http", auth="user", website=True
    )
    def download_dgs_document(self, course_id):
        # import wdb; wdb.set_trace();
        course = request.env["institute.courses"].sudo().browse(course_id)
        if course:
            # Retrieve the file content
            content = base64.b64decode(course.dgs_document_content)
            if content:
                # Return the file as attachment
                headers = [
                    ("Content-Type", "application/octet-stream"),
                    (
                        "Content-Disposition",
                        'attachment; filename="%s"' % course.dgs_document,
                    ),
                ]
                return request.make_response(content, headers=headers)
        return request.not_found()

    # New Code STCW Bulk Uploading
    @http.route(
        "/my/gpbatch/candidates/stcw_format_download/<int:batch_id>",
        type="http",
        auth="user",
        website=True,
    )
    def generate_gp_candidate_stcw_format(self, batch_id, **kw):
        excel_buffer = io.BytesIO()

        # Create a new Excel workbook and add a worksheet
        workbook = xlsxwriter.Workbook(excel_buffer)
        candidate_stcw_worksheet = workbook.add_worksheet("STCW Details")

        locked = workbook.add_format({"locked": True})
        unlocked = workbook.add_format({"locked": False})
        candidate_stcw_worksheet.set_column("A:XDF", None, unlocked)

        candidate_stcw_worksheet.set_column("A:A", 35, locked)  # Name
        candidate_stcw_worksheet.set_column("B:B", 15, locked)  # indos
        candidate_stcw_worksheet.set_column("C:C", 10, unlocked)  # cousre
        candidate_stcw_worksheet.set_column("D:D", 35, unlocked)  # insitute_name
        candidate_stcw_worksheet.set_column("E:E", 15, unlocked)  # mti_no
        # Set the column format for certificate_no to number
        number_format = workbook.add_format({"num_format": "@", "locked": False})

        # Set the column width and format for certificate_no
        candidate_stcw_worksheet.set_column("F:F", 35, number_format)  # certificate_no

        candidate_stcw_worksheet.set_column("G:G", 20, unlocked)  # cousre_start_date
        candidate_stcw_worksheet.set_column("H:H", 20, unlocked)  # cousre_end_date

        candidate_stcw_worksheet.protect()
        date_format = workbook.add_format(
            {"num_format": "dd-mmm-yyyy", "locked": False}
        )

        header_format = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_color": "white",
                "bg_color": "#336699",  # Blue color for the background
                "locked": True,
            }
        )

        header = [
            "Name of Candidate",
            "INDOS NO",
            "COURSE",
            "INSTITUTE NAME",
            "MTI NO",
            "CERTIFICATE NO",
            "COURSE START DATE",
            "COURSE END DATE",
        ]
        for col, value in enumerate(header):
            candidate_stcw_worksheet.write(0, col, value, header_format)

        # Auto fill indos no
        batch = (
            request.env["institute.gp.batches"].sudo().search([("id", "=", batch_id)])
        )
        # import wdb; wdb.set_trace()
        candidates = (
            request.env["gp.candidate"]
            .sudo()
            .search(
                [
                    ("institute_batch_id", "=", batch.id),
                    ("withdrawn_state", "!=", "yes"),
                    ("stcw_criteria","=", "pending"),
                ]
            )
        )

        # Extract valid indos numbers and names from candidates
        indos = [
            candidate.indos_no for candidate in candidates if candidate.indos_no
        ]  # Only include non-empty indos_no
        names = [
            candidate.name for candidate in candidates if candidate.name
        ]  # Only include non-empty Name strs

        # Write the names and indos numbers to the worksheet
        for i, (name, indos_no) in enumerate(zip(names, indos)):
            # Calculate the starting row for the current candidate
            start_row = i * 2 + 2  # Each candidate occupies two rows

            # Write the name in column A, indos number in column B (both rows)
            candidate_stcw_worksheet.write(f"A{start_row}", name, locked)
            candidate_stcw_worksheet.write(f"A{start_row + 1}", name, locked)

            candidate_stcw_worksheet.write(f"B{start_row}", indos_no, locked)
            candidate_stcw_worksheet.write(f"B{start_row + 1}", indos_no, locked)

        # Set date format for DOB column
        candidate_stcw_worksheet.set_column("G:G", 20, date_format)
        candidate_stcw_worksheet.set_column("H:H", 20, date_format)

        cousre_values = ["BST", "STSDSD"]

        candidate_stcw_worksheet.data_validation(
            "C2:C1048576", {"validate": "list", "source": cousre_values}
        )

        instruction_worksheet = workbook.add_worksheet("Instructions")

        instruction_worksheet.set_column("A:P", 20, locked)

        # instruction_worksheet.protect()
        date_format = workbook.add_format(
            {"num_format": "dd-mmm-yyyy", "locked": False}
        )
        header_format = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_color": "white",
                "bg_color": "#336699",  # Blue color for the background
                "locked": True,
            }
        )

        header = [
            "Sr No.",
            "Name of Candidate",
            "INDOS NO",
            "COURSE",
            "INSTITUTE NAME",
            "MTI NO",
            "CERTIFICATE NO",
            "COURSE START DATE",
            "COURSE END DATE",
        ]
        for col, value in enumerate(header):
            instruction_worksheet.write(0, col, value, header_format)

        # Set date format for DOB column
        instruction_worksheet.set_column("F:F", 20, date_format)
        instruction_worksheet.set_column("G:G", 20, date_format)

        cell_format = workbook.add_format()
        cell_format.set_text_wrap()

        mandatory_format = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_color": "red",
                "text_wrap": True,
            }
        )

        # Instruction Description
        merge_format = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_size": 15,
                "font_color": "black",
            }
        )

        # Define a format for instructions
        instruction_format = workbook.add_format(
            {
                "bold": True,
                "align": "left",
                "valign": "top",
                "text_wrap": True,
                "font_size": 12,
            }
        )

        cell_format = workbook.add_format()
        cell_format.set_text_wrap()

        # Header section with sample data
        instruction_worksheet.write("A3", "1) Description")
        instruction_worksheet.write("A4", "2) Format")
        instruction_worksheet.write("A5", "3) Mandatory")

        # Populate instruction details for the STCW table
        # Example of Name
        instruction_worksheet.write("B2", "Candidate Name")
        instruction_worksheet.write(
            "B3",
            "This field contains the student's INDOS number, which is required for identification in the STCW system",
            cell_format,
        )
        instruction_worksheet.write(
            "B4",
            "INDOS number must follow the correct format. Avoid duplicates or incorrect INDOS numbers",
            cell_format,
        )
        instruction_worksheet.write("B5", "Mandatory Field", mandatory_format)

        # Example of INDOS NO
        instruction_worksheet.write("C2", "23GM1234")
        instruction_worksheet.write(
            "C3",
            "This field contains the student's INDOS number, which is required for identification in the STCW system",
            cell_format,
        )
        instruction_worksheet.write(
            "C4",
            "INDOS number must follow the correct format. Avoid duplicates or incorrect INDOS numbers",
            cell_format,
        )
        instruction_worksheet.write("C5", "Mandatory Field", mandatory_format)

        # Example of Course Name
        instruction_worksheet.write("D2", "BST")
        instruction_worksheet.write(
            "D3",
            "This is the name of the STCW course completed by the candidate",
            cell_format,
        )
        instruction_worksheet.write(
            "D4",
            "Ensure the course name follows the STCW standard abbreviations (e.g., BST, STSDSD)",
            cell_format,
        )
        instruction_worksheet.write("D5", "Mandatory Field", mandatory_format)

        # Example of Institute Name
        instruction_worksheet.write("E2", "Oceanic Maritime")
        instruction_worksheet.write(
            "E3",
            "Name of the maritime training institute where the course was completed",
            cell_format,
        )
        instruction_worksheet.write(
            "E4", "Ensure correct and complete institute name", cell_format
        )
        instruction_worksheet.write("E5", "Mandatory Field", mandatory_format)

        # Example of MTI NO
        instruction_worksheet.write("F2", "410210")
        instruction_worksheet.write(
            "F3",
            "Maritime Training Institute (MTI) number of the training center",
            cell_format,
        )
        instruction_worksheet.write(
            "F4", "MTI number should be correctly entered", cell_format
        )
        instruction_worksheet.write("F5", "Mandatory Field", mandatory_format)

        # Example of Certificate Number
        instruction_worksheet.write("G2", "20704561012400415")
        instruction_worksheet.write(
            "G3", "Unique certificate number issued for the course", cell_format
        )
        instruction_worksheet.write(
            "G4", "Certificate number should be correctly entered", cell_format
        )
        instruction_worksheet.write("G5", "Mandatory Field", mandatory_format)

        # Example of Course Start Date
        instruction_worksheet.write("H2", "14-Apr-2002")
        instruction_worksheet.write("H3", "Date when the course started", cell_format)
        instruction_worksheet.write(
            "H4", "Date format: DD-MMM-YYYY (e.g., 14-Apr-2002)", cell_format
        )
        instruction_worksheet.write("H5", "Mandatory Field", mandatory_format)

        # Example of Course End Date
        instruction_worksheet.write("I2", "14-Apr-2002")
        instruction_worksheet.write("I3", "Date when the course ended", cell_format)
        instruction_worksheet.write(
            "I4", "Date format: DD-MMM-YYYY (e.g., 14-Apr-2002)", cell_format
        )
        instruction_worksheet.write("I5", "Mandatory Field", mandatory_format)

        instruction_worksheet.protect()

        workbook.close()

        # Set the buffer position to the beginning
        excel_buffer.seek(0)

        # Generate a response with the Excel file
        response = request.make_response(
            excel_buffer.getvalue(),
            headers=[
                (
                    "Content-Type",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ),
                (
                    "Content-Disposition",
                    "attachment; filename=candidate_STCW_format_file.xlsx",
                ),
            ],
        )

        # Clean up the buffer
        excel_buffer.close()

        return response

    @http.route(
        ["/my/uploadgpcandidatestcwdata"], type="http", auth="user", website=True
    )
    def UploadGPCandidateSTCWData(self, **kw):
        user_id = request.env.user.id
        institute_id = (
            request.env["bes.institute"].sudo().search([("user_id", "=", user_id)]).id
        )

        batch_id = int(kw.get("batch_id"))

        file_content = kw.get("fileUpload").read()
        filename = kw.get("fileUpload").filename

        # Open the uploaded workbook
        workbook = xlrd.open_workbook(file_contents=file_content)
        worksheet = workbook.sheet_by_index(0)

        # Iterate through the rows of the worksheet, starting from the second row
        for row_num in range(1, worksheet.nrows):  # Assuming first row contains headers
            row = worksheet.row_values(row_num)

            # Extracting data from the row
            indos_no = row[1]  # Assuming INDOS NO is in the second column
            course_name = row[2].lower()  # Assuming COURSE is in the third column
            institute_name = row[3]  # Assuming INSTITUTE NAME is in the fourth column

            # Initialize variables
            mti_no = None
            certificate_no = None
            course_start_date = None
            course_end_date = None

            # Check if MTI NO is present and convert to int
            if row[4]:  # If there's a value in the fifth column
                try:
                    # Convert to string, remove unwanted spaces
                    value = str(row[4]).strip()

                    # Check if it's a float ending in .0 and convert to int
                    if value.endswith(".0"):
                        mti_no = int(float(value))
                    else:
                        mti_no = int(value)
                except ValueError:
                    raise ValidationError(
                        f"Incorrect MTI NO in row {row_num + 1}, Please enter only numbers and check for unwanted spaces"
                    )

            # Check if CERTIFICATE NO is present and convert to int
            if row[5]:  # If there's a value in the sixth column
                try:
                    value = str(row[5]).strip()

                    if value.endswith(".0"):
                        certificate_no = int(float(value))
                    else:
                        certificate_no = int(value)
                except ValueError:
                    raise ValidationError(
                        f"Incorrect Certificate NO in row {row_num + 1}, Please enter only numbers and check for unwanted spaces"
                    )

            # Check if COURSE START DATE is present
            if row[6]:  # If there's a value in the seventh column
                try:
                    # If row[6] is a float, treat it as an Excel date
                    if isinstance(row[6], (int, float)):
                        course_start_date = xlrd.xldate.xldate_as_datetime(
                            row[6], workbook.datemode
                        ).date()
                    else:
                        # If it's a string, replace non-breaking spaces, strip, and parse manually
                        cleaned_date = str(row[6]).replace("\xa0", " ").strip()
                        course_start_date = datetime.strptime(
                            cleaned_date, "%d-%b-%Y"
                        ).date()  # Adjust format if necessary
                except (ValueError, TypeError):
                    raise ValidationError(
                        f"Incorrect Course Start Date in row {row_num + 1}, Please enter a valid date and check for unwanted spaces"
                    )

            # Check if COURSE END DATE is present
            if row[7]:  # If there's a value in the eighth column
                try:
                    # If row[7] is a float, treat it as an Excel date
                    if isinstance(row[7], (int, float)):
                        course_end_date = xlrd.xldate.xldate_as_datetime(
                            row[7], workbook.datemode
                        ).date()
                    else:
                        # If it's a string, replace non-breaking spaces, strip, and parse manually
                        cleaned_date = str(row[7]).replace("\xa0", " ").strip()
                        course_end_date = datetime.strptime(
                            cleaned_date, "%d-%b-%Y"
                        ).date()  # Adjust format if necessary
                except (ValueError, TypeError):
                    raise ValidationError(
                        f"Incorrect Course End Date in row {row_num + 1}, Please enter a valid date and check for unwanted spaces"
                    )

            # Find the candidate based on INDOS NO
            candidate = (
                request.env["gp.candidate"]
                .sudo()
                .search(
                    [
                        ("institute_batch_id", "=", batch_id),
                        ("indos_no", "=", indos_no),
                    ],
                    limit=1,
                )
            )

            # Only proceed if all required fields are present
            # Create a new candidate STCW record
            if certificate_no and course_start_date and course_end_date:
                request.env["gp.candidate.stcw.certificate"].sudo().create(
                    {
                        "candidate_id": candidate.id,
                        "course_name": course_name,
                        "other_institute": institute_name,
                        "marine_training_inst_number": mti_no,
                        "mti_indos_no": indos_no,
                        "candidate_cert_no": certificate_no,
                        "course_start_date": course_start_date,
                        "course_end_date": course_end_date,
                    }
                )
                candidate._check_stcw_certificate()

        return request.redirect("/my/gpbatch/candidates/" + str(batch_id))

    @http.route(
        "/my/ccmcbatch/candidates/stcw_format_download/<int:batch_id>",
        type="http",
        auth="user",
        website=True,
    )
    def generate_ccmc_candidate_stcw_format(self, batch_id, **kw):
        excel_buffer = io.BytesIO()

        # Create a new Excel workbook and add a worksheet
        workbook = xlsxwriter.Workbook(excel_buffer)
        candidate_stcw_worksheet = workbook.add_worksheet("STCW Details")

        locked = workbook.add_format({"locked": True})
        unlocked = workbook.add_format({"locked": False})
        candidate_stcw_worksheet.set_column("A:XDF", None, unlocked)

        candidate_stcw_worksheet.set_column("A:A", 35, locked)  # Name
        candidate_stcw_worksheet.set_column("B:B", 15, locked)  # indos
        candidate_stcw_worksheet.set_column("C:C", 10, unlocked)  # cousre
        candidate_stcw_worksheet.set_column("D:D", 35, unlocked)  # insitute_name
        candidate_stcw_worksheet.set_column("E:E", 15, unlocked)  # mti_no
        # Set the column format for certificate_no to number
        number_format = workbook.add_format({"num_format": "@", "locked": False})

        # Set the column width and format for certificate_no
        candidate_stcw_worksheet.set_column("F:F", 35, number_format)  # certificate_no

        candidate_stcw_worksheet.set_column("G:G", 20, unlocked)  # cousre_start_date
        candidate_stcw_worksheet.set_column("H:H", 20, unlocked)  # cousre_end_date

        candidate_stcw_worksheet.protect()
        date_format = workbook.add_format(
            {"num_format": "dd-mmm-yyyy", "locked": False}
        )

        header_format = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_color": "white",
                "bg_color": "#336699",  # Blue color for the background
                "locked": True,
            }
        )

        header = [
            "Name of Candidate",
            "INDOS NO",
            "COURSE",
            "INSTITUTE NAME",
            "MTI NO",
            "CERTIFICATE NO",
            "COURSE START DATE",
            "COURSE END DATE",
        ]
        for col, value in enumerate(header):
            candidate_stcw_worksheet.write(0, col, value, header_format)

        # Auto fill indos no
        batch = (
            request.env["institute.ccmc.batches"].sudo().search([("id", "=", batch_id)])
        )
        # import wdb; wdb.set_trace()
        candidates = (
            request.env["ccmc.candidate"]
            .sudo()
            .search(
                [
                    ("institute_batch_id", "=", batch.id),
                    ("withdrawn_state", "!=", "yes"),
                    ("stcw_criteria","=", "pending"),
                ]
            )
        )

        # Extract valid indos numbers and names from candidates
        indos = [
            candidate.indos_no for candidate in candidates if candidate.indos_no
        ]  # Only include non-empty indos_no
        names = [
            candidate.name for candidate in candidates if candidate.name
        ]  # Only include non-empty Name strs

        # Write the names and indos numbers to the worksheet
        for i, (name, indos_no) in enumerate(zip(names, indos)):
            # Calculate the starting row for the current candidate
            start_row = i * 2 + 2  # Each candidate occupies two rows

            # Write the name in column A, indos number in column B (both rows)
            candidate_stcw_worksheet.write(f"A{start_row}", name, locked)
            candidate_stcw_worksheet.write(f"A{start_row + 1}", name, locked)

            candidate_stcw_worksheet.write(f"B{start_row}", indos_no, locked)
            candidate_stcw_worksheet.write(f"B{start_row + 1}", indos_no, locked)

        # Set date format for DOB column
        candidate_stcw_worksheet.set_column("G:G", 20, date_format)
        candidate_stcw_worksheet.set_column("H:H", 20, date_format)

        cousre_values = ["BST", "STSDSD"]

        candidate_stcw_worksheet.data_validation(
            "C2:C1048576", {"validate": "list", "source": cousre_values}
        )

        instruction_worksheet = workbook.add_worksheet("Instructions")

        instruction_worksheet.set_column("A:P", 20, locked)

        # instruction_worksheet.protect()
        date_format = workbook.add_format(
            {"num_format": "dd-mmm-yyyy", "locked": False}
        )

        # instruction_worksheet.write_comment('M2', 'In the columns Xth, XIIth, ITI , Please enter only number or grade (a,"a+,b,b+,c,c+,d,d+)')

        header_format = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_color": "white",
                "bg_color": "#336699",  # Blue color for the background
                "locked": True,
            }
        )

        header = [
            "Sr No.",
            "Name of Candidate",
            "INDOS NO",
            "COURSE",
            "INSTITUTE NAME",
            "MTI NO",
            "CERTIFICATE NO",
            "COURSE START DATE",
            "COURSE END DATE",
        ]
        for col, value in enumerate(header):
            instruction_worksheet.write(0, col, value, header_format)

        # Set date format for DOB column
        instruction_worksheet.set_column("F:F", 20, date_format)
        instruction_worksheet.set_column("G:G", 20, date_format)

        cell_format = workbook.add_format()
        cell_format.set_text_wrap()

        mandatory_format = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_color": "red",
                "text_wrap": True,
            }
        )

        # Instruction Description
        merge_format = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "font_size": 15,
                "font_color": "black",
            }
        )
        cell_format = workbook.add_format()
        cell_format.set_text_wrap()

        # Header section with sample data
        instruction_worksheet.write("A3", "1) Description")
        instruction_worksheet.write("A4", "2) Format")
        instruction_worksheet.write("A5", "3) Mandatory")

        # Populate instruction details for the STCW table
        # Example of Name
        instruction_worksheet.write("B2", "Candidate Name")
        instruction_worksheet.write(
            "B3",
            "This field contains the student's INDOS number, which is required for identification in the STCW system",
            cell_format,
        )
        instruction_worksheet.write(
            "B4",
            "INDOS number must follow the correct format. Avoid duplicates or incorrect INDOS numbers",
            cell_format,
        )
        instruction_worksheet.write("B5", "Mandatory Field", mandatory_format)

        # Example of INDOS NO
        instruction_worksheet.write("C2", "23GM1234")
        instruction_worksheet.write(
            "C3",
            "This field contains the student's INDOS number, which is required for identification in the STCW system",
            cell_format,
        )
        instruction_worksheet.write(
            "C4",
            "INDOS number must follow the correct format. Avoid duplicates or incorrect INDOS numbers",
            cell_format,
        )
        instruction_worksheet.write("C5", "Mandatory Field", mandatory_format)

        # Example of Course Name
        instruction_worksheet.write("D2", "BST")
        instruction_worksheet.write(
            "D3",
            "This is the name of the STCW course completed by the candidate",
            cell_format,
        )
        instruction_worksheet.write(
            "D4",
            "Ensure the course name follows the STCW standard abbreviations (e.g., BST, STSDSD)",
            cell_format,
        )
        instruction_worksheet.write("D5", "Mandatory Field", mandatory_format)

        # Example of Institute Name
        instruction_worksheet.write("E2", "Oceanic Maritime")
        instruction_worksheet.write(
            "E3",
            "Name of the maritime training institute where the course was completed",
            cell_format,
        )
        instruction_worksheet.write(
            "E4", "Ensure correct and complete institute name", cell_format
        )
        instruction_worksheet.write("E5", "Mandatory Field", mandatory_format)

        # Example of MTI NO
        instruction_worksheet.write("F2", "410210")
        instruction_worksheet.write(
            "F3",
            "Maritime Training Institute (MTI) number of the training center",
            cell_format,
        )
        instruction_worksheet.write(
            "F4", "MTI number should be correctly entered", cell_format
        )
        instruction_worksheet.write("F5", "Mandatory Field", mandatory_format)

        # Example of Certificate Number
        instruction_worksheet.write("G2", "20704561012400415")
        instruction_worksheet.write(
            "G3", "Unique certificate number issued for the course", cell_format
        )
        instruction_worksheet.write(
            "G4", "Certificate number should be correctly entered", cell_format
        )
        instruction_worksheet.write("G5", "Mandatory Field", mandatory_format)

        # Example of Course Start Date
        instruction_worksheet.write("H2", "14-Apr-2002")
        instruction_worksheet.write("H3", "Date when the course started", cell_format)
        instruction_worksheet.write(
            "H4", "Date format: DD-MMM-YYYY (e.g., 14-Apr-2002)", cell_format
        )
        instruction_worksheet.write("H5", "Mandatory Field", mandatory_format)

        # Example of Course End Date
        instruction_worksheet.write("I2", "14-Apr-2002")
        instruction_worksheet.write("I3", "Date when the course ended", cell_format)
        instruction_worksheet.write(
            "I4", "Date format: DD-MMM-YYYY (e.g., 14-Apr-2002)", cell_format
        )
        instruction_worksheet.write("I5", "Mandatory Field", mandatory_format)

        instruction_worksheet.protect()

        workbook.close()

        # Set the buffer position to the beginning
        excel_buffer.seek(0)

        # Generate a response with the Excel file
        response = request.make_response(
            excel_buffer.getvalue(),
            headers=[
                (
                    "Content-Type",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ),
                (
                    "Content-Disposition",
                    "attachment; filename=candidate_STCW_format_file.xlsx",
                ),
            ],
        )

        # Clean up the buffer
        excel_buffer.close()

        return response

    @http.route(
        ["/my/uploadccmccandidatestcwdata"], type="http", auth="user", website=True
    )
    def UploadCCMCCandidateSTCWData(self, **kw):
        # import wdb; wdb.set_trace()
        user_id = request.env.user.id
        institute_id = (
            request.env["bes.institute"].sudo().search([("user_id", "=", user_id)]).id
        )

        batch_id = int(kw.get("ccmc_batch_id"))

        file_content = kw.get("fileUpload").read()
        filename = kw.get("fileUpload").filename

        # Open the uploaded workbook
        workbook = xlrd.open_workbook(file_contents=file_content)
        worksheet = workbook.sheet_by_index(0)

        # Iterate through the rows of the worksheet, starting from the second row
        for row_num in range(1, worksheet.nrows):  # Assuming first row contains headers
            row = worksheet.row_values(row_num)

            # Extracting data from the row
            indos_no = row[1]  # Assuming INDOS NO is in the second column
            course_name = row[2].lower()  # Assuming COURSE is in the third column
            institute_name = row[3]  # Assuming INSTITUTE NAME is in the fourth column

            # Initialize variables
            mti_no = None
            certificate_no = None
            course_start_date = None
            course_end_date = None

            # Check if MTI NO is present and convert to int
            if row[4]:  # If there's a value in the fifth column
                try:
                    # Convert to string, remove unwanted spaces
                    value = str(row[4]).strip()

                    # Check if it's a float ending in .0 and convert to int
                    if value.endswith(".0"):
                        mti_no = int(float(value))
                    else:
                        mti_no = int(value)
                except ValueError:
                    raise ValidationError(
                        f"Incorrect MTI NO in row {row_num + 1}, Please enter only numbers and check for unwanted spaces"
                    )

            # Check if CERTIFICATE NO is present and convert to int
            if row[5]:  # If there's a value in the sixth column
                try:
                    value = str(row[5]).strip()

                    if value.endswith(".0"):
                        certificate_no = int(float(value))
                    else:
                        certificate_no = int(value)
                except ValueError:
                    raise ValidationError(
                        f"Incorrect Certificate NO in row {row_num + 1}, Please enter only numbers and check for unwanted spaces"
                    )

            # Check if COURSE START DATE is present
            if row[6]:  # If there's a value in the seventh column
                try:
                    # If row[6] is a float, treat it as an Excel date
                    if isinstance(row[6], (int, float)):
                        course_start_date = xlrd.xldate.xldate_as_datetime(
                            row[6], workbook.datemode
                        ).date()
                    else:
                        # If it's a string, replace non-breaking spaces, strip, and parse manually
                        cleaned_date = str(row[6]).replace("\xa0", " ").strip()
                        course_start_date = datetime.strptime(
                            cleaned_date, "%d-%b-%Y"
                        ).date()  # Adjust format if necessary
                except (ValueError, TypeError):
                    raise ValidationError(
                        f"Incorrect Course Start Date in row {row_num + 1}, Please enter a valid date and check for unwanted spaces"
                    )

            # Check if COURSE END DATE is present
            if row[7]:  # If there's a value in the eighth column
                try:
                    # If row[7] is a float, treat it as an Excel date
                    if isinstance(row[7], (int, float)):
                        course_end_date = xlrd.xldate.xldate_as_datetime(
                            row[7], workbook.datemode
                        ).date()
                    else:
                        # If it's a string, replace non-breaking spaces, strip, and parse manually
                        cleaned_date = str(row[7]).replace("\xa0", " ").strip()
                        course_end_date = datetime.strptime(
                            cleaned_date, "%d-%b-%Y"
                        ).date()  # Adjust format if necessary
                except (ValueError, TypeError):
                    raise ValidationError(
                        f"Incorrect Course End Date in row {row_num + 1}, Please enter a valid date and check for unwanted spaces"
                    )

            # Find the candidate based on INDOS NO
            candidate = (
                request.env["ccmc.candidate"]
                .sudo()
                .search(
                    [
                        ("institute_batch_id", "=", batch_id),
                        ("indos_no", "=", indos_no),
                    ],
                    limit=1,
                )
            )
            # Only proceed if all required fields are present
            if certificate_no and course_start_date and course_end_date:
                request.env["ccmc.candidate.stcw.certificate"].sudo().create(
                    {
                        "candidate_id": candidate.id,
                        "course_name": course_name,
                        "other_institute": institute_name,
                        "marine_training_inst_number": mti_no,
                        "mti_indos_no": indos_no,
                        "candidate_cert_no": certificate_no,
                        "course_start_date": course_start_date,
                        "course_end_date": course_end_date,
                    }
                )
                candidate._check_stcw_certificate()

        return request.redirect("/my/ccmcbatch/candidates/" + str(batch_id))

    # New Code
    @http.route(
        ["/my/update_candidate_image_and_signature"],
        methods=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def update_candidate_image_and_signature(self, **kw):
        # import wdb; wdb.set_trace()
        candidate = (
            request.env["gp.candidate"]
            .sudo()
            .search([("id", "=", int(kw.get("candidate_id")))])
        )

        candidate_image = kw.get("candidate_photo").read()
        candidate_image_name = kw.get("candidate_photo").filename
        if candidate_image and candidate_image_name:
            candidate.write(
                {
                    "candidate_image": base64.b64encode(candidate_image),
                    "candidate_image_name": candidate_image_name,
                }
            )

        signature_photo = kw.get("signature_photo").read()
        signature_photo_name = kw.get("signature_photo").filename
        if signature_photo and signature_photo_name:
            candidate.write(
                {
                    "candidate_signature": base64.b64encode(signature_photo),
                    "candidate_signature_name": signature_photo_name,
                }
            )

        candidate._check_sign()
        candidate._check_image()

        return request.redirect("/my/gpbatch/candidates/" + str(kw.get("batch_id")))

    @http.route(
        ["/my/ccmc_update_candidate_image_and_signature"],
        methods=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def ccmc_update_candidate_image_and_signature(self, **kw):
        # import wdb; wdb.set_trace()
        candidate = (
            request.env["ccmc.candidate"]
            .sudo()
            .search([("id", "=", int(kw.get("candidate_id")))])
        )

        candidate_image = kw.get("candidate_photo").read()
        candidate_image_name = kw.get("candidate_photo").filename
        if candidate_image and candidate_image_name:
            candidate.write(
                {
                    "candidate_image": base64.b64encode(candidate_image),
                    "candidate_image_name": candidate_image_name,
                }
            )

        signature_photo = kw.get("signature_photo").read()
        signature_photo_name = kw.get("signature_photo").filename
        if signature_photo and signature_photo_name:
            candidate.write(
                {
                    "candidate_signature": base64.b64encode(signature_photo),
                    "candidate_signature_name": signature_photo_name,
                }
            )

        candidate._check_sign()
        candidate._check_image()

        return request.redirect(
            "/my/ccmcbatch/candidates/" + str(kw.get("ccmc_batch_id"))
        )

    @http.route(
        ["/my/gpcandidate/updatewithdrawnstatus"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def UpdateWithdrawnStatusGP(self, **kw):
        # import wdb; wdb.set_trace();
        candidate_id = kw.get("candidate_id")
        withdrawn_state = kw.get("withdrawn_state")
        withdrawn_reason = kw.get("withdrawn_reason")

        candidate = (
            request.env["gp.candidate"].sudo().search([("id", "=", int(candidate_id))])
        )

        candidate.write(
            {"withdrawn_state": withdrawn_state, "withdrawn_reason": withdrawn_reason}
        )

        return request.redirect("/my/gpcandidateprofile/" + str(kw.get("candidate_id")))

    @http.route(
        ["/my/ccmccandidate/updatewithdrawnstatus"],
        method=["POST", "GET"],
        type="http",
        auth="user",
        website=True,
    )
    def UpdateWithdrawnStatusCCMC(self, **kw):
        # import wdb; wdb.set_trace();
        candidate_id = kw.get("candidate_id")
        withdrawn_state = kw.get("withdrawn_state")
        withdrawn_reason = kw.get("withdrawn_reason")

        candidate = (
            request.env["ccmc.candidate"]
            .sudo()
            .search([("id", "=", int(candidate_id))])
        )

        candidate.write(
            {"withdrawn_state": withdrawn_state, "withdrawn_reason": withdrawn_reason}
        )

        return request.redirect(
            "/my/ccmccandidateprofile/" + str(kw.get("candidate_id"))
        )

    # @http.route(['/my/book_orders/list'], type="http", auth="user", website=True)
    # def BookOrdersList(self, **kw):
    #     user_id = request.env.user.id
    #     institute_id = request.env["bes.institute"].sudo().search(
    #         [('user_id', '=', user_id)]).id

    #     vals = {'institute_id':institute_id, "page_name": "book_orders"}
    #     return request.render("bes.book_orders_list", vals)

    @http.route(["/my/create_books_order"], type="http", auth="user", website=True)
    def CreateBookOrders(self, **kw):
        user_id = request.env.user.id
        institute_id = (
            request.env["bes.institute"].sudo().search([("user_id", "=", user_id)]).id
        )

        vals = {"institute_id": institute_id, "page_name": "book_orders"}
        return request.render("bes.books_order_create_template", vals)

    @http.route(["/my/submit_books_order"], type="http", auth="user", website=True)
    def SubmitBookOrder(self, **kw):

        user_id = request.env.user.id
        institute_id = (
            request.env["bes.institute"]
            .sudo()
            .search([("user_id", "=", user_id)])
            .user_id.partner_id.id
        )
        hidden_input = kw.get("hiddenInput")
        product_lines = json.loads(hidden_input)
        order_lines_data = []
        for line in product_lines:
            product_id = int(line.get("product_id"))
            quantity = float(line.get("quantity", 0))
            product = request.env["product.product"].sudo().browse(product_id)
            order_lines_data.append(
                (
                    0,
                    0,
                    {
                        "product_id": product.id,
                        "product_uom_qty": quantity,
                        "price_unit": product.list_price,
                    },
                )
            )
        # import wdb; wdb.set_trace();
        transaction_id = kw.get("transaction_id")
        payment_slip = request.httprequest.files.get("payment_slip_upload")
        if payment_slip:
            payment_slip_file = payment_slip.read()
            payment_slip_filename = payment_slip.filename

            order = (
                request.env["sale.order"]
                .sudo()
                .create(
                    {
                        "partner_id": institute_id,
                        "transaction_id": transaction_id,
                        "payment_slip": base64.b64encode(payment_slip_file),
                        "slip_file_name": payment_slip_filename,
                        "order_line": order_lines_data,
                    }
                )
            )
        else:
            order = (
                request.env["sale.order"]
                .sudo()
                .create(
                    {
                        "partner_id": institute_id,
                        "order_line": order_lines_data,
                    }
                )
            )

        order.sudo().write(
            {"l10n_in_gst_treatment": "unregistered", "state": "sale", "user_id": False}
        )
        return request.redirect("/my/orders")

    @http.route(
        ["/getProduct"], methods=["POST"], type="json", auth="user", website=True
    )
    def GetProduct(self, **kw):
        # import wdb; wdb.set_trace();
        data = request.jsonrequest
        productID = data["productID"]

        price_per_unit = (
            request.env["product.template"]
            .sudo()
            .search([("id", "=", int(productID))])
            .standard_price
        )

        return json.dumps({"status": "success", "price_per_unit": price_per_unit})

    @http.route(
        ["/sale_order/payment_slip/<int:sale_order_id>"], type="http", auth="user"
    )
    def download_payment_slip(self, sale_order_id, **kw):
        sale_order = request.env["sale.order"].browse(sale_order_id)
        # import wdb; wdb.set_trace();

        if sale_order.payment_slip:
            file_data = sale_order.payment_slip

            # Ensure the binary data is handled correctly (no need to decode base64)
            # Just ensure that it's returned as a proper bytes object
            if isinstance(file_data, bytes):
                file_data = bytes(file_data)

            # Return the file content with appropriate headers
            return request.make_response(
                file_data,
                headers=[
                    ("Content-Type", "application/pdf"),  # Ensure PDF content type
                    ("Content-Disposition", "attachment; filename=payment_slip.pdf"),
                ],
            )
