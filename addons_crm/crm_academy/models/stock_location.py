from odoo import api, fields, models


class InheritLocation(models.Model):
    _inherit = 'stock.location'

    faculty_id = fields.Many2one('op.faculty', string='Faculty')
