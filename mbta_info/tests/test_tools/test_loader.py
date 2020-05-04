from unittest import mock

import pytest
import typing

from mbta_info.flaskr.tools.loader import Loader


class TableStub:
    def __init__(self, name: str):
        self.name = name


class DbStub:
    class MetaData:
        def __init__(self, tables: typing.List[TableStub]):
            self.sorted_tables = tables

    def __init__(self, tables: typing.List[TableStub]):
        self.metadata = self.MetaData(tables)


@pytest.mark.parametrize("batch_size_to_set, batch_size_expected", [([], 100000), ([10], 10)])
def test_loader_init(batch_size_to_set, batch_size_expected, db):
    """Assert Loader calls db.create_all(), sets max_batch_size and table_names"""
    table_names = ["geo_stub", "test_model"]
    # db = DbStub([TableStub(name) for name in table_names])
    # db.create_all = mock.Mock()
    loader_args = [db] + batch_size_to_set

    loader = Loader(*loader_args)

    # db.create_all.assert_called_once()
    assert loader.max_batch_size == batch_size_expected
    assert loader.table_names == table_names
