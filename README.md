## Setup environment

Create virtual environment and activate it:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install requirements:

```bash
pip3 install -r requirements.txt
```

## Run tests

Run all tests via:

```bash
python3 -m pytest tests/
```

Run specific test file via:

```bash
python3 -m pytest tests/<directory_name>
```

## Run API

Set environmental variable for directory where data gets saved.
For example:

```bash
 export DATA_DIRECTORY="data/"
```

```bash
gunicorn --config "webserver/gunicorn_config.py" --log-config "webserver/gunicorn_logging.conf" "api.flask_app:create_app_from_environment()"
```

The API is exposed at `http://localhost:5000`.

## Endpoints

All requests must be in JSON format.

### 1. POST "/label_sentiment"

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

**Invalid request:**

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

### 2. POST "/save_sentiment"

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

**Invalid request:**

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