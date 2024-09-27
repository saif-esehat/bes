from odoo import models , fields,api
import json
import base64
from io import BytesIO
from lxml import etree
from datetime import datetime
from odoo.exceptions import UserError,ValidationError

import logging

_logger = logging.getLogger(__name__)



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
    
    # @api.model
    # def _get_report_values(self, docids, data=None):
    #     docs = self.env['iv.candidates'].sudo().browse(docids)

    #     applications = self.env['candidates.application'].sudo().browse(docids)

    #     batch = self.env['iv.batches'].sudo().browse(docids)

        
        
    #     return {
    #         'docids': docids,
    #         'doc_model': 'iv.candidates',
    #         'data': data,
    #         'docs': docs,
    #         'applications':applications,
    #         'batch':batch,
    #     }

    # @api.model
    # def _get_report_values(self, docids, data=None):
    #     # Fetch iv.candidates records
    #     docs = self.env['iv.candidates'].sudo().browse(docids)
        
    #     # Extract batch_ids from iv.candidates records
    #     batch_ids = docs.mapped('batch_id')  # Replace 'batch_id' with the correct field if different

    #     # Fetch iv.batches records where the id is in batch_ids
    #     batches = self.env['iv.batches'].sudo().search([
    #         ('id', 'in', batch_ids.ids)
    #     ])
        
    #     # Extract candidate names from iv.candidates records
    #     candidate_names = docs.mapped('name')  # Assuming 'name' is the field used for matching

    #     # Filter candidates.application records where the name matches
    #     applications = self.env['candidates.application'].sudo().search([
    #         ('name', 'in', candidate_names)  # Assuming 'name' is the field in candidates.application
    #     ])
        
    #     return {
    #         'docids': docids,
    #         'doc_model': 'iv.candidates',
    #         'data': data,
    #         'docs': docs,
    #         'applications': applications,
    #         'batches': batches,
    #     }

    @api.model
    def _get_report_values(self, docids, data=None):
        # Fetch iv.candidates records
        docs = self.env['iv.candidates'].sudo().browse(docids)
        
        # Extract batch_ids from iv.candidates records
        batch_ids = docs.mapped('batch_id.id')  # Ensure 'batch_id' is correctly mapped to 'id'

        # Fetch iv.batches records where the id is in batch_ids
        batches = self.env['iv.batches'].sudo().search([
            ('id', 'in', batch_ids)
        ])
        
        # Extract candidate names from iv.candidates records
        candidate_names = docs.mapped('name')  # Ensure 'name' is the correct field in candidates

        # Filter candidates.application records where the name matches
        applications = self.env['candidates.application'].sudo().search([
            ('name', 'in', candidate_names)  # Ensure 'name' is the correct field in candidates.application
        ])
        
        return {
            'docids': docids,
            'doc_model': 'iv.candidates',
            'data': data,
            'docs': docs,
            'applications': applications,
            'batches': batches,
        }