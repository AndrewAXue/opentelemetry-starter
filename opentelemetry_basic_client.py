import json
import os
import time

import requests
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleExportSpanProcessor,
)

trace.set_tracer_provider(TracerProvider())


def slim_print(span):
    span_json = json.loads(span.to_json())
    return (
        json.dumps(
            {
                "name": span_json["name"],
                "context": span_json["context"],
                "parent_id": span_json["parent_id"],
            }
        )
        + os.linesep
    )


cloud_exporter = CloudTraceSpanExporter()
console_export = ConsoleSpanExporter(formatter=slim_print)

trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(cloud_exporter)
)

tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("opentelemetry_client_manual"):
    time.sleep(5)
    requests.get("http://localhost:5000/opentelemetry_server_flask")
