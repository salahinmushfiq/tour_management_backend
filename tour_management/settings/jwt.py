from datetime import timedelta

SIMPLE_JWT = {
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=10),
    "REFRESH_TOKEN_LIFETIME": timedelta(minutes=10),
    "TOKEN_OBTAIN_SERIALIZER": "accounts.serializers.CustomTokenObtainPairSerializer",
}

DJOSER = {
    # "DOMAIN": "localhost:5173",
    "DOMAIN": "tour-mate-vite.netlify.app",
    "PASSWORD_RESET_CONFIRM_URL": "password-reset-confirm/{uid}/{token}/",
    "SITE_NAME": "Tour Management",
    "USER_CREATE_PASSWORD_RETYPE": True,
    "USERNAME_FIELD": "email",
    "SERIALIZERS": {
        "user_create": "accounts.serializers.CustomUserCreateSerializer",
        "current_user": "accounts.serializers.CustomUserSerializer",
    },
}
