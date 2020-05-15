import opentelemetry.ext.requests
from opentelemetry import trace
from opentelemetry.ext import jaeger
from opentelemetry.ext.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleExportSpanProcessor,
)

def setup_tracer(app):
    trace.set_tracer_provider(TracerProvider())
    opentelemetry.ext.requests.RequestsInstrumentor().instrument()
    FlaskInstrumentor().instrument_app(app)

    jaeger_exporter = jaeger.JaegerSpanExporter(
        service_name="food-finder", agent_host_name="localhost", agent_port=6831
    )
    def slim_print(span):
        import json
        import os
        span_json = json.loads(span.to_json())
        return json.dumps({'name': span_json['name'], 'context': span_json['context'], 'parent_id': span_json['parent_id']}) + os.linesep


    trace.get_tracer_provider().add_span_processor(
        SimpleExportSpanProcessor(jaeger_exporter)
    )