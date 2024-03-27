# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SCIBatch(models.Model):
    _inherit = 'op.batch'

    admission_ids = fields.One2many('op.admission', 'batch_id', 'Admissions')
    bom_cost = fields.Float('Students BOM cost', compute='_get_bom_cost')
    total_cost = fields.Float('Total cost', compute='_get_total_cost')

    # @api.depends('admission_ids')
    # def _get_bom_cost(self):
    #     for batch in self:
    #         batch.bom_cost = 0
    #         for record in batch.admission_ids:
    #             batch.bom_cost += record.bom.total_cost

    @api.depends('course_id', 'num_students')
    def _get_bom_cost(self):
        for record in self:
            if record.course_id:
                record.bom_cost = record.course_id.bom.total_cost * record.num_students
            else:
                record.bom_cost = 0

    @api.depends('teacher_cost', 'bom_cost', 'faculty_bom_cost')
    def _get_total_cost(self):
        for batch in self:
            if not batch.internal:
                batch.total_cost = batch.bom_cost + batch.faculty_bom_cost
            else:
                batch.total_cost = batch.teacher_cost + batch.bom_cost + batch.faculty_bom_cost