from datetime import datetime

from flaskr.mbta_celery.app import celery_app


@celery_app.task
def add(x, y):
    with open(f"celery_test_{datetime.now()}", "w") as f_out:
        f_out.write(str(x + y))
