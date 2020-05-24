broker_url = 'amqp://guest:guest@rabbit:5672'
result_backend = 'rpc://guest:guest@rabbit:5672'

imports = ["flaskr.mbta_celery.tasks"]

timezone = "UTC"

worker_send_task_events = True

beat_schedule = {
    # "do-stuff": {
    #     "task": "flaskr.mbta_celery.tasks.add",
    #     "schedule": 20.0,  # seconds
    #     "args": (2, 3)
    # },
    "retrieve-mbta-data": {
        "task": "flaskr.mbta_celery.tasks.run_retrieve_data",
        "schedule": 60.0,  # seconds
    },
}
