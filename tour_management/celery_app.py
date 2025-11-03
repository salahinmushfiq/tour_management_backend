# celery_app.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tour_management.settings.dev")

app = Celery("tour_management")

# Use Docker service name for Redis
app.conf.broker_url = "redis://redis:6379/0"
app.conf.result_backend = "redis://redis:6379/0"

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

