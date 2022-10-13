## Setup environment

All code should be compatible with Python >=3.9.

Use either virtual environment:
```bash
make initialize-venv
```
Or docker (if you do not have compatible python version):
```bash
docker run -it --rm  -p "5000:5000" -v "$(pwd):/tmp" python:3.10-slim-buster /bin/sh
apt-get update && apt-get install make && cd tmp
```

Install requirements:

```bash
make install-requirements
```

## Run tests

Run all tests via:

```bash
make run-tests
```

Run specific test file via:

```bash
python3 -m pytest tests/<directory_name>
```

## Run Path Analyzer
Run analyzer function that does not account for gaps between months.
(Note that gaps can still be present but this function just returns a minimum and maximum)

Example:
```python
from path_analyzer.analyzer import report_min_max_no_gaps


report_min_max_no_gaps(
    "s3://my-bucket", # bucket
    "xxx/yyy/zzz/def", # full path
    "/Users/jiri/PycharmProjects/model_serving_assignment/data/min_max_no_gaps.json", # output file
)
```

## Run Model Serving API

Set environmental variable for directory where data gets saved.
For example:

```bash
 export DATA_DIRECTORY="data/"
```

```bash
make run-api
```

The API is exposed at `http://localhost:5000`.

## Endpoints

All POST requests must be in JSON format.

### GET "/"
Status code: 200

Returns application name and version.

### GET "/status"
Status code: 200

Returns metrics that can be scraped by Prometheus.

### GET "/metrics"
Status code: 200

Returns metrics that can be scraped by Prometheus.

### GET "/status"
Status code: 200

Returns "OK" if the application is running.

### POST "/label_sentiment"

#### Request format:

```json
{
  "text": "string",
  "languageCode": "string"
}
```

Example:

```json
{
  "text": "This task is awesome. Nope, just kidding.",
  "languageCode": "en"
}
```

#### Successful response:

Status code: 200

```json
{
  "sentiment": {
    "schema": {
      "type": "string",
      "enum": [
        "neutral",
        "positive",
        "negative"
      ]
    }
  }
}
```

Example:

```json
{
  "sentiments": "positive"
}
```

#### Errors:

**Invalid request format:**

Status code: 400

If request is not a valid JSON, status code 400 is returned.


**Invalid request content:**

Status code: 400

If required fields are not present or cannot be coerced to string,
returns error description with status code 400.

Example:

```json
{
  "errors": [
    {
      "loc": [
        "languageCode"
      ],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### POST "/save_sentiment"

#### Request format:

```json
{
  "text": "string",
  "languageCode": "string",
  "isGoodTranslation": "boolean",
  "sentiment": {
    "schema": {
      "type": "string",
      "enum": [
        "neutral",
        "positive",
        "negative"
      ]
    }
  }
}
```

Example:

```json
{
  "text": "Hello",
  "languageCode": "EN",
  "isGoodTranslation": true,
  "sentiment": "positive"
}
```

#### Successful response:

Status code: 201

```json
{}
```

#### Errors:

**Invalid request format:**

Status code: 400

If request is not a valid JSON, status code 400 is returned.

**Invalid request content:**

Status code: 400

If required fields are not present or cannot be coerced to correct data types,
returns error description with status code 400.

Example:

```json
{
  "errors": [
    {
      "loc": [
        "languageCode"
      ],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Duplicate item:**

Status code: 409

Item with the same content is already saved.

Example:

```json
{
  "errors": [
    [
      "item already exists"
    ]
  ]
}
```