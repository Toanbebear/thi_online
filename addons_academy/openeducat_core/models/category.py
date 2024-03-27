# -*- coding: utf-8 -*-
###############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech-Receptives(<http://www.techreceptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import models, fields, api
from odoo.osv import expression


class OpCategory(models.Model):
    _name = "op.category"
    _description = "OpenEduCat Category"

    name = fields.Char('Code', required=True)
    code = fields.Char('Name', required=True)
    parent_id = fields.Many2one('op.category', 'Parent Category')
    icon = fields.Char('Icon')

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('code', operator, name)]
        category_ids = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return self.browse(category_ids).name_get()

    @api.model
    def op_category_switch_name_code(self):
        for record in self.env['op.category'].search([]):
            record.name, record.code = record.code, record.name

    _sql_constraints = [
        ('unique_category_code',
         'unique(name)', 'Code should be unique per category!')]
