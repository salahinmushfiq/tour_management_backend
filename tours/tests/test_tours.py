# tours/tests/test_tours.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from tours.models import Tour
from accounts.models import User
from bookings.models import Booking

class TourViewSetTestCase(APITestCase):
    def setUp(self):
        # Create an organizer
        self.organizer = User.objects.create_user(
            email="organizer@example.com",
            password="password123",
            is_organizer=True
        )

        # Create some tours
        self.tour1 = Tour.objects.create(
            title="Beach Trip",
            description="A fun trip to the beach",
            organizer=self.organizer,
        )
        self.tour2 = Tour.objects.create(
            title="Mountain Trip",
            description="Adventure in the mountains",
            organizer=self.organizer,
        )

        # Create bookings for tour1
        Booking.objects.create(
            tour=self.tour1,
            user=self.organizer,
        )

    def test_tour_list_returns_200(self):
        url = reverse("tour-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tour_list_contains_all_tours(self):
        url = reverse("tour-list")
        response = self.client.get(url)
        self.assertEqual(len(response.data), 2)
        titles = [tour["title"] for tour in response.data]
        self.assertIn("Beach Trip", titles)
        self.assertIn("Mountain Trip", titles)

    def test_tour_list_booking_count_annotation(self):
        url = reverse("tour-list")
        response = self.client.get(url)
        tour1_data = next(t for t in response.data if t["title"] == "Beach Trip")
        self.assertEqual(tour1_data.get("booking_count", None), 1)
        tour2_data = next(t for t in response.data if t["title"] == "Mountain Trip")
        self.assertEqual(tour2_data.get("booking_count", None), 0)
