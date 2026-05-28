from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    'booking_api',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        'app.tasks.notification_tasks',
        'app.tasks.booking_tasks',
        'app.tasks.waitlist_tasks',
    ],
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        'send-pending-emails': {
            'task': 'app.tasks.notification_tasks.send_pending_notifications',
            'schedule': 60.0,
        },
        'expire_waitlist': {
            'task': 'app.tasks.waitlist_tasks.expire_old_waitlist_entries',
            'schedule': 300.0,
        },
        'complete-past-bookings': {
            'task': 'app.tasks.booking_tasks.complete_past_bookings',
            'schedule': 300.0,
        },
        'check-availability': {
            'task': 'app.tasks.waitlist_tasks.check_near_future_availability',
            'schedule': 1800.0,
        },
        'send-reminders': {
            'task': 'app.tasks.notification_tasks.send_booking_reminders',
            'schedule': crontab(minute='0'),
        },
    }
)