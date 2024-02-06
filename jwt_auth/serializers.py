from typing import Any, Dict, TypeVar

from django.contrib.auth.models import AbstractBaseUser
from rest_framework_simplejwt.models import TokenUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

AuthUser = TypeVar("AuthUser", AbstractBaseUser, TokenUser)


class UserInfoTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom TokenObtainPairSerializer to include user info in the token response.
    """

    @classmethod
    def get_token(cls, user: AuthUser):
        token = super().get_token(user)

        # Add user info claims
        token["username"] = getattr(user, "username", None)
        token["name"] = getattr(user, "name", None)
        token["email"] = getattr(user, "email", None)

        return token
