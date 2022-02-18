import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_cinema.settings')

app = Celery('My cinema')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send_spam_every_2_minute': {
        'task': 'account.tasks.send_beat_email',
        'schedule': crontab(minute='*/2'),
    },
}