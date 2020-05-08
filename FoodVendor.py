import argparse
import json

from flask import Flask

app = Flask(__name__)
#get_flask_middleware(app)
VENDOR_URL_BASE = '127.0.0.1'

@app.route('/get_food', methods=['GET'])
def get_food():
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
