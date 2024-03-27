from werkzeug import urls

from odoo import models, api, fields
from odoo.addons.http_routing.models.ir_http import slug


class LoyaltyCard(models.Model):
    _inherit = "loyalty.card"


    def start_survey(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'name': "Start Survey",
            'target': 'self',
            'url': '/survey/start/%s/partner_id=%s' % (self.brand_id.survey_id, self.partner_id)
        }


