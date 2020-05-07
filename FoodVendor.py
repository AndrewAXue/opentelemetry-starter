from flask import Flask, request

from tracer import get_flask_middleware
import argparse
import json
from opencensus.trace.execution_context import get_opencensus_tracer
app = Flask(__name__)
get_flask_middleware(app)
VENDOR_URL_BASE = '127.0.0.1'

@app.route('/get_food', methods=['GET'])
def get_food():
    tracer = get_opencensus_tracer()
    with tracer.span(name="food_vendor_{}:{}".format(VENDOR_URL_BASE, app.config['PORT'])) as _:
        return json.dumps({'stock': 3, 'price': 5})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--port', help='Port of this vendor, we just assume all vendor urls are localhost:<port>', required=True)
    args = parser.parse_args()
    app.config['PORT'] = args.port
    app.run(port=args.port)
