import logging
import re

from odoo import models, fields

try:
    import qrcode
except ImportError:
    qrcode = None
try:
    import base64
except ImportError:
    base64 = None

email_validator = re.compile(r"[^@]+@[^@]+\.[^@]+")
phone_number_validator = re.compile("^[0-9/]*$")
_logger = logging.getLogger(__name__)


class CRMBrand(models.Model):
    _inherit = 'res.brand'

    survey_id = fields.Many2one('Survey')
