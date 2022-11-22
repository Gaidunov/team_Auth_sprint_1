from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME
from .config import JaegerSettings


def configure_tracer() -> None:
    config = JaegerSettings()

    resource = Resource(attributes={
        SERVICE_NAME: "auth_api"
    })
    trace.set_tracer_provider(
        TracerProvider(resource=resource)
    )
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=config.host,
                agent_port=int(config.port),
            )
        )
    )
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(ConsoleSpanExporter())
    )
