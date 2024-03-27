# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields


class ElearningRules(models.Model):
    _name = "elearning.rules"
    _description = "Elearning Rules Details"
    _rec_name = "id"

    id = fields.Integer('Id', required=True)
    name = fields.Text('Rules', required=True)
    rules_action = fields.Text('Action To Be Taken', required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda self: self.env.user.company_id)
