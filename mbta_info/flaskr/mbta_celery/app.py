import os

from celery.app import Celery


celery_app = Celery(
    __name__,
    include=("flaskr.mbta_celery.tasks",),
)

celery_app.conf.beat_schedule = {
    "add_for_file": {
        "task": "flaskr.mbta_celery.tasks.add_for_file",
        "schedule": float(os.environ["TASK_SCHEDULE"]),
    }
}
