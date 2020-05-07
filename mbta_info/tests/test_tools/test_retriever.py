import io
from unittest import mock

from mbta_info.config import Config
from mbta_info.flaskr.tools.retriever import Retriever, requests, zipfile


class ResponseStub:
    def __init__(self):
        self.content = b"content"


def test_retriever_init():
    config = Config().config
    retriever = Retriever()
    assert retriever.data_url == config["mbta_data"]["files_url"]
    assert str(retriever.local_data_path).endswith(config["mbta_data"]["path"])
    assert retriever.errors == []
    assert retriever.missing_filenames == set()


def test_retriever_fetch_zipfile_success(monkeypatch):
    response_stub = ResponseStub()
    unzipped = "unzipped"
    monkeypatch.setattr(requests, "get", mock.Mock(return_value=response_stub))
    monkeypatch.setattr(zipfile, "ZipFile", mock.Mock(return_value=unzipped))

    retriever = Retriever()
    result = retriever.fetch_zipfile()

    requests.get.assert_called_with(
        retriever.data_url,
        timeout=(retriever.CONNECT_TIMEOUT, retriever.READ_TIMEOUT)
    )
    assert zipfile.ZipFile.call_args[0][0].read() == response_stub.content
    assert result == unzipped
