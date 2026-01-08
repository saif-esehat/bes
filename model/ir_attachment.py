from odoo import models, api
from odoo.exceptions import ValidationError
import os
import base64
import magic   # apt install libmagic1 + pip install python-magic

ALLOWED_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.docx', '.csv', '.xlsx']
ALLOWED_MIMES = [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/csv',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
]

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def _validate_file(self, vals):
        if vals.get('datas') and vals.get('name'):
            # Extension check
            ext = os.path.splitext(vals['name'])[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise ValidationError(
                    "File type not allowed. Allowed formats: PDF, JPG, PNG, DOCX, CSV, XLSX"
                )

            # MIME check (real content)
            file_bytes = base64.b64decode(vals['datas'])
            mime = magic.from_buffer(file_bytes, mime=True)

            if mime not in ALLOWED_MIMES:
                raise ValidationError("Invalid or unsafe file type detected.")

    @api.model
    def create(self, vals):
        self._validate_file(vals)
        return super().create(vals)

    def write(self, vals):
        self._validate_file(vals)
        return super().write(vals)
