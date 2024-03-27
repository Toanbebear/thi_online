from odoo import api, fields, models


class Payment(models.Model):
    _inherit = 'account.payment'

    type_brand = fields.Selection(related='brand_id.type')
