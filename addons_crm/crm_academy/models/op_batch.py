from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date


class InheritOpBatch(models.Model):
    _inherit = "op.batch"

    survey_survey = fields.Many2many('survey.survey', 'survey_batch_rel', 'survey_id', 'batch_id', string='Survey',
                                     domain="[('state', '=', 'open')]")
    learn_number = fields.Integer(compute='_compute_learn_number', default=0, store=True)

    @api.depends('student_course')
    def _compute_learn_number(self):
        for record in self:
            if record.student_course:
                record.learn_number = len(
                    record.student_course.filtered(lambda s: s.status == 'finish' or s.status == 'study'))
            else:
                record.learn_number = 0

    # Nếu lớp có 1 Bài học => Hiển thị Thời gian mà không hiển thị ngày kết thúc thì gán ngày kết thúc sẽ giống ngày bắt đầu
    @api.onchange('timing_id', 'start_date')
    def onchange_timing_id(self):
        if self.timing_id and self.start_date:
            self.end_date = self.start_date

    def send_survey(self):
        if self.survey_survey and self.student_course:
            mail_template = self.env.ref('openeducat_core.batch_email_managers')
            finish_learner = self.env['op.student.course'].sudo().search(
                [('course_id', '=', self.course_id.id), ('batch_id', '=', self.id), ('status', '=', 'finish')])
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if finish_learner:
                for learner in finish_learner:
                    student = learner.student_id
                    values = {'model': 'op.batch',
                              'res_id': self.id,
                              'subject': 'Khóa học nội bộ - %s' % (self.name),
                              'parent_id': None,
                              'email_from': self.env.user.email or None,
                              'email_to': student.email or None,
                              'auto_delete': False,
                              }
                    gender = ('Anh', 'Chị')[student.gender == 'f']
                    body_html = '<p>Kính gửi %s %s,</p>' % (gender, student.name) + \
                                '<p>Cảm ơn %s đã tham gia khóa đào tạo lớp <b>%s</b> của Học viện SCI :</p>' % (
                                    gender, self.name) + \
                                '<p> %s vui lòng vào Link sau để tham gia khảo sát: ' % gender
                    for survey in self.survey_survey:
                        body_html += '</table>' + \
                                     '<p><a href="%s/survey/start/%s/batch_id=%s?answer_token">%s</a></p>' % (
                                         base_url, survey.access_token, self.id, survey.display_name)
                    body_html += '</table>' + \
                                 '<p>Trân trọng,</p>' + \
                                 '<p>Học viện SCI.</p>'
                    values['body_html'] = body_html
                    mail = self.env['mail.mail'].create(values)
                    mail.send()
            return {'name': 'Emails',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'tree,form',
                    'res_model': 'mail.mail',
                    'domain': [('res_id', '=', self.id)]}
        elif not self.survey_survey:
            raise ValidationError(_('Please choose Survey.'))
        else:
            raise ValidationError(_('There are currently no students in this class'))