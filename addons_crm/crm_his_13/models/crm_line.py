from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)


class CrmLine(models.Model):
    _inherit = 'crm.line'
    institution = fields.Many2one('sh.medical.health.center', string='Institution')
    institution_shared = fields.Many2many('sh.medical.health.center', 'institution_shared_line_ref', 'institutions',
                                          'line', string='Institution shared', compute='get_institution', store=True)
    service_id = fields.Many2one('sh.medical.health.center.service', string='Service')
    exam_room_ids = fields.Many2many('sh.medical.health.center.ot', 'exam_room_line_ref', 'exam_room', 'line',
                                     string='Exam room', compute='set_service', store=True)
    odontology = fields.Boolean('Odontology', compute='set_odontology', store=True)
    consultants = fields.Many2one('res.users', string='Consultants', default=lambda self: self.env.user)
    come_number = fields.Integer('Come number', compute='come_number_compute', store=True)

    @api.depends('sale_order_line_id', 'crm_id', 'service_id')
    def come_number_compute(self):
        for record in self:
            if record.sale_order_line_id and record.crm_id and record.service_id:
                walkin = self.env['sh.medical.appointment.register.walkin'].search(
                    [('booking_id', '=', record.crm_id.id), ('service', 'in', [record.service_id.id])])
                record.come_number = len(walkin)

    @api.depends('service_id')
    def set_odontology(self):
        for rec in self:
            rec.odontology = False
            if rec.service_id.service_department and 'Odontology' in rec.service_id.service_department.mapped('type'):
                rec.odontology = True

    @api.depends('company_id', 'company_shared')
    def get_institution(self):
        for rec in self:
            if rec.crm_id.type_brand == 'hospital':
                if rec.company_id and rec.company_shared:
                    list_company = rec.company_shared._origin.ids
                    list_company.append(rec.company_id.id)
                    list_institution = []
                    for i in list_company:
                        institution = self.env['sh.medical.health.center'].sudo().search([('his_company', '=', i)])
                        list_institution.append(institution.id)
                    rec.institution_shared = [(6, 0, list_institution)]

                elif rec.company_id:
                    institution = self.env['sh.medical.health.center'].sudo().search(
                        [('his_company', '=', rec.company_id.id)])
                    rec.institution_shared = [(6, 0, [institution.id])]
            else:
                rec.institution_shared = False

    @api.onchange('service_id')
    def get_product_hospital(self):
        if self.service_id:
            self.product_id = self.service_id.product_id.id

    @api.depends('service_id', 'institution_shared')
    def set_service(self):
        for rec in self:
            rec.exam_room_ids = False
            if rec.service_id and rec.institution_shared:
                list_room = []
                for i in rec.service_id.exam_room:
                    if i.institution in rec.institution_shared._origin:
                        list_room.append(i.id)
                rec.exam_room_ids = [(6, 0, list_room)]

    @api.model
    def create(self, vals):
        res = super(CrmLine, self).create(vals)
        if res.product_id:
            _logger.warning('run step 1')
            service = self.env['sh.medical.health.center.service'].search([('product_id', '=', res.product_id.id)])
            _logger.warning(service)
            if service:
                res.service_id = service.id
                _logger.warning('run step 2')
        return res
