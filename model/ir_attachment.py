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
        if not vals.get('datas'):
            return

        # Decode file
        try:
            file_bytes = base64.b64decode(vals['datas'])
        except Exception:
            raise ValidationError("Invalid file encoding.")

        # Detect real MIME
        mime = magic.from_buffer(file_bytes, mime=True)

        if mime not in ALLOWED_MIMES:
            raise ValidationError("Invalid or unsafe file type detected.")

        # OPTIONAL: extension check only if extension exists
        filename = vals.get('name', '')
        ext = os.path.splitext(filename)[1].lower()

        if ext:
            expected_ext = EXTENSION_BY_MIME.get(mime)
            if expected_ext and ext != expected_ext:
                raise ValidationError(
                    f"File extension does not match file content ({expected_ext})."
                )

    @api.model
    def create(self, vals):
        self._validate_file(vals)
        return super().create(vals)

    def write(self, vals):
        self._validate_file(vals)
        return super().write(vals)
