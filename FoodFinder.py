import random
import time

from flask import Flask, redirect, url_for, request, render_template

from tracer import get_tracer
from opencensus.trace.status import Status

import requests
import json


SUPPLIER_URL = 'http://127.0.0.1:5001/get_food?target_food={}'

app = Flask(__name__)


@app.route('/')
def my_form():
    return render_template('food_input_form.html')

@app.route('/', methods=['POST'])
def my_form_post():
    target_food = request.form['target_food']
    return redirect(url_for('.find_food', target_food=target_food))

def _query_supplier(target_food):
    supplier_response = requests.get(SUPPLIER_URL.format(target_food))
    return [x for x in supplier_response]

class FoodOption:
    def __init__(self, vendor_url, stock, price):
        self.vendor_url = vendor_url
        self.stock = stock
        self.price = price


@app.route('/find_food', methods=['GET'])
def find_food():
    tracer = app.config['TRACER']
    with tracer.span(name="finding_food") as _:
        target_food = request.args['target_food']
        food_options = []
        with tracer.span(name="querying_supplier") as _:
            vendors_with_target = _query_supplier(target_food)
        for vendor in vendors_with_target:
            with tracer.span(name="querying_vendor_{}".format(vendor)) as vendor_span:
                vendor_request = vendor + "/get_food?target_food={}".format(target_food)
                try:
                    option = json.loads(requests.get(vendor_request))
                    food_options.append(vendor, option['stock'], option['price'])
                except:
                    vendor_span.status = Status(5, 'Vendor request {} failed'.format(vendor_request))
        if len(food_options) == 0:
            return "No options found :("
        else:
            return_string = 'You have {} options\n'.format(len(food_options))
            for food_option in food_options:
                return_string += '{} has {} left at {} price\n'\
                    .format(food_option.vendor_url, food_option.stock, food_option.price)

        return 'found ' + target_food


if __name__ == '__main__':
    app.config['TRACER'] = get_tracer()

    app.run()
