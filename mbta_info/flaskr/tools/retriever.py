import zipfile
import io
import pathlib
import typing

import requests

from mbta_info.flaskr import config

DATA_PATH = pathlib.Path(
    pathlib.Path(__name__).absolute().parent, config["mbta_data"]["path"].get()
)


class Retriever:
    """Retrieve GTFS data files"""

    def __init__(self):
        self.data_url: str = config["mbta_data"]["files_url"].get()
        self.errors = []
        self.missing_filenames: typing.Set[str] = set()

    def retrieve_data(self):
        zf = self._fetch_zipfile()
        self._validate_zipfile_contents(zf)
        if not self.errors:
            zf.extractall(DATA_PATH)
        else:
            self._report_errors()

    def _fetch_zipfile(self) -> zipfile.ZipFile:
        try:
            response = requests.get(
                self.data_url, timeout=(3.1, 6.2)
            )  # (connect, read)
            compressed_data = io.BytesIO(response.content)
            return zipfile.ZipFile(compressed_data)
        except requests.exceptions.ConnectionError:
            self.errors.append(f"ConnectionError for {self.data_url}")

    def _validate_zipfile_contents(self, zf: zipfile.ZipFile):
        retrieved_filenames = set(zf.namelist())
        for filename in config["mbta_data"]["files"].get():
            if filename not in retrieved_filenames:
                self.missing_filenames.add(filename)
        if self.missing_filenames:
            self.errors.append("Missing data files")

    def _report_errors(self):
        print("BAD STUFF HAPPENED")
