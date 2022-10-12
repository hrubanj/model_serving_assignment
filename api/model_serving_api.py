from __future__ import annotations

import logging
import random

from typing import Any

from pydantic import BaseModel, ValidationError, Field

from common.daos.file_based_dao import FileBasedDAO
from common.exceptions import DuplicateItemException

TEXT_KEY = "text"
LANGUAGE_CODE_KEY = "languageCode"
SENTIMENT_KEY = "sentiment"
TRANSLATION_QUALITY_KEY = "isGoodTranslation"

ERRORS_KEY = "errors"


class SentimentRatingItem(BaseModel):
    text: str
    language_code: str = Field(alias=LANGUAGE_CODE_KEY)


class SentimentSavingItem(SentimentRatingItem):
    sentiment: str
    is_good_translation: bool = Field(alias="isGoodTranslation")


class API:
    def __init__(self, models_dao: FileBasedDAO, logger: logging.Logger) -> None:
        self.models_dao = models_dao
        self.logger = logger

    @staticmethod
    def _label_sentiment(input_text: str) -> str:
        """
        Take input text and label its sentiment.
        Proper implementation would take the text into
        account. This one just assigns sentiment randomly.
        """
        return random.choice(["positive", "neutral", "negative"])

    def get_sentiment(
        self, request_data: dict[str, Any]
    ) -> tuple[dict[str, str | list[str]], int]:
        try:
            rating_input = SentimentRatingItem.parse_obj(request_data)
        except ValidationError as e:
            self.logger.warning(
                "Invalid input for sentiment labelling. Received: %s", request_data
            )
            return {ERRORS_KEY: e.errors()}, 400
        return {SENTIMENT_KEY: self._label_sentiment(rating_input.text)}, 200

    def save_sentiment(
        self, request_data: dict[str, Any]
    ) -> tuple[dict[str, str | list[str]], int]:
        try:
            saving_input = SentimentSavingItem.parse_obj(request_data)
        except ValidationError as e:
            self.logger.warning(
                "Invalid input for sentiment saving. Received: %s", request_data
            )
            return {ERRORS_KEY: e.errors()}, 400
        try:
            self.models_dao.save_scoring_result(saving_input.dict(by_alias=True))
        except DuplicateItemException:
            return {ERRORS_KEY: ["item already exists"]}, 409
        return {}, 201
