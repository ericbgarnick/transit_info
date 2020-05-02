import os

from mbta_info.flaskr import create_app

FLASK_ENV = os.getenv("FLASK_ENV", "dev")
print("FLASK ENV:", FLASK_ENV)
app = create_app(FLASK_ENV)


