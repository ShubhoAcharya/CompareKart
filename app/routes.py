from flask import Flask, Blueprint, render_template, request, jsonify
import pandas as pd
from sqlalchemy import create_engine, text
import json
import os

from app.url_checker import check_and_update_url
from .Amazon_search_product import search_amazon
from .Flipkart_search_product import search_flipkart_product

main = Blueprint('main', __name__)

# PostgreSQL connection string
DATABASE_URL = "postgresql://postgres:root@localhost:5432/CompareKart"  # Corrected username and password
engine = create_engine(DATABASE_URL)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/product_display')
def product_display():
    return render_template('product_display.html')

@main.route('/save_or_check_url', methods=['POST'])
def save_or_check_url():
    data = request.json
    product_url = data.get('url')

    if not product_url:
        return jsonify({'status': 'error', 'message': 'No URL provided'}), 400

    # Check if the URL exists in the database
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM products WHERE original_url = :url"), {"url": product_url}).fetchone()

        if result:
            return jsonify({'status': 'exists', 'message': 'URL already exists in the database', 'data': dict(result)}), 200

        # Save the URL to temp.txt if not found
        with open('temp.txt', 'w') as f:
            f.write(product_url)

        return jsonify({'status': 'not_found', 'message': 'URL not found in the database. Saved to temp.txt'}), 200


@main.route('/check_url', methods=['POST'])
def check_url():
    try:
        with open('product_URL_check.txt', 'r') as f:
            product_url = f.read()
        check_and_update_url(product_url)
        return '', 204
    except FileNotFoundError:
        return jsonify({'status': 'error', 'message': 'File not found'}), 404


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
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        headers = list(df.columns)
        rows = df.values.tolist()
    else:
        headers = []
        rows = []

    return jsonify({
        'headers': headers,
        'rows': rows,
        'product_urls': product_urls
    })


@main.route('/search', methods=['POST'])
def search():
    data = request.json
    product_name = data.get('query')

    if not product_name:
        return jsonify({'status': 'error', 'message': 'No product name provided'}), 400

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


@main.route('/graph_data.json', methods=['GET'])
def serve_graph_data():
    graph_data_file = './graph_data.json'  # Path to the JSON file
    if os.path.exists(graph_data_file):
        with open(graph_data_file, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
        return jsonify(graph_data)
    else:
        return jsonify({'status': 'error', 'message': 'Graph data not found'}), 404
