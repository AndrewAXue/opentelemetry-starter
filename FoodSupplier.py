from flask import Flask, request, jsonify

from tracer import get_flask_middleware
from opencensus.trace.execution_context import get_opencensus_tracer
app = Flask(__name__)
get_flask_middleware(app)


def _get_vendors_with_target(target_food, food_supplier_span, lookup_method='static'):
    food_supplier_span.add_annotation("Using {} lookup method".format(lookup_method))
    if lookup_method == 'static':
        VENDOR_DATA = {
            'http://127.0.0.1:5002': ['egg', 'bean', 'cheese'],
            'http://127.0.0.1:5003': ['egg', 'potato'],
            'http://127.0.0.1:5004': ['bread'],
        }
        return [vendor_url for vendor_url, vendor_items in VENDOR_DATA.items() if target_food in vendor_items]


@app.route('/get_food_vendors', methods=['GET'])
def get_food_vendors():
    tracer = get_opencensus_tracer()
    with tracer.span(name="food_supplier") as food_supplier_span:
        target_food = request.args['target_food']
        return jsonify(_get_vendors_with_target(target_food, food_supplier_span))


if __name__ == '__main__':
    app.run(port=5001)
