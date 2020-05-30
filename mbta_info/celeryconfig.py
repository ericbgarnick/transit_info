broker_url = 'amqp://guest:guest@rabbit:5672'
result_backend = 'rpc://guest:guest@rabbit:5672'

imports = ["flaskr.mbta_celery.tasks"]

timezone = "UTC"

worker_send_task_events = True

beat_schedule = {
    "update-mbta-data": {
        "task": "flaskr.mbta_celery.tasks.run_update_mbta_data",
        "schedule": 60.0 * 60 * 24,  # seconds (once every 24 hours)
    },
}
