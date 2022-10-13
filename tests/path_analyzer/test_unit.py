import datetime
import time

import pytest

from path_analyzer.analyzer import (
    MAXIMUM_MONTH_KEY,
    MINIMUM_MONTH_KEY,
    get_all_keys,
    get_min_max_months_no_gaps,
    parse_id_from_key,
    parse_month_from_key,
    serialize_date,
    update_min_max,
)


@pytest.mark.parametrize(
    "date,expected_serialized_date",
    [
        (datetime.date(9999, 12, 31), "9999-12-31"),
        (datetime.date(2000, 12, 31), "2000-12-31"),
        (datetime.date(2000, 1, 31), "2000-01-31"),
    ],
)
def test_serialize_date_valid(date, expected_serialized_date):
    serialized_date = serialize_date(date)
    assert serialized_date == expected_serialized_date


@pytest.mark.parametrize("object_to_serialize", [[], time.time(), "2000-01-31"])
def test_serialize_date_invalid(object_to_serialize):
    with pytest.raises(TypeError):
        serialize_date(object_to_serialize)


@pytest.mark.parametrize(
    "input_paths,expected_keys",
    [
        (
            [
                "hdfs://my-bucket/aaa/bbb/id=333/month=2019-11-01/2019-12-19T10:35:18.818Z.gz",
                "s3://my-bucket/aaa/bbb/id=333/month=2019-11-01/2019-12-19T10:35:18.818Z.gz",
                "hdfs://my-bucket/aaa/bbb/ccc/id=333/month=2019-11-01/2019-12-19T10:35:18.818Z.gz",
                "hdfs://my-bucket/aaa/id=333/month=2019-11-01/2019-12-19T10:35:18.818Z.gz",
                "hdfs://my-bucket/aaa/bbb/id=555/month=2019-11-01/2019-12-19T10:35:18.818Z.gz",
            ],
            (
                [
                    "id=333/month=2019-11-01/2019-12-19T10:35:18.818Z.gz",
                    "id=555/month=2019-11-01/2019-12-19T10:35:18.818Z.gz",
                ]
            ),
        )
    ],
)
def test_get_all_keys(input_paths, expected_keys):
    found_keys = list(get_all_keys(input_paths, "hdfs://my-bucket", "aaa/bbb"))
    assert sorted(found_keys) == sorted(expected_keys)


@pytest.mark.parametrize(
    "key,expected_id",
    [
        ("id=555/month=2019-11-01/2019-12-19T10:35:18.818Z.gz", "555"),
        ("id=333/month=2019-11-01/2019-12-19T10:35:18.818Z.gz", "333"),
        ("month=2019-11-01/id=999/", "999"),
    ],
)
def test_parse_id_from_key(key, expected_id):
    parsed_id = parse_id_from_key(key)
    assert parsed_id == expected_id


@pytest.mark.parametrize(
    "key,expected_month",
    [
        (
            "id=555/month=2019-11-01/2019-12-19T10:35:18.818Z.gz",
            datetime.date(2019, 11, 1),
        ),
        (
            "id=333/month=2009-09-01/2019-12-19T10:35:18.818Z.gz",
            datetime.date(2009, 9, 1),
        ),
    ],
)
def test_parse_month_from_key(key, expected_month):
    parsed_month = parse_month_from_key(key)
    assert parsed_month == expected_month


@pytest.mark.parametrize(
    "original_dict,updating_value,expected_new_dict",
    [
        (
            {
                MAXIMUM_MONTH_KEY: datetime.date(1, 1, 1),
                MINIMUM_MONTH_KEY: datetime.date(9999, 12, 31),
            },
            datetime.date(2000, 1, 1),
            {
                MAXIMUM_MONTH_KEY: datetime.date(2000, 1, 1),
                MINIMUM_MONTH_KEY: datetime.date(2000, 1, 1),
            },
        ),
        (
            {
                MAXIMUM_MONTH_KEY: datetime.date(2001, 1, 1),
                MINIMUM_MONTH_KEY: datetime.date(1999, 12, 31),
            },
            datetime.date(2000, 1, 1),
            {
                MAXIMUM_MONTH_KEY: datetime.date(2001, 1, 1),
                MINIMUM_MONTH_KEY: datetime.date(1999, 12, 31),
            },
        ),
        (
            {
                MAXIMUM_MONTH_KEY: datetime.date(2001, 1, 1),
                MINIMUM_MONTH_KEY: datetime.date(1999, 12, 31),
            },
            datetime.date(2002, 1, 1),
            {
                MAXIMUM_MONTH_KEY: datetime.date(2002, 1, 1),
                MINIMUM_MONTH_KEY: datetime.date(1999, 12, 31),
            },
        ),
        (
            {
                MAXIMUM_MONTH_KEY: datetime.date(2001, 1, 1),
                MINIMUM_MONTH_KEY: datetime.date(1999, 12, 31),
            },
            datetime.date(1998, 1, 1),
            {
                MAXIMUM_MONTH_KEY: datetime.date(2001, 1, 1),
                MINIMUM_MONTH_KEY: datetime.date(1998, 1, 1),
            },
        ),
    ],
)
def test_update_min_max(original_dict, updating_value, expected_new_dict):
    updated_dict = update_min_max(original_dict, updating_value)
    assert updated_dict == expected_new_dict


@pytest.mark.parametrize(
    "object_keys,expected_result",
    [
        (
            [
                "id=333/month=2019-11-01/2019-12-19T10:35:18.818Z.gz",
                "id=333/month=2021-11-01/2019-12-19T10:35:18.818Z.gz",
                "id=999/month=2019-11-01/2019-12-19T10:35:18.818Z.gz",
                "id=555555/month=2020-11-01/2019-12-19T10:35:18.818Z.gz",
            ],
            {
                "333": {
                    MINIMUM_MONTH_KEY: datetime.date(2019, 11, 1),
                    MAXIMUM_MONTH_KEY: datetime.date(2021, 11, 1),
                },
                "999": {
                    MINIMUM_MONTH_KEY: datetime.date(2019, 11, 1),
                    MAXIMUM_MONTH_KEY: datetime.date(2019, 11, 1),
                },
                "555555": {
                    MINIMUM_MONTH_KEY: datetime.date(2020, 11, 1),
                    MAXIMUM_MONTH_KEY: datetime.date(2020, 11, 1),
                },
            },
        )
    ],
)
def test_get_min_max_no_gaps(object_keys, expected_result):
    result = get_min_max_months_no_gaps(object_keys)
    assert result == expected_result
