import datetime
import json
import tempfile

from api.model_serving_api import SENTIMENT_KEY, SentimentValue

from .conftest import *


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
    @pytest.mark.parametrize(
        "input_text",
        [
            "a",
            "word",
            "This is sentence",
            "fnowenfe",
        ],
    )
    def test_label_sentiment_returns_valid_type(
        self, api_without_duplicates, input_text
    ):
        sentiment = api_without_duplicates._label_sentiment(input_text)
        assert isinstance(sentiment, SentimentValue)

    @pytest.mark.parametrize(
        "input_dict",
        [
            {"test": "fff"},
            {"text": "fff"},
            {"text": "fff", "language_code": "en"},
        ],
    )
    def test_get_sentiment_invalid_data(self, api_without_duplicates, input_dict):
        _, status_code = api_without_duplicates.get_sentiment(input_dict)
        assert status_code == 400

    @pytest.mark.parametrize(
        "input_dict",
        [
            {"text": "fff", "languageCode": "en"},
            {"text": 122333, "languageCode": "EN"},
            {"text": "This is something!", "languageCode": "CZ"},
        ],
    )
    def test_get_sentiment_valid(self, api_without_duplicates, input_dict):
        response, status_code = api_without_duplicates.get_sentiment(input_dict)
        assert status_code == 200
        assert isinstance(response[SENTIMENT_KEY], SentimentValue)

    @pytest.mark.parametrize(
        "input_dict",
        [
            {"text": "fafaf", "languageCode": "en", "sentiment": "positive"},
            {"sentiment": "positive"},
            {
                "text": "fafaf",
                "languageCode": "en",
                "sentiment": "weird",
                "isGoodTranslation": True,
            },
        ],
    )
    def test_save_sentiment_invalid_data(self, api_without_duplicates, input_dict):
        _, status_code = api_without_duplicates.save_sentiment(input_dict)
        assert status_code == 400

    def test_save_sentiment_duplicate(self, api_with_duplicates):
        _, status_code = api_with_duplicates.save_sentiment(
            {
                "text": "aaa",
                "languageCode": "en",
                "sentiment": "positive",
                "isGoodTranslation": True,
            }
        )
        assert status_code == 409

    @pytest.mark.parametrize(
        "input_dict",
        [
            {
                "text": "fafaf",
                "languageCode": "en",
                "sentiment": "positive",
                "isGoodTranslation": True,
            },
            {
                "text": "fafaf",
                "languageCode": "en",
                "sentiment": "positive",
                "isGoodTranslation": False,
            },
            {
                "text": "",
                "languageCode": "EN",
                "sentiment": "neutral",
                "isGoodTranslation": True,
            },
        ],
    )
    def test_save_sentiment_valid(self, api_without_duplicates, input_dict):
        _, status_code = api_without_duplicates.save_sentiment(input_dict)
        assert status_code == 201
