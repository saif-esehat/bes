from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
from datetime import datetime


class BooksOrder(models.Model):
    _name = "order.books"
    _description= 'Books Order'

    institute_id = fields.Many2one('bes.institute',string="Institute")
    order_date = fields.Date('Order Date')
    state = fields.Selection([
        ('posted','Posted'),
        ('order_confirmed','Order Confirmed'),
        ('dispatched','Dispatched'),
        ('completed','Completed'),
        ], string='State',default="draft")
    order_lines = fields.One2many('order.books.line','order_id',string="Orders")
    tracking_id = fields.Char('Tracking Id')
    transaction_id = fields.Char("Transaction Id")
    payment_slip = fields.Binary("Payment Slip")
    slip_file_name = fields.Char('filename')

class BooksOrderLine(models.Model):
    _name = "order.books.line"
    _description= 'Books Order Line'

    order_id = fields.Many2one('order.books')
    product_id = fields.Many2one('product.template',string='Product')
    quantity = fields.Integer("Quantity")
    price_per_unit = fields.Float("Price per unit")
    total_price = fields.Float("Total Price",compute="_compute_total_price")

    @api.depends('quantity','price_per_unit')
    def _compute_total_price(self):
        for record in self:
            record.total = round(record.quantity * record.price_per_unit,2)