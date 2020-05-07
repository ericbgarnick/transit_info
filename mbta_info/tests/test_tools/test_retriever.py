from mbta_info.config import Config
from mbta_info.flaskr.tools.retriever import Retriever


def test_retriever_init():
    config = Config().config
    retriever = Retriever()
    assert retriever.data_url == config["mbta_data"]["files_url"]
    assert str(retriever.local_data_path).endswith(config["mbta_data"]["path"])
    assert retriever.errors == []
    assert retriever.missing_filenames == set()
