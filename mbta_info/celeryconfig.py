broker_url = 'pyamqp://'
result_backend = 'rpc://'

imports = ["mbta_info.flaskr.celery.tasks"]

timezone = "UTC"

worker_send_task_events = True

beat_schedule = {
    "do-stuff": {
        "task": "mbta_info.flaskr.celery.tasks.add",
        "schedule": 20.0,  # seconds
        "args": (2, 3)
    }
}
