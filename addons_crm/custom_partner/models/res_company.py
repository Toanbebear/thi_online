from odoo import fields, api, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    code = fields.Char('Code company')

