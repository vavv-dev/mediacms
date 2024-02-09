from django.conf import settings
from rest_framework.views import Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenViewBase,
)


def set_jwt_cookie(response, access_token=None, refresh_token=None):
    """
    Set JWT in cookie
    """

    cookie_settings = {
        "secure": settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        "httponly": settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
        "samesite": settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
    }

    if access_token:
        # set access token in cookie
        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE_NAME'],
            value=access_token,
            expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
            **cookie_settings,
        )

    if refresh_token:
        # set refresh token in cookie
        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH_NAME'],
            value=refresh_token,
            expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
            **cookie_settings,
        )


class CookieTokenObtainPairView(TokenObtainPairView):
    """
    Custom TokenObtainPairView to set token in cookie
    """

    _serializer_class = "jwt_auth.serializers.UserInfoTokenObtainPairSerializer"

    def finalize_response(self, request, response, *args, **kwargs):
        set_jwt_cookie(response, response.data['access'], response.data['refresh'])
        del response.data['refresh']
        return super().finalize_response(request, response, *args, **kwargs)


class CookieTokenRefreshView(TokenRefreshView):
    """
    This refresh view is not required.
    JWTCookieMiddleware will take care of refreshing token from cookie.
    """


class CookieTokenDestroyView(TokenViewBase):
    """
    Custom TokenDestroyView to delete cookies and blacklist tokens
    """

    def post(self, request, *args, **kwargs):
        # TODO security measure is necessary?

        response = Response({}, status=204)
        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE_NAME'])
        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH_NAME'])

        # TODO blacklist tokens

        return response
