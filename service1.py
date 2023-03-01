import fastapi
import httpx
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def configure_trace(app: fastapi.FastAPI):
    trace.set_tracer_provider(
        TracerProvider(resource=Resource.create({SERVICE_NAME: app.title}))
    )

    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name="localhost",
                agent_port=6831,
            )
        )
    )

    FastAPIInstrumentor.instrument_app(app)
    HTTPXClientInstrumentor().instrument()


app = fastapi.FastAPI(title=__name__)
configure_trace(app)

def get_client():
    return httpx.AsyncClient()

@app.get("/api/check")
async def check(client: httpx.AsyncClient = fastapi.Depends(get_client)):
    await client.get("http://localhost:5004/api/log")
    resp = await client.head("https://www.baidu.com")
    return {"connected": resp.status_code == 200}
