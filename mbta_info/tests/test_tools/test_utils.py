import pytest

from mbta_info.flaskr.tools.utils import create_model_name


@pytest.mark.parametrize(
    'file_name,model_name',
    [
        ('abc.txt', 'Abc'),
        ('abcs.txt', 'Abc'),
        ('abc_xyz.txt', 'AbcXyz')
    ]
)
def test_create_model_name(file_name, model_name):
    assert create_model_name(file_name) == model_name
