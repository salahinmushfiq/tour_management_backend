import os
from decouple import config
from django.core.wsgi import get_wsgi_application

env = config("DJANGO_ENV", default="prod")
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    f"tour_management.settings.{env}"
)

application = get_wsgi_application()
