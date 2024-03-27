from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class ApplyDiscount(models.TransientModel):
    _name = 'crm.apply.voucher'

    name = fields.Char('Voucher')
    partner_id = fields.Many2one('res.partner', string='Partner')
    crm_id = fields.Many2one('crm.lead', string='Booking/lead')

    def check_code_voucher(self):
        voucher = self.env['crm.voucher'].search([('name', '=', self.name)])
        if not voucher:
            raise ValidationError('Mã voucher này không tồn tại')
        if voucher.brand_id != self.crm_id.brand_id:
            raise ValidationError('Voucher này chỉ được áp dụng cho thương hiệu %s' % voucher.brand_id.name)
        elif voucher.voucher_program_id.company_id \
                and self.crm_id.company_id not in voucher.voucher_program_id.company_id:
            raise ValidationError(
                'Chi nhánh %s không được phép áp dụng voucher này !!' % self.crm_id.company_id.name)
        elif voucher.stage_voucher == 'used':
            raise ValidationError('Voucher này đã được sử dụng')
        elif voucher.stage_voucher == 'new':
            raise ValidationError('Voucher này hiện chưa khả dụng')
        elif voucher.end_date < datetime.now():
            voucher.write({'stage_voucher': 'expire'})
            raise ValidationError('Voucher này đã hết hạn')
        elif self.partner_id and voucher.partner_id and voucher.partner_id == self.crm_id.partner_id:
            raise ValidationError('Voucher này thuộc quyền sử dụng của khách hàng %s' % voucher.partner_id.name)
        else:
            self.check_service_voucher(voucher)

    def check_service_voucher(self, voucher):
        prg = voucher.voucher_program_id
        if prg.type_voucher == 'fix':
            self.create_crm_line_by_voucher(prg, voucher)
        elif prg.type_voucher == 'dis':
            lines = self.crm_id.crm_line_ids.filtered(
                lambda
                    line: line.stage == 'new'
                          and line.number_used == 0
                          and not line.voucher_id
                          and prg not in line.prg_voucher_ids)
            if lines:
                if prg.product_ids:
                    prd_1 = lines.mapped('product_id')
                    prd_2 = prg.product_ids
                    prd_3 = set(prd_1) & set(prd_2)
                    if prd_3:
                        list_line = lines.filtered(lambda l: l.product_id in prd_3)
                        self.set_discount(list_line, prg, voucher)
                    else:
                        raise ValidationError(
                            'Các dịch vụ hiện có đang không nằm trong danh sách áp dụng của voucher !!!')

                elif prg.product_ctg_ids:
                    ctg_1 = lines.mapped('product_ctg_id')
                    ctg_2 = prg.product_ctg_ids
                    ctg_3 = set(ctg_1) & set(ctg_2)
                    if ctg_3:
                        list_line = lines.filtered(lambda l: l.product_ctg_id in ctg_3)
                        self.set_discount(list_line, prg, voucher)
                    else:
                        raise ValidationError(
                            'Nhóm dịch vụ hiện có đang không nằm trong danh sách áp dụng của voucher !!!')

                else:
                    self.set_discount(lines, prg)
            else:
                raise ValidationError('Không có bất kỳ line dịch vụ nào đủ điều kiện để áp dụng voucher !!!')

    def mes_success(self):
        view_rec = self.env.ref('crm_base.view_apply_voucher_finish',
                                raise_if_not_found=False)
        action = self.env.ref(
            'crm_base.action_view_apply_success_wizard', raise_if_not_found=False
        ).read([])[0]
        action['views'] = [(view_rec and view_rec.id or False, 'form')]
        return action

    def create_crm_line_by_voucher(self, prg, voucher):
        self.env['crm.line'].create({
            'name': prg.product_id.name,
            'product_id': prg.product_id.id,
            'unit_price': prg.price,
            'price_list_id': self.crm_id.price_list_id.id,
            'voucher_id': voucher.id,
            'company_id': self.crm_id.company_id.id,
            'prg_voucher_ids': [(4, prg.id)],
            'source_extend_id': self.crm_id.source_id.id,
        })
        voucher.crm_id = self.crm_id.id
        voucher.partner2_id = self.crm_id.partner_id
        self.mes_success()

    def set_discount(self, lines, program, voucher):
        for rec in lines:
            rec.discount_percent += program.discount
            rec.prg_voucher_ids = [(4, program.id)]
        voucher.crm_id = self.crm_id.id
        voucher.partner2_id = self.crm_id.partner_id
        self.mes_success()


class ApplyDiscountProgram(models.TransientModel):
    _name = 'crm.apply.discount.program'

    name = fields.Char('Name')
    program_discount_id = fields.Many2one('crm.discount.program', string='Discount program',
                                          domain="[('stage_prg','=','active'),('campaign_id','=',campaign_id)]")
    crm_id = fields.Many2one('crm.lead', string='Booking/lead')
    partner_id = fields.Many2one('res.partner', string='Partner')
    campaign_id = fields.Many2one('utm.campaign', string='Campaign')

    def check_prg(self):
        if self.crm_id and self.program_discount_id.company_ids and \
                self.crm_id.company_id not in self.program_discount_id.company_ids:
            raise ValidationError(
                'Chi nhánh %s không có trong danh sách áp dụng chương trình giảm giá !!!' % self.crm_id.company_id.name)
        else:
            self.check_product_ctg_program()

    def check_product_ctg_program(self):
        lines = self.crm_id.crm_line_ids.filtered(
            lambda line: line.stage == 'new'
                         and line.number_used == 0
                         and not line.voucher_id
                         and self.program_discount_id not in line.prg_ids)
        if lines:
            if self.program_discount_id.discount_program_rule.product_id:
                prd_1 = lines.mapped('product_id')
                prd_2 = self.program_discount_id.discount_program_rule.product_id
                prd_3 = set(prd_1) & set(prd_2)
                if prd_3:
                    list_line = lines.filtered(lambda l: l.product_id in prd_3)
                    self.set_discount(list_line)
                else:
                    raise ValidationError(
                        'Các dịch vụ hiện có đang không nằm trong danh sách áp dụng của chương trình giảm giá !!!')

            elif self.program_discount_id.product_ctg_ids:
                ctg_1 = lines.mapped('product_ctg_id')
                ctg_2 = self.program_discount_id.product_ctg_ids
                ctg_3 = set(ctg_1) & set(ctg_2)
                if ctg_3:
                    list_line = lines.filtered(lambda l: l.product_ctg_id in ctg_3)
                    self.set_discount(list_line)
                else:
                    raise ValidationError(
                        'Nhóm dịch vụ hiện có đang không nằm trong danh sách áp dụng của chương trình giảm giá !!!')
            else:
                self.set_discount(lines)
        else:
            raise ValidationError('Không có bất kỳ line dịch vụ nào đủ điều kiện để áp dụng chương trình giảm giá !!!')

    def set_discount(self, lines):
        for rec in lines:
            discount_program = rec.mapped('prg_ids')
            if self.program_discount_id in discount_program.mapped('related_discounts_program_ids') or not discount_program:
                product_discount = self.program_discount_id.discount_program_rule.filtered(
                    lambda l: l.product_id == rec.product_id)
                if product_discount:
                    if product_discount.type_discount == 'percent':
                        rec.discount_percent += product_discount.discount
                    elif product_discount.type_discount == 'cash':
                        rec.discount_cash += product_discount.discount
                    else:
                        rec.total = rec.quantity * product_discount.discount
                rec.prg_ids = [(4, self.program_discount_id.id)]
            else:
                raise ValidationError('Chương trình khuyến mãi không áp dụng đồng thời với chương trình khuyến mãi hiện hành')
