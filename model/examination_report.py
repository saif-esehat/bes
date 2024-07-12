from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
import random
import logging
import qrcode
import io
import base64
from datetime import datetime , date
import math
from odoo.http import content_disposition, request , Response
from odoo.tools import date_utils
import xlsxwriter



class ExaminationReport(models.Model):
    _name = "examination.report"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'Examination Report'
    
    
    examination_batch = fields.Many2one("dgs.batches",string="Examination Batch",tracking=True)
    

    
    
    