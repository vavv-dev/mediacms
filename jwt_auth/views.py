from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


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
        return super().finalize_response(request, response, *args, **kwargs)


"""
refresh view is not required. JWTCookieMiddleware will take care of refreshing token from cookie
"""
