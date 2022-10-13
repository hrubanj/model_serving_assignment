.PHONY:*

initialize-venv:
	python3 -m venv venv
	source venv/bin/activate

install-requirements:
	pip3 install -r requirements.txt

run-tests:
	python3 -m pytest tests/

run-api:
	gunicorn --config "webserver/gunicorn_config.py" --log-config "webserver/gunicorn_logging.conf" "api.flask_app:create_app_from_environment()"

format:
	isort . --profile "black"
	black .

lint:
	pylint --recursive=y . --ignore-patterns=venv,gunicorn.* --extension-pkg-whitelist='pydantic'


