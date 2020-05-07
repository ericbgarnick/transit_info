import zipfile
import io
import pathlib
import typing

import requests


class Retriever:
    """Retrieve GTFS data files from a remote server and save locally"""

    CONNECT_TIMEOUT = 3.1
    READ_TIMEOUT = 6.2

    config: typing.ClassVar[typing.Dict]

    def __init__(self, verbose=True):
        self.load_config()

        self.verbose = verbose
        self.data_url: str = self.config["mbta_data"]["files_url"]
        self.local_data_path = pathlib.Path(
            pathlib.Path(__name__).absolute().parent, self.config["mbta_data"]["path"],
        )
        self.errors = []
        self.missing_filenames: typing.Set[str] = set()

    def retrieve_data(self):
        zf = self.fetch_zipfile()
        self.validate_zipfile_contents(zf)
        if not self.errors:
            self.extract_zipfile_contents(zf)
        else:
            self.report_errors()

    def load_config(self):
        # FLASK_ENV at runtime may be different from load time
        from mbta_info.config import Config

        self.config = Config().config

    def fetch_zipfile(self) -> zipfile.ZipFile:
        try:
            if self.verbose:
                print("MAKING REQUEST TO:", self.data_url)
            response = requests.get(
                self.data_url, timeout=(self.CONNECT_TIMEOUT, self.READ_TIMEOUT)
            )
            compressed_data = io.BytesIO(response.content)
            return zipfile.ZipFile(compressed_data)
        except requests.exceptions.ConnectionError:
            self.errors.append(f"ConnectionError for {self.data_url}")

    def validate_zipfile_contents(self, zf: zipfile.ZipFile):
        retrieved_filenames = set(zf.namelist())
        if self.verbose:
            print("RETRIEVED:", retrieved_filenames)
        for filename in self.config["mbta_data"]["files"].values():
            if self.verbose:
                print("CHECKING FILE:", filename)
            if filename not in retrieved_filenames:
                self.missing_filenames.add(filename)
        if self.missing_filenames:
            self.errors.append("Missing data files")

    def extract_zipfile_contents(self, zf: zipfile.ZipFile):
        zf.extractall(self.local_data_path)

    def report_errors(self):
        print("BAD STUFF HAPPENED")


if __name__ == "__main__":
    r = Retriever()
    r.retrieve_data()
