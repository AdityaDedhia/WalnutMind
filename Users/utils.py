from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from .models import User

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (six.text_type(user.pk)+six.text_type(timestamp)+six.text_type(user.is_active)).encode('utf-8')


generate_token = TokenGenerator()