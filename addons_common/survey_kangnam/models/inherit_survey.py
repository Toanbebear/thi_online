from odoo import fields, models


class InheritSurvey(models.Model):
    _inherit = 'survey.survey'

    def _create_answer_kangnam(self, user=False, partner=False, email=False, test_entry=False, check_attempts=True,
                               walkin=False, **additional_vals):
        """ Main entry point to get a token back or create a new one. This method
        does check for current user access in order to explicitely validate
        security.

          :param user: target user asking for a token; it might be void or a
                       public user in which case an email is welcomed;
          :param email: email of the person asking the token is no user exists;
        """
        self.check_access_rights('read')
        self.check_access_rule('read')
        answers = self.env['survey.user_input']
        for survey in self:
            if partner and not user and partner.user_ids:
                user = partner.user_ids[0]

            invite_token = additional_vals.pop('invite_token', False)
            survey._check_answer_creation(user, partner, email, test_entry=test_entry, check_attempts=check_attempts,
                                          invite_token=invite_token)

            answer_vals = {
                'survey_id': survey.id,
                'test_entry': test_entry,
                'question_ids': [(6, 0, survey._prepare_answer_questions().ids)]
            }
            if walkin:
                answer_vals['walkin_id'] = walkin
            if user and not user._is_public():
                answer_vals['partner_id'] = user.partner_id.id
                answer_vals['email'] = user.email
            elif partner:
                answer_vals['partner_id'] = partner.id
                answer_vals['email'] = partner.email
            else:
                answer_vals['email'] = email

            if invite_token:
                answer_vals['invite_token'] = invite_token
            elif survey.is_attempts_limited and survey.access_mode != 'public':
                answer_vals['invite_token'] = self.env['survey.user_input']._generate_invite_token()
            answer_vals.update(additional_vals)
            answers += answers.create(answer_vals)

        return answers


class SurveyUserInputs(models.Model):
    _inherit = 'survey.user_input'

    walkin_id = fields.Many2one('sh.medical.appointment.register.walkin', string='walkin')
