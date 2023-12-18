# tasks.py
from celery import shared_task
from django.utils import timezone
from .models import Booking

@shared_task
def update_expired_bookings_status():
    expired_bookings = Booking.objects.filter(
        status='approved',
        reservation_end_date__lt=timezone.now()
    )

    for booking in expired_bookings:
        # Update the booking status to 'done' or anything appropriate
        booking.status = 'done'
        booking.save()
