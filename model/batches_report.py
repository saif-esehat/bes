from odoo import models


class BatchesReport(models.AbstractModel):
    _name = 'report.bes.report_batches'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data,lines):
        
        import wdb; wdb.set_trace()
        gp_candidates = self.env["gp.candidate"].sudo().search([('institute_batch_id','=',lines.id)])
        faculties = self.env["institute.faculty"].sudo().search([('gp_batches_id','=',lines.id)])
        
        candidate_worksheet = workbook.add_worksheet("Candidate")
        candidate_worksheet.write('A1', 'Candidate Name')
    
        
        row = 1
        
        for gp_candidate in gp_candidates:
            candidate_worksheet.write(row,0,gp_candidate.name)
            row += 1
            
        
        faculty_worksheet = workbook.add_worksheet("Faculty")
        faculty_worksheet.write('A1', 'Faculty Name')
        row = 1
        for faculty in faculties:
            faculty_worksheet.write(row,0,faculty.faculty_name)
            row += 1


