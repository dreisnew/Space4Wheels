# celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from Space4Wheels.tasks import update_expired_bookings_status

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')

celery_app = Celery('your_project')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()

# Add periodic task
celery_app.conf.beat_schedule = {
    'update-expired-bookings-status': {
        'task': 'your_app.tasks.update_expired_bookings_status',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
}
