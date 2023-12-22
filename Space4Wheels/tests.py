from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Booking, Post  # Import the Post model

class BookingTestCase(TestCase):
    def test_update_status_past_end_date(self):
        # Create actual instances of Post and User
        post_instance = Post.objects.create(
            title='Test Post',
            content='Test content for the post.',
            country='Test Country',
            city='Test City',
            address='Test Address',
            price=50.00,
            price_rate='day',
            car_space_pics='path/to/car_space_pic.jpg',
            car_space_type='Driveway',
            map_image='Test Map Image URL',
            additional_notes='Additional notes for testing purposes.',
            status='available',
            date_posted=timezone.now(),
            date_updated=timezone.now(),
            author=User.objects.create(username='TestUser', password='test_password'),
            rating_rating=0.0,
        )
        renter_user_instance = User.objects.create(username='AdminLara', password='laraissleepingrn')
        host_user_instance = User.objects.create(username='AdminDre', password='andredre19')

        past_end_date = timezone.now() - timezone.timedelta(days=1)
        booking = Booking.objects.create(
            post=post_instance,
            renter=renter_user_instance,
            host=host_user_instance,
            status='approved',
            reservation_start_date=timezone.now() - timezone.timedelta(days=2),
            reservation_end_date=past_end_date,
            date_requested=timezone.now() - timezone.timedelta(days=3),
            pending_approval=False
        )
        
        booking.update_status()
        self.assertEqual(booking.status, 'done')
