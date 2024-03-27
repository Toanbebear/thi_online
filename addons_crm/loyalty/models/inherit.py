from odoo import fields, api, models
from lxml import etree
import json


class CrmLoyalty(models.Model):
    _inherit = 'crm.lead'

    loyalty_id = fields.Many2one('crm.loyalty.card', string='Loyalty')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(CrmLoyalty, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                      submenu=submenu)
        doc = etree.XML(res['arch'])
        view_booking = self.env.ref('crm_base.crm_lead_form_booking')
        if view_type == 'form' and view_id == view_booking.id:
            for node in doc.xpath("//field[@name='user_id']"):
                node.set("readonly", "True")
                modifiers = json.loads(node.get("modifiers"))
                modifiers['readonly'] = True
                node.set("modifiers", json.dumps(modifiers))
        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res


class LoyaltyCrmLine(models.Model):
    _inherit = 'crm.line'

    reward_id = fields.Many2one('crm.loyalty.line.reward', string='Reward')


class SaleOrderLoyalty(models.Model):
    _inherit = 'sale.order'

    loyalty_id = fields.Many2one('crm.loyalty.card', string='Loyalty')

    @api.model
    def create(self, vals):
        res = super(SaleOrderLoyalty, self).create(vals)
        if res.partner_id:
            loyalty = self.env['crm.loyalty.card'].search(
                [('partner_id', '=', self.partner_id.id),
                 ('brand_id', '=', self.company_id.brand_id.id)])
            res.loyalty_id = loyalty.id
        return res

    @api.onchange('partner_id')
    def set_loyalty(self):
        if self.partner_id:
            loyalty = self.env['crm.loyalty.card'].search(
                [('partner_id', '=', self.partner_id.id), ('brand_id', '=', self.company_id.brand_id.id)])
            self.loyalty_id = loyalty.id

    def action_confirm(self):
        res = super(SaleOrderLoyalty, self).action_confirm()
        if self.loyalty_id:
            self.loyalty_id.amount += self.amount_total
        else:
            loyalty = self.env['crm.loyalty.card'].search(
                [('partner_id', '=', self.partner_id.id), ('brand_id', '=', self.company_id.brand_id.id)])
            self.loyalty_id = loyalty.id
            self.loyalty_id.amount += self.amount_total
        return res


class CheckPartnerLoyalty(models.TransientModel):
    _inherit = 'check.partner.qualify'

    def create_phone_call(self, booking):
        res = super(CheckPartnerLoyalty, self).create_phone_call(booking)
        loyalty = self.env['crm.loyalty.card'].search(
            [('partner_id', '=', booking.partner_id.id), ('brand_id', '=', self.company_id.brand_id.id)])
        if loyalty:
            booking.loyalty_id = loyalty.id
        return res


class LoyaltySelectService(models.TransientModel):
    _inherit = 'crm.select.service'

    def create_quotation(self):
        res = super(LoyaltySelectService, self).create_quotation()

        if not self.booking_id.loyalty_id:
            loyalty = self.env['crm.loyalty.card'].create({
                'partner_id': self.partner_id.id,
                'company_id': self.booking_id.company_id.id,
                'date_interaction': fields.Datetime.now(),
                'source_id': self.booking_id.source_id.id,
            })
            self.booking_id.loyalty_id = loyalty.id

        return res
