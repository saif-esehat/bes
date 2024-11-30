{
 
 'name':'BES',
 'summary': "BES",
 'author': "Saif Kazi", 
 'website': "http://www.esehat.org", 
 'category': 'Uncategorized', 
 'version': '13.0.1', 
 'depends':['base','product','hr','hr_expense','portal','survey','website','sale','odoo_website_helpdesk','account','mail'],
 'data': [
        'data/roll_no_sequence.xml',
        'data/exam_sequence.xml',
        'data/certificate_sequence.xml',
        'data/tags.xml',
        'data/email_template.xml',
        'data/paper_format.xml',
        'views/portal/candidate_portal/candidate_details.xml',
        'views/portal/portal_docs.xml',
        'views/portal/institute.xml',
        'views/candidate_approval.xml',
        'views/portal/candidate.xml',
        'views/portal/examiner_portal/examiner_online_exam.xml',
        'views/portal/examiner_portal/candidate_selection.xml',
        'views/portal/examiner_portal/examiner_assignment.xml',
        'views/custom_brand.xml',
        'views/batches.xml',
        'views/examiner.xml',
        'views/exam_center.xml',
        'views/student.xml',
        'views/portal/examiner_portal/expenses.xml',
        'views/courses_master.xml',
        'views/institution.xml',
        'views/survey.xml',
        'views/books_order.xml',
        'views/invoice.xml',
        'views/marksheet_wizard.xml',
        'views/marksheets/mek.xml',
        'views/marksheets/gsk.xml',
        'views/exam_schedule.xml',
        'views/hr_employee.xml',
        'views/sales_order.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/examiner_expenses_views.xml',
        'views/menu.xml',
        'views/template.xml',
        'views/timesheet.xml',
        'views/examination_report.xml',
        'reports/admit_card_template.xml',
        'reports/report_action.xml',
        'reports/sep_certificate.xml',
        'reports/report_gp_certificate.xml',
        'reports/report_ccmc_certificate.xml',
        'reports/admit_card_template_gp.xml',
        'reports/admit_card_template_ccmc.xml',
        'reports/dgs_report.xml',
        'reports/attendance_sheet.xml',
        'reports/summarised_report.xml',
        'reports/candidates_exam_report.xml',
        'views/sep_batches.xml',
        'views/sep_candidate.xml',
        'reports/sep_candidate_certificate.xml',
        'views/iv_exam/iv_batches.xml',
        'views/iv_exam/iv_candidates.xml',
        'views/iv_exam/candidats_application.xml',
        'reports/iv_candidate_admit_card.xml',
        'views/iv_exam/candidate_remark.xml',
        'views/iv_exam/iv_attendance_sheet.xml',
        'views/iv_exam/iv_invigilator_sheet.xml',
        'reports/iv_attandance_report/iv_written_attendance.xml',
        'views/iv_exam/iv_oral_attendance_sheet.xml',
        'views/iv_exam/iv_exams.xml',
        'reports/iv_attandance_report/iv_oral_attendance.xml',
        'reports/iv_candidate/iv_hold_candidate_list.xml',
        'reports/iv_candidate/iv_eligible_candidats_list.xml',
        'reports/iv_candidate/iv_not_eligible_candidat_list.xml',
        'reports/iv_candidate/iv_candidate_issuance_admitcard.xml',
        'reports/iv_exam_report/iv_written_exam_a.xml',
        'reports/iv_exam_report/iv_oral_exam_result.xml',
        'views/ship_visit/gp_ship_visit.xml',
        'views/ship_visit/ccmc_ship_visit.xml',
        'views/portal/ship_visit/ship_visit.xml',
        'views/portal/ship_visit/ccmc_ship_visi.xml',
        'views/portal/sale_order_portal.xml',
        'reports/iv_invigilator/iv_invigilator_report.xml',
        'reports/sales_order_template.xml'
 
       
        # 'views/sep_batches.xml',
        # 'views/sep_candidate.xml',
        # 'reports/sep_candidate_certificate.xml',
        
        
],
'assets': {
		'web.assets_frontend': [
                        'bes/views/portal/static/src/js/candidate_oral_practical.js',
                        'bes/views/portal/static/src/js/examiner_marksheet.js',
                        'bes/static/js/examiner_portal_marksheet.js',
                        'bes/static/js/repeater_portal_gp_form.js',
                        'bes/static/js/openStartExam.js'
		],
                'web.assets_qweb': [
                        'bes/static/src/xml/gp_exam_tree_button.xml',
                ],
                'web.assets_backend': [
                        'bes/static/src/js/gp_exam_tree_button.js',
                        'bes/static/src/css/customs_color.css',
                        'bes/static/src/js/lost_connection_handler_override.js',
                ],
                
	},
'web.report_assets_common': [
            '/bes/static/src/css/report_css.scss',
            '/bes/static/src/css/style_gp.css',
            '/bes/static/src/css/style_ccmc.css',
            '/bes/static/src/css/dgs_report.css',
           

        ],
}
