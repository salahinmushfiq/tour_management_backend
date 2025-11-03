# tours/management/commands/seed_tours.py
from django.core.management.base import BaseCommand
from tours.models import Tour, Guide, TourParticipant, Offer
from locations.models import VisitedRegion, TourLocation
from accounts.models import User
import random
from faker import Faker
from datetime import timedelta
from django.utils.timezone import make_aware
from decimal import Decimal
import math

fake = Faker()

DESTINATIONS = [
    ("Grand Canyon, USA",
     "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1000&q=80"),
    ("Machu Picchu, Peru",
     "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=1000&q=80"),
    ("Banff National Park, Canada",
     "https://images.unsplash.com/photo-1508264165352-258859e62245?auto=format&fit=crop&w=1000&q=80"),
    ("Angkor Wat, Cambodia",
     "https://images.unsplash.com/photo-1569937959760-36efcaa2700f?auto=format&fit=crop&w=1000&q=80"),
    ("Santorini, Greece",
     "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1000&q=80"),
    ("Patagonia, Argentina",
     "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1000&q=80"),
    ("Seychelles", "https://images.unsplash.com/photo-1518459031867-a89b944bffe2?auto=format&fit=crop&w=1000&q=80"),
    ("Kyoto, Japan", "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1000&q=80"),
    ("Cenotes of Mexico",
     "https://images.unsplash.com/photo-1576086670643-1e0caa199d89?auto=format&fit=crop&w=1000&q=80"),
    ("Luang Prabang, Laos",
     "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1000&q=80"),

    ("Icelandic Waterfalls",
     "https://images.unsplash.com/photo-1508264165352-258859e62245?auto=format&fit=crop&w=1000&q=80"),
    ("Great Wall, China",
     "https://images.unsplash.com/photo-1582431863423-6be6e5be3d6d?auto=format&fit=crop&w=1000&q=80"),
    ("Petra, Jordan", "https://images.unsplash.com/photo-1552633230-d0d2df9d6d7b?auto=format&fit=crop&w=1000&q=80"),
    ("Venice, Italy", "https://images.unsplash.com/photo-1491553895911-0055eca6402d?auto=format&fit=crop&w=1000&q=80"),
    ("Swiss Alps, Switzerland",
     "https://images.unsplash.com/photo-1508264165352-258859e62245?auto=format&fit=crop&w=1000&q=80"),
    (
    "Bali, Indonesia", "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=1000&q=80"),
    ("Sahara Desert, Morocco",
     "https://images.unsplash.com/photo-1485841890310-6a055c88698a?auto=format&fit=crop&w=1000&q=80"),
    ("Phuket, Thailand",
     "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1000&q=80"),
    ("Ha Long Bay, Vietnam",
     "https://images.unsplash.com/photo-1559304715-4506a7d6e6f2?auto=format&fit=crop&w=1000&q=80"),
    ("Kruger National Park, South Africa",
     "https://images.unsplash.com/photo-1560507074-438a0b5d3db1?auto=format&fit=crop&w=1000&q=80"),

    ("Himalayas, Nepal",
     "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=1000&q=80"),
    ("Galápagos Islands, Ecuador",
     "https://images.unsplash.com/photo-1576086670643-1e0caa199d89?auto=format&fit=crop&w=1000&q=80"),
    ("Cinque Terre, Italy",
     "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=1000&q=80"),
    ("Great Barrier Reef, Australia",
     "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1000&q=80"),
    ("Iguazu Falls, Brazil",
     "https://images.unsplash.com/photo-1526481280694-3bfa7568e8f8?auto=format&fit=crop&w=1000&q=80"),
    ("Blue Lagoon, Iceland",
     "https://images.unsplash.com/photo-1508264165352-258859e62245?auto=format&fit=crop&w=1000&q=80"),
    ("Norwegian Fjords",
     "https://images.unsplash.com/photo-1508264165352-258859e62245?auto=format&fit=crop&w=1000&q=80"),
    ("Serengeti, Tanzania",
     "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1000&q=80"),
    ("Amalfi Coast, Italy",
     "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=1000&q=80"),
    ("Yosemite, USA", "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=1000&q=80"),

    ("Maldives", "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1000&q=80"),
    ("Rio de Janeiro, Brazil",
     "https://images.unsplash.com/photo-1501594907352-04cda38ebc29?auto=format&fit=crop&w=1000&q=80"),
    ("New Zealand South Island",
     "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1000&q=80"),
    ("Hạ Long City, Vietnam",
     "https://images.unsplash.com/photo-1559304715-4506a7d6e6f2?auto=format&fit=crop&w=1000&q=80"),
    ("Scottish Highlands, UK",
     "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=1000&q=80"),
    ("Istanbul, Turkey",
     "https://images.unsplash.com/photo-1491553895911-0055eca6402d?auto=format&fit=crop&w=1000&q=80"),
    ("Plitvice Lakes, Croatia",
     "https://images.unsplash.com/photo-1560507074-438a0b5d3db1?auto=format&fit=crop&w=1000&q=80"),
    ("Cintra, Portugal",
     "https://images.unsplash.com/photo-1508264165352-258859e62245?auto=format&fit=crop&w=1000&q=80"),
    ("Taj Mahal, India",
     "https://images.unsplash.com/photo-1569937959760-36efcaa2700f?auto=format&fit=crop&w=1000&q=80"),
    ("Dubai Desert, UAE",
     "https://images.unsplash.com/photo-1485841890310-6a055c88698a?auto=format&fit=crop&w=1000&q=80")
]

CATEGORIES = ["Adventure", "Nature", "Cultural", "Beach", "Historical", "Hiking", "City Tour"]


def random_coordinates():
    return round(random.uniform(-60, 60), 5), round(random.uniform(-170, 170), 5)


class Command(BaseCommand):
    help = 'Seed 300+ tours with participants, offers, guides, and visited regions'

    def handle(self, *args, **kwargs):
        # Clear existing data
        TourParticipant.objects.all().delete()
        Offer.objects.all().delete()
        Tour.objects.all().delete()
        Guide.objects.all().delete()
        VisitedRegion.objects.all().delete()
        TourLocation.objects.all().delete()

        organizers = list(User.objects.filter(role='organizer'))
        guides = list(User.objects.filter(role='guide'))
        tourists = list(User.objects.filter(role='tourist'))

        if not (organizers and guides and tourists):
            self.stdout.write(self.style.ERROR("Need users for each role (organizer, guide, tourist) to seed data."))
            return

        guide_profiles = [Guide.objects.get_or_create(user=g)[0] for g in guides]
        total_tours = 0
        dests = DESTINATIONS.copy()
        random.shuffle(dests)
        ptr = 0
        needed = math.ceil(300 / len(organizers)) + 3

        for org in organizers:
            for _ in range(needed):
                if ptr >= len(dests):
                    ptr = 0
                    random.shuffle(dests)
                title, img = dests[ptr]
                ptr += 1

                start_date = fake.date_between(start_date='-120d', end_date='+120d')
                end_date = start_date + timedelta(days=random.randint(3, 12))
                slat, slng = random_coordinates()
                elat, elng = random_coordinates()

                tour = Tour.objects.create(
                    organizer=org,
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
                    cover_image=f"https://picsum.photos/seed/{total_tours}/800/600"
                )
                total_tours += 1

                # Assign 1-3 guides
                for g in random.sample(guide_profiles, random.randint(1, min(3, len(guide_profiles)))):
                    tour.guides.add(g)

                # Add 6-15 tourists as participants
                selected_tourists = random.sample(tourists, random.randint(6, min(15, len(tourists))))
                for u in selected_tourists:
                    joined_at = fake.date_time_between(
                        start_date=start_date - timedelta(days=60),
                        end_date=start_date
                    )
                    joined_at = make_aware(joined_at) if joined_at.tzinfo is None else joined_at

                    participant = TourParticipant.objects.create(
                        tour=tour,
                        user=u,
                        joined_at=joined_at,
                    )

                    # Seed 1-3 visited regions per participant
                    num_regions = random.randint(1, 3)
                    try:
                        start_coords_str = tour.start_location.split('(')[1].rstrip(')')
                        base_lat, base_lng = map(float, start_coords_str.split(','))
                    except Exception:
                        base_lat, base_lng = random_coordinates()

                    for _ in range(num_regions):
                        offset_lat = base_lat + random.uniform(-0.1, 0.1)
                        offset_lng = base_lng + random.uniform(-0.1, 0.1)
                        region_name = fake.city()
                        visited_on = fake.date_between(start_date=tour.start_date, end_date=tour.end_date)

                        VisitedRegion.objects.create(
                            user=u,
                            tour=tour,
                            region_name=region_name,
                            latitude=Decimal(f"{offset_lat:.6f}"),
                            longitude=Decimal(f"{offset_lng:.6f}"),
                            visited_on=visited_on,
                        )

                    # Optional: Uncomment below to seed TourLocation GPS points per participant
                    """
                    num_gps_points = random.randint(5, 10)
                    tour_duration_seconds = (tour.end_date - tour.start_date).days * 24 * 3600
                    base_timestamp = make_aware(fake.date_time_between(start_date=tour.start_date, end_date=tour.end_date))
                    for i in range(num_gps_points):
                        time_offset = timedelta(seconds=(tour_duration_seconds // num_gps_points) * i)
                        timestamp = base_timestamp + time_offset
                        lat = base_lat + random.uniform(-0.05, 0.05)
                        lng = base_lng + random.uniform(-0.05, 0.05)
                        TourLocation.objects.create(
                            tour=tour,
                            user=u,
                            latitude=lat,
                            longitude=lng,
                            timestamp=timestamp
                        )
                    """

                # Create 1-3 offers per tour
                for __ in range(random.randint(1, 3)):
                    valid_from = start_date - timedelta(days=random.randint(10, 25))
                    valid_until = valid_from + timedelta(days=random.randint(1, 20))  # always after valid_from
                    Offer.objects.create(
                        tour=tour,
                        title=fake.word().capitalize() + " Discount",
                        description=fake.sentence(nb_words=6),
                        discount_percent=random.randint(5, 40),
                        valid_from=valid_from,
                        valid_until=valid_until,
                    )

        self.stdout.write(self.style.SUCCESS(f"✅ Seeded {total_tours} tours with participants, visited regions, offers, and guides."))
