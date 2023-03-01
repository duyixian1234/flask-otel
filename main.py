import logging
import time

import requests
from flask import Flask
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from pymongo import MongoClient
from redis import Redis

from config import configure_logging

configure_logging()
logger = logging.getLogger()


def configure_trace(app: Flask):
    trace.set_tracer_provider(
        TracerProvider(resource=Resource.create({SERVICE_NAME: app.name}))
    )

    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name="localhost",
                agent_port=6831,
            )
        )
    )

    FlaskInstrumentor().instrument_app(app)
    RequestsInstrumentor().instrument()
    PymongoInstrumentor().instrument()
    RedisInstrumentor().instrument()


app = Flask(__name__)
configure_trace(app)


@app.get("/")
def hello():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("step-1") as span:
        span.add_event("step-1-event", {"key": "value"})
        time.sleep(0.1)
        logger.info("step 1 done.")
    with tracer.start_as_current_span("step-2"):
        with tracer.start_as_current_span("step-2-1"):
            time.sleep(0.05)
            logger.info("step 2-1 done.")
        with tracer.start_as_current_span("step-2-2"):
            time.sleep(0.05)
            logger.info("step 2-2 done.")
        logger.info("step 2 done.")
    return "Hello, World!"


@app.get("/external-services")
def external_services():
    requests.head("https://www.baidu.com")
    MongoClient().test.test.find_one()
    Redis().incr("key")
    return "OK"

@app.get("/headers")
def headers():
    return requests.get("https://httpbin.org/headers").json()

@app.get("/check-sites")
def check_sites():
    return requests.get("http://localhost:5001/api/check-sites").json()

@app.get("/check-sites-v2")
def check_sites_v2():
    return requests.get("http://localhost:5001/api/check-sites-v2").json()