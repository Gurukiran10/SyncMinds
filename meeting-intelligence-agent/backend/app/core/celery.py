"""
Celery Configuration for Background Tasks
"""
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "meeting_intelligence",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3300,  # 55 minutes
    beat_schedule={
        # Scan for meetings starting in ~30 min and send pre-meeting briefs
        "dispatch-pre-meeting-briefs": {
            "task": "dispatch_pre_meeting_briefs",
            "schedule": crontab(minute="*/30"),
        },
        # Send 24h action item reminders every hour
        "send-action-reminders": {
            "task": "send_action_reminders",
            "schedule": crontab(minute=0, hour="*/1"),
        },
        # Escalate overdue action items every morning at 9am UTC
        "escalate-overdue-actions": {
            "task": "escalate_overdue_action_items",
            "schedule": crontab(hour=9, minute=0),
        },
        # Sync calendars for all connected users every 6 hours
        "calendar-sync": {
            "task": "sync_calendars_all_users",
            "schedule": crontab(minute=0, hour="*/6"),
        },
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])
