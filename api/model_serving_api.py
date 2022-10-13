"""
Module with API for getting and storing sentiment labelling results.
"""

from __future__ import annotations

import logging
import random
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from common.daos.file_based_dao import FileBasedDAO
from common.exceptions import DuplicateItemException

TEXT_KEY = "text"
LANGUAGE_CODE_KEY = "languageCode"
SENTIMENT_KEY = "sentiment"
TRANSLATION_QUALITY_KEY = "isGoodTranslation"

ERRORS_KEY = "errors"


class SentimentValue(str, Enum):
    """
    Allowed values for sentiment label.
    """

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class SentimentRatingItem(BaseModel):
    """
    A class for parsing sentiment labelling request.
    """

    text: str
    language_code: str = Field(alias=LANGUAGE_CODE_KEY)


class SentimentSavingItem(SentimentRatingItem):
    """
    A class for parsing sentiment saving request.
    """

    sentiment: SentimentValue
    is_good_translation: bool = Field(alias="isGoodTranslation")


class API:
    """
    API for handling sentiment labelling and saving its results.
    Independent of framework (can be bound e.g. to Flask app).
    """

    def __init__(self, models_dao: FileBasedDAO, logger: logging.Logger) -> None:
        self.models_dao = models_dao
        self.logger = logger

    @staticmethod
    def _label_sentiment(
        input_text: str,  # pylint: disable=unused-argument
    ) -> SentimentValue:
        """
        Take input text and label its sentiment.
        Proper implementation would take the text into
        account. This one just assigns sentiment randomly.
        """
        return random.choice(
            [SentimentValue.POSITIVE, SentimentValue.NEUTRAL, SentimentValue.NEGATIVE]
        )

    def get_sentiment(
        self, request_data: dict[str, Any]
    ) -> tuple[dict[str, str | list[str]], int]:
        """
        Process text from request_data dictionary and return
        a dictionary with labelled sentiment and status code.
        Return errors if request does not include required fields
        or if the fields cannot be parsed to appropriate data types.
        """
        try:
            rating_input = SentimentRatingItem.parse_obj(request_data)
        except ValidationError as error:
            self.logger.warning(
                "Invalid input for sentiment labelling. Received: %s", request_data
            )
            return {ERRORS_KEY: error.errors()}, 400
        return {SENTIMENT_KEY: self._label_sentiment(rating_input.text)}, 200

    def save_sentiment(
        self, request_data: dict[str, Any]
    ) -> tuple[dict[str, str | list[str]], int]:
        """
        Proces sentiment labeling result from request_data dictionary
        and save it.
        Return errors if request does not include required fields
        or if the fields cannot be parsed to appropriate data types,
        or if the requested item is already saved.
        """
        try:
            saving_input = SentimentSavingItem.parse_obj(request_data)
        except ValidationError as error:
            self.logger.warning(
                "Invalid input for sentiment saving. Received: %s", request_data
            )
            return {ERRORS_KEY: error.errors()}, 400
        try:
            self.models_dao.save_scoring_result(saving_input.dict(by_alias=True))
        except DuplicateItemException:
            return {ERRORS_KEY: ["item already exists"]}, 409
        return {}, 201
