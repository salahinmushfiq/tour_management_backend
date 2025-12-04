# accounts/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            raw_token = request.COOKIES.get('access')  # <--- cookie
            if raw_token is None:
                return None
            return self.get_user(self.get_validated_token(raw_token))
        return super().authenticate(request)
