from unittest.mock import MagicMock

import pytest

from api.model_serving_api import API
from common.daos.file_based_dao import FileBasedDAO
from common.exceptions import DuplicateItemException


@pytest.fixture(scope="function")
def file_based_dao():
    return FileBasedDAO("dummy")


class DummyDAOSaveNoDuplicate:
    def save_scoring_result(self, data) -> str:
        return "OK"


class DummyDAOSaveDuplicateError:
    def save_scoring_result(self, data) -> None:
        raise DuplicateItemException()


@pytest.fixture(scope="function")
def api_without_duplicates():
    return API(DummyDAOSaveNoDuplicate(), MagicMock())


@pytest.fixture(scope="function")
def api_with_duplicates():
    return API(DummyDAOSaveDuplicateError(), MagicMock())
