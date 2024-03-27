# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

import urllib.parse as urlparse

from odoo import models, api, fields, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import ValidationError
from odoo.tools import image
from odoo.tools.translate import html_translate


class OpCourseMaterial(models.Model):
    _name = "op.material"
    _description = "LMS Material"
    _inherit = [
        "mail.thread",
        "website.seo.metadata",
        "website.published.mixin"
    ]

    image = fields.Binary('Image', attachment=True)
    image_medium = fields.Binary('Medium', compute="_get_image",
                                 store=True, attachment=True)
    image_thumb = fields.Binary('Thumbnail', compute="_get_image",
                                store=True, attachment=True)

    @api.depends('image')
    def _get_image(self):
        for record in self:
            if record.image:
                record.image_medium = image.crop_image(
                    record.image, type='top', ratio=(4, 3), thumbnail_ratio=4)
                record.image_thumb = image.crop_image(
                    record.image, type='top', ratio=(4, 3), thumbnail_ratio=6)
            else:
                record.image_medium = False
                record.iamge_thumb = False

    name = fields.Char('Title', required=True, translate=True)
    short_description = fields.Text('Short Description')
    full_description = fields.Html('Full Description',
                                   translate=html_translate,
                                   sanitize_attributes=False)

    auto_publish = fields.Boolean('Auto Publish')
    auto_publish_type = fields.Selection([
        ('wait_until', 'Wait Until'),
        ('wait_until_duration', 'Wait Until Duration')])
    wait_until_date = fields.Date('Wait Until')
    wait_until_duration = fields.Integer('Wait Until Duration')
    wait_until_duration_period = fields.Selection(
        [('minutes', 'Minutes'), ('hours', 'Hours'), ('days', 'Days'),
         ('weeks', 'Weeks'), ('months', 'Months'), ('years', 'Years')],
        string='Wait at least period')

    user_id = fields.Many2one(
        'res.users', 'User', default=lambda self: self.env.uid, required=True)
    category_id = fields.Many2one('op.course.category', string="Category")
    material_type = fields.Selection([
        ('video', 'Video'), ('audio', 'Audio'), ('document', 'Document/PDF'),
        ('infographic', 'Image'), ('quiz', 'Quiz')],
        string='Material Type', required=True, default='video')
    video_type = fields.Selection([
        ('youtube', 'Youtube'), ('vimeo', 'Vimeo'), ('dartfish', 'Dartfish')],
        string="Video Type", default="youtube")
    quiz_id = fields.Many2one('op.quiz', 'Quiz')
    datas = fields.Binary('Content', attachment=True)
    url = fields.Char('Document URL', help="Youtube or Google Document URL")
    document_id = fields.Char('Document ID')
    total_time = fields.Float('Total Time (HH:MM)', required=True,
                              help='Approx time to complete this material')

    @api.onchange('url')
    def on_change_url(self):
        self.ensure_one()
        if self.url:
            data = urlparse.urlparse(self.url)
            if data.scheme and data.netloc:
                doc_id = False
                if self.video_type == 'youtube':
                    url_data = urlparse.urlparse(self.url)
                    query = urlparse.parse_qs(url_data.query)
                    doc_id = query.get('v', False) and query['v'][0] or False
                    if not doc_id:
                        doc_id = url_data.path and url_data.path[1:] or False
                elif self.video_type == 'vimeo':
                    url_data = urlparse.urlparse(self.url)
                    doc_id = url_data.path and url_data.path[1:] or False
                elif self.video_type == 'dartfish':
                    url_data = urlparse.urlparse(self.url)
                    query = urlparse.parse_qs(url_data.query)
                    doc_id = query.get('CR', False) and query['CR'][0] or False
            else:
                raise ValidationError(
                    _('Please enter valid URL: %s' % self.url))
            if doc_id:
                self.document_id = doc_id
            else:
                raise ValidationError(_('Could not fetch url. Document Id or \
                access right not available:\n%s') % doc_id)

    # website
    date_published = fields.Datetime('Publish Date')
    website_message_ids = fields.One2many(
        'mail.message', 'res_id',
        domain=lambda self: [
            ('model', '=', self._name), ('message_type', '=', 'comment')],
        string='Website Messages', help="Website communication history")
    likes = fields.Integer('Likes')
    dislikes = fields.Integer('Dislikes')
    material_views = fields.Integer('# of Website Views')
    embed_views = fields.Integer('# of Embedded Views')
    total_views = fields.Integer(
        "Total # Views", default="0", compute='_compute_total', store=True)

    @api.depends('material_views', 'embed_views')
    def _compute_total(self):
        for record in self:
            record.total_views = record.material_views + record.embed_views

    embed_code = fields.Text(
        'Embed Code', readonly=True, compute='_get_embed_code')

    def _get_embed_code(self):
        for record in self:
            if record.datas and (record.material_type == 'infographic' and
                                 not record.document_id):
                record.embed_code = '<iframe src="/materials/embed/%s?page=1" \
                allowFullScreen="true" height="%s" width="%s" \
                frameborder="0"></iframe>' % (record.id, 315, 420)
            elif record.datas and (record.material_type == 'document' and
                                   not record.document_id):
                record.embed_code = '<iframe src="/materials/embed/%s?page=1" \
                allowFullScreen="true" height="%s" width="%s" \
                frameborder="0"></iframe>' % (record.id, 315, 420)
            elif record.material_type == 'video' and \
                    record.video_type == 'youtube' and record.document_id:
                record.embed_code = '<iframe \
                src="https://www.youtube.com/embed/%s?theme=light" \
                allowFullScreen="true" frameborder="0"></iframe>' % (
                    record.document_id)
            elif record.material_type == 'video' and \
                    record.video_type == 'vimeo' and record.document_id:
                record.embed_code = '<iframe \
                src="https://player.vimeo.com/video/%s" \
                frameborder="0" webkitallowfullscreen mozallowfullscreen \
                allowfullscreen></iframe>' % (record.document_id)
            elif record.material_type == 'video' and \
                    record.video_type == 'dartfish' and record.document_id:
                record.embed_code = '<iframe \
                src="https://www.dartfish.tv/Embed?CR=' + \
                                    record.document_id + \
                                    '&VW=100%&VH=100%" frameborder="0" \
                                    allowfullscreen ></iframe>'
            elif record.material_type == 'video' and record.datas:
                record.embed_code = '<video controls \
                controlsList="nodownload"><source class="audio" \
                src="data:video/mp4;base64,%s"></video>' % record.datas
            elif record.material_type == 'audio':
                record.embed_code = '<audio controls \
                controlsList="nodownload"><source class="audio" \
                src="data:audio/mp3;base64,%s"></audio>' % record.datas
            else:
                record.embed_code = False

    @api.depends('name')
    def _compute_website_url(self):
        super(OpCourseMaterial, self)._compute_website_url()
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        for material in self:
            if material.id:
                if self.env.registry.get('link.tracker'):
                    url = self.env['link.tracker'].sudo().create({
                        'url': '%s/course/material/%s' % (
                            base_url, slug(material))
                    }).short_url
                else:
                    url = '%s/course/material/%s' % (base_url, slug(material))
                material.website_url = url

    def website_lms_publish_button(self):
        self.ensure_one()
        return self.write({'website_published': not self.website_published})
