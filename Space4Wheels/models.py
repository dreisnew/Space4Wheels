from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.
class Post(models.Model):
    PRICE_RATES = [
        ('day', 'Per Day'),
        ('week', 'Per Week'),
        ('month', 'Per Month'),
        # Add more rates as needed
    ]

    CAR_SPACE_TYPES = [
        ('Driveway', 'Driveway'),
        ('Garage', 'Garage'),
        ('Open Lot', 'Open Lot'),
        # Add more types as needed
    ]

    title = models.CharField(max_length=100)
    content = models.TextField()
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_rate = models.CharField(max_length=20, choices=PRICE_RATES)  # per day, per week, per month
    car_space_pics = models.ImageField(upload_to='car_space_pics')
    car_space_type = models.CharField(max_length=20, choices=CAR_SPACE_TYPES)
    map_image = models.TextField()
    additional_notes = models.TextField(blank=True, null=True)  # Optional
    status = models.CharField(max_length=20, default='available')  # available/booked
    date_posted = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('done', 'Done'),
    ]
    
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    renter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings_made')
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings_received')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reservation_start_date = models.DateTimeField()
    reservation_end_date = models.DateTimeField()
    date_requested = models.DateTimeField(default=timezone.now)
    pending_approval = models.BooleanField(default=True)
    
    def __str__(self):
        return f'{self.renter.username} - {self.post.title}'
    
    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})
    
    