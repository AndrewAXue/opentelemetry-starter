from opencensus.ext.stackdriver import trace_exporter as stackdriver_exporter
import opencensus.trace.tracer
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.trace import config_integration



def _get_exporter():
    """
    An exporter is responsible to sending trace data to a backend (e.g. StackTrace, Prometheus)
    :return:
    """
    return stackdriver_exporter.StackdriverExporter()

def get_flask_middleware(app):
    config_integration.trace_integrations(['requests'])
    exporter = _get_exporter()
    return FlaskMiddleware(
        app,
        sampler=opencensus.trace.tracer.samplers.AlwaysOnSampler(),
        exporter=exporter
    )
