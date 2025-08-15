# tours/management/commands/seed_tours.py
from django.core.management.base import BaseCommand
from accounts.models import User
from tours.models import Tour
from decimal import Decimal
from faker import Faker
import random
from datetime import timedelta
from django.utils.timezone import make_aware

fake = Faker()

DESTINATIONS = [
    "Grand Canyon, USA",
    "Machu Picchu, Peru",
    "Banff National Park, Canada",
    "Santorini, Greece",
    "Kyoto, Japan",
    "Bali, Indonesia",
    "Phuket, Thailand",
    "Petra, Jordan",
    "Venice, Italy",
    "Swiss Alps, Switzerland"
]

CATEGORIES = ["Adventure", "Nature", "Cultural", "Beach", "Historical", "Hiking", "City Tour"]

def random_coordinates():
    return round(random.uniform(-60, 60), 5), round(random.uniform(-170, 170), 5)

class Command(BaseCommand):
    help = "Seed 5 tours for a given organizer"

    def add_arguments(self, parser):
        parser.add_argument("--email", type=str, help="Organizer email")

    def handle(self, *args, **options):
        email = options.get("email")
        if email:
            organizer = User.objects.filter(email=email, role="organizer").first()
            if not organizer:
                self.stdout.write(self.style.ERROR(f"No organizer found with email {email}"))
                return
        else:
            organizer = User.objects.filter(role="organizer").order_by("?").first()
            if not organizer:
                self.stdout.write(self.style.ERROR("No organizers found in DB"))
                return

        self.stdout.write(self.style.WARNING(f"Creating 5 tours for {organizer.email}"))

        for i in range(5):
            title = random.choice(DESTINATIONS)
            start_date = fake.date_between(start_date="+5d", end_date="+30d")
            end_date = start_date + timedelta(days=random.randint(3, 10))
            slat, slng = random_coordinates()
            elat, elng = random_coordinates()

            tour = Tour.objects.create(
                organizer=organizer,
                title=f"Explore {title}",
                description=fake.paragraph(nb_sentences=4),
                start_date=start_date,
                end_date=end_date,
                start_location=f"{fake.city()} ({slat},{slng})",
                end_location=f"{fake.city()} ({elat},{elng})",
                cost_per_person=Decimal(f"{random.uniform(200, 5000):.2f}"),
                is_custom_group=random.choice([True, False]),
                max_participants=random.randint(8, 25),
                category=random.choice(CATEGORIES),
                cover_image=f"https://picsum.photos/seed/customtour{i}/800/600"
            )

            self.stdout.write(self.style.SUCCESS(f"✅ Created tour: {tour.title}"))

        self.stdout.write(self.style.SUCCESS("🎉 5 tours seeded successfully!"))
