import zipfile
import io
from typing import Set

import requests

from mbta_info.flaskr import app


class Retriever:
    """Retrieve GTFS data files"""
    def __init__(self):
        self.data_url: str = app.config['mbta_data']['files_url'].get()
        self.retrieved_filenames: Set[str] = set()
        self.errors = []
        self.missing_filenames: Set[str] = set()

    def retrieve_data(self):
        zf = self._fetch_zipfile()
        self.retrieved_filenames = set(zf.namelist())
        self._validate_zipfile_contents()
        if not self.errors:
            self._save_files()
        else:
            self._report_errors()

    def _fetch_zipfile(self) -> zipfile.ZipFile:
        try:
            response = requests.get(self.data_url, timeout=30)
            compressed_data = io.BytesIO(response.content)
            return zipfile.ZipFile(compressed_data)
        except requests.exceptions.ConnectionError:
            self.errors.append(f"ConnectionError for {self.data_url}")

    def _validate_zipfile_contents(self):
        for filename in app.config['mbta_data']['files']:
            if filename not in self.retrieved_filenames:
                self.missing_filenames.add(filename)
        if self.missing_filenames:
            self.errors.append("Missing data files")

    def _save_files(self):
        pass

    def _report_errors(self):
        pass
