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

from tracer import get_flask_middleware

SUPPLIER_URL = 'http://127.0.0.1:5001/get_food_vendors?target_food={}'

app = Flask(__name__)
get_flask_middleware(app)

stats_recorder = stats_module.stats.stats_recorder
# Create the tag key
key_method = tag_key_module.TagKey("method")
# Create the status key
key_status = tag_key_module.TagKey("status")
# Create the error key
key_error = tag_key_module.TagKey("error")

m_latency_ms = measure_module.MeasureFloat("latency", "The latency in milliseconds per find_food request", "ms")
m_num_requests = measure_module.MeasureInt("request count", "The number of find_food requests", "By")
latency_view = view_module.View("latency_graph", "The distribution of the latencies",
    [key_method, key_status, key_error],
    m_latency_ms,
    # Latency in buckets:
    # [>=0ms, >=25ms, >=50ms, >=75ms, >=100ms, >=200ms, >=400ms, >=600ms, >=800ms, >=1s, >=2s, >=4s, >=6s]
    aggregation_module.DistributionAggregation([0, 25, 50, 75, 100, 200, 400, 600, 800, 1000, 2000, 4000, 6000]))

line_count_view = view_module.View("request_counter", "The number of requests",
    [key_method, key_status, key_error],
    m_num_requests,
    aggregation_module.CountAggregation())

@app.route('/')
def target_food_input():
    return render_template('food_input_form.html')


@app.route('/', methods=['POST'])
def target_food_input_post():
    target_food = request.form['target_food']
    return redirect(url_for('.find_food', target_food=target_food))


def _query_supplier(target_food):
    supplier_response = json.loads(requests.get(SUPPLIER_URL.format(target_food)).content)
    return [x for x in supplier_response]


class FoodOption:
    def __init__(self, vendor_url, stock, price):
        self.vendor_url = vendor_url
        self.stock = stock
        self.price = price


@app.route('/find_food', methods=['GET'])
def find_food():
    tracer = get_opencensus_tracer()
    with tracer.span(name="finding_food") as finding_food_span:

        start = time.time()
        mmap = stats_recorder.new_measurement_map()

        target_food = request.args['target_food']
        finding_food_span.add_annotation("Looking for food {}".format(target_food))
        food_options = []
        with tracer.span(name="querying_supplier") as _:
            vendors_with_target = _query_supplier(target_food)
        no_vendor_fails = True
        for vendor in vendors_with_target:
            with tracer.span(name="querying_vendor_{}".format(vendor)) as vendor_span:
                vendor_request = vendor + "/get_food?target_food={}".format(target_food)
                try:
                    option = json.loads(requests.get(vendor_request).content)
                    food_options.append(FoodOption(vendor, option['stock'], option['price']))
                except Exception as e:
                    vendor_span.status = Status(500, 'Vendor request {} failed with error {}'.format(vendor_request, e))
                    no_vendor_fails = False
        finding_food_span.add_annotation("{} vendor responses".format(len(food_options)),
                                         no_vendor_found=(len(food_options) == 0))
        if len(food_options) == 0:
            return_string = 'No options found :('
        else:
            return_string = 'You have {} options<br/>'.format(len(food_options))
            for food_option in food_options:
                return_string += '{} has {} left at {} price<br/>' \
                    .format(food_option.vendor_url, food_option.stock, food_option.price)

        tmap = tag_map_module.TagMap()
        tmap.insert(key_method, tag_value_module.TagValue("find_food"))
        if no_vendor_fails:
            tmap.insert(key_status, tag_value_module.TagValue("OK"))
        else:
            tmap.insert(key_status, tag_value_module.TagValue("Vendor request failed"))
        end_ms = (time.time() - start) * 1000.0  # Seconds to milliseconds

        mmap.measure_float_put(m_latency_ms, end_ms)
        mmap.measure_int_put(m_num_requests, 1)
        mmap.record(tmap)
        return return_string

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
