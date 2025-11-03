import os
import sys
from decouple import config

def main():
    env = config("DJANGO_ENV", default="dev")
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        f"tour_management.settings.{env}"
    )

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
