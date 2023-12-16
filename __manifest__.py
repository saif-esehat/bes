{
 
 'name':'BES',
 'summary': "BES",
 'author': "Saif Kazi", 
 'website': "http://www.esehat.org", 
 'category': 'Uncategorized', 
 'version': '13.0.1', 
 'depends':['product','portal','survey','website','sale','odoo_website_helpdesk'],
 'data': [
        'data/exam_sequence.xml',
        'data/certificate_sequence.xml',
        'data/tags.xml',
        'views/portal/candidate_portal/candidate_details.xml',
        'views/portal/portal_docs.xml',
        'views/portal/institute.xml',
        'views/portal/candidate.xml',
        'views/portal/examiner_portal/examiner_online_exam.xml',
        'views/portal/examiner_portal/candidate_selection.xml',
        'views/portal/examiner_portal/examiner_assignment.xml',
        'views/custom_brand.xml',
        'views/batches.xml',
        'views/examiner.xml',
        'views/exam_center.xml',
        'views/student.xml',
        'views/courses_master.xml',
        'views/institution.xml',
        'views/survey.xml',
        'views/invoice.xml',
        
        'views/marksheets/mek.xml',
        'views/marksheets/gsk.xml',
        'views/exam_schedule.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/template.xml',
        'reports/admit_card_template.xml',
        'reports/report_action.xml',
        'reports/sep_certificate.xml',
        'reports/report_gp_certificate.xml',
        'reports/report_ccmc_certificate.xml',
        'reports/admit_card_template_gp.xml',
        'reports/admit_card_template_ccmc.xml',
        
],
'assets': {
		'web.assets_frontend': [
			'bes/static/src/js/custom_validation.js',
		],
                
	},
'web.report_assets_common': [
            '/bes/static/src/css/report_css.scss',
            '/bes/static/src/css/style_gp.css',
            '/bes/static/src/css/style_ccmc.css',

        ],
}
