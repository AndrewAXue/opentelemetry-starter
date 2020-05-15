from flask import Flask, redirect, url_for, request, render_template, jsonify
from tracer_setup import setup_tracer
import os

app = Flask(__name__)
from opentelemetry import trace
setup_tracer(app)

def _get_vendors_with_target(target_food, lookup_method='static'):
    if lookup_method == 'static':
        VENDOR_DATA = {
            'https://food-vendor-airgfkjhea-ue.a.run.app': ['egg', 'bean', 'cheese'],
            'http://127.0.0.1:5003': ['egg', 'potato'],
            'http://127.0.0.1:5004': ['bread'],
        }
        return [vendor_url for vendor_url, vendor_items in VENDOR_DATA.items() if target_food in vendor_items]


@app.route('/get_food_vendors', methods=['GET'])
def get_food_vendors():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span('supplying_food_manual') as food_span:
        food_span.set_attribute('key', 'value')
        target_food = request.args['target_food']
        return jsonify(_get_vendors_with_target(target_food))


if __name__ == '__main__':
    port = os.getenv('PORT') or 5001
    print("running supplier")
    app.run(host='0.0.0.0', port=port)
