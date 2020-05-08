import json
import time

import requests
from flask import Flask, redirect, url_for, request, render_template

SUPPLIER_URL = 'http://127.0.0.1:5001/get_food_vendors?target_food={}'

app = Flask(__name__)
#get_flask_middleware(app)

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
    target_food = request.args['target_food']
    food_options = []
    vendors_with_target = _query_supplier(target_food)
    for vendor in vendors_with_target:
        vendor_request = vendor + "/get_food?target_food={}".format(target_food)
        try:
            option = json.loads(requests.get(vendor_request).content)
            food_options.append(FoodOption(vendor, option['stock'], option['price']))
        except Exception as e:
            pass
    if len(food_options) == 0:
        return_string = 'No options found :('
    else:
        return_string = 'You have {} options<br/>'.format(len(food_options))
        for food_option in food_options:
            return_string += '{} has {} left at {} price<br/>' \
                .format(food_option.vendor_url, food_option.stock, food_option.price)
    return return_string

if __name__ == '__main__':
    app.run(port=5000)
