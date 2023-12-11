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
            print('candidateeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',rec)
            assignment = request.env['examiner.assignment'].sudo().browse(int(rec_id))

            # Check if gp_candidate is set
            if assignment.assigned_to == "gp_candidate":
                gp_oral_prac = assignment.gp_oral_prac
                candidate = assignment.gp_oral_prac.gp_candidate
                subject = assignment.subject_id.name
            # Check if ccmc_candidate is set
            elif assignment.assigned_to == "ccmc_candidate":
                candidate = assignment.ccmc_candidates
            else:
                # Handle the case when both gp_candidate and ccmc_candidate are not set
                candidate = False

            return request.render("bes.examiner_candidate_list", {'candidate': candidate,'gp_oral_prac':gp_oral_prac , 'subject':subject})
        else:
            print('candidateeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',rec)
            search_filter = rec.get('search_filter') or request.params.get('search_filter')
            search_value = rec.get('search_value') or request.params.get('search_value')
            print('filterrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr',search_filter)
            print('valueeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',search_value)



    @http.route('/open_gsk_oral_form', type='http', auth="user", website=True)
    def open_gsk_oral_form(self, **rec):
        # import wdb;wdb.set_trace();
        candidate = request.env['gp.candidate'].sudo()
        if 'indos' in rec:
            print('exittttttttttttttttttttttttttttttt')
            indos = rec['indos']

            # Convert string values to integers
            subject_area1 = int(rec['subject_area1'])
            subject_area2 = int(rec['subject_area2'])
            subject_area3 = int(rec['subject_area3'])
            subject_area4 = int(rec['subject_area4'])
            subject_area5 = int(rec['subject_area5'])
            subject_area6 = int(rec['subject_area6'])
            state=rec['state']

            practical_record_journals = int(rec['practical_record_journals'])
       
            remarks_oral_gsk = rec['remarks_oral_gsk']

            candidate_rec = candidate.search([('indos_no', '=', indos)])
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
               
                'gsk_oral_remarks': remarks_oral_gsk
            }

            print('valssssssssssssssssssssssssssssssssssssssssssssssss', vals)

            # Write to the One2many field using the constructed dictionary
            draft_records.write(vals)

        else:
            print('enterrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr', rec)
            rec_id = rec['rec_id']
            candidate_rec = candidate.search([('indos_no', '=', rec_id)])
            name=candidate_rec.name
            candidate_image = candidate_rec.candidate_image
            draft_records = candidate_rec.gsk_oral_child_line.filtered(lambda line: line.gsk_oral_draft_confirm == 'draft')

            print('recccccccccccccccccccccccccccccccccc',candidate_rec)
            print('dateeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',draft_records.gsk_oral_exam_date)
            exam_date = draft_records.gsk_oral_exam_date
            return request.render("bes.gsk_oral_marks_submit", {'indos': rec_id,'exam_date':exam_date,'candidate_name':name, 'candidate_image': candidate_image})
                

    @http.route('/open_gsk_practical_form', type='http', auth="user", website=True)
    def open_gsk_practical_form(self, **rec):
        candidate = request.env['gp.candidate'].sudo()
        if 'indos' in rec:
            print('exittttttttttttttttttttttttttttttt')
            indos = rec['indos']

            # Convert string values to integers
            subject_area1 = int(rec['climbing_mast'])
            subject_area2 = int(rec['buoy_flags_recognition'])
            subject_area3 = int(rec['bosun_chair'])
            subject_area4 = int(rec['rig_stage'])
            subject_area5 = int(rec['rig_pilot'])
            subject_area6 = int(rec['rig_scoffolding'])
            subject_area7 = int(rec['fast_ropes'])
            subject_area8 = int(rec['knots_bend'])
            subject_area9 = int(rec['sounding_rod'])
            state = rec['state']
            remarks_oral_gsk = rec['gsk_practical_remarks']

            candidate_rec = candidate.search([('indos_no', '=', indos)])
            draft_records = candidate_rec.gsk_practical_child_line.filtered(lambda line: line.gsk_practical_draft_confirm == 'draft')

            # Construct the dictionary with integer values
            vals = {
                'climbing_mast': subject_area1,
                'buoy_flags_recognition': subject_area2,
                'bosun_chair': subject_area3,
                'rig_stage': subject_area4,
                'rig_pilot': subject_area5,
                'rig_scaffolding': subject_area6,
                'fast_ropes': subject_area7,
                'knots_bend': subject_area8,
                'sounding_rod': subject_area9,
                'gsk_practical_draft_confirm': state,
               
                'gsk_practical_remarks': remarks_oral_gsk
            }

            print('valssssssssssssssssssssssssssssssssssssssssssssssss', vals)

            # Write to the One2many field using the constructed dictionary
            draft_records.write(vals)

        else:
            print('enterrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr', rec)
            rec_id = rec['rec_id']
            candidate_rec = candidate.search([('indos_no', '=', rec_id)])
            name=candidate_rec.name
            candidate_image = candidate_rec.candidate_image
            draft_records = candidate_rec.gsk_practical_child_line.filtered(lambda line: line.gsk_practical_draft_confirm == 'draft')

            print('recccccccccccccccccccccccccccccccccc',candidate_rec)
            
            exam_date = draft_records.gsk_practical_exam_date
            return request.render("bes.gsk_practical_marks_submit", {'indos': rec_id,'exam_date':exam_date,'candidate_name':name, 'candidate_image': candidate_image})       
            

    @http.route('/open_mek_oral_form', type='http', auth="user", website=True)
    def open_mek_oral_form(self, **rec):
        candidate = request.env['gp.candidate'].sudo()
        if 'indos' in rec:
            print('exittttttttttttttttttttttttttttttt')
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

            candidate_rec = candidate.search([('indos_no', '=', indos)])
            draft_records = candidate_rec.mek_oral_child_line.filtered(lambda line: line.mek_oral_draft_confirm == 'draft')


            # Construct the dictionary with integer values
            vals = {
                'using_hand_plumbing_carpentry_tools': subject_area1,
                'use_of_chipping_tools_paints': subject_area2,
                'welding': subject_area3,
                'lathe_drill_grinder': subject_area4,
                'electrical': subject_area5,
                'journal': subject_area6,
                'mek_oral_remarks': mek_oral_remarks,
                'mek_oral_draft_confirm': state,
                
                
            }

            print('valssssssssssssssssssssssssssssssssssssssssssssssss', vals)

            # Write to the One2many field using the constructed dictionary
            draft_records.write(vals)

        else:
            print('enterrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr', rec)
            rec_id = rec['rec_id']
            candidate_rec = candidate.search([('indos_no', '=', rec_id)])
            name=candidate_rec.name
            candidate_image = candidate_rec.candidate_image
            draft_records = candidate_rec.mek_oral_child_line.filtered(lambda line: line.mek_oral_draft_confirm == 'draft')

            print('recccccccccccccccccccccccccccccccccc',candidate_rec)
            
            exam_date = draft_records.mek_oral_exam_date
            return request.render("bes.mek_oral_marks_submit", {'indos': rec_id,'exam_date':exam_date,'candidate_name':name, 'candidate_image': candidate_image})

    @http.route('/open_practical_mek_form', type='http', auth="user", website=True)
    def open_practical_mek_form(self, **rec):
        print("enterrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
        candidate = request.env['gp.candidate'].sudo()
        if 'indos' in rec:
            print('exittttttttttttttttttttttttttttttt')
            indos = rec['indos']
           

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

            candidate_rec = candidate.search([('indos_no', '=', indos)])
            draft_records = candidate_rec.mek_practical_child_line.filtered(lambda line: line.mek_practical_draft_confirm == 'draft')


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
                'mek_practical_draft_confirm': state,
                
            }

            print('valssssssssssssssssssssssssssssssssssssssssssssssss', vals)

            # Write to the One2many field using the constructed dictionary
            draft_records.write(
                 vals)

        else:
            print('enterrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr', rec)
            rec_id = rec['rec_id']
            candidate_rec = candidate.search([('indos_no', '=', rec_id)])
            name=candidate_rec.name
            candidate_image = candidate_rec.candidate_image
            draft_records = candidate_rec.mek_practical_child_line.filtered(lambda line: line.mek_practical_draft_confirm == 'draft')

            print('recccccccccccccccccccccccccccccccccc',candidate_rec)
            
            exam_date = draft_records.mek_practical_exam_date
            return request.render("bes.mek_practical_marks", {'indos': rec_id,'exam_date':exam_date,'candidate_name':name, 'candidate_image': candidate_image})

    @http.route('/open_cookery_bakery_form', type='http', auth="user", website=True)
    def open_cookery_bakery_form(self, **rec):

        candidate = request.env['ccmc.candidate'].sudo()
        if 'indos' in rec:
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
            return request.render("bes.cookery_bakery_marks_submit", {'indos': rec_id})

    @http.route('/open_ccmc_oral_form', type='http', auth="user", website=True)
    def open_ccmc_oral_form(self, **rec):

        if 'indos' in rec:
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
            return request.render("bes.ccmc_gsk_oral_marks_submit", {'indos': rec_id})