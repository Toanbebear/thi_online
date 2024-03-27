from odoo.http import request

from odoo import http
from odoo.exceptions import UserError
import werkzeug
from odoo.addons.survey.controllers.main import Survey


class SurveyInherits(Survey):

    @http.route('/survey/start/<string:survey_token>/batch_id=<string:batch_id>', type='http', auth='public',
                website=True)
    def survey_start_academy(self, survey_token, answer_token=None, batch_id=None, email=False, **post):
        """ Start a survey by providing
         * a token linked to a survey;
         * a token linked to an answer or generate a new token if access is allowed;
        """
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=False)
        if access_data['validity_code'] is not True:
            return self._redirect_with_error(access_data, access_data['validity_code'])

        survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']
        if not answer_sudo:
            try:
                answer_sudo = survey_sudo._create_answer_academy(user=request.env.user, batch=batch_id, email=email)
            except UserError:
                answer_sudo = False

        if not answer_sudo:
            try:
                survey_sudo.with_user(request.env.user).check_access_rights('read')
                survey_sudo.with_user(request.env.user).check_access_rule('read')
            except:
                return werkzeug.utils.redirect("/")
            else:
                return request.render("survey.403", {'survey': survey_sudo})

        # Select the right page
        if answer_sudo.state == 'new':  # Intro page
            user_ids = request.env['res.users'].search([])
            data = {'survey': survey_sudo, 'answer': answer_sudo, 'page': 0, 'user_ids': user_ids}
            return request.render('survey.survey_init', data)
        else:
            return request.redirect('/survey/fill/%s/%s' % (survey_sudo.access_token, answer_sudo.token))
