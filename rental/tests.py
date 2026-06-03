from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Car, Booking
from datetime import date, timedelta

class DriveHubTestCase(TestCase):
    def setUp(self):
        """Set up test data dependencies before each test case execution."""
        self.user = User.objects.create_user(
            username='testcustomer', 
            password='securepassword123'
        )
        
        self.car = Car.objects.create(
            make="Toyota", 
            model="Corolla", 
            year=2022, 
            daily_price=35.00, 
            status="available",
            license_plate="ABC-001",
            category="economy"
        )

    def test_car_list_view_availability(self):
        """Verify that the vehicle discovery page loads and filters active inventory."""
        self.client.login(username='testcustomer', password='securepassword123')
        
        response = self.client.get(reverse('car_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Toyota Corolla")
        self.assertContains(response, "$35.00")

    def test_booking_request_pipeline(self):
        """Verify that an authenticated customer can successfully submit a booking request."""
        self.client.login(username='testcustomer', password='securepassword123')
        
        start_date = date.today()
        end_date = start_date + timedelta(days=5)
        
        response = self.client.post(reverse('book_car', args=[self.car.pk]), {
            'start_date': start_date,
            'end_date': end_date,
            'notes': 'Coursework verification unit test booking.'
        })
        
        self.assertEqual(Booking.objects.count(), 1)
        new_booking = Booking.objects.first()
        self.assertEqual(new_booking.car, self.car)
        self.assertEqual(new_booking.user, self.user)
        self.assertEqual(new_booking.status, 'pending')