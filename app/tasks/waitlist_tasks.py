from app.tasks.celery_app import celery_app

@celery_app.task(name='app.tasks.waitlist_tasks.expire_old_waitlist_entries')
def expire_old_waitlist_entries() -> None:
    """Expire active waitlist entries whose preferred_date_to is in the past."""
    pass #TODO: Stage 7

@celery_app.task(name='app.tasks.waitlist_tasks.check_near_future_availability')
def check_near_future_availability() -> None:
    """Check free slots in next NEAR_FUTURE_HOURS and notify waitlist subscribers."""
    pass #TODO: Stage 7