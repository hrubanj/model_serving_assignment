import tempfile

import pytest

from common.daos.file_based_dao import FileBasedDAO


@pytest.fixture(scope="function")
def file_based_dao():
    return FileBasedDAO("dummy")