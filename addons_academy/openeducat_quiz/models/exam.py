#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime
from datetime import datetime


class OpExam(models.Model):
    _inherit = "op.exam"

    exam_formation = fields.Selection([
        ('offline', 'Offline'),
        ('online', 'Online'),
    ], default='offline', string='Exam Formation')
    quiz_id = fields.Many2one('op.quiz', 'Quiz')
    quiz_result_id = fields.One2many('op.quiz.result', 'exam_id')

    @api.onchange('exam_formation')
    def onchange_exam_formation(self):
        self.quiz_id = False

    @api.depends('quiz_result_id')
    def retrieving_points(self):
        for record in self:
            quiz_result = self.env['op.quiz.result'].search([])
            for rec in quiz_result:
                if rec.quiz_id == record.quiz_id:
                    for ret in record.attendees_line:
                        if ret.student_id.partner_id.user_ids == rec.user_id:
                            ret.online_marks = (rec.score) / ( 100 / float(record.total_marks))


    # @api.model
    # def open_and_close_quiz(self):
    #     for exam in self.env['op.exam'].search([('quiz_id', '!=', 'False')]):
    #         today = fields.Datetime.today()
    #         start_time = fields.Datetime.from_string(exam.start_time)
    #         end_time = fields.Datetime.from_string(exam.end_time)
    #         if start_time < today and today < end_time:
    #             exam.quiz_id.state = 'open'
    #         if today < start_time:
    #             exam.quiz_id.state = 'draft'
    #         if today > end_time:
    #             exam.quiz_id.state = 'done'


class OpResultLine(models.Model):
    _inherit = "op.result.line"

    exam_formation = fields.Selection([
        ('offline', 'Offline'),
        ('online', 'Online'),
    ], related='exam_id.exam_formation', store=True, string='Exam Formation')
    online_marks = fields.Float('Marks', readonly=True)
    offline_marks = fields.Float('Marks', group_operator='avg')
    marks = fields.Integer('Marks', compute='_compute_mark', store=True)

    @api.depends('online_marks', 'offline_marks', 'exam_formation')
    def _compute_mark(self):
        for record in self:
            if record.exam_formation == 'online':
                record.marks = record.online_marks
            else:
                record.marks = record.offline_marks

    @api.constrains('online_marks')
    def onchange_online_marks(self):
        for record in self:
            if record.online_marks > record.exam_id.total_marks:
                raise ValidationError(_(
                    "score cannot be greater than the total score"))
            elif self.online_marks < 0:
                raise ValidationError(_(
                    "Score must not be less than 0"))

    @api.constrains('offline_marks')
    def onchange_offline_marks(self):
        for rec in self:
            if rec.offline_marks > rec.exam_id.total_marks:
                raise ValidationError(_(
                    "score cannot be greater than the total score"))
            elif rec.offline_marks < 0:
                raise ValidationError(_(
                    "Score must not be less than 0"))