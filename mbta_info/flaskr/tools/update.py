from flaskr.database import db
from flaskr.tools.loader import Loader
from flaskr.tools.retriever import Retriever


def update_mbta_data():
    """Pull the latest data from MBTA and update the database"""
    if not all(table.exists(db.get_engine()) for table in db.metadata.tables.values()):
        retriever = Retriever()
        retriever.retrieve_data()
        loader = Loader(db)
        loader.load_data()
