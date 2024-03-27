# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FacultyBomUpdate(models.TransientModel):
    _name = 'op.faculty.bom'
    _description = 'Update batch faculty bom'

    def _default_product_lines(self):
        batch = self.env['op.batch'].browse(self._context.get('active_id'))
        vals = []
        for record in self.env['products.line'].search([('course_id', '=', batch.course_id.id)]):
            vals.append((0, 0, {'product': record.product.id,
                                'quantity': 1,
                                'uom_id': record.uom_id.id,
                                'currency_id': record.currency_id.id,
                                'cost': record.cost,
                                'price': record.price}))
        return vals

    def _get_location_domain(self):
        faculties = self.env['op.faculty'].search([('full_time', '=', True), ('location_id', '!=', False)])
        return [('faculty_id', 'in', faculties.ids)]

    def _reverse_pick_domain(self):
        batch = self.env['op.batch'].browse(self._context.get('active_id'))
        batch_picks = self.env['stock.picking'].search(
            [('origin', 'ilike', 'Batch BOM - %s - %s' % (batch.code, batch.name)),
             ('partner_id', '=', self.env.user.partner_id.id)])
        return [('id', 'in', batch_picks.ids)]

    reverse = fields.Boolean('Reverse')
    reverse_pick = fields.Many2one('stock.picking', string='Stock pick to reverse',
                                   domain=lambda self: self._reverse_pick_domain())
    faculty_stock_location = fields.Many2one('stock.location', 'Faculty stock',
                                             domain=lambda self: self._get_location_domain(),
                                             default=lambda self: self.env['op.faculty'].search(
                                                 [('user_id', '=', self.env.user.id)], limit=1).location_id)
    products = fields.Many2many('products.line', string='Products', default=_default_product_lines)
    products_domain = fields.Many2many('product.product', string='Duma', compute='_get_products_domain')

    @api.depends('products')
    def _get_products_domain(self):
        for record in self:
            if len(record.products) > 0:
                record.products_domain = [
                    (6, 0, [product.product.id for product in record.products if product.product])]
            else:
                record.products_domain = False

    def reverse_materials(self):
        batch = self.env['op.batch'].browse(self._context.get('active_id'))
        new_wizard = self.env['stock.return.picking'].new({'picking_id': self.reverse_pick.id})
        new_wizard._onchange_picking_id()
        wizard_vals = new_wizard._convert_to_write(new_wizard._cache)
        wizard = self.env['stock.return.picking'].with_context(reopen_flag=True, no_check_quant=True).create(
            wizard_vals)
        new_picking_id, pick_type_id = wizard._create_returns()
        new_picking = self.env['stock.picking'].browse(new_picking_id)
        new_picking.button_validate()
        for move_line in new_picking.move_ids_without_package:
            move_line.quantity_done = move_line.product_uom_qty
        new_picking.button_validate()
        for move_line in new_picking.move_ids_without_package:
            batch_bom_line = batch.faculty_bom.filtered(
                lambda b: b.product == move_line.product_id)  # Todo: check performance
            if move_line.product_uom == batch_bom_line.uom_id:
                batch_bom_line.quantity -= move_line.quantity_done
            else:  # just in case, normally won't happen
                qty_to_process = batch_bom_line.uom_id._compute_quantity(move_line.quantity_done, move_line.product_uom)
                batch_bom_line.quantity -= qty_to_process

    def update_materials(self):
        self.ensure_one()
        location = self.faculty_stock_location
        warehouse = location.get_warehouse()
        picking_type = warehouse.out_type_id
        if not location:
            raise ValidationError(_('Only stock location owner can update materials.'))
        batch = self.env['op.batch'].browse(self._context.get('active_id'))
        vals = []
        batch_products = [batch_product.product for batch_product in batch.faculty_bom]
        for record in self.products:
            qty_on_hand = self.env['stock.quant']._get_available_quantity(product_id=record.product,
                                                                          location_id=location)
            if record.uom_id != record.product.uom_id:
                record.write({'quantity': record.uom_id._compute_quantity(record.quantity, record.product.uom_id),
                              'uom_id': record.product.uom_id.id})
            if qty_on_hand < record.quantity:
                raise ValidationError(_("Products out of stock.\
                                         Please contact inventory manager."))
            else:
                vals.append((0, 0, {'name': 'BOM' + record.product.name,
                                    'date': fields.Date.today(),
                                    'company_id': self.env.company.id,
                                    'date_expected': fields.Date.today(),
                                    'product_id': record.product.id,
                                    'product_uom_qty': record.quantity,
                                    'product_uom': record.uom_id.id,
                                    'location_id': location.id,
                                    'location_dest_id': self.env['stock.location'].search([('usage', '=', 'customer')],
                                                                                          limit=1).id}))
                if record.product not in batch_products:
                    record.write({'batch_id': batch.id})
                else:
                    self.env['products.line'].search(
                        [('product', '=', record.product.id), ('batch_id', '=', batch.id)]).quantity += record.quantity
        pick_name = 'Batch BOM - %s - %s - %s' % (batch.code, batch.name, fields.Datetime.now())
        stock_picking = self.env['stock.picking'].create({'origin': pick_name,
                                                          'partner_id': self.env.user.partner_id.id,
                                                          'picking_type_id': picking_type.id,
                                                          'location_id': location.id,
                                                          'location_dest_id': self.env['stock.location'].search(
                                                              [('usage', '=', 'customer')], limit=1).id,
                                                          'immediate_transfer': True,
                                                          'move_ids_without_package': vals})
        stock_picking.action_assign()
        for move_id in stock_picking.move_ids_without_package:
            move_id.quantity_done = move_id.product_uom_qty
        stock_picking.button_validate()
        self.env['products.line'].search(
            [('bundle', '=', False), ('course_id', '=', False), ('batch_id', '=', False)]).unlink()
