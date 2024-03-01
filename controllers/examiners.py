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
from odoo.exceptions import AccessError
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
        
        survey = request.env["survey.survey"].sudo().search(
            [('examiner', '=', examiner_id)])
        
        vals = {"surveys":survey}
        
        return request.render("bes.examiner_portal_online_exam_list", vals)
    
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
        examiner_assignments = request.env['bes.examiner'].sudo().search([('user_id','=',user_id)]).assignments
        
        vals = {'assignments':examiner_assignments, 'examiner':examiner}
        # self.env["gp.candidate"].sudo().search([('')])
        return request.render("bes.examiner_assignment_list", vals)

    
    
    # def check_user_groups(group_xml_id):
    #     ​def decorator(func):
    #     ​	​def wrapper(self, *args, **kwargs):
    #     ​	​	​if not request.env.user.has_group(group_xml_id):
    #     ​	​	​	​raise AccessError("You do not have access rights to view this page.")
    #     ​	​	​return func(self, *args, **kwargs)
    #     ​	​return wrapper
    #     ​return decorator
    @http.route('/open_candidate_form', type='http', auth="user", website=True)
    def open_candidate_form(self, **rec):
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
            
            return request.render("bes.examiner_candidate_list", {'candidate': candidate,'gp_oral_prac':gp_oral_prac , 'subject':subject ,'assignment_id':rec_id})
        else:
            print('candidateeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',rec)
            search_filter = rec.get('search_filter') or request.params.get('search_filter')
            search_value = rec.get('search_value') or request.params.get('search_value')
            print('filterrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr',search_filter)
            print('valueeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',search_value)


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
            # Check if ccmc_candidate is set
            elif assignment.assigned_to == "gp_candidate":
                candidate = assignment.gp_candidate
            else:
                # Handle the case when both gp_candidate and ccmc_candidate are not set
                candidate = False
            
            return request.render("bes.examiner_candidate_list", {'candidate': candidate,'ccmc_assignment':ccmc_assignment , 'subject':subject ,'assignment_id':rec_id, "page_name": "ccmc_assignment"})
        else:
            print('candidateeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',rec)
            search_filter = rec.get('search_filter') or request.params.get('search_filter')
            search_value = rec.get('search_value') or request.params.get('search_value')
            print('filterrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr',search_filter)
            print('valueeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',search_value)



    @http.route('/open_gsk_oral_form', type='http', auth="user", website=True,method=["POST","GET"])
    def open_gsk_oral_form(self, **rec):
        # import wdb;wdb.set_trace();
        candidate = request.env['gp.candidate'].sudo()
        print("=======================================================",request.httprequest.method)
        
        if request.httprequest.method == "POST":
            print('exittttttttttttttttttttttttttttttt==============================================')
            print(rec)
            
            # import wdb; wdb.set_trace()
            rec_id = rec['rec_id']
            
            marksheet = request.env['gp.gsk.oral.line'].sudo().search([('id','=',rec['gsk_oral'])])

            # Convert string values to integers
            subject_area1 = int(rec['subject_area1'])
            subject_area2 = int(rec['subject_area2'])
            subject_area3 = int(rec['subject_area3'])
            subject_area4 = int(rec['subject_area4'])
            subject_area5 = int(rec['subject_area5'])
            subject_area6 = int(rec['subject_area6'])
            state=rec['state']

            exam_date = rec['exam_date']
            practical_record_journals = int(rec['practical_record_journals'])
       
            remarks_oral_gsk = rec['remarks_oral_gsk']

            candidate_rec = candidate.search([('id', '=', rec_id)])
            draft_records = candidate_rec.gsk_oral_child_line.filtered(lambda line: line.gsk_oral_draft_confirm == 'draft') 

            # Construct the dictionary with integer values
            vals = {
                'subject_area_1': subject_area1,                
                'subject_area_2': subject_area2,
                'subject_area_3': subject_area3,
                'subject_area_4': subject_area4,
                'subject_area_5': subject_area5, 
                'subject_area_6': subject_area6,
                'practical_record_journals': practical_record_journals,
                'gsk_oral_draft_confirm': state,
                'gsk_oral_exam_date': exam_date,
                'gsk_oral_remarks': remarks_oral_gsk
            }
            
            

            marksheet.write(vals)
            # import wdb; wdb.set_trace()
            
            return request.redirect("/open_candidate_form?rec_id="+rec["assignment_id"]+"&subject_name=GSK")
            # return request.redirect()
            
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
            
            # draft_records = candidate_rec.gsk_oral_child_line.filtered(lambda line: line.gsk_oral_draft_confirm == 'draft')
            # import wdb; wdb.set_trace()
            # print('recccccccccccccccccccccccccccccccccc',candidate_rec)
            # return request.render("bes.gsk_oral_marks_submit", {'indos': candidate_indos,'gsk_marksheet':gsk_marksheet,'candidate_name':name, 'candidate_image': candidate_image})
            return request.render("bes.gsk_oral_marks_submit", {'indos': candidate_indos, 'gsk_marksheet': gsk_marksheet, 'candidate_name': name, 'candidate_image': candidate_image, 'candidate': candidate_rec , 'exam_date':gsk_marksheet.gsk_oral_exam_date, "page_name": "gsk_oral"})


    @http.route('/open_gsk_practical_form', type='http', auth="user", website=True,method=["POST","GET"])
    def open_gsk_practical_form(self, **rec):
        candidate = request.env['gp.candidate'].sudo()
        print("=======================================================",request.httprequest.method)
        
        if request.httprequest.method == "POST":
            print('exittttttttttttttttttttttttttttttt')
            indos = rec['indos']

            # Convert string values to integers
            climbing_mast = int(rec['climbing_mast'])
            buoy_flags_recognition = int(rec['buoy_flags_recognition'])
            bosun_chair = int(rec['bosun_chair'])
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
                'climbing_mast': climbing_mast,
                'buoy_flags_recognition': buoy_flags_recognition,
                'bosun_chair': bosun_chair,
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
            
            return request.redirect("/open_candidate_form?rec_id="+rec["assignment_id"]+"&subject_name=GSK")

            print('valssssssssssssssssssssssssssssssssssssssssssssssss', vals)

            # Write to the One2many field using the constructed dictionary
            # draft_records.write(vals)

        else:
            # import wdb; wdb.set_trace()
            print('enterrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr', rec)
            rec_id = rec['rec_id']
            candidate_rec = candidate.search([('id', '=', rec['rec_id'])])
            name=candidate_rec.name
            candidate_image = candidate_rec.candidate_image
            # draft_records = candidate_rec.gsk_practical_child_line.filtered(lambda line: line.gsk_practical_draft_confirm == 'draft')
            gsk_prac_marksheet = request.env['gp.gsk.practical.line'].sudo().search([('id','=',rec['gsk_practical'])])
            print('recccccccccccccccccccccccccccccccccc',candidate_rec)
            exam_date = gsk_prac_marksheet.gsk_practical_exam_date
            return request.render("bes.gsk_practical_marks_submit", {'indos': candidate_rec.indos_no,'exam_date':exam_date,'candidate_name':name, 'candidate_image': candidate_image, 'candidate': candidate_rec,'gsk_prac_marksheet':gsk_prac_marksheet, "page_name": "gsk_prac"})       
            

    @http.route('/open_mek_oral_form', type='http', auth="user", website=True,method=["POST","GET"])
    def open_mek_oral_form(self, **rec):
        candidate = request.env['gp.candidate'].sudo()
        print("=======================================================",request.httprequest.method)
        
        if request.httprequest.method == "POST":
            # print('exittttttttttttttttttttttttttttttt')
            indos = rec['indos']

            # Convert string values to integers
            subject_area1 = int(rec['subject_area1'])
            subject_area2 = int(rec['subject_area2'])
            subject_area3 = int(rec['subject_area3'])
            subject_area4 = int(rec['subject_area4'])
            subject_area5 = int(rec['subject_area5'])
            subject_area6 = int(rec['subject_area6'])
            mek_oral_remarks = rec['remarks_oral_mek']
            state = rec['state']

            # candidate_rec = candidate.search([('indos_no', '=', indos)])
            # draft_records = candidate_rec.mek_oral_child_line.filtered(lambda line: line.mek_oral_draft_confirm == 'draft')


            # Construct the dictionary with integer values
            vals = {
                'using_hand_plumbing_carpentry_tools': subject_area1,
                'use_of_chipping_tools_paints': subject_area2,
                'welding': subject_area3,
                'lathe_drill_grinder': subject_area4,
                'electrical': subject_area5,
                'journal': subject_area6,
                'mek_oral_remarks': mek_oral_remarks,
                'mek_oral_draft_confirm': state
            }
            
            marksheet = request.env['gp.mek.oral.line'].sudo().search([('id','=',rec['mek_oral'])])
            marksheet.write(vals)
            
            return request.redirect("/open_candidate_form?rec_id="+rec["assignment_id"]+"&subject_name=MEK")

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
            
            exam_date = mek_oral_marksheet.mek_oral_exam_date
            return request.render("bes.mek_oral_marks_submit", {'indos': candidate_rec.indos_no,'exam_date':exam_date,'candidate_name':name, 'candidate_image': candidate_image, 'candidate': candidate_rec,'mek_oral_marksheet':mek_oral_marksheet, "page_name": "mek_oral"})

    @http.route('/open_practical_mek_form', type='http', auth="user", website=True,method=["POST","GET"])
    def open_practical_mek_form(self, **rec):
        print("enterrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
        candidate = request.env['gp.candidate'].sudo()
        print("=======================================================",request.httprequest.method)
        
        if request.httprequest.method == "POST":
            print('exittttttttttttttttttttttttttttttt')
            # rec_id = rec['rec_id']
           

            # Convert string values to integers
            subject_area1 = int(rec['subject_area1'])
            subject_area2 = int(rec['subject_area2'])
            subject_area3 = int(rec['subject_area3'])
            subject_area4 = int(rec['subject_area4'])
            subject_area5 = int(rec['subject_area5'])
            subject_area6 = int(rec['subject_area6'])
            subject_area7 = int(rec['subject_area7'])
            subject_area8 = int(rec['subject_area8'])
            subject_area9 = int(rec['subject_area9'])
           
            mek_practical_remarks = rec['remarks_practical_mek']
            state = rec['state']

            # candidate_rec = candidate.search([('id', '=', rec_id)])
            # draft_records = candidate_rec.mek_practical_child_line.filtered(lambda line: line.mek_practical_draft_confirm == 'draft')


            # Construct the dictionary with integer values
            vals = {
                'using_hand_plumbing_tools_task_1': subject_area1,
                'using_hand_plumbing_tools_task_2': subject_area2,
                'using_hand_plumbing_tools_task_3': subject_area3,
                'use_of_chipping_tools_paint_brushes': subject_area4,
                'use_of_carpentry': subject_area5,
                'use_of_measuring_instruments': subject_area6,
                'welding': subject_area7,
                'lathe': subject_area8,
                'electrical': subject_area9,
                'mek_practical_remarks': mek_practical_remarks,
                'mek_practical_draft_confirm': state
            }
            
            marksheet = request.env['gp.mek.practical.line'].sudo().search([('id','=',rec['mek_practical'])])
            
            marksheet.write(vals)
            
            return request.redirect("/open_candidate_form?rec_id="+rec["assignment_id"]+"&subject_name=MEK")

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
            exam_date = mek_prac_marksheet.mek_practical_exam_date
            return request.render("bes.mek_practical_marks", {'indos': candidate_rec.indos_no,'exam_date':exam_date,'candidate_name':name, 'candidate_image': candidate_image, 'candidate': candidate_rec,'mek_prac_marksheet':mek_prac_marksheet,  "page_name": "mek_prac"})


    @http.route('/open_cookery_bakery_form', type='http', auth="user", website=True,method=["POST","GET"])
    def open_cookery_bakery_form(self, **rec):

        candidate = request.env['ccmc.candidate'].sudo()
        if request.httprequest.method == "POST":
            print('exittttttttttttttttttttttttttttttt')
            indos = rec['indos']
            

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
            candidate_rec.write({
                'cookery_child_line': [(0, 0, vals)]
            })

        else:
            print('enterrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr', rec)
            rec_id = rec['rec_id']
            return request.render("bes.cookery_bakery_marks_submit", {'indos': rec_id,  "page_name": "cooker_bakery_form"})

    @http.route('/open_ccmc_oral_form', type='http', auth="user", website=True,method=["POST","GET"])
    def open_ccmc_oral_form(self, **rec):

        if request.httprequest.method == "POST":
            print('exittttttttttttttttttttttttttttttt')
            indos = rec['indos']
            

            # Convert string values to integers
            subject_area1 = int(rec['ccmc_gsk'])
            subject_area2 = int(rec['safety_ccmc'])
          
           

            candidate = request.env['ccmc.candidate'].sudo()
            candidate_rec = candidate.search([('indos_no', '=', indos)])

            # Construct the dictionary with integer values
            vals = {
                'gsk_ccmc': subject_area1,
                'safety_ccmc': subject_area2,
               
                
            }

            print('valssssssssssssssssssssssssssssssssssssssssssssssss', vals)

            # Write to the One2many field using the constructed dictionary
            candidate_rec.write({
                'ccmc_oral_child_line': [(0, 0, vals)]
            })

        else:
            print('enterrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr', rec)
            rec_id = rec['rec_id']
            return request.render("bes.ccmc_gsk_oral_marks_submit", {'indos': rec_id,  "page_name": "ccmc_oral"})