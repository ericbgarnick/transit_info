from celery.app import Celery

import celeryconfig


celery_app = Celery(
    __name__,
)

celery_app.config_from_object(celeryconfig)
