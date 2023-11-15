from odoo import models , fields,api
import json
import base64
from io import BytesIO
from lxml import etree


class CandidateAdmitCard(models.AbstractModel):
    _name = 'report.bes.candidate_admit_card'
    _description = 'Candidate Admit Card'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs1 = self.env['gp.candidate'].sudo().browse(docids)
        # try:
        #     docs1.candidate_image.decode('utf-8')
        # except QWebException:
        #     docs1.candidate_image = None
        return {
            'doc_ids': docids,
            'doc_model': 'gp.candidate',
            'docs': docs1,
        }
