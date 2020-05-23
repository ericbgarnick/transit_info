import pytest

from flaskr.tools import utils


@pytest.mark.parametrize(
    "file_name,model_name", [("abc", "Abc"), ("abc_xyz", "AbcXyz")]
)
def test_create_model_name(file_name, model_name):
    assert utils.model_name_from_table_name(file_name) == model_name
