import os
from pathlib import Path
from decouple import config
from datetime import timedelta
import cloudinary
from corsheaders.defaults import default_headers

BASE_DIR = Path(__file__).resolve().parent.parent

# 🔹 Security
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", cast=bool)
DJANGO_ENV = config("DJANGO_ENV")
USE_SUPABASE = config("USE_SUPABASE", cast=bool, default=False)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost").split(",")
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="localhost")
EMAIL_PORT = config("EMAIL_PORT", cast=int, default=25)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=True)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
# 🔹 Installed apps
INSTALLED_APPS = [
    # Django core
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',

    # Third-party
    'rest_framework', 'rest_framework.authtoken', 'djoser', 'social_django',
    'corsheaders', 'cloudinary', 'cloudinary_storage',
    'rest_framework_simplejwt.token_blacklist',

    # Local apps
    'accounts', 'tours', 'media_gallery', 'costs', 'locations',
    'bookings', 'payments'
]

AUTH_USER_MODEL = "accounts.User"

# 🔹 Middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware'
]

# 🔹 CORS & CSRF
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:5173"
).split(",")
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = list(default_headers) + ["Authorization"]

# 🔹 Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

# 🔹 WSGI & ASGI
ROOT_URLCONF = "tour_management.urls"
WSGI_APPLICATION = "tour_management.wsgi.application"

# 🔹 Databases
if USE_SUPABASE:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("SUPABASE_DB_NAME"),
            "USER": config("SUPABASE_DB_USER"),
            "PASSWORD": config("SUPABASE_DB_PASSWORD"),
            "HOST": config("SUPABASE_DB_HOST"),
            "PORT": config("SUPABASE_DB_PORT", default=5432, cast=int),
            'CONN_MAX_AGE': 10,  # short-lived connections
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DB_NAME"),
            "USER": config("DB_USER"),
            "PASSWORD": config("DB_PASSWORD"),
            "HOST": config("DB_HOST"),
            "PORT": config("DB_PORT", default=5432, cast=int),
        }
    }

# 🔹 Cloudinary
CLOUDINARY = {
    'cloud_name': config("CLOUDINARY_CLOUD_NAME"),
    'api_key': config("CLOUDINARY_API_KEY"),
    'api_secret': config("CLOUDINARY_API_SECRET"),
}
cloudinary.config(
    cloud_name=CLOUDINARY['cloud_name'],
    api_key=CLOUDINARY['api_key'],
    api_secret=CLOUDINARY['api_secret'],
    secure=True,
)

# 🔹 Auth backends (social login)
AUTHENTICATION_BACKENDS = (
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = config("GOOGLE_OAUTH_CLIENT_ID")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = config("GOOGLE_OAUTH_CLIENT_SECRET")
SOCIAL_AUTH_FACEBOOK_KEY = config("FACEBOOK_OAUTH2_KEY")
SOCIAL_AUTH_FACEBOOK_SECRET = config("FACEBOOK_OAUTH2_SECRET")

SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['email', 'profile']
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {'fields': 'id, name, email'}

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# 🔹 JWT / Djoser
from .jwt import *
# 🔹 Caching / Redis
from .cache import *
# 🔹 Logging
from .logging import *

# 🔹 Static & Media (Cloudinary)
STATIC_URL = 'static/'
STATICFILES_STORAGE = 'cloudinary_storage.storage.StaticHashedCloudinaryStorage'
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_RESULT_BACKEND = "redis://redis:6379/0"

SSLCOMMERZ_STORE_ID = config("SSLCOMMERZ_STORE_ID")
SSLCOMMERZ_STORE_PASSWORD = config("SSLCOMMERZ_STORE_PASSWORD")
SSL_SUCCESS_URL = config("SSL_SUCCESS_URL")
SSL_FAIL_URL = config("SSL_FAIL_URL")
SSL_CANCEL_URL = config("SSL_CANCEL_URL")
