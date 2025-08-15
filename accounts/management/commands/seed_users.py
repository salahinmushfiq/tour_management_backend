from django.core.management.base import BaseCommand
from accounts.models import User
from tours.models import Guide
from faker import Faker
from django.db.utils import IntegrityError

fake = Faker()

DEFAULT_PASSWORD = "password123"

class Command(BaseCommand):
    help = 'Seed users with roles and create Guide profiles for guide users'

    def add_arguments(self, parser):
        parser.add_argument('--organizers', type=int, default=15, help='Number of organizers to create')
        parser.add_argument('--guides', type=int, default=40, help='Number of guides to create')
        parser.add_argument('--tourists', type=int, default=150, help='Number of tourists to create')
        parser.add_argument('--no-delete', action='store_true', help='Do not delete existing users and guides before seeding')

    def create_user(self, role):
        for _ in range(10):  # retry to avoid duplicates
            email = fake.unique.email()
            username = fake.unique.user_name()
            # Truncate phone number to max 15 chars
            phone = fake.phone_number()[:15]

            try:
                user = User.objects.create_user(
                    email=email,
                    username=username,
                    password=DEFAULT_PASSWORD,
                    role=role,
                    contact_number=phone,
                    bio=fake.sentence(nb_words=10),
                    profile_picture=None,  # or a dummy URL string
                )
                return user
            except IntegrityError:
                continue
        return None

    def handle(self, *args, **options):
        if not options['no_delete']:
            # Delete guides first to avoid FK constraints
            guides_deleted, _ = Guide.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {guides_deleted} Guide profiles"))
            users_deleted, _ = User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.WARNING(f"Deleted {users_deleted} non-superuser users"))

        role_counts = {
            'organizer': options['organizers'],
            'guide': options['guides'],
            'tourist': options['tourists'],
        }

        total_created = 0
        total_guides_created = 0
        for role, count in role_counts.items():
            created = 0
            for _ in range(count):
                user = self.create_user(role)
                if user:
                    created += 1
                    total_created += 1
                    # Create Guide profile for guide users
                    if role == 'guide':
                        # Also truncate contact_number here
                        guide_phone = fake.phone_number()[:15]
                        Guide.objects.create(
                            user=user,
                            bio=fake.text(max_nb_chars=200),
                            contact_number=guide_phone,
                            # profile_picture=f"https://i.pravatar.cc/150?u={user.email}"
                        )
                        total_guides_created += 1
            self.stdout.write(self.style.SUCCESS(f"Created {created} users with role '{role}'"))

        self.stdout.write(self.style.SUCCESS(f"✅ Total users created: {total_created}"))
        self.stdout.write(self.style.SUCCESS(f"✅ Total Guide profiles created: {total_guides_created}"))
        self.stdout.write(self.style.SUCCESS(f"All users have default password: '{DEFAULT_PASSWORD}'"))
