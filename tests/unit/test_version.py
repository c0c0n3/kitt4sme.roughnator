from fipy import pyproject_version

from roughnator import __version__, pyproject_file
from roughnator.main import read_root, read_version


def test_project_version_same_as_lib():
    project_version = pyproject_version(pyproject_file())
    assert __version__ == project_version


def test_lib_version_same_as_service():
    assert read_root() == read_version()
    svc_version = read_version()['roughnator']
    assert __version__ == svc_version
