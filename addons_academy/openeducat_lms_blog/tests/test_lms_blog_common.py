# -*- coding: utf-8 -*-

from odoo.tests import common


class TestLmsBlogCommon(common.SavepointCase):
    def setUp(self):
        super(TestLmsBlogCommon, self).setUp()
        self.op_course = self.env['op.course']
        self.blogs = self.env['blog.blog']
        self.blog_posts = self.env['blog.post']
        self.blog_tags = self.env['blog.blog']
