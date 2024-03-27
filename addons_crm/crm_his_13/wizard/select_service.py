from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class CRMSelectService(models.TransientModel):
    _inherit = 'crm.select.service'

    institution = fields.Many2one('sh.medical.health.center', string='Institution',
                                  domain="[('id','in',institution_ids)]")
    exam_room_id = fields.Many2one('sh.medical.health.center.ot', string='Exam room',
                                   domain="[('department.type','=','Examination'),('institution','=',institution),('related_department', '!=', False)]")
    crm_line_ids = fields.Many2many(
        domain="['|',('stage', '=', 'new'),('odontology','=',True),"
               "('exam_room_ids','in',exam_room_id),('crm_id','=',booking_id)]")

    institution_ids = fields.Many2many('sh.medical.health.center', string='List institution',
                                       compute='set_institutions', store=True)
    dentistry = fields.Boolean('Dentistry')

    @api.constrains('set_total_order')
    def check_set_total_order(self):
        for rec in self:
            tt = 0
            if rec.crm_line_ids:
                for record in rec.crm_line_ids:
                    tt += record.total / record.quantity
                if rec.set_total_order > tt:
                    raise ValidationError(_('The amount entered exceeds the amount for the service'))

    @api.onchange('crm_line_ids')
    def set_dentistry(self):
        if self.crm_line_ids and True in self.crm_line_ids.mapped('odontology'):
            self.dentistry = True

    @api.onchange('institution')
    def reset_exam(self):
        self.exam_room_id = False

    @api.onchange('exam_room_id')
    def reset_service(self):
        self.crm_line_ids = False

    @api.depends('company_ids')
    def set_institutions(self):
        for rec in self:
            if rec.booking_id.type_brand == 'hospital':
                list_institution = []
                if rec.company_ids:
                    for company in rec.company_ids._origin.ids:
                        ins = self.env['sh.medical.health.center'].sudo().search([('his_company', '=', company)])
                        list_institution.append(ins.id)
                    rec.institution_ids = [(6, 0, list_institution)]
            else:
                rec.institution_ids = False
