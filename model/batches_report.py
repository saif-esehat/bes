from odoo import models


class BatchesReport(models.AbstractModel):
    _name = 'report.bes.report_batches'
    # _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data,lines):
        
        # import wdb; wdb.set_trace()
        gp_candidates = self.env["gp.candidate"].sudo().search([('institute_batch_id','=',lines.id)])
        faculties = self.env["institute.faculty"].sudo().search([('gp_batches_id','=',lines.id)])
        institutes = self.env["institute.gp.batches"].sudo().search([('id','=',lines.id)])
        
        candidate_worksheet = workbook.add_worksheet("Candidate")
        # candidate_worksheet.column_dimensions['A'].bestFit = True

        # candidate_worksheet.write('A1', 'Candidate Name')

        candidate_worksheet.write('A1', 'SR. NO.')
        candidate_worksheet.write('B1', 'ROLL NO')
        candidate_worksheet.write('C1', 'NAME')
        candidate_worksheet.write('D1', 'DOB')
        candidate_worksheet.write('E1', 'Xth')
        candidate_worksheet.write('F1', 'XIIth')


        
        row = 1
        
        for gp_candidate in gp_candidates:
            candidate_worksheet.write(row,0,row)
            candidate_worksheet.write(row,1,gp_candidate.roll_no)
            candidate_worksheet.write(row,2,gp_candidate.name)
            candidate_worksheet.write(row,3,gp_candidate.dob)
            candidate_worksheet.write(row,4,gp_candidate.tenth_percent)
            candidate_worksheet.write(row,5,gp_candidate.twelve_percent)

            row += 1
            
        
        
        faculty_worksheet = workbook.add_worksheet("Faculty")
        # faculty_worksheet.column_dimensions['A'].bestFit = True
        faculty_worksheet.write('A1', 'Qualification')
        faculty_worksheet.write('B1', 'Faculty Name')
        faculty_worksheet.write('C1', 'Specialization')
        faculty_worksheet.write('D1', 'DOB')
        faculty_worksheet.write('E1', 'FT or PT')
        row = 1
        for faculty in faculties:
            faculty_worksheet.write(row,0,faculty.qualification)
            faculty_worksheet.write(row,1,faculty.faculty_name)
            faculty_worksheet.write(row,2,faculty.designation)
            faculty_worksheet.write(row,3,faculty.dob)
            row += 1
        
        institute_worksheet = workbook.add_worksheet("Institute")
        institute_worksheet.column_dimensions['A1'].bestFit = True
        institute_worksheet.column_dimensions['A2'].bestFit = True
        institute_worksheet.column_dimensions['A3'].bestFit = True
        institute_worksheet.column_dimensions['A4'].bestFit = True
        institute_worksheet.column_dimensions['A5'].bestFit = True
        institute_worksheet.column_dimensions['A6'].bestFit = True
        institute_worksheet.column_dimensions['A7'].bestFit = True


        institute_worksheet.write('A1','Information of Institute')
        institute_worksheet.write('A2','Name of the Institute')
        institute_worksheet.write('A3','MTI No. of institute')
        institute_worksheet.write('A4','Approved Capacity')
        institute_worksheet.write('A5','Course Title')
        institute_worksheet.write('A6','Batch No.')
        institute_worksheet.write('A7','Date of commencement and ending of the course')

        print("Institute",institutes.institute_id.name)

        institute_worksheet.write(1,1,institutes.institute_id.name)
        institute_worksheet.write(2,1,institutes.institute_id.mti)
        institute_worksheet.write(3,1,institutes.institute_id.computer_lab_pc_count)
        institute_worksheet.write(4,1,institutes.course.name)
        institute_worksheet.write(5,1,institutes.batch_name)
        institute_worksheet.write('B7',1,str(institutes.from_date) + ' to ' + str(institutes.to_date))








