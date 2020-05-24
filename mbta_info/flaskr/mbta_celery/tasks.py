from datetime import datetime

from flaskr.mbta_celery.app import celery_app
from flaskr.tools.retriever import Retriever


@celery_app.task
def add(x, y):
    with open(f"celery_test_{datetime.now()}", "w") as f_out:
        f_out.write(str(x + y))


@celery_app.task
def run_retrieve_data():
    retriever = Retriever()
    retriever.retrieve_data()
