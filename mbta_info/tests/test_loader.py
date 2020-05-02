from unittest import mock

import pytest
from flask_sqlalchemy import Model
from sqlalchemy.testing import db

from mbta_info.flaskr.tools.loader import Loader


class DbStub:
    pass


class ModelStub(Model):
    primary = db.Column(db.Int)


@pytest.mark.parametrize("batch_size_to_set, batch_size_expected", [([], 100000), ([10], 10)])
def test_loader_init(batch_size_to_set, batch_size_expected):
    """Assert Loader calls db.create_all() and sets _max_batch_size"""
    db = DbStub()
    db.create_all = mock.Mock()
    loader_args = [db] + batch_size_to_set

    loader = Loader(*loader_args)

    db.create_all.assert_called_once()
    assert loader._max_batch_size == batch_size_expected
