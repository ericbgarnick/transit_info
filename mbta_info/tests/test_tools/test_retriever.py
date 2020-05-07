from unittest import mock

from mbta_info.config import Config
from mbta_info.flaskr.tools.retriever import Retriever, requests, zipfile


class ResponseStub:
    def __init__(self):
        self.content = b"content"


def test_retriever_init():
    # GIVEN
    config = Config().config

    # WHEN
    retriever = Retriever()

    # THEN
    assert retriever.data_url == config["mbta_data"]["files_url"]
    assert str(retriever.local_data_path).endswith(config["mbta_data"]["path"])
    assert retriever.errors == []
    assert retriever.missing_filenames == set()


def test_retriever_fetch_zipfile_success(monkeypatch):
    # GIVEN
    response_stub = ResponseStub()
    unzipped = "unzipped"
    monkeypatch.setattr(requests, "get", mock.Mock(return_value=response_stub))
    monkeypatch.setattr(zipfile, "ZipFile", mock.Mock(return_value=unzipped))

    # WHEN
    retriever = Retriever()
    result = retriever.fetch_zipfile()

    # THEN
    requests.get.assert_called_with(
        retriever.data_url,
        timeout=(retriever.CONNECT_TIMEOUT, retriever.READ_TIMEOUT)
    )
    assert zipfile.ZipFile.call_args[0][0].read() == response_stub.content
    assert result == unzipped


def test_retriever_fetch_zipfile_failure(monkeypatch):
    # GIVEN
    monkeypatch.setattr(requests, "get", mock.Mock(side_effect=requests.exceptions.ConnectionError))

    # WHEN
    retriever = Retriever()
    retriever.fetch_zipfile()

    # THEN
    assert retriever.errors == [f"ConnectionError for {retriever.data_url}"]
