# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    survey_id = fields.Many2one('survey.survey', 'Survey Kangnam HN')
    survey_hcm_id = fields.Many2one('survey.survey', 'Survey Kangnam HCM')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    survey_id = fields.Many2one('survey.survey', 'Survey Kangnam HN',
                                related='company_id.survey_id',
                                readonly=False)
    survey_hcm_id = fields.Many2one('survey.survey', 'Survey Kangnam HCM',
                                    related='company_id.survey_hcm_id',
                                    readonly=False)

    @api.model
    def create(self, vals):
        if vals['survey_id']:
            self.env.user.company_id.survey_id = vals['survey_id']
        else:
            self.env.user.company_id.survey_id = False
        if vals['survey_hcm_id']:
            self.env.user.company_id.survey_hcm_id = vals['survey_hcm_id']
        else:
            self.env.user.company_id.survey_hcm_id = False
        return super(ResConfigSettings, self).create(vals)
