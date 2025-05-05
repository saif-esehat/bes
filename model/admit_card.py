from odoo import models , fields,api
import json
import base64
from io import BytesIO
from lxml import etree
from odoo.exceptions import UserError,ValidationError


class CandidateAdmitCardGp(models.AbstractModel):
    _name = 'report.bes.candidate_admit_card_gp'
    _description = 'Candidate Admit Card'
    
    @api.model
    def _get_report_values(self, docids, data=None):
            
            # import wdb; wdb.set_trace();
        
            # docs1 = self.env['gp.exam.schedule'].sudo().search([('id','=',docids)])
            
            docs1 = self.env['gp.exam.schedule'].sudo().browse(docids)
            
            print("doc_idsss",docids)
            user_id = self.env.user
            # import wdb; wdb.set_trace()
            if user_id.has_group('bes.download_not_allowed'):
                # User is in the group
                raise ValidationError("Please Contact Administrator")
            

            
            for docs in docs1:
                if docs.attendance_criteria == 'pending' :
                    raise UserError("Admit Card Not Generated Attendance Criteria not Complied")
            
                if docs.ship_visit_criteria == 'pending' :
                    raise UserError("Admit Card Not Generated Ship Visit  Criteria not Complied")
                
                # if not docs.institute_id.code == "M05":
                
                #     if docs.stcw_criterias == 'pending':
                #         raise UserError("Admit Card Not Generated STCW  Criteria not Complied")
            
            # candidate_image = base64.b64encode(docs1.candidate_image).decode()
            
            # try:
            #     docs1.candidate_image.decode('utf-8')
            # except QWebException:
            #     docs1.candidate_image = None
            # import wdb; wdb.set_trace();
            return {
                'doc_ids': docids,
                'doc_model': 'gp.exam.schedule',
                'docs': docs1
                }


class CandidateAdmitCardCcmc(models.AbstractModel):
    _name = 'report.bes.candidate_admit_card_ccmc'
    _description = 'Candidate Admit Card'
    

    
    
    
    @api.model
    def _get_report_values(self, docids, data=None):
        
        
        docs1 = self.env['ccmc.exam.schedule'].sudo().browse(docids)
        # docs1 = self.env['gp.exam.schedule'].sudo().search([('id','=',docids)])
        # print("doc_idsss")
        user_id = self.env.user
        # import wdb; wdb.set_trace()
        if user_id.has_group('bes.download_not_allowed'):
            # User is in the group
            raise ValidationError("Please Contact Administrator")
        
        for docs in docs1:
            if docs.attendance_criteria == 'pending' :
                raise ValidationError("Admit Card Not Generated Attendance Criteria not Complied")
            
            
            if docs.ship_visit_criteria == 'pending' :
                raise ValidationError("Admit Card Not Generated Ship Visit  Criteria not Complied")
            
            # if not docs.institute_id.code == "M05":
                
            #     if docs.stcw_criteria == 'pending':
            #         raise ValidationError("Admit Card Not Generated STCW  Criteria not Complied")

        # import wdb; wdb.set_trace();
        
        # candidate_image = base64.b64encode(docs1.candidate_image).decode()
        
        # try:
        #     docs1.candidate_image.decode('utf-8')
        # except QWebException:
        #     docs1.candidate_image = None
        return {
            'doc_ids': docids,
            'doc_model': 'ccmc.exam.schedule',
            'docs': docs1
            }

