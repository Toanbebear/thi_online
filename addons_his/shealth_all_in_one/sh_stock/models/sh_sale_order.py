from odoo import fields, api, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, AccessError, ValidationError, Warning
import datetime
from datetime import timedelta
import logging
from lxml import etree
import json


class SHealthSaleOrder(models.Model):
    _inherit = "sale.order"

    sh_room_id = fields.Many2one('sh.medical.health.center.ot', 'Phòng xuất hàng', domain="[('institution.his_company', '=', company_id)]")

    def action_confirm(self):
        date_order = self.date_order

        #check xuất hàng bán
        if self.sh_room_id:
            validate_str = ''

            for order_line in self.order_line:
                if order_line.product_uom_qty > 0:  # CHECK SO LUONG SU DUNG > 0
                    location_by_categ = order_line._get_location_by_categ()
                    quantity_on_hand = self.env['stock.quant']._get_available_quantity(order_line.product_id, location_by_categ)  # check quantity trong location

                    qty_sale = order_line.product_uom._compute_quantity(order_line.product_uom_qty, order_line.product_id.uom_id)
                    if quantity_on_hand < qty_sale:
                        validate_str += "+ ""[%s]%s"": Còn %s %s tại ""%s"" \n" % (
                            order_line.product_id.default_code, order_line.product_id.name, str(quantity_on_hand), str(order_line.product_id.uom_id.name),
                            location_by_categ.name)

            if validate_str != '':
                raise ValidationError(_(
                    "Các SP sau đang không đủ số lượng tại tủ xuất:\n" + validate_str + "Hãy liên hệ với quản lý kho!"))

        res = super(SHealthSaleOrder, self).action_confirm()

        self.write({
            'date_order': date_order
        })

        #XÁC NHẬN PHIẾU GIAO HÀNG
        if self.picking_ids:
            for stock_picking in self.picking_ids.filtered(lambda pick : pick.state not in ['done','cancel']):

                stock_picking.with_context(exact_location=True).action_assign()  # ham check available trong inventory
                for move_line in stock_picking.move_ids_without_package:
                    for move_live_detail in move_line.move_line_ids:
                        move_live_detail.qty_done = move_live_detail.product_uom_qty
                stock_picking.with_context(
                    force_period_date=date_order).sudo().button_validate()  # ham tru product trong inventory, sudo để đọc stock.valuation.layer

                # sua ngay hoan thanh
                for move_line in stock_picking.move_ids_without_package:
                    move_line.move_line_ids.write({'date': date_order})  # sửa ngày hoàn thành ở stock move line
                stock_picking.move_ids_without_package.write(
                    {'date': date_order})  # sửa ngày hoàn thành ở stock move
                stock_picking.date_done = date_order
                stock_picking.sci_date_done = date_order
        return res

    def _prepare_invoice(self):
        res = super(SHealthSaleOrder, self)._prepare_invoice()
        res['invoice_date'] = self.date_order
        return res


class SHealthSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _get_location_by_categ(self):
        """Lấy địa điểm theo phòng bệnh viện và nhóm sản phẩm"""
        room = self.order_id.sh_room_id
        location = self.env['stock.location']
        if self.product_id.categ_id == self.env.ref('shealth_all_in_one.sh_medicines') and room.location_medicine_stock:
            location = room.location_medicine_stock
        elif self.product_id.categ_id == self.env.ref('shealth_all_in_one.sh_supplies') and room.location_supply_stock:
            location = room.location_supply_stock
        return location

    def _prepare_procurement_values(self, group_id=False):
        """Điều chỉnh location của move theo nhóm sản phẩm: vật tư hay thuốc,
        chen vào giữa hàm _action_launch_stock_rule() của order line"""
        values = super(SHealthSaleOrderLine, self)._prepare_procurement_values(group_id=group_id)
        adj_location = self._get_location_by_categ()
        if self.order_id.sh_room_id and adj_location:
            values['location_id'] = adj_location.id
        return values

# Code cũ của sale.order
    # location_id = fields.Many2one('stock.location', 'Tủ xuất hàng', domain="[('company_id', '=', company_id), ('usage', '=', 'internal'), ('child_ids', '=', False)]")
    #
    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(SHealthSaleOrder, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
    #                                                            submenu=submenu)
    #
    #     warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.companies.ids[0])], limit=1)
    #
    #     # CƠ SỞ GẮN VỚI CTY HIỆN TẠI
    #     institution = self.env['sh.medical.health.center'].search([('his_company', '=', self.env.companies.ids[0])],
    #                                                               limit=1)
    #
    #     access_location = []
    #     # NẾU QUẢN LÝ KHO HOẶC ADMIN HOẶC NHẬP LIỆU => XEM TẤT CẢ LOCATION
    #     if self.env.user.has_group('shealth_all_in_one.group_sh_medical_stock_manager'):
    #         location_stock0 = institution.warehouse_ids[
    #             0].lot_stock_id.id if institution else warehouse.lot_stock_id.id  # dia diem kho tổng
    #         access_location.append(location_stock0)
    #     else:
    #         receptionist_ward = lab_ward = spa_ward = laser_ward = surgery_ward = odontology_ward = False
    #
    #         if institution:
    #             receptionist_ward = self.env['stock.location'].sudo().search([('company_id', '=', institution.his_company.id), ('name', 'ilike', 'lễ tân')], limit=1)
    #             lab_ward = self.env['sh.medical.health.center.ward'].sudo().search(
    #                 [('institution', '=', institution.id), ('type', '=', 'Laboratory')], limit=1)
    #             spa_ward = self.env['sh.medical.health.center.ward'].sudo().search(
    #                 [('institution', '=', institution.id), ('type', '=', 'Spa')], limit=1)
    #             laser_ward = self.env['sh.medical.health.center.ward'].sudo().search(
    #                 [('institution', '=', institution.id), ('type', '=', 'Laser')], limit=1)
    #             surgery_ward = self.env['sh.medical.health.center.ward'].sudo().search(
    #                 [('institution', '=', institution.id), ('type', '=', 'Surgery')], limit=1)
    #             odontology_ward = self.env['sh.medical.health.center.ward'].sudo().search(
    #                 [('institution', '=', institution.id), ('type', '=', 'Odontology')], limit=1)
    #
    #         grp_loc_dict = {
    #             'shealth_all_in_one.group_sh_medical_receptionist': receptionist_ward,
    #             'shealth_all_in_one.group_sh_medical_physician_subclinical_labtest': lab_ward,
    #             'shealth_all_in_one.group_sh_medical_physician_surgery': surgery_ward,
    #             'shealth_all_in_one.group_sh_medical_physician_odontology': odontology_ward,
    #             'shealth_all_in_one.group_sh_medical_physician_spa': spa_ward,
    #             'shealth_all_in_one.group_sh_medical_physician_laser': laser_ward}
    #
    #         for grp, loc in grp_loc_dict.items():
    #             if self.env.user.has_group(grp) and loc:
    #                 if grp == 'shealth_all_in_one.group_sh_medical_receptionist':
    #                     access_location.append(loc.id)
    #                 else:
    #                     access_location.append(loc.location_id.id)
    #
    #         # quyen dieu duong
    #         if self.env.user.has_group('shealth_all_in_one.group_sh_medical_nurse') and self.env.user.physician_ids:
    #             physician_loc = self.env.user.physician_ids[0].department.mapped('location_id').ids
    #             access_location += physician_loc
    #
    #     doc = etree.XML(res['arch'])
    #
    #     for node in doc.xpath("//field[@name='location_id']"):
    #         node_domain = "[('location_id', 'child_of', %s),('location_institution_type','in',['supply','medicine'])]" % str(
    #                 access_location)
    #
    #         node.set('domain', node_domain)
    #         modifiers = json.loads(node.get("modifiers"))
    #         modifiers['domain'] = node_domain
    #         node.set("modifiers", json.dumps(modifiers))
    #
    #     res['arch'] = etree.tostring(doc, encoding='unicode')
    #     return res
