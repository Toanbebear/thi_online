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

from odoo import models, fields, api, _
import re
from odoo.exceptions import ValidationError


class OPInstitute(models.Model):
    _name = "op.institute"
    _inherit = "mail.thread"
    _description = "Institute"

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)
    location = fields.Many2one('stock.location', 'Storage')
    address = fields.Many2one('res.partner', 'Address', required=True)
    department = fields.Many2one('hr.department', 'Department')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)

    def no_accent_vietnamese(selft, s):
        s = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
        s = re.sub(r'[ÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪ]', 'A', s)
        s = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', s)
        s = re.sub(r'[ÈÉẸẺẼÊỀẾỆỂỄ]', 'E', s)
        s = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
        s = re.sub(r'[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]', 'O', s)
        s = re.sub(r'[ìíịỉĩ]', 'i', s)
        s = re.sub(r'[ÌÍỊỈĨ]', 'I', s)
        s = re.sub(r'[ùúụủũưừứựửữ]', 'u', s)
        s = re.sub(r'[ƯỪỨỰỬỮÙÚỤỦŨ]', 'U', s)
        s = re.sub(r'[ỳýỵỷỹ]', 'y', s)
        s = re.sub(r'[ỲÝỴỶỸ]', 'Y', s)
        s = re.sub(r'[Đ]', 'D', s)
        s = re.sub(r'[đ]', 'd', s)
        s = re.sub(r'[^\w.]', '', s)
        return s

    @api.model
    def create(self, vals):
        str_name = vals['name'].split()
        codeWH = ''
        for str in str_name:
            codeWH += str[0]
        codeWH = self.no_accent_vietnamese(codeWH).upper()
        institute = super(OPInstitute, self).create(vals)
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', institute.company_id.id)], limit=1)
        if warehouse:
            institute_wh = self.env['stock.location'].sudo().create({
                'name': codeWH,
                'location_id': warehouse.lot_stock_id.id,
                'usage': 'internal'})
            institute.location = institute_wh.id
        return institute

    def open_stock_quant(self):
        return {
            'name': _('Institute stock'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'stock.quant',
            'context': {'search_default_productgroup': 1},
            'domain': [('location_id', '=', self.location.id)],
        }
