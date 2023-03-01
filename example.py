from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (ConsoleSpanExporter,
                                            SimpleSpanProcessor)

trace.set_tracer_provider(
        TracerProvider(resource=Resource.create({SERVICE_NAME: 'example'}))
    )
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(ConsoleSpanExporter())
)

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("foo"):
    print("Hello world!")


with tracer.start_as_current_span("bar")  as  span:
    span.add_event("Event 0",{'a':1,'b':2})


@tracer.start_as_current_span("child-2")
def child_2():
    print("\t child 2")

with tracer.start_as_current_span("parent"):
    print("parent")
    with tracer.start_as_current_span("child-1"):
        print("\t child 1")
    child_2()


