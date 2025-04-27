# -*- coding: utf-8 -*-
import re
from flask import Blueprint, render_template, request, jsonify
import pandas as pd
from sqlalchemy import create_engine, text
import json
import os
from subprocess import run, PIPE
import threading
import time
from datetime import datetime, timedelta
from flask_mail import Mail, Message
from flask import current_app

from app.Amazon_search_product import search_amazon
from app.Flipkart_search_product import search_flipkart_product
from app.tempCodeRunnerFile import scrape_amazon_product_selenium
from app.webscraping_Flipkart import scrape_flipkart_product

main = Blueprint('main', __name__)

# Enhanced database connection with pool_pre_ping and echo for debugging
DATABASE_URL = "postgresql://postgres:root@localhost:5432/CompareKart"
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=True,
    connect_args={
        'connect_timeout': 10,
        'keepalives': 1,
        'keepalives_idle': 30,
        'keepalives_interval': 10,
        'keepalives_count': 5
    }
)

def log_error(message, error=None):
    """Helper function for consistent error logging"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_msg = f"[{timestamp}] ERROR: {message}"
    if error:
        error_msg += f"\n{str(error)}"
    print(error_msg)
    return error_msg

def get_next_sequence_id(connection):
    try:
        max_id_result = connection.execute(text("SELECT COALESCE(MAX(id), 0) FROM products")).fetchone()
        return max_id_result[0] + 1
    except Exception as e:
        log_error("Failed to get next sequence ID", e)
        raise

def clean_price(price_str):
    if not price_str:
        return 0.0
    try:
        return float(price_str.replace('₹', '').replace(',', '').strip())
    except Exception as e:
        log_error(f"Failed to clean price string: {price_str}", e)
        return 0.0

def update_product_data_periodically():
    while True:
        try:
            with engine.connect() as conn:
                # Check database connection first
                try:
                    conn.execute(text("SELECT 1"))
                except Exception as e:
                    log_error("Database connection check failed", e)
                    time.sleep(60)
                    continue

                products = conn.execute(text("""
                    SELECT id, modified_url FROM products 
                    WHERE last_updated < NOW() - INTERVAL '10 minutes' 
                    OR last_updated IS NULL
                    ORDER BY last_updated ASC NULLS FIRST
                    LIMIT 1
                """)).fetchall()

                if not products:
                    time.sleep(60)
                    continue
                
                for product in products:
                    try:
                        print(f"\nUpdating product ID: {product.id}")
                        product_proc = run(
                            ["python", "./app/product_data.py", product.modified_url],
                            stdout=PIPE, stderr=PIPE, text=True
                        )
                        
                        if product_proc.returncode != 0:
                            log_error(f"product_data.py failed for product {product.id}", product_proc.stderr)
                            time.sleep(60)
                            continue
                        
                        result = json.loads(product_proc.stdout)
                        product_details = result.get("product", {})
                        cleaned_price = clean_price(product_details.get("Price"))
                        
                        conn.execute(text("""
                            UPDATE products
                            SET name = :name,
                                price = :price,
                                rating = :rating,
                                image_link = :image_link,
                                last_updated = NOW()
                            WHERE id = :id
                        """), {
                            "name": product_details.get("Product Name"),
                            "price": cleaned_price,
                            "rating": product_details.get("Rating"),
                            "image_link": product_details.get("Image URL"),
                            "id": product.id
                        })
                        print(f"✅ Updated product ID: {product.id}")
                        
                    except Exception as e:
                        log_error(f"Error updating product {product.id}", e)
                    
                    time.sleep(3600)

        except Exception as e:
            log_error("Error in update loop", e)
            time.sleep(60)

# Give the app time to initialize before starting the update thread
time.sleep(5)
update_thread = threading.Thread(target=update_product_data_periodically, daemon=True)
update_thread.start()

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/product_display')
def product_display():
    return render_template('product_display.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/terms')
def terms():
    return render_template('terms.html')

@main.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main.route('/search', methods=['POST'])
def search():
    try:
        data = request.json
        query = data.get('query')
        if not query:
            return jsonify({'status': 'error', 'message': 'No search query provided'}), 400

        with engine.connect() as connection:
            # Search for products matching the query in name
            results = connection.execute(
                text("""
                    SELECT id, name, price, rating, image_link 
                    FROM products 
                    WHERE name ILIKE :query
                    ORDER BY last_updated DESC
                    LIMIT 1
                """),
                {"query": f"%{query}%"}
            ).fetchone()

            if results:
                return jsonify({
                    'status': 'success',
                    'product': {
                        'id': results.id,
                        'name': results.name,
                        'price': f"₹{int(results.price):,}" if results.price else "N/A",
                        'rating': str(results.rating) if results.rating else "N/A",
                        'imageUrl': results.image_link or ""
                    },
                    'redirect': f'/product_display?id={results.id}'
                })
            else:
                return jsonify({
                    'status': 'not_found',
                    'message': 'No matching products found'
                })

    except Exception as e:
        log_error("Search failed", e)
        return jsonify({'status': 'error', 'message': 'Search failed'}), 500

@main.route('/graph_data.json', methods=['GET'])
def serve_graph_data():
    try:
        if os.path.exists('./graph_data.json'):
            with open('./graph_data.json', 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        return jsonify({'status': 'error', 'message': 'Graph data not found'}), 404
    except Exception as e:
        log_error("Failed to serve graph data", e)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@main.route('/process_url', methods=['POST'])
def process_url():
    try:
        data = request.json
        product_url = data.get('url')
        if not product_url:
            return jsonify({'status': 'error', 'message': 'No URL provided'}), 400

        print(f"\nProcessing URL: {product_url}")

        with engine.begin() as connection:
            existing = connection.execute(
                text("SELECT id, modified_url FROM products WHERE original_url = :url"),
                {"url": product_url}
            ).fetchone()
            
            if existing:
                print(f"✅ Found existing ID: {existing.id}")
                return jsonify({
                    'status': 'exists', 
                    'id': existing.id,
                    'redirect': f'/product_display?id={existing.id}'
                }), 200

            next_id = get_next_sequence_id(connection)
            result = connection.execute(
                text("""
                    INSERT INTO products (id, original_url, created_at, last_updated)
                    VALUES (:id, :url, NOW(), NOW())
                    RETURNING id
                """),
                {"id": next_id, "url": product_url}
            ).fetchone()
            inserted_id = result[0]
            print(f"✅ Inserted new product with ID: {inserted_id}")

            verify = connection.execute(
                text("SELECT 1 FROM products WHERE id = :id"),
                {"id": inserted_id}
            ).fetchone()
            
            if not verify:
                raise Exception("Failed to verify product insertion")

        print("\nRunning buyhatke_url.py...")
        buyhatke_proc = run(["python", "./app/buyhatke_url.py", product_url], 
                           stdout=PIPE, stderr=PIPE, text=True, timeout=60)
        
        if buyhatke_proc.returncode != 0:
            log_error("BuyHatke script failed", buyhatke_proc.stderr)
            return jsonify({'status': 'error', 'message': 'Failed to process URL'}), 500

        with open('temp.txt', 'r') as f:
            modified_url = f.read().strip()
        print(f"Modified URL: {modified_url}")

        with engine.begin() as connection:
            connection.execute(
                text("UPDATE products SET modified_url = :url WHERE id = :id"),
                {"url": modified_url, "id": inserted_id}
            )

        print("\nRunning product_data.py...")
        product_proc = run(["python", "./app/product_data.py", modified_url], 
                          stdout=PIPE, stderr=PIPE, text=True, timeout=60)
        
        if product_proc.returncode != 0:
            log_error("Product data script failed", product_proc.stderr)
            return jsonify({'status': 'error', 'message': 'Failed to get product data'}), 500

        try:
            product_data = json.loads(product_proc.stdout)['product']
            cleaned_price = clean_price(product_data.get("Price"))
            
            with engine.begin() as connection:
                connection.execute(text("""
                    UPDATE products
                    SET name = :name,
                        price = :price,
                        rating = :rating,
                        image_link = :image_link,
                        last_updated = NOW()
                    WHERE id = :id
                """), {
                    "name": product_data.get("Product Name"),
                    "price": cleaned_price,
                    "rating": product_data.get("Rating"),
                    "image_link": product_data.get("Image URL"),
                    "id": inserted_id
                })

            print("✅ Product data saved successfully")
            return jsonify({
                'status': 'success',
                'id': inserted_id,
                'redirect': f'/product_display?id={inserted_id}'
            }), 200

        except json.JSONDecodeError as e:
            log_error("Invalid product data JSON", e)
            return jsonify({'status': 'error', 'message': 'Invalid product data'}), 500

    except Exception as e:
        log_error("Unhandled error in process_url", e)
        return jsonify({'status': 'error', 'message': str(e)}), 500

@main.route('/get_product_details/<int:id>', methods=['GET'])
def get_product_details(id):
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("""
                    SELECT name, price, rating, image_link, original_url, modified_url 
                    FROM products WHERE id = :id
                """),
                {"id": id}
            ).fetchone()
            
            if not result:
                return jsonify({"status": "error", "message": "Product not found"}), 404

            price = f"₹{int(result.price):,}" if result.price is not None else "N/A"
            rating = str(result.rating) if result.rating is not None else "N/A"
            
            return jsonify({
                "status": "success",
                "product": {
                    "name": result.name,
                    "price": price,
                    "rating": rating,
                    "imageUrl": result.image_link or "",
                    "buy_link": result.original_url
                },
                "modified_url": result.modified_url
            })
    except Exception as e:
        log_error(f"Failed to get product details for ID {id}", e)
        return jsonify({"status": "error", "message": "Internal server error"}), 500

@main.route('/get_graph_data', methods=['GET'])
def get_graph_data():
    try:
        product_id = request.args.get('product_id')
        modified_url = request.args.get('modified_url')
        
        if not product_id or not modified_url:
            return jsonify({'status': 'error', 'message': 'Missing parameters'}), 400

        print(f"\nFetching graph data for product {product_id}")
        
        graph_proc = run(
            ["python", "./app/graph.py", modified_url],
            stdout=PIPE, stderr=PIPE, text=True, timeout=30
        )
        
        if graph_proc.returncode != 0:
            error_msg = graph_proc.stderr or "Unknown error in graph script"
            log_error("Graph script failed", error_msg)
            return jsonify({
                'status': 'error', 
                'message': 'Failed to fetch graph data',
                'details': error_msg
            }), 500
        
        result = json.loads(graph_proc.stdout)
        return jsonify(result) if result.get('status') == 'success' else (
            jsonify({
                'status': 'error',
                'message': result.get('message', 'Failed to get graph data')
            }), 500
        )
            
    except json.JSONDecodeError as e:
        log_error("Failed to parse graph data", e)
        return jsonify({'status': 'error', 'message': 'Invalid graph data format'}), 500
    except Exception as e:
        log_error("Error in get_graph_data", e)
        return jsonify({'status': 'error', 'message': 'Error fetching graph data'}), 500

@main.route('/set_price_alert', methods=['POST'])
def set_price_alert():
    try:
        data = request.json
        product_id = data.get('product_id')
        desired_price = float(data.get('desired_price'))
        email = data.get('email')

        if not all([product_id, desired_price, email]):
            return jsonify({'status': 'error', 'message': 'Missing data'}), 400
        
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return jsonify({'status': 'error', 'message': 'Invalid email format'}), 400

        with engine.begin() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM price_alerts")).scalar()
            if count == 0:
                conn.execute(text("ALTER SEQUENCE price_alerts_id_seq RESTART WITH 1"))
            
            existing = conn.execute(
                text("SELECT id FROM price_alerts WHERE product_id = :pid AND email = :email"),
                {'pid': product_id, 'email': email}
            ).fetchone()
            
            if existing:
                return jsonify({
                    'status': 'error', 
                    'message': 'You already have an alert for this product'
                }), 400
                
            result = conn.execute(
                text("""
                    INSERT INTO price_alerts (product_id, desired_price, email, created_at)
                    VALUES (:pid, :price, :email, NOW())
                    RETURNING id
                """),
                {'pid': product_id, 'price': desired_price, 'email': email}
            ).fetchone()
            
            alert_id = result[0]

            product = conn.execute(
                text("""
                    SELECT name, price, image_link 
                    FROM products 
                    WHERE id = :id
                """),
                {"id": product_id}
            ).fetchone()

        email_success = True
        try:
            mail = Mail(current_app)
            msg = Message(
                f"Price Alert Set for {product.name if product else 'Your Product'}",
                sender=("CompareKart", "alerts@comparekart.com"),
                recipients=[email]
            )
            msg.html = render_template(
                'price_alert_email.html',
                product_name=product.name if product else 'Your Product',
                current_price=f"₹{product.price:,}" if product else 'N/A',
                alert_price=f"₹{desired_price:,}",
                product_image=product.image_link if product else '',
                product_url=f"{request.host_url}product_display?id={product_id}",
                remove_alert_url=f"{request.host_url}remove_price_alert/{alert_id}",
                year=datetime.now().year,
                support_email="support@comparekart.com"
            )
            mail.send(msg)
        except Exception as e:
            log_error("Failed to send alert email", e)
            email_success = False

        return jsonify({
            'status': 'success',
            'warning': not email_success,
            'alert_id': alert_id
        })

    except ValueError:
        return jsonify({'status': 'error', 'message': 'Invalid price format'}), 400
    except Exception as e:
        log_error("Failed to set price alert", e)
        return jsonify({'status': 'error', 'message': 'Failed to set alert'}), 500

@main.route('/remove_price_alert/<int:alert_id>', methods=['GET'])
def remove_price_alert(alert_id):
    try:
        with engine.begin() as conn:
            result = conn.execute(
                text("DELETE FROM price_alerts WHERE id = :id RETURNING email, product_id"),
                {'id': alert_id}
            ).fetchone()
            
            if not result:
                return render_template('alert_removed.html', error="Alert not found"), 404

            product = conn.execute(
                text("SELECT name FROM products WHERE id = :id"),
                {'id': result[1]}
            ).fetchone()

            return render_template(
                'alert_removed.html',
                product_name=product[0] if product else 'your product',
                email=result[0]
            )

    except Exception as e:
        log_error(f"Failed to remove price alert {alert_id}", e)
        return render_template('alert_removed.html', error="Failed to remove alert"), 500

@main.route('/compare_with_url', methods=['POST'])
def compare_with_url():
    try:
        url = request.json.get('url')
        if not url:
            return jsonify({'status': 'error', 'message': 'No URL provided'}), 400

        if "flipkart.com" in url:
            product = scrape_flipkart_product(url) or {}
            product['buy_link'] = url
        elif "amazon.in" in url:
            product = scrape_amazon_product_selenium(url) or {}
            product['buy_link'] = url
        else:
            return jsonify({'status': 'error', 'message': 'Invalid URL'}), 400

        return jsonify({'status': 'success', 'product': product})
    except Exception as e:
        log_error("Comparison failed", e)
        return jsonify({'status': 'error', 'message': 'Comparison failed'}), 500
    

@main.route('/get_similar_products', methods=['GET'])
def get_similar_products():
    try:
        modified_url = request.args.get('modified_url')
        if not modified_url:
            return jsonify({'status': 'error', 'message': 'Missing modified_url'}), 400

        proc = run(
            ["python", "./app/found_similar_products.py", modified_url],
            stdout=PIPE, stderr=PIPE, text=True, timeout=30
        )
        
        if proc.returncode != 0:
            return jsonify({'status': 'error', 'message': 'Failed to fetch similar products'}), 500
            
        data = json.loads(proc.stdout)
        return jsonify(data)
        
    except Exception as e:
        log_error("Error in get_similar_products", e)
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
    

@main.route('/get_price_drop_prediction', methods=['GET'])
def get_price_drop_prediction():
    try:
        modified_url = request.args.get('modified_url')
        if not modified_url:
            return jsonify({'status': 'error', 'message': 'Missing modified_url'}), 400

        proc = run(
            ["python", "./app/price_drop_prediction.py", modified_url],
            stdout=PIPE, stderr=PIPE, timeout=60  # REMOVE text=True here
        )
        
        if proc.returncode != 0:
            error_msg = proc.stderr.decode('utf-8', errors='replace') if proc.stderr else "Unknown error in price drop prediction script"
            current_app.logger.error(f"Price drop script failed: {error_msg}")
            return jsonify({
                'status': 'error', 
                'message': 'Failed to fetch price drop prediction',
                'details': error_msg
            }), 500
        
        try:
            output = proc.stdout.decode('utf-8', errors='replace') if proc.stdout else None
            if not output:
                raise ValueError("No output from price drop script")

            data = json.loads(output)

            if data.get('status') != 'success':
                current_app.logger.error(f"Price drop prediction failed: {data.get('message', 'Unknown error')}")
                return jsonify({
                    'status': 'error',
                    'message': data.get('message', 'Failed to get price drop prediction')
                }), 500
                
            return jsonify(data)

        except json.JSONDecodeError as e:
            raw_output = proc.stdout.decode('utf-8', errors='replace') if proc.stdout else "No output"
            current_app.logger.error(f"Failed to parse price drop data: {e}\nRaw output: {raw_output}")
            return jsonify({
                'status': 'error',
                'message': 'Invalid data format from prediction service',
                'details': str(e)
            }), 500

    except Exception as e:
        current_app.logger.error(f"Error in get_price_drop_prediction: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error', 
            'message': 'Internal server error',
            'details': str(e)
        }), 500
