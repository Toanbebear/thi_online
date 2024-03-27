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


class OpCourseEnrollment(models.Model):
    _name = "op.course.enrollment"
    _rec_name = "user_id"
    _description = "LMS Course Enrollment"

    course_id = fields.Many2one('op.course', 'Course', required=True)
    navigation_policy = fields.Selection(
        related='course_id.navigation_policy', string='Navigation Policy')
    user_id = fields.Many2one(
        'res.users', 'User', required=True, ondelete="cascade")
    enrollment_date = fields.Datetime('Enrollment Date', required=True,
                                      default=fields.Datetime.now())
    completion_date = fields.Datetime('Completion Date')
    state = fields.Selection([('draft', 'Draft'),
                              ('in_progress', 'In Progress'),
                              ('done', 'Done')],
                             'State', default='draft')
    enrollment_material_line = fields.One2many(
        'op.course.enrollment.material', 'enrollment_id',
        string='Materials', order='sequence asc')
    completed_percentage = fields.Integer(
        compute="_compute_completed_percentage",
        string="Completed Percentage", store=True)

    @api.depends('course_id.training_material', 'enrollment_material_line')
    def _compute_completed_percentage(self):
        for enrollment in self:
            if not enrollment.course_id.training_material == 0:
                enrollment.completed_percentage = (len(
                    enrollment.enrollment_material_line
                ) * 100) / enrollment.course_id.training_material
            else:
                enrollment.completed_percentage = 0


class OpCourseEnrollmentMaterial(models.Model):
    _name = "op.course.enrollment.material"
    _rec_name = "enrollment_id"
    _description = "LMS Course Enrollment Material"

    enrollment_id = fields.Many2one('op.course.enrollment', 'Enrollment',
                                    ondelete='cascade')
    course_id = fields.Many2one(related='enrollment_id.course_id',
                                string='Course')
    section_id = fields.Many2one('op.course.section', 'Section')
    material_id = fields.Many2one('op.material', 'Material')
    completed = fields.Boolean('Completed')
    completed_date = fields.Datetime('Completed Time')
    last_access_date = fields.Datetime('Last Access Time')
