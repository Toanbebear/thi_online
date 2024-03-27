from odoo import api,fields
from odoo import models
from odoo.tools.translate import html_translate
from odoo.tools import image
class ofcourse(models.Model):
    _inherit = ['op.course']

    time_ofcourse = fields.Char('Thời lượng khóa học')

    @api.onchange('num_lessons')
    def _onchange_num_lessons(self):
        if self.num_lessons:
            self.time_ofcourse = str(self.num_lessons) + ' tiết'

class admissionregister_of(models.Model):

    _inherit = ['op.admission.register']

    # category_ids = fields.Many2one('op.category',
    #                                  'course_category_rel_2',
    #                                  'course_id',
    #                                  'category_id', 'Categories')
    category_ids = fields.Many2one('op.category')

    publish = fields.Boolean('Publish offline course')
    image = fields.Binary(attachment=True)
    image_medium = fields.Binary('Medium', compute="_get_image",
                                  store=True, attachment=True)
    image_thumb = fields.Binary('Thumbnail', compute="_get_image",
                                 store=True, attachment=True)
    short_description = fields.Char('Short Description', size=80)
    full_description = fields.Html('Full Description',
                                    translate=html_translate,
                                    sanitize_attributes=False)

    @api.depends('image')
    def _get_image(self):
         for record in self:
             if record.image:
                 record.image_medium = image.crop_image(
                     record.image, type='top', ratio=(4, 3))
                 record.image_thumb = image.crop_image(
                     record.image, type='top', ratio=(4, 3))
             else:
                 record.image_medium = False
                 record.iamge_thumb = False

    @api.onchange('course_id')
    def get_category(self):
        self.category_ids = self.course_id.category_id