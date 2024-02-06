from typing import Optional

from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.utils import aware_utcnow


class TokenExpiredError(Exception):
    pass


class AutoRefreshToken(AccessToken):
    def __init__(self, token: Optional["Token"] = None, verify: bool = True):
        super().__init__(token, verify)

        exp = self.payload.get("exp", None)
        if not token or not exp:
            return

        """
        In the settings, I have set a longer leeway to prevent the immediate
        raising of an "invalid token" exception when the token has expired.
        Instead, I now allow the token to be considered valid for a longer period.
        """

        # ex. exp 1707155570
        if float(exp) < aware_utcnow().timestamp():
            raise TokenExpiredError
