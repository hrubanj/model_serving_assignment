"""
Module that binds API to Flask app, defines its endpoints, and
adds logging and metrics for endpoint calls.
"""

from __future__ import annotations

import logging
import os
import time

import flask
from prometheus_client import Counter, Gauge, generate_latest

from api.model_serving_api import API
from common.constants import APPLICATION_NAME
from common.daos.file_based_dao import FileBasedDAO
from common.log import setup_logging

APPLICATION_VERSION = "1.0"


def create_app(config_dictionary: dict[str, str] | None = None) -> flask.Flask:
    """
    Setup API and bind it to Flask app, define metrics, and logging.
    """
    up_metric = Gauge("up", "1 if API is running, 0 otherwise.")
    up_metric.set(0)

    endpoint_call_count_metric = Counter(
        "endpoint_calls",
        "How many times the endpoint was called.",
        labelnames=["endpoint", "pid", "status_code"],
    )
    endpoint_duration_metric = Gauge(
        "endpoint_duration_seconds",
        "How long the endpoint took to respond.",
        labelnames=["endpoint", "pid", "status_code"],
    )

    models_dao = FileBasedDAO(data_directory=config_dictionary["DATA_DIRECTORY"])
    logger = setup_logging(logging.INFO)

    api_worker = API(models_dao, logger)
    app = flask.Flask(APPLICATION_NAME)
    app.api_worker = api_worker

    @app.route("/")
    def index() -> tuple[dict[str, str], int]:
        return {
            "application_name": APPLICATION_NAME,
            "version": APPLICATION_VERSION,
        }, 200

    @app.route("/metrics")
    def show_metrics() -> bytes:
        return generate_latest()

    @app.route("/status")
    def status():
        up_metric.set(1)
        return "OK", 200

    @app.route("/label_sentiment", methods=["POST"])
    def label_sentiment() -> tuple[dict[str, str], int]:
        request_data = flask.request.get_json()
        return app.api_worker.get_sentiment(request_data)

    @app.route("/save_sentiment", methods=["POST"])
    def save_sentiment() -> tuple[dict[str, str], int]:
        request_data = flask.request.get_json()
        return app.api_worker.save_sentiment(request_data)

    @app.before_request
    def before_request() -> None:
        flask.request.time_start = time.monotonic()

    @app.after_request
    def log_after_request(response: flask.Response) -> flask.Response:
        # log only if client is not localhost (prevent logging consul proxy checks)
        # disable logging kubernetes probes
        time_start = getattr(flask.request, "time_start", None)
        duration = time.monotonic() - time_start if time_start is not None else None
        common_info = {
            "request_method": flask.request.method,
            "request_url": flask.request.url,
            "request_path": flask.request.path,
            "request_full_path": flask.request.full_path,
            "request_endpoint": flask.request.endpoint,
            "response_status": response.status,
            "response_status_code": response.status_code,
            "response_duration_seconds": duration,
        }
        app.api_worker.logger.info("Request", extra=common_info)

        if duration is not None:
            endpoint = getattr(flask.request, "path", None)
            endpoint_labels = {
                "endpoint": endpoint,
                "pid": os.getpid(),
                "status_code": response.status_code,
            }
            endpoint_duration_metric.labels(**endpoint_labels).set(duration)
            endpoint_call_count_metric.labels(**endpoint_labels).inc()
        return response

    return app


def create_app_from_environment() -> flask.Flask:
    """
    Setup API and bind it to Flask app, define metrics, and logging.
    Use configuration taken from the environment.
    """
    return create_app(os.environ.copy())
