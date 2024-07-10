from flask import Flask, Blueprint, render_template, request, jsonify
import pandas as pd

from app.url_checker import check_and_update_url
from .Amazon_search_product import search_amazon
from .Flipkart_search_product import search_flipkart_product
import json
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/save_url', methods=['POST'])
def save_url():
    data = request.json
    product_url = data['url']
    with open('product_URL_check.txt', 'w') as f:
        f.write(product_url)
    return '', 204

@main.route('/check_url', methods=['POST'])
def check_url():
    with open('product_URL_check.txt', 'r') as f:
        product_url = f.read()
    check_and_update_url(product_url)
    return '', 204


@main.route('/compare', methods=['GET'])
def compare():
    # Load the product URLs from the file
    urls_file = './product_urls.json'
    if os.path.exists(urls_file):
        with open(urls_file, 'r') as f:
            product_urls = json.load(f)
    else:
        product_urls = {
            'amazon_link': '',
            'flipkart_link': ''
        }
    
    # Run webscraping scripts
    os.system('python ./app/webscraping_amazon.py')
    os.system('python ./app/webscraping_Flipkart.py')

    # Run datatabulation script to generate the CSV file
    os.system('python ./app/datatabulation_pandas.py')

    csv_file = './product_comparison.csv'  # Update this path accordingly
    df = pd.read_csv(csv_file)
    headers = list(df.columns)
    rows = df.values.tolist()
    
    return jsonify({
        'headers': headers,
        'rows': rows,
        'product_urls': product_urls
    })

@main.route('/search', methods=['POST'])
def search():
    data = request.json
    product_name = data.get('query')

    # Search on Amazon
    amazon_url = search_amazon(product_name)
    
    # Search on Flipkart
    flipkart_url = search_flipkart_product(product_name)

    # Save the URLs to a file
    urls_file = './product_urls.json'
    product_urls = {
        'amazon_link': amazon_url,
        'flipkart_link': flipkart_url
    }
    with open(urls_file, 'w') as f:
        json.dump(product_urls, f)

    return jsonify(product_urls)
