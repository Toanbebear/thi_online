# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from datetime import timedelta, datetime

from odoo import models, fields, api


class OpFeesTemplateLine(models.Model):
    _name = "op.fees.template.line"
    _description = "Fees Template Line"

    line_id = fields.Many2one('op.fees.terms.line', 'Fees Line')
    duration_type = fields.Selection([
        ('before', 'Before'), ('after', 'After')], 'Duration Type')
    days = fields.Integer('Days')
    template_id = fields.Many2one('mail.template', 'Template')


class OpFeesTermsLine(models.Model):
    _inherit = "op.fees.terms.line"

    line_ids = fields.One2many('op.fees.template.line', 'line_id', 'Lines')


class OpFeesTerms(models.Model):
    _inherit = "op.fees.terms"

    @api.model
    def run_send_fees_reminder(self):
        fees_line_ids = self.env['op.student.fees.details'].search(
            [('state', '=', 'draft')])
        for line in fees_line_ids:
            if not line.fees_line_id or not line.date or not line.student_id:
                continue
            student_id = line.student_id.id
            submit_date = line.date
            term = line.fees_line_id
            for val in term.line_ids:
                if not val.template_id:
                    continue
                days = val.days or 0
                if val.duration_type == 'before':
                    days = days * (-1)
                ddate = fields.Date.from_string(submit_date)
                mail_date = ddate + timedelta(days)
                current_date = datetime.today().date()
                if mail_date == current_date:
                    val.template_id.send_mail(student_id, force_send=True)

        return True
