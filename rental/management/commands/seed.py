from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rental.models import UserProfile, Car, Booking
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Seeds the database with demo data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding demo data...')

        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_user('admin', 'admin@drivehub.com', 'admin123')
            admin.first_name = 'Admin'
            admin.last_name = 'User'
            admin.save()
            UserProfile.objects.create(user=admin, role='admin')
            self.stdout.write('  Admin user created (username: admin, password: admin123)')

        if not User.objects.filter(username='customer').exists():
            cust = User.objects.create_user('customer', 'cyrus@example.com', 'customer123')
            cust.first_name = 'Cyrus'
            cust.last_name = 'Kalema'
            cust.save()
            UserProfile.objects.create(user=cust, role='customer', phone='+256700000000')
            self.stdout.write(' Customer created (username: customer, password: customer123)')

        cars_data = [
            {'make': 'Toyota', 'model': 'Corolla', 'year': 2022, 'category': 'economy',
             'license_plate': 'ABC-001', 'daily_price': 35.00, 'seats': 5,
             'transmission': 'Automatic', 'fuel_type': 'Petrol',
             'image_url': 'https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?w=600'},
            {'make': 'Honda', 'model': 'CR-V', 'year': 2023, 'category': 'suv',
             'license_plate': 'XYZ-002', 'daily_price': 65.00, 'seats': 5,
             'transmission': 'Automatic', 'fuel_type': 'Petrol',
             'image_url': 'https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=600'},
            {'make': 'BMW', 'model': '3 Series', 'year': 2023, 'category': 'luxury',
             'license_plate': 'BMW-003', 'daily_price': 110.00, 'seats': 5,
             'transmission': 'Automatic', 'fuel_type': 'Petrol',
             'image_url': 'https://images.unsplash.com/photo-1555215695-3004980ad54e?w=600'},
            {'make': 'Ford', 'model': 'Transit', 'year': 2021, 'category': 'van',
             'license_plate': 'VAN-004', 'daily_price': 80.00, 'seats': 8,
             'transmission': 'Manual', 'fuel_type': 'Diesel',
             'image_url': 'https://images.unsplash.com/photo-1769159511492-aa484c036c06?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MjB8fGZvcmQlMjB0cmFuc2l0JTIwdmFufGVufDB8fDB8fHww'},
            {'make': 'Volkswagen', 'model': 'Golf', 'year': 2022, 'category': 'compact',
             'license_plate': 'VWG-005', 'daily_price': 45.00, 'seats': 5,
             'transmission': 'Manual', 'fuel_type': 'Petrol',
             'image_url': 'https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?w=600'},
        ]

        for data in cars_data:
            car, created = Car.objects.get_or_create(license_plate=data['license_plate'], defaults=data)
            if not created:
                car.image_url = data['image_url']
                car.save()
            self.stdout.write(f"Car synchronized: {car.make} {car.model}")
        try:
            customer = User.objects.get(username='customer')
            car = Car.objects.first()
            if car and not Booking.objects.filter(user=customer).exists():
                Booking.objects.create(
                    user=customer, car=car,
                    start_date=date.today() + timedelta(days=3),
                    end_date=date.today() + timedelta(days=6),
                    status='pending'
                )
                self.stdout.write(' Sample booking created')
        except Exception as e:
            self.stdout.write(f' Skipping booking: {e}')

        self.stdout.write(self.style.SUCCESS('\n Demo data seeded successfully!'))