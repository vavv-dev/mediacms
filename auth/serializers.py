from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserInfoTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add user info claims
        token["username"] = getattr(user, "username", None)
        token["name"] = getattr(user, "name", None)
        token["email"] = getattr(user, "email", None)

        return token
