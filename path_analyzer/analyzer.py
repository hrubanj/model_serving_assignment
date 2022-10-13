"""
A collection of functions for analyzing object paths in and object store.
"""

from __future__ import annotations

import datetime
import json
import pathlib
import re
from collections import defaultdict
from typing import Any, Iterator

KEY_START = "id="

MINIMUM_MONTH_KEY = "min_month"
MAXIMUM_MONTH_KEY = "max_month"

EXAMPLES_FILENAME = "examples.txt"


def serialize_date(object_to_serialize: Any) -> str:
    """
    Serialize datetime.date to iso-format. Throw TypeError
    for all other objects.
    """
    if isinstance(object_to_serialize, datetime.date):
        return object_to_serialize.isoformat()
    raise TypeError(f"Type {type(object_to_serialize)} not serializable")


def read_examples() -> list[str]:
    """
    Read examples from a text file.
    """
    examples_path = pathlib.Path(__file__).parent / EXAMPLES_FILENAME
    with open(examples_path, "rt", encoding="utf-8") as in_file:
        return in_file.readlines()


def write_output(output_dict: dict, output_path: str) -> None:
    """
    Write dictionary to a JSON file.
    """
    with open(output_path, "wt", encoding="utf-8") as out_file:
        json.dump(output_dict, out_file, default=serialize_date)


def get_all_keys(
    input_addresses: Iterator[str], bucket: str, full_path: str
) -> Iterator[str]:
    """
    Yield all keys extracted from input_addresses that correspond
    to given bucket and full path.
    Allow only exact match in path. (If bucket / full_path is only
    a substring of object's path, it is not yielded).
    """
    object_prefix = f"{bucket}/{full_path}/"
    for address in input_addresses:
        potential_key = address.removeprefix(object_prefix)
        if address.startswith(object_prefix) and potential_key.startswith(KEY_START):
            yield potential_key


def parse_id_from_key(object_key: str) -> str:
    """
    Extract object id from object_key.
    """
    return re.search("id=(.+?)/", object_key).group(1)


def parse_month_from_key(object_key: str) -> datetime.date:
    """
    Extract month string from object_key and convert it to
    datetime.date.
    """
    month_string = re.search("month=(.+?)/", object_key).group(1)
    return datetime.datetime.strptime(month_string, "%Y-%m-%d").date()


def update_min_max(
    min_max_dictionary: dict[str, datetime.date], updating_value: datetime.date
) -> dict[str, datetime.date]:
    """
    Update minimum and maximum value in a dictionary with updating_value.
    """
    current_maximum_month = min_max_dictionary.get(
        MAXIMUM_MONTH_KEY, datetime.date(1, 1, 1)  # min python date
    )
    current_minimum_month = min_max_dictionary.get(
        MINIMUM_MONTH_KEY, datetime.date(9999, 12, 31)  # max python date
    )

    min_max_dictionary[MAXIMUM_MONTH_KEY] = max(current_maximum_month, updating_value)
    min_max_dictionary[MINIMUM_MONTH_KEY] = min(current_minimum_month, updating_value)
    return min_max_dictionary


def get_min_max_months_no_gaps(
    object_keys: Iterator[str],
) -> defaultdict[str, dict[str, datetime.date]]:
    """
    Return mappings of minimum and maximum months
    extracted from object_keys for each id in object_keys.
    """
    result = defaultdict(dict)
    for object_key in object_keys:
        key_id = parse_id_from_key(object_key)
        key_month = parse_month_from_key(object_key)
        result[key_id] = update_min_max(result[key_id], key_month)
    return result


def report_min_max_no_gaps(bucket: str, full_path: str, output_file_path: str) -> None:
    """
    Find minimum and maximum month for each object in bucket with given full_path.
    Write results to JSON file specified by output_file_path.
    """
    examples = read_examples()
    keys = get_all_keys(examples, bucket, full_path)
    min_max_no_gaps = get_min_max_months_no_gaps(keys)
    write_output(min_max_no_gaps, output_file_path)
