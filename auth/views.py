from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView


class CookieTokenObtainPairWithView(TokenObtainPairView):
    _serializer_class = "auth.serializers.UserInfoTokenObtainPairSerializer"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        response = Response(serializer.validated_data, status=status.HTTP_200_OK)

        cookie_settings = {
            "secure": settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            "httponly": settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            "samesite": settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
        }

        # set access token in cookie
        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE_NAME'],
            value=serializer.validated_data["access"],
            expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
            **cookie_settings,
        )

        # set refresh token in cookie
        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH_NAME'],
            value=serializer.validated_data["refresh"],
            expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
            **cookie_settings,
        )

        return response
