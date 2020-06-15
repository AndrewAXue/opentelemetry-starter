import json
import time

import requests
from flask import Flask, redirect, url_for, request, render_template
from opencensus.ext.stackdriver import stats_exporter
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module
from opencensus.tags import tag_key as tag_key_module
from opencensus.tags import tag_map as tag_map_module
from opencensus.tags import tag_value as tag_value_module
from opencensus.trace.execution_context import get_opencensus_tracer
from opencensus.trace.status import Status
from opencensus.common.transports.async_ import AsyncTransport
from opencensus.ext.stackdriver.trace_exporter import StackdriverExporter
from opencensus.trace.tracer import Tracer
import os
from tracer import get_flask_middleware


SUPPLIER_URL = 'http://127.0.0.1:5001/get_food_vendors?target_food={}'

app = Flask(__name__)
get_flask_middleware(app)


@app.route("/opencensus_server_flask", methods=["GET"])
def opencensus_server_flask():
    sde = StackdriverExporter(
        project_id=os.environ.get("aaxue-starter"),
        transport=AsyncTransport)

    tracer = Tracer(exporter=sde, sampler=samplers.ProbabilitySampler())
    with tracer.start_as_current_span("opencensus_server_manual"):
        time.sleep(5)
        return "GOOD"

def setupOpenCensusAndPrometheusExporter():
    stats = stats_module.stats
    view_manager = stats.view_manager
    view_manager.register_view(latency_view)
    view_manager.register_view(line_count_view)

    exporter = stats_exporter.new_stats_exporter()

    view_manager.register_exporter(exporter)

if __name__ == '__main__':
    setupOpenCensusAndPrometheusExporter()
    app.run(port=5000)
