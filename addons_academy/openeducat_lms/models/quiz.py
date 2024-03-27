# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields, api


class OpQuiz(models.Model):
    _inherit = "op.quiz"

    lms = fields.Boolean('LMS')

    @api.onchange('lms')
    def _onchange_lms(self):
        (self.single_que, self.show_result) = (True, True) \
            if self.lms else (False, False)
