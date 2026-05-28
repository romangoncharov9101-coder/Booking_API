from app.tasks.celery_app import celery_app

@celery_app.task(name='app.tasks.booking_tasks.complete_past_bookings')
def complete_past_bookings() -> None:
    """Mark confirmed bookings whose ends_at < now() as completed."""
    pass #TODO: Stage 7