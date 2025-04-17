from flask import Blueprint, render_template, request, jsonify
import pandas as pd
from sqlalchemy import create_engine, text
import json
import os
from subprocess import run, PIPE

from app.url_checker import check_and_update_url
from .Amazon_search_product import search_amazon
from .Flipkart_search_product import search_flipkart_product

main = Blueprint('main', __name__)

DATABASE_URL = "postgresql://postgres:root@localhost:5432/CompareKart"
engine = create_engine(DATABASE_URL)

def get_next_sequence_id(connection):
    # Get the maximum existing ID
    max_id_result = connection.execute(text("SELECT COALESCE(MAX(id), 0) FROM products")).fetchone()
    max_id = max_id_result[0]
    
    # Return next ID (max_id + 1)
    return max_id + 1

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/product_display')
def product_display():
    return render_template('product_display.html')

@main.route('/compare', methods=['GET'])
def compare():
    urls_file = './product_urls.json'
    if os.path.exists(urls_file):
        with open(urls_file, 'r') as f:
            product_urls = json.load(f)
    else:
        product_urls = {'amazon_link': '', 'flipkart_link': ''}

    os.system('python ./app/webscraping_amazon.py')
    os.system('python ./app/webscraping_Flipkart.py')
    os.system('python ./app/datatabulation_pandas.py')

    csv_file = './product_comparison.csv'
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

    amazon_url = search_amazon(product_name)
    flipkart_url = search_flipkart_product(product_name)

    urls_file = './product_urls.json'
    product_urls = {'amazon_link': amazon_url, 'flipkart_link': flipkart_url}
    with open(urls_file, 'w') as f:
        json.dump(product_urls, f)

    return jsonify(product_urls)

@main.route('/graph_data.json', methods=['GET'])
def serve_graph_data():
    graph_data_file = './graph_data.json'
    if os.path.exists(graph_data_file):
        with open(graph_data_file, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
        return jsonify(graph_data)
    else:
        return jsonify({'status': 'error', 'message': 'Graph data not found'}), 404

def clean_price(price_str):
    if not price_str:
        return 0.0
    try:
        return float(price_str.replace('₹', '').replace(',', '').strip())
    except Exception as e:
        print(f"An error occurred in clean_price: {e}")
        return 0.0


@main.route('/process_url', methods=['POST'])
def process_url():
    try:
        data = request.json
        product_url = data.get('url')
        if not product_url:
            return jsonify({'status': 'error', 'message': 'No URL provided'}), 400

        print(f"\nProcessing URL: {product_url}")

        with engine.connect() as connection:
            # Start transaction
            trans = connection.begin()
            try:
                # Check if URL already exists
                existing = connection.execute(
                    text("SELECT id, modified_url FROM products WHERE original_url = :url"),
                    {"url": product_url}
                ).fetchone()
                
                if existing:
                    print(f"✅ Found existing ID: {existing.id}")
                    # Run product_data.py with the modified_url
                    print("\nRunning product_data.py for existing URL...")
                    product_proc = run(
                        ["python", "./app/product_data.py", existing.modified_url],
                        stdout=PIPE, stderr=PIPE, text=True
                    )
                    
                    if product_proc.returncode != 0:
                        trans.commit()
                        print("❌ product_data.py error:", product_proc.stderr)
                        return jsonify({'status': 'error', 'message': 'Product data script failed'}), 500
                    
                    try:
                        result = json.loads(product_proc.stdout)
                        product_details = result.get("product", {})
                        
                        # Update database with new product details
                        cleaned_price = clean_price(product_details.get("Price"))
                        
                        connection.execute(text("""
                            UPDATE products
                            SET name = :name,
                                price = :price,
                                rating = :rating,
                                image_link = :image_link
                            WHERE id = :id
                        """), {
                            "name": product_details.get("Product Name"),
                            "price": cleaned_price,
                            "rating": product_details.get("Rating"),
                            "image_link": product_details.get("Image URL"),
                            "id": existing.id
                        })
                        
                        trans.commit()
                        print("✅ Product data updated for existing URL.")
                        return jsonify({'status': 'exists', 'id': existing.id}), 200
                        
                    except json.JSONDecodeError as e:
                        trans.rollback()
                        print("❌ Failed to parse product data:", e)
                        return jsonify({'status': 'error', 'message': 'Invalid JSON from product_data.py'}), 500

                # If URL doesn't exist, proceed with new entry
                next_id = get_next_sequence_id(connection)
                print(f"Next available ID: {next_id}")

                # Insert with explicit ID
                result = connection.execute(
                    text("""
                        INSERT INTO products (id, original_url)
                        VALUES (:id, :url)
                        RETURNING id
                    """),
                    {"id": next_id, "url": product_url}
                ).fetchone()
                
                inserted_id = result[0]
                print(f"Inserted with ID: {inserted_id}")
                
                trans.commit()
            except Exception as e:
                trans.rollback()
                print(f"❌ Database error: {e}")
                return jsonify({'status': 'error', 'message': 'Database operation failed'}), 500

        # For new URLs, first run buyhatke_url.py
        print("\nStep 1: Running buyhatke_url.py...")
        buyhatke_proc = run(["python", "./app/buyhatke_url.py", product_url], stdout=PIPE, stderr=PIPE, text=True)
        if buyhatke_proc.returncode != 0:
            return jsonify({'status': 'error', 'message': 'BuyHatke script failed'}), 500

        with open('temp.txt', 'r') as f:
            modified_url = f.read().strip()
        print(f"Modified URL: {modified_url}")

        # Update database with modified URL
        with engine.connect() as connection:
            trans = connection.begin()
            try:
                connection.execute(
                    text("UPDATE products SET modified_url = :modified_url WHERE id = :id"),
                    {"modified_url": modified_url, "id": inserted_id}
                )
                trans.commit()
            except Exception as e:
                trans.rollback()
                print(f"❌ Database error: {e}")
                return jsonify({'status': 'error', 'message': 'Database update failed'}), 500

        # Step 2: Run product_data.py
        print("\nStep 2: Running product_data.py...")
        product_proc = run(["python", "./app/product_data.py", modified_url], stdout=PIPE, stderr=PIPE, text=True)
        if product_proc.returncode != 0:
            return jsonify({'status': 'error', 'message': 'Product data script failed'}), 500

        try:
            result = json.loads(product_proc.stdout)
            product_details = result.get("product", {})
            
            # Update database with product details
            cleaned_price = clean_price(product_details.get("Price"))
            
            with engine.connect() as connection:
                trans = connection.begin()
                try:
                    connection.execute(text("""
                        UPDATE products
                        SET name = :name,
                            price = :price,
                            rating = :rating,
                            image_link = :image_link
                        WHERE id = :id
                    """), {
                        "name": product_details.get("Product Name"),
                        "price": cleaned_price,
                        "rating": product_details.get("Rating"),
                        "image_link": product_details.get("Image URL"),
                        "id": inserted_id
                    })
                    trans.commit()
                except Exception as e:
                    trans.rollback()
                    print(f"❌ Database error: {e}")
                    return jsonify({'status': 'error', 'message': 'Database update failed'}), 500

            print("✅ Final data saved successfully to database.")
            return jsonify({
                'status': 'success',
                'message': 'URL processed and data saved',
                'id': inserted_id
            }), 200

        except json.JSONDecodeError as e:
            print("❌ Failed to parse product data:", e)
            return jsonify({'status': 'error', 'message': 'Invalid JSON from product_data.py'}), 500

    except Exception as e:
        print("🔥 Unhandled error in process_url:", e)
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
    
@main.route('/get_product_details/<int:id>', methods=['GET'])
def get_product_details(id):
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT name, price, rating, image_link, original_url FROM products WHERE id = :id"),
            {"id": id}
        ).fetchone()
        if result:
            # Format price as ₹1,699
            price = f"₹{int(result.price):,}" if result.price is not None else "N/A"
            return jsonify({
                "status": "success",
                "product": {
                    "name": result.name,
                    "price": price,
                    "rating": str(result.rating),
                    "imageUrl": result.image_link,
                    "buy_link": result.original_url
                }
            })
        else:
            return jsonify({"status": "error", "message": "Product not found"}), 404