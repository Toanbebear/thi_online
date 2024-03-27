# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class FacilityInvoice(models.TransientModel):
    _name = "facility.invoice"
    _description = "Faculty Invoice"

    partner_id = fields.Many2one('res.partner', 'Customer', required=True)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    from_date = fields.Date('From Date', required=True)
    to_date = fields.Date('To Date', required=True)

    def create_invoice(self):
        self.ensure_one()
        facility = self.env['op.facility.allocation'].browse(
            [self.env.context.get('active_id', False)])
        account_id = False
        product = self.product_id
        if product.id:
            account_id = product.property_account_income_id.id
        if not account_id:
            account_id = product.categ_id.property_account_income_categ_id.id
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s". \
                   You may have to install a chart of account from Accounting \
                   app, settings menu.') % (product.name,))

        invoice = self.env['account.move'].create({
            'partner_id': self.partner_id.id,
            'type': 'out_invoice',
            'reference': False,
            'date_invoice': fields.Date.today(),
            'account_id': self.partner_id.property_account_receivable_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': product.name,
                'account_id': account_id,
                'price_unit': self.product_id.list_price,
                'quantity': 1.0,
                'discount': 0.0,
                'uom_id': self.product_id.uom_id.id,
                'product_id': product.id,
            })],
        })
        invoice.compute_taxes()
        facility.invoice_id = invoice.id
        form_view = self.env.ref('account.invoice_form')
        tree_view = self.env.ref('account.invoice_tree')
        value = {
            'domain': str([('id', '=', invoice.id)]),
            'view_mode': 'form',
            'res_model': 'account.move',
            'view_id': False,
            'views': [(form_view.id, 'form'),
                      (tree_view.id, 'tree')],
            'type': 'ir.actions.act_window',
            'res_id': invoice.id,
            'target': 'current',
            'nodestroy': True
        }
        return value
