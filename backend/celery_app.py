"""
Celery application configuration for background tasks.
"""
import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Create Celery app
celery = Celery(
    "flow_forecaster",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1"),
)

# Celery configuration
celery.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Task settings
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 minutes soft limit

    # Retry settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,

    # Result settings
    result_expires=86400,  # Results expire after 24 hours

    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,

    # Beat schedule for periodic tasks
    beat_schedule={
        # Example: 'cleanup-old-data': {
        #     'task': 'tasks.cleanup_old_data',
        #     'schedule': 86400.0,  # Daily
        # },
    },
)

# Auto-discover tasks from the tasks module
celery.autodiscover_tasks(["tasks"])


def make_celery(app):
    """
    Create Celery app with Flask application context.
    """
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
