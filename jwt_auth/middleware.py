# middleware.py

from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from jwt_auth.tokens import TokenExpiredError
from jwt_auth.views import set_jwt_cookie


class JwtCookeMiddlewate(MiddlewareMixin):
    """
    Middleware to refresh token from cookie if expired
    """

    def process_exception(self, request, exception):
        if not isinstance(exception, TokenExpiredError):
            return

        # redirect to current page after saving refreshed token in cookie
        response = HttpResponseRedirect(request.get_full_path())

        # refresh token from cookie
        raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH_NAME'])
        refresh = RefreshToken(raw_token)
        raw_token = str(refresh.access_token)
        validated_token = api_settings.AUTH_TOKEN_CLASSES[0](raw_token.encode('utf-8'))
        set_jwt_cookie(response, validated_token)

        return response
