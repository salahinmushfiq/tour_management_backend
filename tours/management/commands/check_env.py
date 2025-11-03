from django.core.management.base import BaseCommand
from django.conf import settings
from decouple import config


class Command(BaseCommand):
    help = "Check current Django environment, debug status, and database connection"

    env = config("DJANGO_ENV", default="prod")

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=== Django Environment Info ==="))
        self.stdout.write(f"DJANGO_ENV: {config('DJANGO_ENV', default='prod')}")
        self.stdout.write(f"DEBUG: {settings.DEBUG}")

        db = settings.DATABASES.get("default", {})
        self.stdout.write("DATABASE:")
        self.stdout.write(f"  ENGINE: {db.get('ENGINE')}")
        self.stdout.write(f"  NAME: {db.get('NAME')}")
        self.stdout.write(f"  USER: {db.get('USER')}")
        self.stdout.write(f"  HOST: {db.get('HOST')}")
        self.stdout.write(f"  PORT: {db.get('PORT')}")

        use_supabase = getattr(settings, "USE_SUPABASE", False)
        self.stdout.write(f"Using Supabase: {use_supabase}")
