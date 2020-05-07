from unittest import mock

import typing

from mbta_info.config import Config
from mbta_info.flaskr.tools.retriever import Retriever, requests, zipfile


class ResponseStub:
    def __init__(self):
        self.content = b"content"


class ZipFileStub:
    def __init__(self, namelist: typing.Optional[typing.List[str]] = None):
        self._namelist = namelist or ["geo_stubs.txt", "test_models.txt"]

    def namelist(self) -> typing.List[str]:
        return self._namelist


def test_init():
    # GIVEN
    config = Config().config

    # WHEN
    retriever = Retriever()

    # THEN
    assert retriever.data_url == config["mbta_data"]["files_url"]
    assert str(retriever.local_data_path).endswith(config["mbta_data"]["path"])
    assert retriever.errors == []
    assert retriever.missing_filenames == set()


def test_fetch_zipfile_success(monkeypatch):
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


def test_fetch_zipfile_failure(monkeypatch):
    # GIVEN
    monkeypatch.setattr(
        requests, "get", mock.Mock(side_effect=requests.exceptions.ConnectionError)
    )

    # WHEN
    retriever = Retriever(verbose=False)
    retriever.fetch_zipfile()

    # THEN
    assert retriever.errors == [f"ConnectionError for {retriever.data_url}"]


def test_validate_zipfile_contents_success(capsys):
    # GIVEN
    test_zf = ZipFileStub()

    # WHEN
    retriever = Retriever()
    retriever.validate_zipfile_contents(test_zf)

    # THEN
    captured = capsys.readouterr().out.strip().split("\n")
    namelist = test_zf.namelist()
    assert f"RETRIEVED: {sorted(namelist)}" in captured
    for filename in namelist:
        assert f"CHECKING FILE: {filename}" in captured
    assert not retriever.missing_filenames
    assert not retriever.errors


def test_validate_zipfile_contents_missing_file():
    # GIVEN
    test_zf = ZipFileStub(["geo_stubs.txt", "something_else.txt"])

    # WHEN
    retriever = Retriever(verbose=False)
    retriever.validate_zipfile_contents(test_zf)

    # THEN
    assert retriever.missing_filenames == {"test_models.txt", }
    assert retriever.errors == ["Missing data files"]
