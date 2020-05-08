from flask import Flask, request, jsonify

app = Flask(__name__)
#get_flask_middleware(app)


def _get_vendors_with_target(target_food, lookup_method='static'):
    if lookup_method == 'static':
        VENDOR_DATA = {
            'http://127.0.0.1:5002': ['egg', 'bean', 'cheese'],
            'http://127.0.0.1:5003': ['egg', 'potato'],
            'http://127.0.0.1:5004': ['bread'],
        }
        return [vendor_url for vendor_url, vendor_items in VENDOR_DATA.items() if target_food in vendor_items]


@app.route('/get_food_vendors', methods=['GET'])
def get_food_vendors():
    target_food = request.args['target_food']
    return jsonify(_get_vendors_with_target(target_food))


if __name__ == '__main__':
    app.run(port=5001)
