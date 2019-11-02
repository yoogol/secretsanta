from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
import hashlib


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.userinfo.email_confirmed)
        )


def generate_invite_token(by_user, to_user_email):
    input = str(by_user) + str(to_user_email)

    return hashlib.sha224(input.encode('utf-8')).hexdigest()


account_activation_token = AccountActivationTokenGenerator()

# https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html