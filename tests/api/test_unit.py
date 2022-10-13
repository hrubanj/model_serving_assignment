import datetime
import json

import pytest

from .conftest import *
from common.exceptions import DuplicateItemException


class TestFileBasedDAO:
    @pytest.mark.parametrize(
        "input_dictionary,expected_hash",
        [
            ({"a": 1, "b": "ffff"}, "ba3a08a31c2b7a7ca088d219497fe0d8"),
            (
                {"abrakadabra": "fafafa", "b": "ffff"},
                "5662cffebe8de5d80871313d744a8364",
            ),
        ],
    )
    def test_hash_dictionary_contents(
        self, file_based_dao, input_dictionary, expected_hash
    ):
        actual_hash = file_based_dao._hash_dictionary_contents(input_dictionary)
        assert actual_hash == expected_hash

    @pytest.mark.parametrize(
        "input_dictionary", [{1: set(), "444": datetime.datetime.now()}]
    )
    def test_hash_dictionary_contents_non_serializable(
        self, file_based_dao, input_dictionary
    ):
        with pytest.raises(TypeError):
            file_based_dao._hash_dictionary_contents(input_dictionary)

    def test_save_scoring_result_valid(self):
        input_dict = {"ggg": 111}

        with tempfile.TemporaryDirectory() as tmp_dir:
            dao = FileBasedDAO(tmp_dir)
            filepath = dao.save_scoring_result(input_dict)

            with open(filepath, "rt") as in_file:
                written_dict = json.load(in_file)
            assert input_dict == written_dict

    def test_save_scoring_result_duplicate(self):
        input_dict = {"ggg": 111}

        with tempfile.TemporaryDirectory() as tmp_dir:
            dao = FileBasedDAO(tmp_dir)
            dao.save_scoring_result(input_dict)
            with pytest.raises(DuplicateItemException):
                dao.save_scoring_result(input_dict)


class TestModelServingAPI:
    def test_fail(self):
        assert False
