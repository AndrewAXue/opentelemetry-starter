import argparse
import json
import os

from flask import Flask
from tracer_setup import setup_tracer
app = Flask(__name__)
setup_tracer(app)

@app.route('/get_food', methods=['GET'])
def get_food():
    return json.dumps({'stock': 3, 'price': 5})


if __name__ == '__main__':
    port = os.getenv('PORT') or 5002
    app.run(host='0.0.0.0', port=port)
