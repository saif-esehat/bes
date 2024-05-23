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
        for record in docids:
        
            docs1 = self.env['gp.exam.schedule'].sudo().browse(record)
            print("doc_idsss",docids)
            
            # import wdb; wdb.set_trace();
            if docs1.attendance_criteria == 'pending' and docs1.ship_visit_criteria == 'pending' and  docs1.stcw_criteria == 'pending' :
                raise ValidationError("Admit Card Not Generated Due to  Criteria not Complied")
            
            # candidate_image = base64.b64encode(docs1.candidate_image).decode()
            
            # try:
            #     docs1.candidate_image.decode('utf-8')
            # except QWebException:
            #     docs1.candidate_image = None
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
        print("doc_idsss",docids)
        
        
        if docs1.attendance_criteria == 'pending' and docs1.ship_visit_criteria == 'pending' and  docs1.stcw_criteria == 'pending' :
            raise ValidationError("Admit Card Not Generated Due to  Criteria not Complied")
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

