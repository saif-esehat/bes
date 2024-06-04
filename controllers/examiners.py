from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request, Response
from odoo import http
from werkzeug.utils import secure_filename
import base64
import csv
import io
from io import StringIO
from datetime import datetime
import xlsxwriter
from odoo.exceptions import AccessError
import xlrd
import json
from odoo.exceptions import UserError
from odoo.tools import html_escape
import mimetypes

from functools import wraps


def check_user_groups(group_xml_id):
    def decorator(func):
        @wraps(func)
        def wrapper(self,*args, **kwargs):
            if not request.env.user.has_group(group_xml_id):
                raise AccessError("You Do not have Access")
            return func(self,*args, **kwargs)
        return wrapper
    return decorator




class ExaminerPortal(CustomerPortal):
    
    @http.route(['/my/examiner/online_exam'],type="http",auth="user",website=True)
    @check_user_groups("bes.group_examiners")
    def ExamListView(self,**kw):
        user_id = request.env.user.id
        
        examiner_id = request.env["bes.examiner"].sudo().search(
            [('user_id', '=', user_id)]).id
        
        
        
        survey = request.env["survey.user_input"].sudo().search(
            [('examiner', '=', examiner_id)])
        
        dgs_batch = survey.mapped('dgs_batch')
        
        # import wdb; wdb.set_trace(); 
         
        vals = {"dgs_batches":dgs_batch}
        
        return request.render("bes.examiner_portal_online_exam_list", vals)
    
    
    @http.route(['/my/generatetoken/<int:batch_id>/<int:input_id>'],type="http",auth="user",website=True)
    @check_user_groups("bes.group_examiners")
    def GenerateToken(self,batch_id,input_id,**kw):
        
        user_input = request.env["survey.user_input"].sudo().search([('id','=',input_id)])
        
        token = user_input.sudo().generate_unique_string()
        
        user_input.write({'examiner_token':token})
        
        
        return request.redirect("/my/examiner/online_exam/"+str(batch_id))


    
    
    @http.route(['/my/examiner/online_exam/<int:batch_id>'],type="http",auth="user",website=True)
    @check_user_groups("bes.group_examiners")
    def BatchExamListView(self,batch_id,**kw):
        user_id = request.env.user.id
        
        examiner_id = request.env["bes.examiner"].sudo().search(
            [('user_id', '=', user_id)]).id
        
        
        
        survey = request.env["survey.user_input"].sudo().search(
            [('examiner', '=', examiner_id),('dgs_batch','=',batch_id)])
        

        
        # import wdb; wdb.set_trace(); 
         
        vals = {'survey_user_inputs':survey,'batch_id':batch_id}
        
        return request.render("bes.examiner_portal_online_batch_exam_list", vals)
    
    @http.route(['/my/examiner/online_exam/start/<int:survey_id>'],type="http",auth="user",website=True)
    @check_user_groups("bes.group_examiners")
    def ExamStart(self,survey_id,**kw):
        
        survey = request.env["survey.survey"].sudo().search([('id', '=', survey_id)])
        survey.write({"exam_state":"in_progress"})        
        return request.redirect("/my/examiner/online_exam")
    
    @http.route(['/my/examiner/online_exam/stop/<int:survey_id>'],type="http",auth="user",website=True)
    @check_user_groups("bes.group_examiners")
    def ExamStop(self,survey_id,**kw):
        
        survey = request.env["survey.survey"].sudo().search([('id', '=', survey_id)])
        survey.write({"exam_state":"stopped"})        
        return request.redirect("/my/examiner/online_exam")


    @http.route(['/my/assignments'], type="http", auth="user", website=True)
    def ExaminerAssignmentListView(self, **kw):
        # import wdb; wdb.set_trace()

        user_id = request.env.user.id
        examiner = request.env['bes.examiner'].sudo().search([('user_id','=',user_id)])
        # examiner_assignments = request.env['bes.examiner'].sudo().search([('user_id','=',user_id)]).assignments
        filtered_batches = []

        # Assuming examiner is already defined
        for batch in request.env['dgs.batches'].sudo().search([]):
            count = request.env['exam.type.oral.practical.examiners'].sudo().search_count([
                ('dgs_batch', '=', batch.id),
                ('examiner', '=', examiner.id)
            ])
            if count > 0:
                filtered_batches.append(batch)


        
        vals = {'batches':filtered_batches,'assignments':'', 'examiner':examiner,'page_name':'batches'}
        # self.env["gp.candidate"].sudo().search([('')])
        return request.render("bes.examiner_assignment_list", vals)
    
    @http.route(['/my/assignments/batches/<int:batch_id>'], type="http", auth="user", website=True)
    def ExaminerAssignmentBatchListView(self,batch_id, **kw):
        # import wdb; wdb.set_trace()

        user_id = request.env.user.id
        batch_id = batch_id
        examiner = request.env['bes.examiner'].sudo().search([('user_id','=',user_id)])
        # batch_info = request.env['exam.type.oral.practical'].sudo().search([('dgs_batch.id','=',batch_id)])
        examiner_assignments = request.env['exam.type.oral.practical.examiners'].sudo().search([('dgs_batch.id','=',batch_id),('examiner','=',examiner.id)])
        # import wdb; wdb.set_trace()
        vals = {'assignments':examiner_assignments, 'examiner':examiner,'batch':batch_id,'page_name':'institutes'}
        return request.render("bes.examiner_assignment_institute_list",vals)
    
    @http.route(['/my/assignments/batches/candidates/<int:batch_id>/<int:assignment_id>'], type="http", auth="user", website=True)
    def ExaminerAssignmentCandidateListView(self,batch_id,assignment_id, **kw):

        user_id = request.env.user.id
        batch_id = batch_id
        examiner = request.env['bes.examiner'].sudo().search([('user_id','=',user_id)])
        examiner_subject  = request.env['exam.type.oral.practical.examiners'].sudo().search([('id','=',assignment_id)]).subject.name
        # examiner_subject = examiner.subject_id.name
        # batch_info = request.env['exam.type.oral.practical'].sudo().search([('dgs_batch.id','=',batch_id)])
        examiner_assignments = request.env['exam.type.oral.practical.examiners'].sudo().search([('dgs_batch.id','=',batch_id),('examiner','=',examiner.id)])
        marksheets = request.env['exam.type.oral.practical.examiners.marksheet'].sudo().search([('examiners_id','=',assignment_id)])

        # import wdb; wdb.set_trace()
        
        
        vals = {'assignments':examiner_assignments,
                'examiner_subject':examiner_subject,
                'examiner':examiner,
                'marksheets':marksheets ,
                'assignment_id':assignment_id, 
                'batch_id':batch_id,'page_name':'institutes1',}
        
        print(examiner_subject)
        return request.render("bes.examiner_assignment_candidate_list",vals)

    # def check_user_groups(group_xml_id):
    #     ​def decorator(func):
    #     ​	​def wrapper(self, *args, **kwargs):
    #     ​	​	​if not request.env.user.has_group(group_xml_id):
    #     ​	​	​	​raise AccessError("You do not have access rights to view this page.")
    #     ​	​	​return func(self, *args, **kwargs)
    #     ​	​return wrapper
    #     ​return decorator
    
    
    @http.route(['/confirm/gsk/marksheet'],method=["POST"],type="json", auth="user")
    def ConfirmGSKMarksheet(self, **kw):
        print("KW Confirm GSK")
        print(request.jsonrequest)
        data = request.jsonrequest
        marksheet_id = data["id"]
        last_part = marksheet_id.split('_')[-1]
        marksheet_id = int(last_part)
        marksheet = request.env["exam.type.oral.practical.examiners.marksheet"].sudo().search([('id','=',marksheet_id)])
        marksheet.gsk_oral.write({"gsk_oral_draft_confirm": 'confirm' })
        marksheet.gsk_prac.write({"gsk_practical_draft_confirm": 'confirm' })
        return json.dumps({"status":"success"})
    
    @http.route(['/confirm/mek/marksheet'],method=["POST"],type="json", auth="user")
    def ConfirmMEKMarksheet(self, **kw):
        print("KW Confirm MEK")
        
        print(request.jsonrequest)
        data = request.jsonrequest
        marksheet_id = data["id"]
# Split the string by underscore and take the last element
        last_part = marksheet_id.split('_')[-1]

        # Extract the number from the last part
        marksheet_id = int(last_part)

        
        marksheet = request.env["exam.type.oral.practical.examiners.marksheet"].sudo().search([('id','=',marksheet_id)])
        marksheet.mek_oral.write({"mek_oral_draft_confirm": 'confirm' })
        marksheet.mek_prac.write({"mek_practical_draft_confirm": 'confirm' })
        return json.dumps({"status":"success"})
    
    
    @http.route('/open_candidate_form', type='http', auth="user", website=True)
    def open_candidate_form(self, **rec):
        
        # import wdb;wdb.set_trace();
        
        if 'rec_id' in rec:
            rec_id =rec['rec_id']
            assignment = request.env['examiner.assignment'].sudo().browse(int(rec_id))
            # Check if gp_candidate is set
            if assignment.assigned_to == "gp_candidate":
                gp_oral_prac = assignment.gp_oral_prac
                candidate = assignment.gp_oral_prac.gp_candidate
                subject = assignment.subject_id.name
            # Check if ccmc_candidate is set
            elif assignment.assigned_to == "ccmc_candidate":
                candidate = assignment.ccmc_candidate
            else:
                # Handle the case when both gp_candidate and ccmc_candidate are not set
                candidate = False
            
            return request.render("bes.examiner_candidate_list", 
                                  {'candidate': candidate,
                                   'gp_oral_prac':gp_oral_prac , 
                                   'subject':subject ,
                                   'assignment_id':rec_id, 
                                   'page_name':'gp_assignment'})
        else:
            search_filter = rec.get('search_filter') or request.params.get('search_filter')
            search_value = rec.get('search_value') or request.params.get('search_value')


    @http.route('/open_ccmc_candidate_form', type='http', auth="user", website=True)
    def open_ccmc_candidate_form(self, **rec):
        
        
        if 'rec_id' in rec:
            rec_id = rec['rec_id']
            assignment = request.env['examiner.assignment'].sudo().browse(int(rec_id))
            # Check if gp_candidate is set
            if assignment.assigned_to == "ccmc_candidate":
                ccmc_assignment = assignment.ccmc_assignment
                candidate = assignment.ccmc_assignment.ccmc_candidate
                subject = assignment.subject_id.name
            # Check if gp_candidate is set
            elif assignment.assigned_to == "gp_candidate":
                candidate = assignment.gp_candidate
            else:
                # Handle the case when both gp_candidate and ccmc_candidate are not set
                candidate = False
            
            import wdb;wdb.set_trace();
            return request.render("bes.examiner_candidate_list", 
                                  {'candidate': candidate,
                                   'ccmc_assignment':ccmc_assignment , 
                                   'subject':subject ,
                                   'assignment_id':rec_id, 
                                   "page_name": "ccmc_assignment"})
        else:
            search_filter = rec.get('search_filter') or request.params.get('search_filter')
            search_value = rec.get('search_value') or request.params.get('search_value')




    @http.route('/open_gsk_oral_form', type='http', auth="user", website=True,method=["POST","GET"])
    def open_gsk_oral_form(self, **rec):
        # import wdb;wdb.set_trace();
        candidate = request.env['gp.candidate'].sudo()
        
        if request.httprequest.method == "POST":
            print(rec)
            
            # import wdb; wdb.set_trace()
            
            rec_id = rec['rec_id']
            
            marksheet = request.env['gp.gsk.oral.line'].sudo().search([('id','=',rec['gsk_oral'])])

            # Convert string values to integers
            subject_area_1_2_3 = int(rec['subject_area_1_2_3'])
            subject_area_4_5_6 = int(rec['subject_area_4_5_6'])
            # subject_area3 = int(rec['subject_area3'])
            # subject_area4 = int(rec['subject_area4'])
            # subject_area5 = int(rec['subject_area5'])
            # subject_area6 = int(rec['subject_area6'])
            state=rec['state']

            # exam_date = rec['exam_date']
            practical_record_journals = int(rec['practical_record_journals'])
       
            remarks_oral_gsk = rec['remarks_oral_gsk']
            
            total = subject_area_1_2_3 + subject_area_4_5_6

            candidate_rec = candidate.search([('id', '=', rec_id)])
            draft_records = candidate_rec.gsk_oral_child_line.filtered(lambda line: line.gsk_oral_draft_confirm == 'draft') 

            # assignment_id = int(rec['assignment_id'])
            # batch_id = int(rec['batch_id'])
            # Construct the dictionary with integer values
            vals = {
                'subject_area_1_2_3': subject_area_1_2_3,                
                'subject_area_4_5_6': subject_area_4_5_6,
                # 'subject_area_3': subject_area3,
                # 'subject_area_4': subject_area4,
                # 'subject_area_5': subject_area5, 
                # 'subject_area_6': subject_area6,
                'practical_record_journals': practical_record_journals,
                'gsk_oral_draft_confirm': state,
                'gsk_oral_remarks': remarks_oral_gsk,
            }
            
            

            marksheet.write(vals)
            
            
            return request.redirect("/my/assignments/batches/candidates/"+rec["batch_id"]+"/"+rec['assignment_id'])
            
            
            # Write to the One2many field using the constructed dictionary
            # 

        else:
            print('enterrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr======================', rec)
            rec_id = rec['rec_id']
            candidate_rec = candidate.search([('id', '=', rec_id)])
            candidate_indos = candidate_rec.indos_no
            name=candidate_rec.name
            candidate_image = candidate_rec.candidate_image
            
            gsk_marksheet = request.env['gp.gsk.oral.line'].sudo().search([('id','=',rec['gsk_oral'])])
            
            assignment_id = int(rec['assignment_id'])
            batch_id = int(rec['batch_id'])
            vals = {'indos': candidate_indos,
                    'gsk_marksheet': gsk_marksheet,
                    'candidate_name': name,
                    'candidate_image': candidate_image,
                    'candidate': candidate_rec,
                    'assignment_id':assignment_id,
                    'batch_id':batch_id,
                    "page_name": "gsk_oral"}
            
            # draft_records = candidate_rec.gsk_oral_child_line.filtered(lambda line: line.gsk_oral_draft_confirm == 'draft')
            # print('recccccccccccccccccccccccccccccccccc',candidate_rec)
            # return request.render("bes.gsk_oral_marks_submit", {'indos': candidate_indos,'gsk_marksheet':gsk_marksheet,'candidate_name':name, 'candidate_image': candidate_image})'exam_date':gsk_marksheet.gsk_oral_exam_date,
            return request.render("bes.gsk_oral_marks_submit",vals)


    @http.route('/open_gsk_practical_form', type='http', auth="user", website=True,method=["POST","GET"])
    def open_gsk_practical_form(self, **rec):
        
        # import wdb;wdb.set_trace();
        candidate = request.env['gp.candidate'].sudo()
        print("=======================================================",request.httprequest.method)
        
        if request.httprequest.method == "POST":
            print('exittttttttttttttttttttttttttttttt')
            indos = rec['indos']

            # Convert string values to integers
            climbing_mast_bosun_chair = int(rec['climbing_mast'])
            buoy_flags_recognition = int(rec['buoy_flags_recognition'])
            # bosun_chair = int(rec['bosun_chair'])
            rig_stage = int(rec['rig_stage'])
            rig_pilot = int(rec['rig_pilot'])
            rig_scoffolding = int(rec['rig_scoffolding'])
            fast_ropes = int(rec['fast_ropes'])
            knots_bend = int(rec['knots_bend'])
            sounding_rod = int(rec['sounding_rod'])
            state = rec['state']
            remarks_oral_gsk = rec['gsk_practical_remarks']
            
            
            # marksheet = request.env['gp.gsk.practical.line'].sudo().search([('id','=',rec['gsk_oral'])])

            # candidate_rec = candidate.search([('indos_no', '=', indos)])
            # draft_records = candidate_rec.gsk_practical_child_line.filtered(lambda line: line.gsk_practical_draft_confirm == 'draft')

            # Construct the dictionary with integer values
            vals = {
                'climbing_mast_bosun_chair': climbing_mast_bosun_chair,
                'buoy_flags_recognition': buoy_flags_recognition,
                # 'bosun_chair': bosun_chair,
                'rig_stage': rig_stage,
                'rig_pilot': rig_pilot,
                'rig_scaffolding': rig_scoffolding,
                'fast_ropes': fast_ropes,
                'knots_bend': knots_bend,
                'sounding_rod': sounding_rod,
                'gsk_practical_draft_confirm': state,
                'gsk_practical_remarks': remarks_oral_gsk
            }
            
            marksheet = request.env['gp.gsk.practical.line'].sudo().search([('id','=',rec['gsk_practical'])])
            marksheet.write(vals)
            
            return request.redirect("/my/assignments/batches/candidates/"+rec["batch_id"]+"/"+rec['assignment_id'])
        
        else:
            # import wdb; wdb.set_trace()
            print('enterrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr', rec)
            rec_id = rec['rec_id']
            candidate_rec = candidate.search([('id', '=', rec['rec_id'])])
            name=candidate_rec.name
            candidate_image = candidate_rec.candidate_image
            # draft_records = candidate_rec.gsk_practical_child_line.filtered(lambda line: line.gsk_practical_draft_confirm == 'draft')
            gsk_prac_marksheet = request.env['gp.gsk.practical.line'].sudo().search([('id','=',rec['gsk_practical'])])
            
            assignment_id = int(rec['assignment_id'])
            batch_id = int(rec['batch_id'])
            print('recccccccccccccccccccccccccccccccccc',candidate_rec)
            vals = {'indos': candidate_rec.indos_no,
                    'candidate_name':name,
                    'candidate_image': candidate_image,
                    'candidate': candidate_rec,
                    'gsk_prac_marksheet':gsk_prac_marksheet,
                    'assignment_id':assignment_id,
                    'batch_id':batch_id,
                    "page_name": "gsk_prac"
                    }
            # exam_date = gsk_prac_marksheet.gsk_practical_exam_date 'exam_date':exam_date,
            return request.render("bes.gsk_practical_marks_submit", vals)       
            

    @http.route('/open_mek_oral_form', type='http', auth="user", website=True,method=["POST","GET"])
    def open_mek_oral_form(self, **rec):
        candidate = request.env['gp.candidate'].sudo()
        print("=======================================================",request.httprequest.method)
        
        if request.httprequest.method == "POST":
            # print('exittttttttttttttttttttttttttttttt')
            indos = rec['indos']

            # Convert string values to integers
            subject_area1 = int(rec['subject_area1'])
            subject_area2 = int(rec['subject_area3'])
            # subject_area3 = int(rec['subject_area3'])
            # subject_area4 = int(rec['subject_area4'])
            subject_area5 = int(rec['subject_area5'])
            subject_area6 = int(rec['subject_area6'])
            mek_oral_remarks = rec['remarks_oral_mek']
            state = rec['state']

            # candidate_rec = candidate.search([('indos_no', '=', indos)])
            # draft_records = candidate_rec.mek_oral_child_line.filtered(lambda line: line.mek_oral_draft_confirm == 'draft')


            # Construct the dictionary with integer values
            vals = {
                'using_of_tools': subject_area1,
                'welding_lathe_drill_grinder': subject_area2,
                # 'welding': subject_area3,
                # 'lathe_drill_grinder': subject_area4,
                'electrical': subject_area5,
                'journal': subject_area6,
                'mek_oral_remarks': mek_oral_remarks,
                'mek_oral_draft_confirm': state
            }
            
            marksheet = request.env['gp.mek.oral.line'].sudo().search([('id','=',rec['mek_oral'])])
            marksheet.write(vals)
            
            return request.redirect("/my/assignments/batches/candidates/"+rec["batch_id"]+"/"+rec['assignment_id'])

            # print('valssssssssssssssssssssssssssssssssssssssssssssssss', vals)

            # # Write to the One2many field using the constructed dictionary
            # if draft_records:
            #     draft_records.write(vals)
            #     print("++++==============================+++++++++++++++++++ data is entered",draft_records)
            # else:
            #     print("Record not found for updating.========================================================================")
        
            # return {}

        else:
            print('enterrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr', rec)
            rec_id = rec['rec_id']
            candidate_rec = candidate.search([('id', '=', rec_id)])
            name=candidate_rec.name
            candidate_image = candidate_rec.candidate_image
            # draft_records = candidate_rec.mek_oral_child_line.filtered(lambda line: line.mek_oral_draft_confirm == 'draft')
            mek_oral_marksheet = request.env['gp.mek.oral.line'].sudo().search([('id','=',rec['mek_oral'])])

            print('recccccccccccccccccccccccccccccccccc',candidate_rec)
            assignment_id = int(rec['assignment_id'])
            batch_id = int(rec['batch_id'])
            
            # exam_date = mek_oral_marksheet.mek_oral_exam_date 'exam_date':exam_date,
            return request.render("bes.mek_oral_marks_submit", {'indos': candidate_rec.indos_no,'candidate_name':name, 'candidate_image': candidate_image, 'candidate': candidate_rec,'mek_oral_marksheet':mek_oral_marksheet,'assignment_id':assignment_id,'batch_id':batch_id,'page_name':'mek_oral'})

    @http.route('/open_practical_mek_form', type='http', auth="user", website=True,method=["POST","GET"])
    def open_practical_mek_form(self, **rec):
       
        candidate = request.env['gp.candidate'].sudo()
        
        if request.httprequest.method == "POST":
            print('exittttttttttttttttttttttttttttttt')
            # rec_id = rec['rec_id']
           

            # Convert string values to integers
            # subject_area1 = int(rec['subject_area1'])
            # subject_area2 = int(rec['subject_area2'])
            subject_area3 = int(rec['subject_area3'])
            subject_area4 = int(rec['subject_area4'])
            # subject_area5 = int(rec['subject_area5'])
            # subject_area6 = int(rec['subject_area6'])
            subject_area7 = int(rec['subject_area7'])
            # subject_area8 = int(rec['subject_area8'])
            subject_area9 = int(rec['subject_area9'])
           
            mek_practical_remarks = rec['remarks_practical_mek']
            state = rec['state']


            # Construct the dictionary with integer values
            vals = {
                # 'using_hand_plumbing_tools_task_1': subject_area1,
                # 'using_hand_plumbing_tools_task_2': subject_area2,
                'using_hand_plumbing_tools_task_3': subject_area3,
                'use_of_chipping_tools_paint': subject_area4,
                # 'welding_lathe': subject_area5,
                # 'electrical': subject_area6,
                'welding_lathe': subject_area7,
                # 'lathe': subject_area8,
                'electrical': subject_area9,
                'mek_practical_remarks': mek_practical_remarks,
                'mek_practical_draft_confirm': state
            }
            
            marksheet = request.env['gp.mek.practical.line'].sudo().search([('id','=',rec['mek_practical'])])
            marksheet.write(vals)
            
            return request.redirect("/my/assignments/batches/candidates/"+rec["batch_id"]+"/"+rec['assignment_id'])

            # print('valssssssssssssssssssssssssssssssssssssssssssssssss', vals)

            # Write to the One2many field using the constructed dictionary
            # draft_records.write(vals)

        else:
            print('enterrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr', rec)
            rec_id = rec['rec_id']
            candidate_rec = candidate.search([('id', '=', rec_id)])
            name=candidate_rec.name
            candidate_image = candidate_rec.candidate_image
            # draft_records = candidate_rec.mek_practical_child_line.filtered(lambda line: line.mek_practical_draft_confirm == 'draft')
            mek_prac_marksheet = request.env['gp.mek.practical.line'].sudo().search([('id','=',rec['mek_practical'])])
            assignment_id = int(rec['assignment_id'])
            batch_id = int(rec['batch_id'])
            # exam_date = mek_prac_marksheet.mek_practical_exam_date 'exam_date':exam_date,
            return request.render("bes.mek_practical_marks", {'indos': candidate_rec.indos_no,'candidate_name':name, 'candidate_image': candidate_image, 'candidate': candidate_rec,'mek_prac_marksheet':mek_prac_marksheet,'assignment_id':assignment_id,'batch_id':batch_id, "page_name": "mek_prac"})


    @http.route('/open_cookery_bakery_form', type='http', auth="user", website=True,method=["POST","GET"])
    def open_cookery_bakery_form(self, **rec):

        # import wdb;wdb.set_trace();
        
        candidate = request.env['ccmc.candidate'].sudo()
        
        if request.httprequest.method == "POST":
            print('exittttttttttttttttttttttttttttttt')
            indos = rec['indos']
            
            rec_id = rec['rec_id']
            
            print(rec,'reccccccccccccccccccccccccccccc')
            marksheet = request.env['ccmc.cookery.bakery.line'].sudo().search([('id','=',rec['cookery_bakery'])])

            # Convert string values to integers
            subject_area1 = int(rec['hygiene_grooming'])
            subject_area2 = int(rec['appearance_dish1'])
            subject_area3 = int(rec['taste_dish1'])
            subject_area4 = int(rec['texture_dish1'])
            subject_area5 = int(rec['appearance_dish2'])
            subject_area6 = int(rec['taste_dish2'])
            subject_area7 = int(rec['texture_dish2'])
            subject_area8 = int(rec['appearance_dish3'])
            subject_area9 = int(rec['taste_dish3'])
            subject_area10 = int(rec['texture_dish3'])
            subject_area11 = int(rec['identification_of_ingredients'])
            subject_area12 = int(rec['knowledge_of_menu'])
           

            candidate_rec = candidate.search([('indos_no', '=', indos)])

            # Construct the dictionary with integer values
            vals = {
                'hygien_grooming': subject_area1,
                'appearance': subject_area2,
                'taste': subject_area3,
                'texture': subject_area4,
                'appearance_2': subject_area5,
                'taste_2': subject_area6,
                'texture_2': subject_area7,
                'appearance_3': subject_area8,
                'taste_3': subject_area9,
                'texture_3':subject_area10,
                'identification_ingredians': subject_area11,
                'knowledge_of_menu': subject_area12,
                
            }

            print('valssssssssssssssssssssssssssssssssssssssssssssssss', vals)

            # Write to the One2many field using the constructed dictionary
            # candidate_rec.write({
            #     'cookery_child_line': [(0, 0, vals)]
            # })
            marksheet.write(vals)

            return request.redirect("/my/assignments/batches/candidates/"+rec["batch_id"]+"/"+rec['assignment_id'])
        else:

            rec_id = rec['rec_id']
            ccmc_candidate_rec = candidate.search([('id', '=', rec_id)])
            candidate_indos = ccmc_candidate_rec.indos_no
            candidate_name = ccmc_candidate_rec.name
            candidate_image = ccmc_candidate_rec.candidate_image
        
            print(rec,'cccceeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
            cooker_bakery = request.env['ccmc.cookery.bakery.line'].sudo().search([('id','=',rec['cookery_bakery'])]) 
            # exam_date = cooker_bakery.cookery_exam_date   'exam_date':exam_date, 
            return request.render("bes.cookery_bakery_marks_submit", {'indos': candidate_indos,'cookery_bakery':cooker_bakery,'candidate_name': candidate_name, 'candidate_image': candidate_image,   "page_name": "cooker_bakery_form"})
        
            # return request.render("bes.gsk_oral_marks_submit", {'indos': candidate_indos, 'gsk_marksheet': gsk_marksheet, 'candidate_name': name, 'candidate_image': candidate_image, 'candidate': candidate_rec , 'exam_date':gsk_marksheet.gsk_oral_exam_date, "page_name": "gsk_oral"})

    # @http.route('/open_ccmc_gsk_oral_form', type='http', auth="user", website=True,method=["POST","GET"])
    # def open_ccmc_gsk_oral_form(self, **rec):
    #     candidate = request.env['ccmc.candidate'].sudo()
        
    #     if request.httprequest.method == "POST":
    #         print('exittttttttttttttttttttttttttttttt')
    #         # indos = rec['indos']
            
    #         marksheet = request.env['ccmc.oral.line'].sudo().search([('id','=',rec['ccmc_oral'])])

    #         # Convert string values to integers                    
    #         subject_area1 = int(rec['ccmc_gsk'])
    #         # subject_area2 = int(rec['safety_ccmc'])
    #         subject_area3 = int(rec['house_keeping'])
    #         subject_area4 = int(rec['f_b'])
    #         subject_area5 = int(rec['orals_house_keeping'])
    #         subject_area6 = int(rec['attitude_proffessionalism'])
    #         subject_area7 = int(rec['equipment_identification'])

    #         # Construct the dictionary with integer values
    #         vals = {
    #             'gsk_ccmc': subject_area1,
    #             # 'safety_ccmc': subject_area2,
    #             'house_keeping': subject_area3,
    #             'f_b': subject_area4,
    #             'orals_house_keeping': subject_area5,
    #             'attitude_proffessionalism': subject_area6,
    #             'equipment_identification': subject_area7,
               
                
    #         }

    #         # Write to the One2many field using the constructed dictionary
    #         marksheet.write(vals)
            
    #         return request.redirect("/my/assignments/batches/candidates/"+rec["batch_id"]+"/"+rec['assignment_id'])

    #     else:

    #         rec_id = rec['rec_id']
            
    #         ccmc_candidate_rec = candidate.search([('id', '=', rec_id)])
    #         candidate_indos = ccmc_candidate_rec.indos_no
    #         candidate_name = ccmc_candidate_rec.name
    #         candidate_image = ccmc_candidate_rec.candidate_image
        
    #         ccmc_oral = request.env['ccmc.oral.line'].sudo().search([('id','=',rec['ccmc_oral'])]) 
    #         # exam_date = ccmc_oral.ccmc_oral_exam_date 'exam_date':exam_date, 
            
    #         return request.render("bes.ccmc_gsk_oral_marks_submit", {'indos': candidate_indos,'ccmc_oral':ccmc_oral ,'candidate_name': candidate_name, 'candidate_image': candidate_image, "page_name": "ccmc_gsk_oral"})

    @http.route('/open_ccmc_oral_form', type='http', auth="user", website=True,method=["POST","GET"])
    def open_ccmc_oral_form(self, **rec):

        # import wdb;wdb.set_trace();
        
        candidate = request.env['ccmc.candidate'].sudo()
        
        if request.httprequest.method == "POST":
            print('exittttttttttttttttttttttttttttttt')
            # indos = rec['indos']
            
            marksheet = request.env['ccmc.oral.line'].sudo().search([('id','=',rec['ccmc_oral'])])

            # Convert string values to integers                    
            subject_area1 = int(rec['ccmc_gsk'])
            # subject_area2 = int(rec['safety_ccmc'])
            subject_area3 = int(rec['house_keeping'])
            subject_area4 = int(rec['f_b'])
            subject_area5 = int(rec['orals_house_keeping'])
            subject_area6 = int(rec['attitude_proffessionalism'])
            subject_area7 = int(rec['equipment_identification'])

            # Construct the dictionary with integer values
            vals = {
                'gsk_ccmc': subject_area1,
                # 'safety_ccmc': subject_area2,
                'house_keeping': subject_area3,
                'f_b': subject_area4,
                'orals_house_keeping': subject_area5,
                'attitude_proffessionalism': subject_area6,
                'equipment_identification': subject_area7,
               
                
            }

            # Write to the One2many field using the constructed dictionary
            marksheet.write(vals)
            
            return request.redirect("/my/assignments/batches/candidates/"+rec["batch_id"]+"/"+rec['assignment_id'])

        else:

            rec_id = rec['rec_id']
            
            ccmc_candidate_rec = candidate.search([('id', '=', rec_id)])
            candidate_indos = ccmc_candidate_rec.indos_no
            candidate_name = ccmc_candidate_rec.name
            candidate_image = ccmc_candidate_rec.candidate_image
        
            ccmc_oral = request.env['ccmc.oral.line'].sudo().search([('id','=',rec['ccmc_oral'])]) 
            # exam_date = ccmc_oral.ccmc_oral_exam_date 'exam_date':exam_date, 
            
            return request.render("bes.ccmc_oral_marks_submit", {'indos': candidate_indos,'ccmc_oral':ccmc_oral ,'candidate_name': candidate_name, 'candidate_image': candidate_image, "page_name": "ccmc_oral"})
        
    @http.route('/open_ccmc_gsk_oral_form', type='http', auth="user", website=True,method=["POST","GET"])
    def open_ccmc_gsk_oral_form(self, **rec):

        # import wdb;wdb.set_trace();
        
        candidate = request.env['ccmc.candidate'].sudo()
        
        if request.httprequest.method == "POST":
            print('exittttttttttttttttttttttttttttttt')
            # indos = rec['indos']
            
            marksheet = request.env['ccmc.gsk.oral.line'].sudo().search([('id','=',rec['ccmc_gsk_oral'])])

            # Convert string values to integers                    
            gsk_ccmc = int(rec['gsk_ccmc'])
            safety_ccmc = int(rec['safety_ccmc'])

            # Construct the dictionary with integer values
            vals = {
                'gsk_ccmc': gsk_ccmc,
                'safety_ccmc': safety_ccmc,
               
                
            }

            # Write to the One2many field using the constructed dictionary
            marksheet.write(vals)
            
            return request.redirect("/my/assignments/batches/candidates/"+rec["batch_id"]+"/"+rec['assignment_id'])

        else:

            rec_id = rec['rec_id']
            
            ccmc_candidate_rec = candidate.search([('id', '=', rec_id)])
            candidate_indos = ccmc_candidate_rec.indos_no
            candidate_name = ccmc_candidate_rec.name
            candidate_image = ccmc_candidate_rec.candidate_image
        
            ccmc_gsk_oral = request.env['ccmc.gsk.oral.line'].sudo().search([('id','=',rec['ccmc_gsk_oral'])]) 
            # exam_date = ccmc_oral.ccmc_oral_exam_date 'exam_date':exam_date, 
            
            return request.render("bes.ccmc_gsk_oral_marks_submit", {'indos': candidate_indos,'ccmc_gsk_oral':ccmc_gsk_oral ,'candidate_name': candidate_name, 'candidate_image': candidate_image, "page_name": "ccmc_oral"})


        
    @http.route('/open_candidate_form/download_gsk_marksheet/<int:batch_id>/<int:assignment_id>', type='http', auth="user", website=True)
    def download_gsk_marksheet(self,batch_id,assignment_id, **rec):
        
        user_id = request.env.user.id
        examiner = request.env['bes.examiner'].sudo().search([('user_id','=',user_id)])
        batch_id = batch_id
        examiner = request.env['bes.examiner'].sudo().search([('user_id','=',user_id)])
        # batch_info = request.env['exam.type.oral.practical'].sudo().search([('dgs_batch.id','=',batch_id)])
        examiner_assignments = request.env['exam.type.oral.practical.examiners'].sudo().search([('dgs_batch.id','=',batch_id),('id','=',assignment_id)])

        marksheets = request.env['exam.type.oral.practical.examiners.marksheet'].sudo().search([('examiners_id','=',assignment_id)])

        # import wdb;wdb.set_trace();
        
        for exam in examiner_assignments:
            if examiner.subject_id.name == 'GSK':
                assignment = exam.id
                
        # for candidate in assignment.gp_oral_prac

        excel_buffer = io.BytesIO()

        # Create a new Excel workbook and add a worksheet
        workbook = xlsxwriter.Workbook(excel_buffer)
        # workbook   = xlsxwriter.Workbook('filename.xlsx')

        gsk_oral_sheet = workbook.add_worksheet('GSK Oral')
        gsk_practical_sheet = workbook.add_worksheet('GSK Practical')
        
        locked = workbook.add_format({'locked':True})
        unlocked = workbook.add_format({'locked':False})
        # Set the wrap text format
        wrap_format = workbook.add_format({'text_wrap': True})
        
        #For GSK Oral Marksheet
        gsk_oral_sheet.set_column('A:XDF',None, unlocked)
        gsk_oral_sheet.set_column('A2:A2',35, unlocked)
        gsk_oral_sheet.set_column('B2:B2',10, unlocked)
        gsk_oral_sheet.set_column('C2:C2',20, unlocked)
        gsk_oral_sheet.set_column('D2:E2',25, unlocked)
        gsk_oral_sheet.set_column('F2:F2',30, unlocked)
        gsk_oral_sheet.set_column('G:G',15, unlocked)
            
        gsk_oral_sheet.protect()
        date_format = workbook.add_format({'num_format': 'dd-mmm-yy','locked':False})

        header_format = workbook.add_format({
                                                'bold': True,
                                                'align': 'center',
                                                'valign': 'vcenter',
                                                'font_color': 'black',
                                                'locked':True,
                                                'text_wrap': True,
                                            })
        
        merge_format = workbook.add_format({
                                                'bold':     True,
                                                'align':    'center',
                                                'valign':   'vcenter',
                                                'font_size': 20,
                                                'font_color': 'black',
                                            })
        instruction = workbook.add_format({
                                                'bold':     True,
                                                # 'align':    'center',
                                                'valign':   'vcenter',
                                                'font_size': 10,
                                                'font_color': 'red',
                                            })

        gsk_oral_sheet.merge_range("A1:D1", examiner_assignments.institute_id.name, merge_format)
        gsk_oral_sheet.write("E1:H1", "After filling the marks please save the file. \n Go back to the page where you download this excel and upload it.",instruction)
        header_oral = ['Name of the Candidate','Roll No', 'Candidate Code No',
          'Subject area 1 and 2 and 3 \n Minimum 8 question \n 25 marks',
          'Subject area 4 and 5 and 6 \n Minimum 9 question \n 25 marks',
          'Practical Record Book and Journal \n 25 Marks', 'Remarks']
        for col, value in enumerate(header_oral):
            gsk_oral_sheet.write(1, col, value, header_format)
        
          
        candidate_list = [] #List of Candidates
        roll_no = []
        candidate_code = [] #Candidates Code No.

        for candidate in marksheets:
            candidate_list.append(candidate.gp_candidate.name)
            roll_no.append(candidate.gp_marksheet.exam_id)
            candidate_code.append(candidate.gp_candidate.candidate_code)
        
        # import wdb;wdb.set_trace();
        
        for i, candidate in enumerate(candidate_list):
            gsk_oral_sheet.write('A{}'.format(i+3), candidate, locked)

        for i, code in enumerate(roll_no):
            gsk_oral_sheet.write('B{}'.format(i+3), code, locked)

        for i, code in enumerate(candidate_code):
            gsk_oral_sheet.write('C{}'.format(i+3), code, locked)

        marks_values_5 = [1,2,3,4,5]
        marks_values_6 = [1,2,3,4,5,6]
        marks_values_8 = [1,2,3,4,5,6,7,8]
        marks_values_10 = [1,2,3,4,5,6,7,8,9,10]
        marks_values_12 = [1,2,3,4,5,6,7,8,9,10,11,12]
        marks_values_18 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]
        marks_values_25 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]
        marks_values_30 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
        
        gsk_oral_sheet.data_validation('D3:D1048576', {'validate': 'list', 'source': marks_values_25 })
        gsk_oral_sheet.data_validation('E3:E1048576', {'validate': 'list', 'source': marks_values_25 })
        gsk_oral_sheet.data_validation('F3:F1048576', {'validate': 'list', 'source': marks_values_25 })
        
        remarks = ['Absent','Good','Average','Weak']
        gsk_oral_sheet.data_validation('G3:G1048576', {'validate': 'list', 'source': remarks })

        #For GSK Practical Marksheet
        gsk_practical_sheet.set_column('A:XDF',None, unlocked)
        gsk_practical_sheet.set_column('A2:A2',35, unlocked)
        gsk_practical_sheet.set_column('B2:B2',10, unlocked)
        gsk_practical_sheet.set_column('C2:C2',20, unlocked)
        gsk_practical_sheet.set_column('D2:G2',35, unlocked)
        gsk_practical_sheet.set_column('H2:H2',15, unlocked)
        gsk_practical_sheet.set_column('I2:I2',15, unlocked)
        gsk_practical_sheet.set_column('N2:N2',15, unlocked)
            
        gsk_practical_sheet.protect()
        
        
        # Merge 3 cells over two rows.
        gsk_practical_sheet.merge_range("A1:G1", examiner_assignments.institute_id.name, merge_format)
        
        header_prac = ['Name of the Candidate','Roll No', 'Candidate Code No',
          '-Climb the mast with safe practices \n -Prepare and throw Heaving Line \n Rigging Bosun\'s Chair and self lower and hoist \n 30 Marks', #D
          '-Rig a stage for painting shipside \n -Rig a Pilot Ladder \n -Rig scaffolding to work at a height  \n 30 marks',#E
          '-Making fast Ropes and Wires \n -Use Rope-Stopper / Chain Stopper \n -Knots, Bends, Hitches \n -Whippings/Seizing/Splicing Ropes/Wires \n ·Taking Soundings with sounding rod / sounding taps \n ·Reading of Draft \n .Mannual lifting of weight (30 Marks)',#G
          '-Recognise buyos and flags \n -Hoisting a Flag correctly \n -Steering and Helm Orders \n 10 Marks',#G
        #   '-Rigging Bosuns Chair and self lower and hoist \n 8 marks',
            'Remarks']
        for col, value in enumerate(header_prac):
            gsk_practical_sheet.write(1, col, value, header_format)
        
        # # import wdb;wdb.set_trace();
        
        for i, candidate in enumerate(candidate_list):
            gsk_practical_sheet.write('A{}'.format(i+3), candidate, locked)
            
        for i, code in enumerate(roll_no):
            gsk_practical_sheet.write('B{}'.format(i+3), code, locked)

        for i, code in enumerate(candidate_code):
            gsk_practical_sheet.write('C{}'.format(i+3), code, locked)
        
        gsk_practical_sheet.data_validation('D3:D1048576', {'validate': 'list', 'source': marks_values_30 })
        gsk_practical_sheet.data_validation('E3:E1048576', {'validate': 'list', 'source': marks_values_30 })
        gsk_practical_sheet.data_validation('F3:F1048576', {'validate': 'list', 'source': marks_values_30 })
        gsk_practical_sheet.data_validation('G3:G1048576', {'validate': 'list', 'source': marks_values_10 })

        gsk_practical_sheet.data_validation('H3:H1048576', {'validate': 'list', 'source': remarks })
        # gsk_practical_sheet.data_validation('I3:I1048576', {'validate': 'list', 'source': marks_values_8 })
        # gsk_practical_sheet.data_validation('J3:J1048576', {'validate': 'list', 'source': marks_values_8 })
        # gsk_practical_sheet.data_validation('K3:K1048576', {'validate': 'list', 'source': marks_values_18 })
        # gsk_practical_sheet.data_validation('L3:L1048576', {'validate': 'list', 'source': marks_values_18 })
        
        # gsk_practical_sheet.data_validation('M3:M1048576', {'validate': 'list', 'source': remarks })
        
        workbook.close()

        # Set the buffer position to the beginning
        excel_buffer.seek(0)

        date = examiner_assignments[0].exam_date
        
        file_name = examiner.name+"-GSK-"+str(date)+".xlsx"
        
        # Generate a response with the Excel file
        response = request.make_response(
            excel_buffer.getvalue(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', 'attachment; filename='+file_name)
            ]
        )

        # Clean up the buffer
        excel_buffer.close()

        return response
    
    
    
    
    
    
    @http.route('/open_candidate_form/download_mek_marksheet/<int:batch_id>/<int:assignment_id>', type='http', auth="user", website=True)
    def download_mek_marksheet(self,batch_id,assignment_id, **rec):
        
        user_id = request.env.user.id
        examiner = request.env['bes.examiner'].sudo().search([('user_id','=',user_id)])
        batch_id = batch_id
        # batch_info = request.env['exam.type.oral.practical'].sudo().search([('dgs_batch.id','=',batch_id)])
        examiner_assignments = request.env['exam.type.oral.practical.examiners'].sudo().search([('dgs_batch.id','=',batch_id),('examiner','=',examiner.id)])

        marksheets = request.env['exam.type.oral.practical.examiners.marksheet'].sudo().search([('examiners_id','=',assignment_id)])

        # import wdb;wdb.set_trace();
        excel_buffer = io.BytesIO()

        # Create a new Excel workbook and add a worksheet
        workbook = xlsxwriter.Workbook(excel_buffer)
        # workbook   = xlsxwriter.Workbook('filename.xlsx')

        mek_oral_sheet = workbook.add_worksheet('MEK Oral')
        mek_practical_sheet = workbook.add_worksheet('MEK Practical')
        
        locked = workbook.add_format({'locked':True})
        unlocked = workbook.add_format({'locked':False})
        # Set the wrap text format
        wrap_format = workbook.add_format({'text_wrap': True})
        
        #For GSK Oral Marksheet
        mek_oral_sheet.set_column('A:XDF',None, unlocked)
        mek_oral_sheet.set_column('A2:A2',35, unlocked)
        mek_oral_sheet.set_column('B2:B2',10, unlocked)
        mek_oral_sheet.set_column('C2:C2',20, unlocked)
        mek_oral_sheet.set_column('D2:F2',20, unlocked)
        mek_oral_sheet.set_column('G2:G2',15, unlocked)
        mek_oral_sheet.set_column('H2:H2',15, unlocked)
            
        mek_oral_sheet.protect()
        date_format = workbook.add_format({'num_format': 'dd-mmm-yy','locked':False})

        header_format = workbook.add_format({
                                                'bold': True,
                                                'align': 'center',
                                                'valign': 'vcenter',
                                                'font_color': 'black',
                                                'locked':True,
                                                'text_wrap': True,
                                            })
        
        merge_format = workbook.add_format({
                                                'bold':     True,
                                                'align':    'center',
                                                'valign':   'vcenter',
                                                'font_size': 20,
                                                'font_color': 'black',
                                            })
        
        instruction = workbook.add_format({
                                                'bold':     True,
                                                # 'align':    'center',
                                                'valign':   'vcenter',
                                                'font_size': 10,
                                                'font_color': 'red',
                                            })

        mek_oral_sheet.merge_range("A1:D1", examiner_assignments.institute_id.name, merge_format)
        mek_oral_sheet.write("E1:H1", "After filling the marks please save the file. \n Go back to the page where you download this excel and upload it.",instruction)
       
        header_oral = ['Name of the Candidate','Roll No', 'Candidate Code No',
          'Uses of Hand/ Plumbing/Carpentry Tools \n Use of chipping Tools & Brushes & Paints \n 20 Marks',
          'Welding \n Lathe /Drill/Grinder \n 20 Marks',
          'Electrical  \n 10 Marks',
          'Journal \n 25 Marks', 'Remarks']
        for col, value in enumerate(header_oral):
            mek_oral_sheet.write(1, col, value, header_format)
        
          
        candidate_list = [] #List of Candidates
        candidate_code = [] #Candidates Code No.
        roll_no = []

        for candidate in marksheets:
            candidate_list.append(candidate.gp_candidate.name)
            candidate_code.append(candidate.gp_candidate.candidate_code)

            # import wdb;wdb.set_trace();
            roll_no.append(candidate.gp_marksheet.exam_id)
        
        
        for i, candidate in enumerate(candidate_list):
            mek_oral_sheet.write('A{}'.format(i+3), candidate, locked)
        
        for i, code in enumerate(roll_no):
            mek_oral_sheet.write('B{}'.format(i+3), code, locked)

        for i, code in enumerate(candidate_code):
            mek_oral_sheet.write('C{}'.format(i+3), code, locked)
        
        marks_values_10 = [1,2,3,4,5,6,7,8,9,10]
        marks_values_20 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
        marks_values_25 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]
        marks_values_30 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
        
        mek_oral_sheet.data_validation('D3:D1048576', {'validate': 'list', 'source': marks_values_20 })
        mek_oral_sheet.data_validation('E3:E1048576', {'validate': 'list', 'source': marks_values_20 })
        # mek_oral_sheet.data_validation('F3:F1048576', {'validate': 'list', 'source': marks_values_10 })
        # mek_oral_sheet.data_validation('G3:G1048576', {'validate': 'list', 'source': marks_values_10 })
        mek_oral_sheet.data_validation('F3:F1048576', {'validate': 'list', 'source': marks_values_10 })
        mek_oral_sheet.data_validation('G3:G1048576', {'validate': 'list', 'source': marks_values_25 })
        
        remarks = ['Absent','Good','Average','Weak']
        mek_oral_sheet.data_validation('H3:H1048576', {'validate': 'list', 'source': remarks })
        
        #For GSK Practical Marksheet
        mek_practical_sheet.set_column('A:XDF',None, unlocked)
        mek_practical_sheet.set_column('A2:A2',35, unlocked)
        mek_practical_sheet.set_column('B2:B2',10, unlocked)
        mek_practical_sheet.set_column('C2:C2',20, unlocked)
        mek_practical_sheet.set_column('D2:G2',25, unlocked)
        mek_practical_sheet.set_column('H2:H2',15, unlocked)
            
        mek_practical_sheet.protect()
        
        
        # Merge 3 cells over two rows.
        mek_practical_sheet.merge_range("A1:G1",examiner_assignments.institute_id.name, merge_format)
        
        header_prac = ['Name of the Candidate','Roll No', 'Candidate Code No',
        #   '-Using Hand & Plumbing Tools \n -Task 1 \n 10 Marks', #D
        #   '-Using Hand & Plumbing Tools \n -Task 2 \n 10 Marks', #E
          '-Using Hand & Plumbing Tools \n -3 Task  \n 30 Marks', #F
          '-Use of Chipping Tools & paint Brushes \n -Use of Carpentry Tools \n -Use of Measuring Instruments 30 marks', #G
        #   '-Use of Carpentry Tools \n 10 marks', #H
        #   '-Use of Measuring Instruments \n 10 marks', #I
          '-Welding (1 Task)  \n -Lathe Work (1 Task)\n  30 marks', #J
        #   '-Lathe Work (1 Task) \n 10 Marks', #K
          '-Electrical (1 Task) \n 10 Marks', #L
           'Remarks']
        for col, value in enumerate(header_prac):
            mek_practical_sheet.write(1, col, value, header_format)
        
        # import wdb;wdb.set_trace();
        
        for i, candidate in enumerate(candidate_list):
            mek_practical_sheet.write('A{}'.format(i+3), candidate, locked)

        for i, code in enumerate(roll_no):
            mek_practical_sheet.write('B{}'.format(i+3), code, locked)

        for i, code in enumerate(candidate_code):
            mek_practical_sheet.write('C{}'.format(i+3), code, locked)
        
        mek_practical_sheet.data_validation('D3:D1048576', {'validate': 'list', 'source': marks_values_30 })
        mek_practical_sheet.data_validation('E3:E1048576', {'validate': 'list', 'source': marks_values_30 })
        mek_practical_sheet.data_validation('F3:F1048576', {'validate': 'list', 'source': marks_values_30 })
        mek_practical_sheet.data_validation('G3:G1048576', {'validate': 'list', 'source': marks_values_10 })
        mek_practical_sheet.data_validation('H3:H1048576', {'validate': 'list', 'source': remarks })
        # mek_practical_sheet.data_validation('I3:I1048576', {'validate': 'list', 'source': marks_values_10 })
        # mek_practical_sheet.data_validation('J3:J1048576', {'validate': 'list', 'source': marks_values_30 })
        # mek_practical_sheet.data_validation('K3:K1048576', {'validate': 'list', 'source': marks_values_10 })
        # mek_practical_sheet.data_validation('L3:L1048576', {'validate': 'list', 'source': marks_values_10 })
        
        # mek_practical_sheet.data_validation('M3:M1048576', {'validate': 'list', 'source': remarks })
        
        
        workbook.close()

        # Set the buffer position to the beginning
        excel_buffer.seek(0)
        
        date = examiner_assignments[0].exam_date
        
        file_name = examiner.name+"-MEK-"+str(date)+".xlsx"

       
        # Generate a response with the Excel file
        response = request.make_response(
            excel_buffer.getvalue(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', 'attachment; filename='+file_name)
            ]
        )

        # Clean up the buffer
        excel_buffer.close()

        return response
    


    @http.route('/my/uploadgskmarksheet', type='http', auth="user", website=True)
    def upload_gsk_marksheet(self,**kw):
        user_id = request.env.user.id
        batch_id = int(kw['batch_id'])
        # import wdb;wdb.set_trace();
        file_content = kw.get("fileUpload").read()
        filename = kw.get('fileUpload').filename

        # workbook = xlsxwriter.Workbook(BytesIO(file_content))
        workbook = xlrd.open_workbook(file_contents=file_content)
        worksheet_oral = workbook.sheet_by_index(0)
        for row_num in range(2, worksheet_oral.nrows):  # Assuming first row contains headers
            row = worksheet_oral.row_values(row_num)
            
            roll_no = row[1]
            candidate_code_no = row[2]  
            subject_area_1_2_3 = row[3]  
            subject_area_4_5_6 = row[4]  
            # subject_area_3 = row[5]  
            # subject_area_4 = row[6]  
            # subject_area_5 = row[7]  
            # subject_area_6 = row[8] 
            practical_journal = row[5] 
            total_marks = 0  # Initialize total_marks to 0
            if subject_area_1_2_3:
                total_marks += int(subject_area_1_2_3)
            if subject_area_4_5_6:
                total_marks += int(subject_area_4_5_6)
            # if subject_area_3:
            #     total_marks += int(subject_area_3)
            # if subject_area_4:
            #     total_marks += int(subject_area_4)
            # if subject_area_5:
            #     total_marks += int(subject_area_5)
            # if subject_area_6:
            #     total_marks += int(subject_area_6)
            if practical_journal:
                total_marks += int(practical_journal)
                    
            remarks = row[6]
            
            candidate = request.env['gp.exam.schedule'].sudo().search([('exam_id','=',roll_no)])
            
            if candidate and candidate.gsk_oral:
                candidate.gsk_oral.sudo().write({
                    'subject_area_1_2_3':subject_area_1_2_3,
                    'subject_area_4_5_6':subject_area_4_5_6,
                    # 'subject_area_3':subject_area_3,
                    # 'subject_area_4':subject_area_4,
                    # 'subject_area_5':subject_area_5,
                    # 'subject_area_6':subject_area_6,
                    'practical_record_journals':practical_journal,
                    'gsk_oral_total_marks':total_marks,
                    'gsk_oral_remarks':remarks,


                })

        worksheet_practical = workbook.sheet_by_index(1)
        for row_num in range(2, worksheet_practical.nrows):  # Assuming first row contains headers
            row = worksheet_practical.row_values(row_num)
            
            roll_no = row[1]
            candidate_code_no = row[2]  
            climbing_mast_bosun_chair = row[3]  
            rig_stage_rig_pilot_rig_scaffolding = row[4]  
            fast_ropes_knots_bend_sounding_rod = row[5]  
            buoy_flags_recognition = row[6]  
            # rig_pilot = row[7]  
            # rig_scaffolding = row[8] 
            # fast_ropes = row[9] 
            # knots_bend = row[10]
            # sounding_rod = row[11] 

            gsk_practical_total_marks = 0  # Initialize gsk_practical_total_marks to 0
            if climbing_mast_bosun_chair:
                gsk_practical_total_marks += int(climbing_mast_bosun_chair)
            if buoy_flags_recognition:
                gsk_practical_total_marks += int(buoy_flags_recognition)
            if rig_stage_rig_pilot_rig_scaffolding:
                gsk_practical_total_marks += int(rig_stage_rig_pilot_rig_scaffolding)
            if fast_ropes_knots_bend_sounding_rod:
                gsk_practical_total_marks += int(fast_ropes_knots_bend_sounding_rod)
            # if rig_pilot:
            #     gsk_practical_total_marks += int(rig_pilot)
            # if rig_scaffolding:
            #     gsk_practical_total_marks += int(rig_scaffolding)
            # if fast_ropes:
            #     gsk_practical_total_marks += int(fast_ropes)
            # if knots_bend:
            #     gsk_practical_total_marks += int(knots_bend)
            # if sounding_rod:
            #     gsk_practical_total_marks += int(sounding_rod)
                
            gsk_practical_remarks = row[7]

            candidate = request.env['gp.exam.schedule'].sudo().search([('exam_id','=',roll_no)])
            if candidate and candidate.gsk_prac:
                candidate.gsk_prac.sudo().write({
                    'climbing_mast_bosun_chair':climbing_mast_bosun_chair,
                    'buoy_flags_recognition':buoy_flags_recognition,
                    'rig_stage_rig_pilot_rig_scaffolding':rig_stage_rig_pilot_rig_scaffolding,
                    'fast_ropes_knots_bend_sounding_rod':fast_ropes_knots_bend_sounding_rod,
                    # 'rig_pilot':rig_pilot,
                    # 'rig_scaffolding':rig_scaffolding,
                    # 'fast_ropes':fast_ropes,
                    # 'knots_bend':knots_bend,
                    # 'sounding_rod':sounding_rod,
                    'gsk_practical_total_marks':gsk_practical_total_marks,
                    'gsk_practical_remarks':gsk_practical_remarks


                })
        examiner = request.env['bes.examiner'].sudo().search([('user_id','=',user_id)])
        examiner_assignments = request.env['exam.type.oral.practical.examiners'].sudo().search([('dgs_batch.id','=',batch_id),('examiner','=',examiner.id)])
        examiner_assignments.write({
            'marksheet_uploaded' : True 
        })

        # marksheets = request.env['exam.type.oral.practical.examiners.marksheet'].sudo().search([('examiners_id','=',assignment_id)])
        
            
        # return request.redirect("/my/assignments/batches/"+str(batch_id) + '/' +str(batch_id))
        return request.render("bes.examiner_assignment_candidate_list")



    @http.route('/my/uploadmekmarksheet', type='http', auth="user", website=True)
    def upload_mek_marksheet(self,**kw):
        user_id = request.env.user.id
        # import wdb;wdb.set_trace();
        batch_id = int(kw['mek_batch_ids'])
        file_content = kw.get("fileUpload").read()
        filename = kw.get('fileUpload').filename

        # workbook = xlsxwriter.Workbook(BytesIO(file_content))
        workbook = xlrd.open_workbook(file_contents=file_content)
        worksheet_oral = workbook.sheet_by_index(0)
        for row_num in range(2, worksheet_oral.nrows):  # Assuming first row contains headers
            row = worksheet_oral.row_values(row_num)
            
            roll_no = row[1]
            candidate_code_no = row[2]  
            using_of_tools = row[3]  
            welding_more = row[4]  
            # welding = row[5]  
            # grinder = row[6]  
            electrical = row[5]  
            mek_journal = row[6] 

            total_marks = 0  # Initialize gsk_practical_total_marks to 0
            if using_of_tools:
                total_marks += int(using_of_tools)
            if welding_more:
                total_marks += int(welding_more)
            # if welding:
            #     total_marks += int(welding)
            # if grinder:
            #     total_marks += int(grinder)
            if electrical:
                total_marks += int(electrical)
            if mek_journal:
                total_marks += int(mek_journal)  

            remarks = row[7]
            
            candidate = request.env['gp.exam.schedule'].sudo().search([('exam_id','=',roll_no)])
            if candidate and candidate.mek_oral:
                candidate.mek_oral.sudo().write({
                    'using_of_tools':using_of_tools,
                    'welding_lathe_drill_grinder':welding_more,
                    # 'welding':welding,
                    # 'lathe_drill_grinder':grinder,
                    'electrical':electrical,
                    'journal':mek_journal,
                    'mek_oral_total_marks':total_marks,
                    'mek_oral_remarks':remarks,


                })

        worksheet_practical = workbook.sheet_by_index(1)
        for row_num in range(2, worksheet_practical.nrows):  # Assuming first row contains headers
            row = worksheet_practical.row_values(row_num)
            
            roll_no = row[1]
            candidate_code_no = row[2]  
            using_hand_plumbing_tools_task_3 = row[3]  
            # using_hand_plumbing_tools_task_2 = row[4]  
            # using_hand_plumbing_tools_task_3 = row[5]  
            use_of_chipping_tools_paint = row[4]  
            # use_of_carpentry = row[7]  
            # use_of_measuring_instruments = row[8] 
            welding_lathe = row[5]                   
            # lathe = row[10]
            electrical = row[6]             

            # mek_practical_total_marks = row[12] 
            mek_practical_total_marks = 0  # Initialize gsk_practical_total_marks to 0
            # if using_hand_plumbing_tools_task_1:
            #     mek_practical_total_marks += int(using_hand_plumbing_tools_task_1)
            # if using_hand_plumbing_tools_task_2:
            #     mek_practical_total_marks += int(using_hand_plumbing_tools_task_2)
            if using_hand_plumbing_tools_task_3:
                mek_practical_total_marks += int(using_hand_plumbing_tools_task_3)
            if use_of_chipping_tools_paint:
                mek_practical_total_marks += int(use_of_chipping_tools_paint)
            # if use_of_carpentry:
            #     mek_practical_total_marks += int(use_of_carpentry)
            # if use_of_measuring_instruments:
            #     mek_practical_total_marks += int(use_of_measuring_instruments) 
            if welding_lathe:
                mek_practical_total_marks += int(welding_lathe) 
            # if lathe:
            #     mek_practical_total_marks += int(lathe) 
            if electrical:
                mek_practical_total_marks += int(electrical) 

            mek_practical_remarks = row[7]

            candidate = request.env['gp.exam.schedule'].sudo().search([('exam_id','=',roll_no)])
            if candidate and candidate.mek_prac:
                candidate.mek_prac.sudo().write({
                    # 'using_hand_plumbing_tools_task_1':using_hand_plumbing_tools_task_1,
                    # 'using_hand_plumbing_tools_task_2':using_hand_plumbing_tools_task_2,
                    'using_hand_plumbing_tools_task_3':using_hand_plumbing_tools_task_3,
                    'use_of_chipping_tools_paint':use_of_chipping_tools_paint,
                    # 'use_of_carpentry':use_of_carpentry,
                    # 'use_of_measuring_instruments':use_of_measuring_instruments,
                    'welding_lathe':welding_lathe,
                    # 'lathe':lathe,
                    'electrical':electrical,
                    'mek_practical_total_marks':mek_practical_total_marks,
                    'mek_practical_remarks':mek_practical_remarks


                })
        examiner = request.env['bes.examiner'].sudo().search([('user_id','=',user_id)])
        examiner_assignments = request.env['exam.type.oral.practical.examiners'].sudo().search([('dgs_batch.id','=',batch_id),('examiner','=',examiner.id)])
        examiner_assignments.write({
            'marksheet_uploaded' : True 
        })
        # marksheets = request.env['exam.type.oral.practical.examiners.marksheet'].sudo().search([('examiners_id','=',assignment_id)])
        
            
        # return request.redirect("/my/assignments/batches/"+str(batch_id))
        return request.render("bes.examiner_assignment_candidate_list")



            
    
    # @http.route('/open_ccmc_candidate_form/download_ccmc_oral_marksheet/<int:batch_id>/<int:assignment_id>', type='http', auth="user", website=True)
    # def download_ccmc_oral_marksheet(self,batch_id,assignment_id, **rec):
        
    #     user_id = request.env.user.id
    #     examiner = request.env['bes.examiner'].sudo().search([('user_id','=',user_id)])
    #     batch_id = batch_id
    #     examiner = request.env['bes.examiner'].sudo().search([('user_id','=',user_id)])
    #     # batch_info = request.env['exam.type.oral.practical'].sudo().search([('dgs_batch.id','=',batch_id)])
    #     examiner_assignments = request.env['exam.type.oral.practical.examiners'].sudo().search([('dgs_batch.id','=',batch_id),('examiner','=',examiner.id)])
    #     # import wdb;wdb.set_trace();
    #     marksheets = request.env['exam.type.oral.practical.examiners.marksheet'].sudo().search([('examiners_id','=',assignment_id)])
        
    #     excel_buffer = io.BytesIO()

    #     # Create a new Excel workbook and add a worksheet
    #     workbook = xlsxwriter.Workbook(excel_buffer)
    #     # workbook   = xlsxwriter.Workbook('filename.xlsx')

    #     ccmc_oral_summary_sheet = workbook.add_worksheet('CCMC Oral')
        
    #     locked = workbook.add_format({'locked':True})
    #     unlocked = workbook.add_format({'locked':False})
    #     # Set the wrap text format
    #     wrap_format = workbook.add_format({'text_wrap': True})
        
                
    #     marks_values_5 = [1,2,3,4,5]
    #     marks_values_6 = [1,2,3,4,5,6]
    #     marks_values_8 = [1,2,3,4,5,6,7,8]
    #     marks_values_9 = [1,2,3,4,5,6,7,8,9]
    #     marks_values_10 = [1,2,3,4,5,6,7,8,9,10]
    #     marks_values_20 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
                      
    #     #For GSK Practical Marksheet
    #     ccmc_oral_summary_sheet.set_column('A:XDF',None, unlocked)
    #     ccmc_oral_summary_sheet.set_column('A2:A2',35, unlocked)
    #     ccmc_oral_summary_sheet.set_column('B2:B2',10, unlocked)
    #     ccmc_oral_summary_sheet.set_column('C2:C2',20, unlocked)
    #     ccmc_oral_summary_sheet.set_column('D2:J2',25, unlocked)
    #     ccmc_oral_summary_sheet.set_column('K2:K2',15, unlocked)
            
    #     ccmc_oral_summary_sheet.protect()
        
    #     header_format = workbook.add_format({
    #                                             'bold': True,
    #                                             'align': 'center',
    #                                             'valign': 'vcenter',
    #                                             'font_color': 'black',
    #                                             'locked':True,
    #                                             'text_wrap': True,
    #                                         })
        
    #     merge_format = workbook.add_format({
    #                                             'bold':     True,
    #                                             'align':    'center',
    #                                             'valign':   'vcenter',
    #                                             'font_size': 20,
    #                                             'font_color': 'black',
    #                                         })
        
    #     # Merge 3 cells over two rows.
    #     ccmc_oral_summary_sheet.merge_range("A1:G1",examiner_assignments.institute_id.name, merge_format)
        
    #     header_prac = ['Name of the Candidate','Roll No', 'Candidate Code No',
    #       '-House keeping Practical \n 20 Marks',
    #       '-F&B services practical \n 20 Marks',
    #       '-Orals on Housekeeping and F& B Service \n 20 Marks',
    #       '-Attitude & Proffesionalism \n 10 Marks',
    #       '-Identification of Equipment \n 10 Marks',
    #       '-GSK ORAL \n 10 Marks',
    #       '-Safety \n 10 Marks',
    #       'Remarks if any']
    #     for col, value in enumerate(header_prac):
    #         ccmc_oral_summary_sheet.write(1, col, value, header_format)
        
    #     # # import wdb;wdb.set_trace();
    #     candidate_list = [] #List of Candidates
    #     candidate_code = [] #Candidates Code No.
    #     roll_no = []

    #     for candidate in examiner_assignments.marksheets:
    #         candidate_list.append(candidate.ccmc_candidate.name)
    #         candidate_code.append(candidate.ccmc_candidate.candidate_code)
    #         roll_no.append(candidate.ccmc_marksheet.exam_id)
        
    #     for i, candidate in enumerate(candidate_list):
    #         ccmc_oral_summary_sheet.write('A{}'.format(i+3), candidate, locked)

    #     for i, code in enumerate(roll_no):
    #         ccmc_oral_summary_sheet.write('B{}'.format(i+3), code, locked)

    #     for i, code in enumerate(candidate_code):
    #         ccmc_oral_summary_sheet.write('C{}'.format(i+3), code, locked)
        
    #     ccmc_oral_summary_sheet.data_validation('D3:D1048576', {'validate': 'list', 'source': marks_values_20 })
    #     ccmc_oral_summary_sheet.data_validation('E3:E1048576', {'validate': 'list', 'source': marks_values_20 })
    #     ccmc_oral_summary_sheet.data_validation('F3:F1048576', {'validate': 'list', 'source': marks_values_20 })
    #     ccmc_oral_summary_sheet.data_validation('G3:G1048576', {'validate': 'list', 'source': marks_values_10 })
    #     ccmc_oral_summary_sheet.data_validation('H3:H1048576', {'validate': 'list', 'source': marks_values_10 })
    #     ccmc_oral_summary_sheet.data_validation('I3:I1048576', {'validate': 'list', 'source': marks_values_10 })
    #     ccmc_oral_summary_sheet.data_validation('J3:J1048576', {'validate': 'list', 'source': marks_values_10 })
        
    #     remarks = ['Absent','Good','Average','Weak']
    #     ccmc_oral_summary_sheet.data_validation('K3:K1048576', {'validate': 'list', 'source': remarks })
        
    #     workbook.close()

    #     # Set the buffer position to the beginning
    #     excel_buffer.seek(0)


    #     date = marksheets[0].examiners_id.exam_date
        
    #     file_name = examiner.name+"-CCMC Oral-"+str(date)+".xlsx"


    #     # Generate a response with the Excel file
    #     response = request.make_response(
    #         excel_buffer.getvalue(),
    #         headers=[
    #             ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
    #             ('Content-Disposition', 'attachment; filename='+file_name)
    #         ]
    #     )

    #     # Clean up the buffer
    #     excel_buffer.close()

    #     return response
    
    @http.route('/open_ccmc_candidate_form/download_ccmc_practical_marksheet/<int:batch_id>/<int:assignment_id>', type='http', auth="user", website=True)
    def download_ccmc_practical_marksheet(self,batch_id,assignment_id, **rec):
        
        user_id = request.env.user.id
        examiner = request.env['bes.examiner'].sudo().search([('user_id','=',user_id)])
        batch_id = batch_id
        examiner = request.env['bes.examiner'].sudo().search([('user_id','=',user_id)])
        # batch_info = request.env['exam.type.oral.practical'].sudo().search([('dgs_batch.id','=',batch_id)])
        examiner_assignments = request.env['exam.type.oral.practical.examiners'].sudo().search([('dgs_batch.id','=',batch_id),('examiner','=',examiner.id)])
        marksheets = request.env['exam.type.oral.practical.examiners.marksheet'].sudo().search([('examiners_id','=',assignment_id)])
        

        # import wdb;wdb.set_trace();
        
        excel_buffer = io.BytesIO()

        # Create a new Excel workbook and add a worksheet
        workbook = xlsxwriter.Workbook(excel_buffer)

        ccmc_cookery_bakery_sheet = workbook.add_worksheet('CCMC Cookery & Bakery')
        
        locked = workbook.add_format({'locked':True})
        unlocked = workbook.add_format({'locked':False})
        # Set the wrap text format
        wrap_format = workbook.add_format({'text_wrap': True})
        
        #For GSK Oral Marksheet
        ccmc_cookery_bakery_sheet.set_column('A1:XDF2',None, unlocked)
        ccmc_cookery_bakery_sheet.set_column('A2:A2',35, unlocked)
        ccmc_cookery_bakery_sheet.set_column('B2:B2',10, unlocked)
        ccmc_cookery_bakery_sheet.set_column('C2:C2',20, unlocked)
        ccmc_cookery_bakery_sheet.set_column('D2:O2',20, unlocked)
        # ccmc_cookery_bakery_sheet.set_column('P2:P2',15, unlocked)
            
        ccmc_cookery_bakery_sheet.protect()
        date_format = workbook.add_format({'num_format': 'dd-mmm-yy','locked':False})

        header_format = workbook.add_format({
                                                'bold': True,
                                                'align': 'center',
                                                'valign': 'vcenter',
                                                'font_color': 'black',
                                                'locked':True,
                                                'text_wrap': True,
                                            })
        
        merge_format = workbook.add_format({
                                                'bold':     True,
                                                'align':    'center',
                                                'valign':   'vcenter',
                                                'font_size': 20,
                                                'font_color': 'black',
                                            })
        
        # Merge 3 cells over two rows.
        ccmc_cookery_bakery_sheet.merge_range("A1:G1", examiner_assignments.institute_id.name, merge_format)
        
        header_oral = ['Name of the Candidate','Roll No', 'Candidate Code No',
          'Hygiene & Grooming \n 10 Marks', 
          
          'Dish 1 \n Appearance \n 10 Marks',
          'Dish 1 \n Taste \n 10 Marks',
          'Dish 1 \n Texture \n 9 Marks',
          
          'Dish 2 \n Appearance \n 10 Marks',
          'Dish 2 \n Taste \n 10 Marks',
          'Dish 2 \n Texture \n 9 Marks',
          
          'Dish 3 \n Appearance \n 5 Marks',
          'Dish 3 \n Taste \n 5 Marks',
          'Dish 3 \n Texture \n 5 Marks',
          'Identification of Ingredients \n 9 Marks',
          'Knowledge of menu \n 8 Marks']
        
        for col, value in enumerate(header_oral):
            ccmc_cookery_bakery_sheet.write(1, col, value, header_format)
        
          
        candidate_list = [] #List of Candidates
        candidate_code = [] #Candidates Code No.
        roll_no = []

        for candidate in examiner_assignments.marksheets:
            candidate_list.append(candidate.ccmc_candidate.name)
            candidate_code.append(candidate.ccmc_candidate.candidate_code)
            roll_no.append(candidate.ccmc_marksheet.exam_id)
        
        # # import wdb;wdb.set_trace();
        
        for i, candidate in enumerate(candidate_list):
            ccmc_cookery_bakery_sheet.write('A{}'.format(i+3), candidate, locked)
        
        for i, code in enumerate(roll_no):
            ccmc_cookery_bakery_sheet.write('B{}'.format(i+3), code, locked)

        for i, code in enumerate(candidate_code):
            ccmc_cookery_bakery_sheet.write('C{}'.format(i+3), code, locked)
        
        marks_values_5 = [1,2,3,4,5]
        marks_values_6 = [1,2,3,4,5,6]
        marks_values_8 = [1,2,3,4,5,6,7,8]
        marks_values_9 = [1,2,3,4,5,6,7,8,9]
        marks_values_10 = [1,2,3,4,5,6,7,8,9,10]
        marks_values_20 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
        
        ccmc_cookery_bakery_sheet.data_validation('D3:D1048576', {'validate': 'list', 'source': marks_values_10 })
        ccmc_cookery_bakery_sheet.data_validation('E3:E1048576', {'validate': 'list', 'source': marks_values_10 })
        ccmc_cookery_bakery_sheet.data_validation('F3:F1048576', {'validate': 'list', 'source': marks_values_10 })
        ccmc_cookery_bakery_sheet.data_validation('G3:G1048576', {'validate': 'list', 'source': marks_values_9 })
        ccmc_cookery_bakery_sheet.data_validation('H3:H1048576', {'validate': 'list', 'source': marks_values_10 })
        ccmc_cookery_bakery_sheet.data_validation('I3:I1048576', {'validate': 'list', 'source': marks_values_10 })
        ccmc_cookery_bakery_sheet.data_validation('J3:J1048576', {'validate': 'list', 'source': marks_values_9 })
        ccmc_cookery_bakery_sheet.data_validation('K3:K1048576', {'validate': 'list', 'source': marks_values_5 })
        ccmc_cookery_bakery_sheet.data_validation('L3:L1048576', {'validate': 'list', 'source': marks_values_5 })
        ccmc_cookery_bakery_sheet.data_validation('M3:M1048576', {'validate': 'list', 'source': marks_values_5 })
        ccmc_cookery_bakery_sheet.data_validation('N3:N1048576', {'validate': 'list', 'source': marks_values_9 })
        ccmc_cookery_bakery_sheet.data_validation('O3:O1048576', {'validate': 'list', 'source': marks_values_8 })
        
        remarks = ['Absent','Good','Average','Weak']
        # ccmc_cookery_bakery_sheet.data_validation('P3:P1048576', {'validate': 'list', 'source': remarks })


        ccmc_oral_summary_sheet = workbook.add_worksheet('CCMC Oral')
        
        locked = workbook.add_format({'locked':True})
        unlocked = workbook.add_format({'locked':False})
        # Set the wrap text format
        wrap_format = workbook.add_format({'text_wrap': True})
        
                
        marks_values_5 = [1,2,3,4,5]
        marks_values_6 = [1,2,3,4,5,6]
        marks_values_8 = [1,2,3,4,5,6,7,8]
        marks_values_9 = [1,2,3,4,5,6,7,8,9]
        marks_values_10 = [1,2,3,4,5,6,7,8,9,10]
        marks_values_20 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
                      
        #For GSK Practical Marksheet
        ccmc_oral_summary_sheet.set_column('A:XDF',None, unlocked)
        ccmc_oral_summary_sheet.set_column('A2:A2',35, unlocked)
        ccmc_oral_summary_sheet.set_column('B2:B2',10, unlocked)
        ccmc_oral_summary_sheet.set_column('C2:C2',20, unlocked)
        ccmc_oral_summary_sheet.set_column('D2:H2',25, unlocked)
        ccmc_oral_summary_sheet.set_column('I2:I2',15, unlocked)

        # Merge 3 cells over two rows.
        ccmc_oral_summary_sheet.merge_range("A1:G1",examiner_assignments.institute_id.name, merge_format)
        
        header_prac = ['Name of the Candidate','Roll No', 'Candidate Code No',
          '-House keeping Practical \n 20 Marks',
          '-F&B services practical \n 20 Marks',
          '-Orals on Housekeeping and F& B Service \n 20 Marks',
          '-Attitude & Proffesionalism \n 10 Marks',
          '-Identification of Equipment \n 10 Marks',
        #   '-GSK ORAL \n 20 Marks',
          'Remarks']
        for col, value in enumerate(header_prac):
            ccmc_oral_summary_sheet.write(1, col, value, header_format)
        
        # # import wdb;wdb.set_trace();
        candidate_list = [] #List of Candidates
        candidate_code = [] #Candidates Code No.
        roll_no = []

        for candidate in examiner_assignments.marksheets:
            candidate_list.append(candidate.ccmc_candidate.name)
            candidate_code.append(candidate.ccmc_candidate.candidate_code)
            roll_no.append(candidate.ccmc_marksheet.exam_id)
        
        for i, candidate in enumerate(candidate_list):
            ccmc_oral_summary_sheet.write('A{}'.format(i+3), candidate, locked)

        for i, code in enumerate(roll_no):
            ccmc_oral_summary_sheet.write('B{}'.format(i+3), code, locked)

        for i, code in enumerate(candidate_code):
            ccmc_oral_summary_sheet.write('C{}'.format(i+3), code, locked)
        
        ccmc_oral_summary_sheet.data_validation('D3:D1048576', {'validate': 'list', 'source': marks_values_20 })
        ccmc_oral_summary_sheet.data_validation('E3:E1048576', {'validate': 'list', 'source': marks_values_20 })
        ccmc_oral_summary_sheet.data_validation('F3:F1048576', {'validate': 'list', 'source': marks_values_20 })
        ccmc_oral_summary_sheet.data_validation('G3:G1048576', {'validate': 'list', 'source': marks_values_10 })
        ccmc_oral_summary_sheet.data_validation('H3:H1048576', {'validate': 'list', 'source': marks_values_10 })
        # ccmc_oral_summary_sheet.data_validation('I3:I1048576', {'validate': 'list', 'source': marks_values_20 })
        
       
        ccmc_oral_summary_sheet.data_validation('I3:I1048576', {'validate': 'list', 'source': remarks })
               
        workbook.close()

        # Set the buffer position to the beginning
        excel_buffer.seek(0)


        date = marksheets[0].examiners_id.exam_date
        
        file_name = examiner.name+"-CCMC Practical-"+str(date)+".xlsx"


        # Generate a response with the Excel file
        response = request.make_response(
            excel_buffer.getvalue(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', 'attachment; filename='+file_name)
            ]
        )

        # Clean up the buffer
        excel_buffer.close()

        return response
    
    @http.route('/open_ccmc_candidate_form/download_ccmc_gsk_oral_marksheet/<int:batch_id>/<int:assignment_id>', type='http', auth="user", website=True)
    def download_ccmc_gsk_oral_marksheet(self,batch_id,assignment_id, **rec):
        
        user_id = request.env.user.id
        examiner = request.env['bes.examiner'].sudo().search([('user_id','=',user_id)])
        batch_id = batch_id
        examiner = request.env['bes.examiner'].sudo().search([('user_id','=',user_id)])
        # batch_info = request.env['exam.type.oral.practical'].sudo().search([('dgs_batch.id','=',batch_id)])
        examiner_assignments = request.env['exam.type.oral.practical.examiners'].sudo().search([('dgs_batch.id','=',batch_id),('examiner','=',examiner.id)])
        marksheets = request.env['exam.type.oral.practical.examiners.marksheet'].sudo().search([('examiners_id','=',assignment_id)])
        

        # import wdb;wdb.set_trace();
        
        excel_buffer = io.BytesIO()

        # Create a new Excel workbook and add a worksheet
        workbook = xlsxwriter.Workbook(excel_buffer)

        ccmc_gsk_oral_sheet = workbook.add_worksheet('CCMC GSK Oral')
        
        locked = workbook.add_format({'locked':True})
        unlocked = workbook.add_format({'locked':False})
        # Set the wrap text format
        wrap_format = workbook.add_format({'text_wrap': True})
        
        #For GSK Oral Marksheet
        ccmc_gsk_oral_sheet.set_column('A1:XDF2',None, unlocked)
        ccmc_gsk_oral_sheet.set_column('A2:A2',35, unlocked)
        ccmc_gsk_oral_sheet.set_column('B2:B2',10, unlocked)
        ccmc_gsk_oral_sheet.set_column('C2:C2',20, unlocked)
        ccmc_gsk_oral_sheet.set_column('D2:O2',20, unlocked)
        # ccmc_cookery_bakery_sheet.set_column('P2:P2',15, unlocked)
            
        ccmc_gsk_oral_sheet.protect()
        date_format = workbook.add_format({'num_format': 'dd-mmm-yy','locked':False})

        header_format = workbook.add_format({
                                                'bold': True,
                                                'align': 'center',
                                                'valign': 'vcenter',
                                                'font_color': 'black',
                                                'locked':True,
                                                'text_wrap': True,
                                            })
        
        merge_format = workbook.add_format({
                                                'bold':     True,
                                                'align':    'center',
                                                'valign':   'vcenter',
                                                'font_size': 20,
                                                'font_color': 'black',
                                            })
        
        # Merge 3 cells over two rows.
        ccmc_gsk_oral_sheet.merge_range("A1:G1", examiner_assignments.institute_id.name, merge_format)
        
        header_oral = ['Name of the Candidate','Roll No', 'Candidate Code No',
            'GSK \n 10 Marks',
            'Safety \n 10 Marks'
        ]
        
        for col, value in enumerate(header_oral):
            ccmc_gsk_oral_sheet.write(1, col, value, header_format)
        
          
        candidate_list = [] #List of Candidates
        candidate_code = [] #Candidates Code No.
        roll_no = []

        for candidate in examiner_assignments.marksheets:
            candidate_list.append(candidate.ccmc_candidate.name)
            candidate_code.append(candidate.ccmc_candidate.candidate_code)
            roll_no.append(candidate.ccmc_marksheet.exam_id)
        
        # # import wdb;wdb.set_trace();
        
        for i, candidate in enumerate(candidate_list):
            ccmc_gsk_oral_sheet.write('A{}'.format(i+3), candidate, locked)
        
        for i, code in enumerate(roll_no):
            ccmc_gsk_oral_sheet.write('B{}'.format(i+3), code, locked)

        for i, code in enumerate(candidate_code):
            ccmc_gsk_oral_sheet.write('C{}'.format(i+3), code, locked)
        
        marks_values_5 = [1,2,3,4,5]
        marks_values_6 = [1,2,3,4,5,6]
        marks_values_8 = [1,2,3,4,5,6,7,8]
        marks_values_9 = [1,2,3,4,5,6,7,8,9]
        marks_values_10 = [1,2,3,4,5,6,7,8,9,10]
        marks_values_20 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
        
        ccmc_gsk_oral_sheet.data_validation('D3:D1048576', {'validate': 'list', 'source': marks_values_10 })
        ccmc_gsk_oral_sheet.data_validation('E3:E1048576', {'validate': 'list', 'source': marks_values_10 })
        
        remarks = ['Absent','Good','Average','Weak']
        # ccmc_cookery_bakery_sheet.data_validation('P3:P1048576', {'validate': 'list', 'source': remarks })

        workbook.close()

        # Set the buffer position to the beginning
        excel_buffer.seek(0)


        date = marksheets[0].examiners_id.exam_date
        
        file_name = examiner.name+"-CCMC-GSK-Oral-"+str(date)+".xlsx"


        # Generate a response with the Excel file
        response = request.make_response(
            excel_buffer.getvalue(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', 'attachment; filename='+file_name)
            ]
        )

        # Clean up the buffer
        excel_buffer.close()

        return response
    
    
    @http.route('/my/uploadccmcmarksheet', type='http', auth="user", website=True)
    def upload_ccmc_marksheet(self,**kw):
        user_id = request.env.user.id
        batch_id = int(kw['ccmc_batch_ids'])
        # import wdb;wdb.set_trace();
        assignment_id = int(kw['ccmc_assignment_ids'])
        file_content = kw.get("fileUpload").read()
        filename = kw.get('fileUpload').filename

        # workbook = xlsxwriter.Workbook(BytesIO(file_content))
        workbook = xlrd.open_workbook(file_contents=file_content)
        worksheet_oral = workbook.sheet_by_index(1)
        for row_num in range(2, worksheet_oral.nrows):  # Assuming first row contains headers
            row = worksheet_oral.row_values(row_num)
            
            roll_no = row[1]
            candidate_code_no = row[2]  
            house_keeping = row[3]  
            f_b = row[4]  
            orals_house_keeping = row[5]  
            attitude_proffessionalism = row[6]  
            equipment_identification = row[7]  
            # gsk_ccmc = row[8] 

            toal_ccmc_rating = 0  # Initialize gsk_practical_total_marks to 0
            if house_keeping:
                toal_ccmc_rating += int(house_keeping)
            if f_b:
                toal_ccmc_rating += int(f_b)
            if orals_house_keeping:
                toal_ccmc_rating += int(orals_house_keeping)
            if attitude_proffessionalism:
                toal_ccmc_rating += int(attitude_proffessionalism)
            if equipment_identification:
                toal_ccmc_rating += int(equipment_identification)
            # if gsk_ccmc:
            #     toal_ccmc_rating += int(gsk_ccmc)  

            remarks = row[8]
            
            candidate = request.env['ccmc.exam.schedule'].sudo().search([('exam_id','=',roll_no)])
            if candidate and candidate.ccmc_oral:
                candidate.ccmc_oral.sudo().write({
                    'house_keeping':house_keeping,
                    'f_b':f_b,
                    'orals_house_keeping':orals_house_keeping,
                    'attitude_proffessionalism':attitude_proffessionalism,
                    'equipment_identification':equipment_identification,
                    # 'gsk_ccmc':gsk_ccmc,
                    'toal_ccmc_rating':toal_ccmc_rating,
                    # 'mek_oral_remarks':remarks,


                })

        worksheet_practical = workbook.sheet_by_index(0)
        for row_num in range(2, worksheet_practical.nrows):  # Assuming first row contains headers
            row = worksheet_practical.row_values(row_num)
            
            roll_no = row[1]
            candidate_code_no = row[2]  
            hygien_grooming = row[3]  
            appearance = row[4]  
            taste = row[5]  
            texture = row[6]  
            appearance_2 = row[7]  
            taste_2 = row[8] 
            texture_2 = row[9] 
            appearance_3 = row[10]
            taste_3 = row[11] 
            texture_3 = row[12] 
            identification_ingredians = row[13]
            knowledge_of_menu = row[14]

            # mek_practical_total_marks = row[12] 
            total_mrks = 0  # Initialize gsk_practical_total_marks to 0
            if hygien_grooming:
                total_mrks += int(hygien_grooming)
            if appearance:
                total_mrks += int(appearance)
            if taste:
                total_mrks += int(taste)
            if texture:
                total_mrks += int(texture)
            if appearance_2:
                total_mrks += int(appearance_2)
            if taste_2:
                total_mrks += int(taste_2) 
            if texture_2:
                total_mrks += int(texture_2) 
            if appearance_3:
                total_mrks += int(appearance_3) 
            if taste_3:
                total_mrks += int(taste_3) 
            if texture_3:
                total_mrks += int(texture_3) 
            if identification_ingredians:
                total_mrks += int(identification_ingredians) 
            if knowledge_of_menu:
                total_mrks += int(knowledge_of_menu) 

            # mek_practical_remarks = row[12]

            candidate = request.env['ccmc.exam.schedule'].sudo().search([('exam_id','=',roll_no)])
            if candidate and candidate.cookery_bakery:
                candidate.cookery_bakery.sudo().write({
                    'hygien_grooming':hygien_grooming,
                    'appearance':appearance,
                    'taste':taste,
                    'texture':appearance_2,
                    'taste_2':taste_2,
                    'texture_2':texture_2,
                    'appearance_3':appearance_3,
                    'taste_3':taste_3,
                    'texture_3':texture_3,
                    'identification_ingredians':identification_ingredians,
                    'knowledge_of_menu':knowledge_of_menu,
                    'total_mrks':total_mrks,
                    # 'knowledge_of_menu':knowledge_of_menu,


                })
        examiner = request.env['bes.examiner'].sudo().search([('user_id','=',user_id)])
        examiner_assignments = request.env['exam.type.oral.practical.examiners'].sudo().search([('dgs_batch.id','=',batch_id),('examiner','=',examiner.id)])
        # marksheets = request.env['exam.type.oral.practical.examiners.marksheet'].sudo().search([('examiners_id','=',assignment_id)])
        
            
        return request.redirect("/my/assignments/batches/candidates/"+str(batch_id)+'/'+str(assignment_id))
        # return request.render("bes.examiner_assignment_candidate_list")
    
    @http.route('/my/uploadccmcgskmarksheet', type='http', auth="user", website=True)
    def upload_ccmc_gsk_marksheet(self,**kw):
        # import wdb;wdb.set_trace();
        user_id = request.env.user.id
        batch_id = int(kw['ccmc_gsk_ids'])
        assignment_id = int(kw['ccmc_ass_ids'])
        file_content = kw.get("fileUpload").read()
        filename = kw.get('fileUpload').filename

        # workbook = xlsxwriter.Workbook(BytesIO(file_content))
        workbook = xlrd.open_workbook(file_contents=file_content)
        worksheet_oral = workbook.sheet_by_index(0)
        for row_num in range(2, worksheet_oral.nrows):  # Assuming first row contains headers
            row = worksheet_oral.row_values(row_num)
            
            roll_no = row[1]
            candidate_code_no = row[2]  
            gsk_ccmc = row[3]  
            safety_ccmc = row[4]    

            toal_ccmc_oral_rating = 0  # Initialize gsk_practical_total_marks to 0
            if gsk_ccmc:
                toal_ccmc_oral_rating += int(gsk_ccmc)
            if safety_ccmc:
                toal_ccmc_oral_rating += int(safety_ccmc) 

            # remarks = row[8]
            # import wdb;wdb.set_trace();
            candidate = request.env['ccmc.exam.schedule'].sudo().search([('exam_id','=',roll_no)])
            if candidate and candidate.ccmc_gsk_oral:
                candidate.ccmc_gsk_oral.sudo().write({
                    'gsk_ccmc':gsk_ccmc,
                    'safety_ccmc':safety_ccmc,
                    'toal_ccmc_oral_rating':toal_ccmc_oral_rating,
                    # 'mek_oral_remarks':remarks,


                })

    
            # mek_practical_remarks = row[12]
        examiner = request.env['bes.examiner'].sudo().search([('user_id','=',user_id)])
        examiner_assignments = request.env['exam.type.oral.practical.examiners'].sudo().search([('dgs_batch.id','=',batch_id),('examiner','=',examiner.id)])
        # marksheets = request.env['exam.type.oral.practical.examiners.marksheet'].sudo().search([('examiners_id','=',assignment_id)])
        
            
        return request.redirect("/my/assignments/batches/candidates/"+str(batch_id)+'/'+str(assignment_id))
        # return request.render("bes.examiner_assignment_candidate_list")
    

    # @http.route('/my/gpcandidate/update_marks', type='json', auth='user', methods=["POST"])
    # def update_marks(self, **post):
    #     try:
    #         candidate_id = post.get('candidate_id')
    #         subject_area = post.get('subject_area')
    #         marks = post.get('marks')

    #         if not candidate_id or not subject_area or marks is None:
    #             return Response(json.dumps({'result': 'error', 'message': 'Missing required parameters'}), status=400)

    #         candidate = request.env['gp.candidate'].sudo().browse(int(candidate_id))
    #         if candidate:
    #             candidate.write({subject_area: int(marks)})
    #             return json.dumps({'result': 'success'})
    #         else:
    #             return json.dumps({'result': 'error', 'message': 'Candidate not found'})
    #     except Exception as e:
    #         return json.dumps({'result': 'error', 'message': str(e)})
    #     # return json.dumps({"status":"success", 'candidate_id':candidate_id ,'attendance_compliance_1':attendance_compliance_1  })
        

    # @http.route('/my/gpcandidate/update_total_marks', type='json', auth='user', methods=["POST"])
    # def update_total_marks(self, **post):
    #     try:
    #         candidate_id = post.get('candidate_id')
    #         total_marks = post.get('gsk_oral_total_marks')

    #         if not candidate_id or total_marks is None:
    #             return Response(json.dumps({'result': 'error', 'message': 'Missing required parameters'}), status=400)

    #         candidate = request.env['gp.candidate'].sudo().browse(int(candidate_id))
    #         if candidate:
    #             candidate.write({'gsk_oral_total_marks': int(total_marks)})
    #             return {'result': 'success'}
    #         else:
    #             return {'result': 'error', 'message': 'Candidate not found'}
    #     except Exception as e:
    #         return {'result': 'error', 'message': str(e)}

    @http.route('/my/uploadmarksheetimg', type='http', auth="user", website=True)
    def upload_marksheet_img(self, **kw):
        user_id = request.env.user.id
        batch_id = int(kw['marksheet_id'])
        file_content = kw.get("fileUpload").read()
        filename = kw.get('fileUpload').filename

        examiner_assignments = request.env['exam.type.oral.practical.examiners'].sudo().search([
            ('dgs_batch.id', '=', batch_id),
            ('examiner.user_id', '=', user_id)
        ])
        examiner_assignments.sudo().write({
            'marksheet_image':  base64.b64encode(file_content),
            'marksheet_image_name': filename
        })

        return request.redirect("/my/assignments/batches/" + str(batch_id))

    @http.route('/my/viewmarksheetimg/<int:batch_id>/<int:assignment_id>', type='http', auth="user", website=True)
    def view_marksheet_img(self, batch_id, assignment_id, **kw):
        user_id = request.env.user.id

        examiner_assignment = request.env['exam.type.oral.practical.examiners'].sudo().search([
            ('dgs_batch.id', '=', batch_id),
            ('id', '=', assignment_id),
            ('examiner.user_id', '=', user_id)
        ], limit=1)

        if not examiner_assignment:
            return request.not_found()

        file_content = examiner_assignment.marksheet_image
        if not file_content:
            raise UserError("No marksheet image found for this assignment.")

        # Convert the binary image data to base64 for rendering in the template
        image_base64 = base64.b64encode(file_content).decode('utf-8')
        image_data = f"data:image/jpeg;base64,{image_base64}"

        return request.render("bes.view_marksheet_image_template", {'image_data': image_data,'examiner_assignment':examiner_assignment})