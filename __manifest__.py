{
 
 'name':'BES',
 'summary': "BES",
 'author': "Saif Kazi", 
 'website': "http://www.esehat.org", 
 'category': 'Uncategorized', 
 'version': '13.0.1', 
 'depends':['product','hr','hr_expense','portal','survey','website','sale','odoo_website_helpdesk','account','mail'],
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
        'views/invoice.xml',
        'views/marksheet_wizard.xml',
        'views/marksheets/mek.xml',
        'views/marksheets/gsk.xml',
        'views/exam_schedule.xml',
        'views/hr_employee.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
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
        
        
],
'assets': {
		'web.assets_frontend': [
                        'bes/views/portal/static/src/js/candidate_oral_practical.js',
                        'bes/static/js/examiner_portal_marksheet.js',
                        'bes/static/js/repeater_portal_gp_form.js'
		],
                'web.assets_qweb': [
                        'bes/static/src/xml/gp_exam_tree_button.xml',
                ],
                'web.assets_backend': [
                        'bes/static/src/js/gp_exam_tree_button.js',
                ],
                
	},
'web.report_assets_common': [
            '/bes/static/src/css/report_css.scss',
            '/bes/static/src/css/style_gp.css',
            '/bes/static/src/css/style_ccmc.css',
            '/bes/static/src/css/dgs_report.css'

        ],
}
