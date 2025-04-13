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

@main.route('/save_temp', methods=['POST'])
def save_temp():
    data = request.json
    product_url = data.get('url')

    if not product_url:
        return jsonify({'status': 'error', 'message': 'No URL provided'}), 400

    # Save the URL to temp.txt
    try:
        with open('temp.txt', 'w') as f:
            f.write(product_url)
        return jsonify({'status': 'success', 'message': 'URL saved to temp.txt'}), 200
    except IOError as e:
        return jsonify({'status': 'error', 'message': f'Failed to save URL: {e}'}), 500

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
