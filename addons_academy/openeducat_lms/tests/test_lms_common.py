# -*- coding: utf-8 -*-

from odoo.tests import common


class TestLmsCommon(common.SavepointCase):
    def setUp(self):
        super(TestLmsCommon, self).setUp()
        self.op_material = self.env['op.material']
