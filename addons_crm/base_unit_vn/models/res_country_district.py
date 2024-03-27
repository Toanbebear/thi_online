# -*- coding: utf-8 -*-

from odoo import fields, api, models, _


class CountryDistrict(models.Model):
    _name = "res.country.district"

    name = fields.Char('Name', required=True)
    state_id = fields.Many2one('res.country.state', 'City', required=True)
    active = fields.Boolean('Active', default=True)

