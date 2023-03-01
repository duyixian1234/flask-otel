import asyncio

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

@app.get("/api/check-sites")
async def check_sites(client: httpx.AsyncClient = fastapi.Depends(get_client)):
    baidu = (await client.get("http://localhost:5002/api/check")).json()['connected']
    qq = (await client.get("http://localhost:5003/api/check")).json()['connected']
    return {"baidu": baidu, "qq": qq}

@app.get("/api/check-sites-v2")
async def check_sites_v2(client: httpx.AsyncClient = fastapi.Depends(get_client)):
    baidu , qq = await asyncio.gather(check("baidu",client),check("qq",client))
    return {"baidu": baidu, "qq": qq}

async def check(site:str,client: httpx.AsyncClient):
    match site:
        case "baidu":
            return (await client.get("http://localhost:5002/api/check")).json()['connected']
        case "qq":
            return (await client.get("http://localhost:5003/api/check")).json()['connected']
        case _:
            return False