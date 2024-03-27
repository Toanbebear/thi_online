##############################################################################
#    Copyright (C) 2018 shealth (<http://scigroup.com.vn/>). All Rights Reserved
#    shealth, Hospital Management Solutions

# Odoo Proprietary License v1.0
#
# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, shealth.in, openerpestore.com, or if you have received a written
# agreement from the authors of the Software.
#
# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).
#
# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.
#
# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

##############################################################################

from odoo import api, fields, models, _
import datetime
import locale
from odoo.exceptions import UserError
from lxml import etree
from odoo.tools.float_utils import float_round, float_compare
from ...sh_walkins.models.sh_medical_register_for_walkin import num2words_vnm
from odoo.exceptions import UserError, AccessError, ValidationError, Warning


class wizardChooseWalkin(models.TransientModel):
    _name = 'wizard.choose.walkin'
    _description = 'Sử dụng tiền khách hàng đã đặt cọc'

    def _get_domain_walkin(self):
        return [('patient', '=', self.env.context.get('patient_id')), ('state', 'not in', ['Completed', 'Cancelled'])]

    walkin_id = fields.Many2one('sh.medical.appointment.register.walkin', string='Phiếu khám',
                                domain=lambda self: self._get_domain_walkin(), track_visibility='onchange',
                                required=True)

    def add_walkin_for_payment(self):
        payment_detail = self.env['account.payment'].browse(self.env.context.get('active_id'))
        if payment_detail:
            payment_detail.write({
                'walkin': self.walkin_id.id,
            })

            # check tiền đủ chưa
            if payment_detail.walkin and payment_detail.walkin.state not in ['Completed', 'Cancelled']:
                total_so = payment_detail.walkin.sale_order_id.amount_total
                total_so_remain = payment_detail.walkin.sale_order_id.amount_remain

                if payment_detail.walkin.sale_order_id.debt_review is True:
                    payment_detail.walkin.set_to_progress()

                elif payment_detail.walkin.sale_order_id.odontology is True:
                    payment_detail.walkin.set_to_progress()

                elif total_so > total_so_remain:  # thiếu tiền
                    view = self.env.ref('sh_message.sh_message_wizard')
                    context = dict(self._context or {})
                    context[
                        'message'] = 'Tổng số tiền thanh toán vẫn chưa đủ để thực hiện dịch vụ! Hãy thay toán thêm: %s VNĐ' % "{:,.0f}".format(
                        total_so - total_so_remain)

                    return {
                        'name': _('Thông báo'),  # label
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'view_id': self.env.ref('sh_message.sh_message_wizard').id,
                        'res_model': 'sh.message.wizard',  # model want to display
                        'target': 'new',  # if you want popup
                        'context': context,
                    }

                else:
                    payment_detail.walkin.set_to_progress()


# Inherit Payment

class SHealthAccountPayment(models.Model):
    _inherit = 'account.payment'

    _order = "payment_date desc, name"

    def get_domain_user(self):
        thungan_job = self.env['hr.job'].sudo().search([('name','ilike','thu ngân'),('company_id', '=', self.env.company.id)])

        emp_user = self.env['hr.employee'].sudo().search([('job_id', 'in', thungan_job.ids),('company_id', '=', self.env.company.id),('user_id','!=', False)])

        if thungan_job and emp_user:
            return [("groups_id", "in", [self.env.ref("account.group_account_invoice").id]),('company_id', '=', self.env.company.id),('id','in',emp_user.sudo().mapped('user_id').ids)]
        else:
            return [("groups_id", "in", [self.env.ref("account.group_account_invoice").id]),
                    ('company_id', '=', self.env.company.id)]

    walkin = fields.Many2one('sh.medical.appointment.register.walkin', string='Phiếu khám')
    patient = fields.Many2one('sh.medical.patient', string='Bệnh nhân')
    # note = fields.Text('Lý do thu')
    text_total = fields.Text('Số tiền bằng chữ')
    date_requested = fields.Datetime(string='Ngày giờ yêu cầu', help="Ngày giờ yêu cầu", readonly=False,
                                     states={'posted': [('readonly', True)], 'cancelled': [('readonly', True)]},
                                     default=lambda *a: datetime.datetime.now())

    # người thanh toán
    user = fields.Many2one('res.users', string='Người thu', domain=lambda self: self.get_domain_user(),
                           default=lambda self: self.env.user if self.env.user.has_group("shealth_all_in_one.group_sh_medical_accountant") else False)

    # ,
    #    default=lambda self: self.env.ref( "__import__.data_user_medical_7").id if self.env.ref( "__import__.data_user_medical_7",False) else False,
    #    domain=lambda self: [("id", "in", [self.env.ref( "__import__.data_user_medical_7").id if self.env.ref( "__import__.data_user_medical_7",False) else False])])

    # nội dung giao dịch
    # @api.onchange('communication')
    # def get_communication(self):
    #     if self.walkin:
    #         self.communication = self.note

    # XÁC NHẬN THANH TOÁN
    def post(self):
        for payment in self:
            rec = super(SHealthAccountPayment, self).post()
            if payment.payment_type != 'outbound':  # nếu hóa đơn hoàn tiền cho khách
                if payment.walkin and payment.walkin.state not in ['Completed', 'Cancelled']:
                    total_so = payment.walkin.sale_order_id.amount_total
                    total_so_remain = payment.walkin.sale_order_id.amount_remain
                    amount_set = payment.walkin.sale_order_id.set_total

                    # order duyệt nợ -> đi thẳng
                    if payment.walkin.sale_order_id.debt_review is True:
                        payment.walkin.set_to_progress()

                    # order nha khoa,amount_set > 0 and remain > amount_set
                    elif payment.walkin.sale_order_id.odontology is True and amount_set > 0 \
                            and total_so_remain >= amount_set:
                        payment.walkin.set_to_progress()

                    # order nha khoa, amount_set > 0 , set > remain
                    elif payment.walkin.sale_order_id.odontology is True and amount_set > total_so_remain:
                        view = self.env.ref('sh_message.sh_message_wizard')
                        context = dict(self._context or {})
                        context[
                            'message'] = 'Tổng số tiền thanh toán vẫn chưa đủ để thực hiện dịch vụ! Hãy thay toán thêm: %s VNĐ' % "{:,.0f}".format(
                            amount_set - total_so_remain)

                        return {
                            'name': _('Thông báo'),  # label
                            'type': 'ir.actions.act_window',
                            'view_mode': 'form',
                            'view_id': self.env.ref('sh_message.sh_message_wizard').id,
                            'res_model': 'sh.message.wizard',  # model want to display
                            'target': 'new',  # if you want popup
                            'context': context,
                        }

                    elif total_so_remain >= total_so:
                        payment.walkin.set_to_progress()

                    elif total_so > total_so_remain:  # thiếu tiền
                        view = self.env.ref('sh_message.sh_message_wizard')
                        context = dict(self._context or {})
                        context[
                            'message'] = 'Tổng số tiền thanh toán vẫn chưa đủ để thực hiện dịch vụ! Hãy thay toán thêm: %s VNĐ' % "{:,.0f}".format(
                            total_so - total_so_remain)

                        return {
                            'name': _('Thông báo'),  # label
                            'type': 'ir.actions.act_window',
                            'view_mode': 'form',
                            'view_id': self.env.ref('sh_message.sh_message_wizard').id,
                            'res_model': 'sh.message.wizard',  # model want to display
                            'target': 'new',  # if you want popup
                            'context': context,
                        }

                    else:
                        payment.walkin.set_to_progress()
            return rec

    def unlink(self):  # xóa phiếu thu sẽ hiện lại yêu cầu thu phí
        for payment in self:
            payment.walkin.write({'state': 'Scheduled'})
        return super(SHealthAccountPayment, self).unlink()

    @api.onchange('amount')
    def onchange_amount(self):
        if self.amount and self.amount > 0:
            self.text_total = num2words_vnm(int(self.amount)) + " đồng"
        elif self.amount and self.amount < 0:
            raise ValidationError(
                _('Số tiền thanh toán không hợp lệ!'))
        else:
            self.text_total = "Không đồng"

    @api.onchange('walkin')
    def onchange_walkin(self):
        if self.walkin:
            self.patient = self.walkin.patient.id

    # sử dụng tiền khách đã đặt cọc
    def view_choose_walkin(self):
        patient_id = self.patient.id or self.env['sh.medical.patient'].search([('partner_id', '=', self.partner_id.id)],
                                                                              limit=1).id
        return {
            'name': _('Sử dụng tiền khách đã đặt cọc'),  # label
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('shealth_all_in_one.form_view_choose_walkin_wizard').id,
            'res_model': 'wizard.choose.walkin',  # model want to display
            'target': 'new',  # if you want popup
            'context': {'patient_id': patient_id}
        }

    #SonZ
    def get_account(self):
        debit = []
        credit = []
        for rec in self.move_line_ids:
            if rec.debit == 0 and rec.credit > 0:
                credit.append(rec.account_id.code)
            if rec.debit > 0 and rec.credit == 0:
                debit.append(rec.account_id.code)
        values = {
            'debit': debit,
            'credit': credit,
        }
        return values
    #SonZ
