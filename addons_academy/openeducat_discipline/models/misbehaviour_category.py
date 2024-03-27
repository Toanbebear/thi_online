# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields


class OpMisbehaviourSubCategory(models.Model):
    _name = "op.misbehaviour.sub.category"
    _description = "Misbehaviour Sub Category"

    name = fields.Char('Name', required=True)
    misbehaviour_category_id = fields.Many2one(
        'op.misbehaviour.category', 'Misbehaviour Category')
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda self: self.env.user.company_id)


class OpMisbehaviourCategory(models.Model):
    _name = "op.misbehaviour.category"
    _description = "Misbehaviour Category Details"

    name = fields.Char('Name', required=True)
    misbehaviour_type = fields.Selection(
        [('major', 'Major'), ('minor', 'Minor')],
        'Category Type', required=True)
    misbehaviour_sub_category_ids = fields.One2many(
        'op.misbehaviour.sub.category', 'misbehaviour_category_id',
        'Misbehaviour Sub Categories')
    misbehaviour_template_id = fields.Many2one(
        'mail.template', 'Misbehaviour Template', required=True)
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda self: self.env.user.company_id)
