from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            # read from jwt cookie
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_NAME']) or None
        else:
            raw_token = self.get_raw_token(header)

        # if no token is provided, return None
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
