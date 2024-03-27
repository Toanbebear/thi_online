from odoo import fields, models, api, _


class TypeCrm(models.Model):
    _name = 'crm.type'

    name = fields.Char('Name')
    type_crm = fields.Selection([('lead', 'Lead'), ('opportunity', 'Opportunity')], string='Type')
    phone_call = fields.Boolean('Phone call')
    stage_id = fields.Many2many('crm.stage', 'stage_type_crm_ref', 'type_crm', 'stage', string='Stage')
