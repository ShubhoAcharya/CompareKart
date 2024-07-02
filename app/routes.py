import subprocess
from flask import Flask, Blueprint, render_template, request, jsonify
import pandas as pd
from .Amazon_search_product import search_amazon
from .Flipkart_search_product import search_flipkart_product
import json
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/compare', methods=['GET'])
def compare():
    # Execute the web scraping scripts
    subprocess.run(['python', 'webscraping_Flipkart.py'])
    subprocess.run(['python', 'webscraping_amazon.py'])
    
    # Read the data from the files
    flipkart_file = './flipkart_product.txt'
    amazon_file = './amazon_product.txt'
    
    if os.path.exists(flipkart_file):
        with open(flipkart_file, 'r', encoding='utf-8') as f:
            flipkart_data = f.read()
    else:
        flipkart_data = ""
    
    if os.path.exists(amazon_file):
        with open(amazon_file, 'r', encoding='utf-8') as f:
            amazon_data = f.read()
    else:
        amazon_data = ""
    
    # Combine data into a comparison table format
    flipkart_lines = flipkart_data.split('\n')
    amazon_lines = amazon_data.split('\n')
    
    headers = ['Attribute', 'Flipkart', 'Amazon']
    rows = []
    
    for flipkart_line, amazon_line in zip(flipkart_lines, amazon_lines):
        attribute_flipkart = flipkart_line.split(': ', 1)
        attribute_amazon = amazon_line.split(': ', 1)
        if len(attribute_flipkart) == 2 and len(attribute_amazon) == 2:
            rows.append([attribute_flipkart[0], attribute_flipkart[1], attribute_amazon[1]])
    
    # Add product URLs for redirection links
    urls_file = './product_urls.json'
    if os.path.exists(urls_file):
        with open(urls_file, 'r') as f:
            product_urls = json.load(f)
    else:
        product_urls = {
            'amazon_link': '',
            'flipkart_link': ''
        }
    
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