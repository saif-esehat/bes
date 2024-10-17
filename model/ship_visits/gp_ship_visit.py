from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError
import base64
from io import BytesIO
import xlsxwriter
from datetime import datetime
import xlrd


class GPShipVisit(models.Model):
    _name = "gp.batches.ship.visit"
    _rec_name = "ship_name1"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description= 'Gp Ship Visit'


    ship_name1 = fields.Char(string="Ship Name")
    port_name = fields.Char(string="Port Name")
    imo_no = fields.Char(string="IMO  No.")
    date_of_visit = fields.Date(string="Date Of Visit")
    time_spent = fields.Float(string="Time Spent")
    gp_image = fields.Binary(string="Image", attachment=True)
    candidate_ids = fields.Many2many('gp.candidate', string="GP Candidates")
    course_gp = fields.Char(string="Course")
    no_of_candidate = fields.Char(string="Number Of Candidate")
    institute_id = fields.Many2one("bes.institute","Institute ID",tracking=True)
    gp_ship_batch_id = fields.Many2one('institute.gp.batches', string="Batch")
    gp_or_ccmc_batch = fields.Selection([('gp','GP'),('ccmc','CCMC')],string="GP / CCMC",tracking=True)
    dgs_batch = fields.Many2one('dgs.batches', string="DGS Batch", required=True)
    # institute_batch_id = fields.Many2one('institute.batch', string="Institute Batch")


