from odoo import models , fields,api
import json
import base64
from io import BytesIO
from lxml import etree
from datetime import datetime
from odoo.exceptions import UserError,ValidationError


class IVCanditateAdmitCard(models.AbstractModel):
    _name = 'report.bes.reports_iv_candidate_admit_card'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['iv.candidates'].sudo().browse(docids)
        
        
        return {
            'docids': docids,
            'doc_model': 'iv.candidates',
            'data': data,
            'docs': docs,
        }


class IVCanditateCertificate(models.AbstractModel):
    _name = 'report.bes.reports_iv_candidate_certificates'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['iv.candidates'].sudo().browse(docids)

        applications = self.env['candidates.application'].sudo().browse(docids)
        batch = self.env['iv.batches'].sudo().browse(docids)
        
        
        return {
            'docids': docids,
            'doc_model': 'iv.candidates',
            'data': data,
            'docs': docs,
            'applications':applications,
            'batch':batch,
        }
    
    
    