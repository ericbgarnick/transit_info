from unittest import mock

import typing

from mbta_info.config import Config
from mbta_info.flaskr.tools.retriever import Retriever, requests, zipfile


class ResponseStub:
    def __init__(self):
        self.content = b"content"


class ZipFileStub:
    @staticmethod
    def namelist() -> typing.List[str]:
        return ["geo_stubs.txt", "test_models.txt"]


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
        retriever.data_url, timeout=(retriever.CONNECT_TIMEOUT, retriever.READ_TIMEOUT)
    )
    assert zipfile.ZipFile.call_args[0][0].read() == response_stub.content
    assert result == unzipped


def test_retriever_fetch_zipfile_failure(monkeypatch):
    # GIVEN
    monkeypatch.setattr(
        requests, "get", mock.Mock(side_effect=requests.exceptions.ConnectionError)
    )

    # WHEN
    retriever = Retriever()
    retriever.fetch_zipfile()

    # THEN
    assert retriever.errors == [f"ConnectionError for {retriever.data_url}"]


def test_retriever_validate_zipfile_contents():
    # GIVEN
    test_zf = ZipFileStub()

    # WHEN
    retriever = Retriever(verbose=False)
    retriever.validate_zipfile_contents(test_zf)

    # THEN
    assert not retriever.missing_filenames
    assert not retriever.errors
