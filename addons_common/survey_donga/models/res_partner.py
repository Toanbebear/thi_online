# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import re

from werkzeug import urls

from odoo import models, api, fields
from odoo.addons.http_routing.models.ir_http import slug

try:
    import qrcode
except ImportError:
    qrcode = None
try:
    import base64
except ImportError:
    base64 = None
from io import BytesIO

email_validator = re.compile(r"[^@]+@[^@]+\.[^@]+")
phone_number_validator = re.compile("^[0-9/]*$")
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    survey_qr = fields.Binary(string="QR Code", compute='generate_qr')
    survey_url = fields.Char(string="Survey URL", compute='generate_qr')

    @api.depends('company_id.survey_id', 'name')
    def generate_qr(self):
        for record in self:
            base_url = '/' if self.env.context.get('relative_url') else \
                self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if type(record.id) is int:
                survey_url = urls.url_join \
                    (base_url, "survey/start-loyalty/%s/%s" % (slug(record.company_id.survey_id), slug(record)))
                record.survey_url = survey_url
            else:
                survey_url = ''
            if qrcode and base64 and survey_url:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(survey_url)
                qr.make(fit=True)
                img = qr.make_image()
                temp = BytesIO()
                img.save(temp, format="PNG")
                qr_image = base64.b64encode(temp.getvalue())
                record.survey_qr = qr_image

    @api.multi
    def start_survey(self):
        base_url = '/' if self.env.context.get('relative_url') else \
            self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {
            'type': 'ir.actions.act_url',
            'name': "Start Survey",
            'target': 'self',
            'url': urls.url_join(base_url,
                                 "survey/start-loyalty/%s/%s" % (slug(self.company_id.survey_id), slug(self)))
        }

    @api.multi
    def start_hcm_survey(self):
        base_url = '/' if self.env.context.get('relative_url') else \
            self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {
            'type': 'ir.actions.act_url',
            'name': "Start Survey",
            'target': 'self',
            'url': urls.url_join(base_url,
                                 "survey/start-loyalty/%s/%s" % (slug(self.company_id.survey_hcm_id), slug(self)))
        }
