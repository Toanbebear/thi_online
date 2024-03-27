from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime


class CreateStudent(models.TransientModel):
    _name = 'student.from.booking'

    def _get_lines_domain(self):
        # Todo: Tìm cách viết tối ưu hơn
        res_ids = []
        original_domain = [('crm_id', '=', self.env.context.get('default_lead_id')), ('stage', '=', 'new')]
        original_lines = self.env['crm.line'].search(original_domain)
        for rec in original_lines:
            if rec.paid and rec.paid == rec.total:
                res_ids.append(rec.id)
            debt = self.env['crm.debt.review'].search(
                [('booking_id', '=', rec.crm_id.id), ('crm_line_ids.product_id', '=', rec.product_id.id)])
            if debt.stage == 'approve':
                res_ids.append(rec.id)
        return [('id', 'in', res_ids)]

    name = fields.Char('Name')
    phone = fields.Char('Phone')
    institute_id = fields.Many2one('op.institute', string='Institute')
    course_ids = fields.Many2many('op.course', string='Course')
    line_ids = fields.Many2many('crm.line', 'select_courses_ref', 'crm_line_s', 'select_course_s',
                                string='Courses', domain=_get_lines_domain)
    class_ids = fields.Many2many('op.batch', string='Class',
                                 domain="[('institute','=',institute_id), ('course_id', '=', course_ids)]")
    lead_id = fields.Many2one('crm.lead', string='Lead')
    covert_gender_to_op_student = fields.Selection(
        [('m', 'Male'), ('f', 'Female'), ('o', 'Other')],
        string='Gender', compute='convert_gender', store=True)

    @api.onchange('line_ids')
    def set_course(self):
        self.course_ids = False
        if self.line_ids:
            self.course_ids = [(6, 0, self.line_ids.mapped('course_id').ids)]

    @api.onchange('institute_id')
    def reset_course_ids(self):
        self.course_ids = False
        self.line_ids = False

    @api.onchange('course_ids')
    def reset_class_ids(self):
        self.class_ids = False

    @api.depends('lead_id.gender')
    def convert_gender(self):
        if self.lead_id:
            if self.lead_id.gender == 'male':
                self.covert_gender_to_op_student = 'm'
            elif self.lead_id.gender == 'female':
                self.covert_gender_to_op_student = 'f'
            else:
                self.covert_gender_to_op_student = 'o'

    def create_student(self):
        if self.lead_id:
            if self.lead_id.birth_date:
                student = self.env['op.student'].create({
                    'name': self.lead_id.partner_id.name,
                    'already_partner': True,
                    'partner_id': self.lead_id.partner_id.id,
                    'birth_date': self.lead_id.partner_id.birth_date,
                    'gender': self.covert_gender_to_op_student,
                    'phone': self.lead_id.partner_id.phone,
                    'institute_id': self.institute_id.id,
                    'email': self.lead_id.email_from,
                    'visa_info': self.lead_id.pass_port,
                    'street': self.lead_id.street
                })
            else:
                date_birth = datetime.strptime('01-01-' + self.lead_id.year_of_birth, '%d-%m-%Y').date()
                student = self.env['op.student'].create({
                    'name': self.lead_id.partner_id.name,
                    'student_id': self.lead_id.partner_id.code_customer,
                    'already_partner': True,
                    'partner_id': self.lead_id.partner_id.id,
                    'birth_date': date_birth,
                    'gender': self.covert_gender_to_op_student,
                    'phone': self.lead_id.partner_id.phone,
                    'institute_id': self.institute_id.id,
                    'email': self.lead_id.email_from,
                    'visa_info': self.lead_id.pass_port
                })
        return student

    def create_student_user(self):
        # Nesu chưa có user thì tạo user
        if self.lead_id.partner_id.code_customer:
            login = self.lead_id.partner_id.code_customer.lower()
            user = self.env['res.users'].sudo().create({
                'name': self.lead_id.partner_id.name,
                'type': 'contact',
                'login': login,
                'partner_id': self.lead_id.partner_id.id,
                'company_ids': [(6, 0, [self.lead_id.company_id.id])],
                'company_id': self.lead_id.company_id.id,
                'password': '1',
                'groups_id': [(6, 0, [self.env.ref('openeducat_core.group_op_student').id])],
            })

    def arrange_class(self):
        # Nếu chưa có học viên thì tạo học viên
        sci_student = self.env['op.student'].search([('phone', '=', self.phone)], limit=1)
        if not sci_student:
            sci_student = self.create_student()
            self.create_student_user()
        # xếp lớp
        if self.class_ids:
            for rec in self.class_ids:
                rec.write({
                    'student_course': [(0, 0, {
                        'student_id': sci_student.id,
                        'course_id': rec.course_id.id,
                    })]
                })
        # Xuất Bom đi kèm khóa học
        vals = []
        institute_location = self.institute_id.location
        warehouse = institute_location.get_warehouse()
        picking_type = warehouse.out_type_id
        origin = 'Student BOM - %s' % self.name
        for course in self.course_ids:
            if course.bom.products:
                for line in course.bom.products:
                    qty_on_hand = self.env['stock.quant']._get_available_quantity(product_id=line.product,
                                                                                  location_id=institute_location)
                    line_qty = line.quantity
                    if line.uom_id != line.product.uom_id:
                        line_qty = line.uom_id._compute_quantity(line.quantity, line.product.uom_id)
                    if qty_on_hand < line_qty:
                        raise ValidationError(("%s out of stock in %s.\
                                                 Please contact inventory manager." % (
                            line.product.name, institute_location)))
                    else:
                        vals.append((0, 0, {'name': 'BOM' + line.product.name,
                                            'date': fields.Date.today(),
                                            'company_id': self.env.user.company_id.id,
                                            'date_expected': fields.Date.today(),
                                            'product_id': line.product.id,
                                            'product_uom_qty': line.quantity,
                                            'product_uom': line.uom_id.id,
                                            'location_id': institute_location.id,
                                            'location_dest_id': sci_student.partner_id.property_stock_customer.id}))
                origin += '- %s' % course.name
        if vals:
            stock_picking = self.env['stock.picking'].sudo().create({'name': picking_type.sequence_id.next_by_id(),
                                                                     'origin': origin,
                                                                     'partner_id': sci_student.partner_id.id,
                                                                     'picking_type_id': picking_type.id,
                                                                     'location_id': institute_location.id,
                                                                     'location_dest_id': sci_student.partner_id.property_stock_customer.id,
                                                                     'immediate_transfer': True,
                                                                     'move_ids_without_package': vals})
            stock_picking.sudo().action_assign()
            for move_id in stock_picking.move_ids_without_package:
                move_id.quantity_done = move_id.product_uom_qty
            stock_picking.sudo().button_validate()

        # Tạo SO và xác nhận
        for rec in self.line_ids:
            if rec.stage == 'new':
                order = self.env['sale.order'].create({
                    'partner_id': self.lead_id.partner_id.id,
                    'pricelist_id': self.lead_id.price_list_id.id,
                    'company_id': self.env.user.company_id.id,
                    'booking_id': self.lead_id.id,
                    'campaign_id': self.lead_id.campaign_id.id,
                    'source_id': self.lead_id.source_id.id,
                    # 'set_total': self.set_total_order,
                })
                order_line = self.env['sale.order.line'].create({
                    'order_id': order.id,
                    'crm_line_id': rec.id,
                    'product_id': rec.product_id.id,
                    'product_uom': rec.product_id.uom_id.id,
                    'company_id': self.env.user.company_id.id,
                    'price_unit': rec.unit_price,
                    'discount': rec.discount_percent,
                    'discount_cash': rec.discount_cash / rec.quantity,
                    'product_uom_qty': 1,
                    'tax_id': False,
                })
        return {
            'name': 'Student',
            'res_id': sci_student.id,
            'active_id': sci_student.id,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('openeducat_core.view_op_student_form').id,
            'res_model': 'op.student',
        }
