from opencensus.ext.stackdriver import trace_exporter as stackdriver_exporter
import opencensus.trace.tracer

def _get_exporter():
    """
    An exporter is responsible to sending trace data to a backend (e.g. StackTrace, Prometheus)
    :return:
    """
    return stackdriver_exporter.StackdriverExporter()

def get_tracer():
    exporter = _get_exporter()
    return opencensus.trace.tracer.Tracer(
        exporter=exporter,
        sampler=opencensus.trace.tracer.samplers.AlwaysOnSampler()
    )