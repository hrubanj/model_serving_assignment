from __future__ import annotations

import hashlib
import json
import os
import pathlib

from common.exceptions import DuplicateItemException


class FileBasedDAO:
    def __init__(self, data_directory: str) -> None:
        self.directory_path = pathlib.Path(data_directory)
        os.makedirs(self.directory_path, exist_ok=True)

    @staticmethod
    def _hash_dictionary_contents(
        input_dictionary: dict[str, str | float | bool]
    ) -> str:
        data_string = json.dumps(input_dictionary, sort_keys=True)
        return hashlib.md5(data_string.encode("utf=8")).hexdigest()

    def save_scoring_result(
        self, input_dictionary: dict[str, str | float | bool]
    ) -> None:
        filepath = (
            self.directory_path
            / f"{self._hash_dictionary_contents(input_dictionary)}.json"
        )
        try:
            filepath.touch(exist_ok=False)  # avoid race condition
            # filepath.touch -> if the file does not exist, 'claim' the name
        except FileExistsError as e:
            raise DuplicateItemException from e
        with open(filepath, "wt") as out_file:
            json.dump(input_dictionary, out_file)
