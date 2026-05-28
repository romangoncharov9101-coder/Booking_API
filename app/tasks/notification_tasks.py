from app.tasks.celery_app import celery_app

@celery_app.task(name='app.tasks.notification_tasks.send_pending_notifications')
def send_pending_notifications() -> None:
    """Send all pending notification events via email."""
    pass #TODO: Stage 7

@celery_app.task(name='app.tasks.notification_tasks.send_booking_reminders')
def send_booking_reminders() -> None:
    """Send reminders for upcoming bookings."""
    pass #TODO: Stage 7