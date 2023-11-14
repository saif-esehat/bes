{
 
 'name':'BES',
 'summary': "BES",
 'author': "Saif Kazi", 
 'website': "http://www.esehat.org", 
 'category': 'Uncategorized', 
 'version': '13.0.1', 
 'depends':['product','portal','survey','website','sale'],
 'data': [
        'data/tags.xml',
        'views/portal/portal_docs.xml',
        'views/portal/institute.xml',
        'views/portal/candidate.xml',
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
        'views/template.xml'
],
'assets': {
		'web.assets_frontend': [
			'bes/static/src/js/candidate.js',
		],
	},
}
