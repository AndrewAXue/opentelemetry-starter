import os
import time

import requests
from flask import Flask
from opencensus.common.transports.async_ import AsyncTransport
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.ext.stackdriver.trace_exporter import StackdriverExporter
from opencensus.trace import config_integration
from opencensus.trace.execution_context import get_opencensus_tracer
from opencensus.trace.samplers import AlwaysOnSampler

app = Flask(__name__)
config_integration.trace_integrations(["requests"])
sde = StackdriverExporter(
    project_id=os.environ.get("aaxue-starter"), transport=AsyncTransport
)
middleware = FlaskMiddleware(app, exporter=sde, sampler=AlwaysOnSampler())

talk_to = None
port = 5003


@app.route("/opencensus_server_flask_" + str(port), methods=["GET"])
def opencensus_server_flask():
    tracer = get_opencensus_tracer()
    with tracer.span(name="opencensus_server_manual_" + str(port)):
        time.sleep(0.5)
        if talk_to:
            requests.get(talk_to)
        return "GOOD"

@app.route('/')
def hello_world():
    return 'You probably want {}'.format("/opencensus_server_flask_" + str(port))


if __name__ == "__main__":
    port = os.getenv('PORT') or port
    print("running finder")
    app.run(host='0.0.0.0', port=port)
