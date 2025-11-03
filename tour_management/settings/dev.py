from .base import *
DEBUG = True

# Dev email backend
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# DEFAULT_FROM_EMAIL = "TourMate <noreply@tourmate.local>"
EMAIL_BACKEND = config("EMAIL_BACKEND")
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT", cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=True)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL")


# Security relaxed for dev
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
