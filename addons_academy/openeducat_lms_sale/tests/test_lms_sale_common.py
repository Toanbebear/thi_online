# -*- coding: utf-8 -*-

from odoo.tests import common


class TestLmsCommonSale(common.SavepointCase):
    def setUp(self):
        super(TestLmsCommonSale, self).setUp()
        self.op_course = self.env['op.course']
        self.op_material = self.env['op.material']
        self.op_enrollment = self.env['op.course.enrollment']
