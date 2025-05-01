# -*- coding: utf-8 -*-
import re
from flask import Blueprint, redirect, render_template, request, jsonify, url_for
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

# Update the update_product_data_periodically function in routes.py
def update_product_data_periodically():
    while True:
        try:
            with engine.begin() as conn:  # This should auto-commit
                # Check database connection first
                try:
                    conn.execute(text("SELECT 1"))
                except Exception as e:
                    log_error("Database connection check failed", e)
                    time.sleep(60)
                    continue

                # Get products that need updating
                products = conn.execute(text("""
                    SELECT id, original_url FROM products 
                    WHERE last_updated < NOW() - INTERVAL '12 hours' 
                    OR last_updated IS NULL
                    ORDER BY last_updated ASC NULLS FIRST
                    LIMIT 10
                """)).fetchall()

                if not products:
                    time.sleep(3600)
                    continue
                
                for product in products:
                    try:
                        print(f"\nUpdating product ID: {product.id}")
                        
                        # Scrape product data
                        if "flipkart.com" in product.original_url:
                            product_data = scrape_flipkart_product(product.original_url)
                        elif "amazon.in" in product.original_url:
                            product_data = scrape_amazon_product_selenium(product.original_url)
                        else:
                            continue
                        
                        if not product_data:
                            print(f"❌ Failed to scrape product {product.id}")
                            continue
                        
                        # Prepare data with fallbacks
                        cleaned_price = clean_price(product_data.get("Price"))
                        cleaned_rating = clean_rating(product_data.get("Rating"))
                        description = product_data.get("Description", "No description available")[:2000]
                        delivery_time = product_data.get("Delivery Time", "Delivery time not specified")[:255]
                        
                        # Debug print before update
                        print(f"Updating product {product.id} with:")
                        print(f"Description: {description[:100]}...")
                        print(f"Delivery Time: {delivery_time}")
                        
                        # Execute update
                        result = conn.execute(text("""
                            UPDATE products
                            SET 
                                name = COALESCE(:name, name),
                                price = COALESCE(:price, price),
                                rating = COALESCE(:rating, rating),
                                description = :description,
                                delivery_time = :delivery_time,
                                last_updated = NOW()
                            WHERE id = :id
                            RETURNING description, delivery_time
                        """), {
                            "id": product.id,
                            "name": product_data.get("Product Name"),
                            "price": cleaned_price,
                            "rating": cleaned_rating,
                            "description": description,
                            "delivery_time": delivery_time
                        })
                        
                        # Verify the update
                        updated = result.fetchone()
                        print(f"✅ Updated product ID: {product.id}")
                        print(f"Stored description: {updated.description[:100]}...")
                        print(f"Stored delivery_time: {updated.delivery_time}")
                        
                    except Exception as e:
                        log_error(f"Error updating product {product.id}", e)
                        # Add explicit rollback in case of error
                        conn.rollback()
                    
                    time.sleep(10)
                
                time.sleep(600)

        except Exception as e:
            log_error("Error in update loop", e)
            time.sleep(60)

# Give the app time to initialize before starting the update thread
time.sleep(5)
update_thread = threading.Thread(target=update_product_data_periodically, daemon=True)
update_thread.start()

@main.route('/')
def index():
    with engine.connect() as conn:
        categories = conn.execute(text("SELECT id, name, icon FROM categories ORDER BY name")).fetchall()
    return render_template('index.html', categories=categories)

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
            # Check if product exists and get current price
            product = conn.execute(
                text("""
                    SELECT name, price, image_link 
                    FROM products 
                    WHERE id = :id
                """),
                {"id": product_id}
            ).fetchone()
            
            if not product:
                return jsonify({'status': 'error', 'message': 'Product not found'}), 404
            
            current_price = product.price if product.price else 0
            
            # Check if price is already below desired price
            if current_price <= desired_price:
                return jsonify({
                    'status': 'success',
                    'message': f'Current price (₹{current_price:,.2f}) is already below your alert price!',
                    'already_below': True
                })
            
            # Check if alert already exists
            existing = conn.execute(
                text("""
                    SELECT id, is_active 
                    FROM price_alerts 
                    WHERE product_id = :pid AND email = :email
                """),
                {'pid': product_id, 'email': email}
            ).fetchone()
            
            if existing:
                if existing.is_active:
                    return jsonify({
                        'status': 'error', 
                        'message': 'You already have an active alert for this product'
                    }), 400
                else:
                    # Reactivate existing alert
                    conn.execute(
                        text("""
                            UPDATE price_alerts
                            SET desired_price = :price,
                                is_active = TRUE,
                                updated_at = NOW(),
                                triggered_at = NULL
                            WHERE id = :id
                        """),
                        {'price': desired_price, 'id': existing.id}
                    )
                    alert_id = existing.id
            else:
                # Create new alert
                result = conn.execute(
                    text("""
                        INSERT INTO price_alerts (
                            product_id, 
                            desired_price, 
                            email, 
                            created_at,
                            updated_at
                        )
                        VALUES (:pid, :price, :email, NOW(), NOW())
                        RETURNING id
                    """),
                    {'pid': product_id, 'price': desired_price, 'email': email}
                ).fetchone()
                alert_id = result[0]

            # Send confirmation email
            email_success = True
            try:
                mail = Mail(current_app)
                msg = Message(
                    f"Price Alert Set for {product.name}",
                    sender=("CompareKart", "alerts@comparekart.com"),
                    recipients=[email]
                )
                msg.html = render_template(
                    'price_alert_email.html',
                    product_name=product.name,
                    current_price=f"₹{current_price:,.2f}",
                    alert_price=f"₹{desired_price:,.2f}",
                    product_image=product.image_link if product.image_link else '',
                    product_url=f"{current_app.config['BASE_URL']}/product_display?id={product_id}",
                    remove_alert_url=f"{current_app.config['BASE_URL']}/remove_price_alert/{alert_id}",
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
                'alert_id': alert_id,
                'message': 'Price alert set successfully!'
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
                text("""
                    UPDATE price_alerts 
                    SET is_active = FALSE, 
                        updated_at = NOW()
                    WHERE id = :id
                    RETURNING email, product_id
                """),
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

# Add to routes.py
# Update the /create_comparison route in routes.py
@main.route('/create_comparison', methods=['POST'])
def create_comparison():
    try:
        data = request.json
        product_id = data.get('product_id')
        urls = data.get('urls', [])
        
        if not product_id or not urls:
            return jsonify({'status': 'error', 'message': 'Missing data'}), 400
        
        product_ids = [product_id]
        
        with engine.begin() as conn:
            # Process each URL
            for url in urls:
                # Check if product already exists
                existing = conn.execute(
                    text("SELECT id FROM products WHERE original_url = :url"),
                    {"url": url}
                ).fetchone()
                
                if existing:
                    product_ids.append(existing.id)
                    continue
                
                # Scrape new product based on URL domain
                if "flipkart.com" in url:
                    product_data = scrape_flipkart_product(url)
                elif "amazon.in" in url:
                    product_data = scrape_amazon_product_selenium(url)
                else:
                    continue
                
                if not product_data:
                    continue
                
                # Clean and prepare data for database
                price = clean_price(product_data.get("Price", "0"))
                rating = clean_rating(product_data.get("Rating", "0"))
                
                # Insert new product
                result = conn.execute(
                    text("""
                        INSERT INTO products (
                            original_url, 
                            name, 
                            price, 
                            rating, 
                            image_link, 
                            description,
                            delivery_time,
                            created_at, 
                            last_updated
                        )
                        VALUES (
                            :url, 
                            :name, 
                            :price, 
                            :rating, 
                            :image, 
                            :description,
                            :delivery_time,
                            NOW(), 
                            NOW()
                        )
                        RETURNING id
                    """),
                    {
                        "url": url,
                        "name": product_data.get("Product Name", "Unknown Product"),
                        "price": price,
                        "rating": rating,
                        "image": product_data.get("Image URL", ""),
                        "description": product_data.get("Description", ""),
                        "delivery_time": product_data.get("Delivery Time", "")
                    }
                ).fetchone()
                
                product_ids.append(result[0])
            
            # Create comparison record
            result = conn.execute(
                text("""
                    INSERT INTO comparisons (user_session, product_ids)
                    VALUES (:session, :product_ids)
                    RETURNING id
                """),
                {
                    "session": request.remote_addr,  # Simple session identifier
                    "product_ids": product_ids
                }
            ).fetchone()
            
            return jsonify({
                'status': 'success',
                'comparison_id': result[0],
                'product_count': len(product_ids)
            })
            
    except Exception as e:
        log_error("Failed to create comparison", e)
        return jsonify({'status': 'error', 'message': 'Failed to create comparison'}), 500

def clean_price(price_str):
    if not price_str:
        return None
    try:
        # Remove currency symbols and commas
        numeric_str = re.sub(r'[^0-9.]', '', price_str)
        return float(numeric_str)
    except Exception as e:
        log_error(f"Failed to clean price string: {price_str}", e)
        return None

def clean_rating(rating_str):
    if not rating_str:
        return None
    try:
        # Extract first number from rating string (e.g., "4.2 (1234)" -> 4.2)
        match = re.search(r'(\d+\.\d+)', rating_str)
        return float(match.group(1)) if match else None
    except Exception as e:
        log_error(f"Failed to clean rating string: {rating_str}", e)
        return None
    

# Update the /compare_page route in routes.py

@main.route('/compare_page')
def compare_page():
    comparison_id = request.args.get('id')
    if not comparison_id:
        return redirect(url_for('main.index'))
    
    try:
        with engine.connect() as conn:
            comparison = conn.execute(
                text("SELECT product_ids FROM comparisons WHERE id = :id"),
                {"id": comparison_id}
            ).fetchone()
            
            if not comparison:
                return render_template('404.html'), 404
            
            products = []
            for product_id in comparison[0]:
                product = conn.execute(
                    text("""
                        SELECT 
                            id, 
                            name, 
                            price, 
                            rating, 
                            image_link, 
                            original_url,
                            description,
                            delivery_time
                        FROM products WHERE id = :id
                    """),
                    {"id": product_id}
                ).fetchone()
                
                if product:
                    products.append({
                        'id': product.id,
                        'name': product.name,
                        'price': f"₹{int(product.price):,}" if product.price else "N/A",
                        'rating': str(product.rating) if product.rating else "N/A",
                        'image': product.image_link or "",
                        'url': product.original_url,
                        'description': product.description or "No description available",
                        'delivery_time': product.delivery_time or "Not specified"
                    })
            
            return render_template('compare_page.html', 
                                 products=products, 
                                 comparison_id=comparison_id)
            
    except Exception as e:
        log_error(f"Failed to load comparison {comparison_id}", e)
        return render_template('500.html'), 500

@main.route('/update_comparison', methods=['POST'])
def update_comparison():
    try:
        data = request.json
        comparison_id = data.get('comparison_id')
        product_id = data.get('product_id')
        new_url = data.get('new_url')
        
        if not all([comparison_id, product_id, new_url]):
            return jsonify({'status': 'error', 'message': 'Missing data'}), 400
        
        if not re.match(r'https?://(www\.)?(flipkart\.com|amazon\.in)/', new_url):
            return jsonify({'status': 'error', 'message': 'Invalid URL'}), 400
        
        with engine.begin() as conn:
            # Scrape new product
            if "flipkart.com" in new_url:
                product = scrape_flipkart_product(new_url) or {}
            elif "amazon.in" in new_url:
                product = scrape_amazon_product_selenium(new_url) or {}
            
            # Insert or update product
            existing = conn.execute(
                text("SELECT id FROM products WHERE original_url = :url"),
                {"url": new_url}
            ).fetchone()
            
            if existing:
                new_product_id = existing.id
            else:
                result = conn.execute(
                    text("""
                        INSERT INTO products (original_url, name, price, rating, image_link, description, delivery_time, created_at, last_updated)
                        VALUES (:url, :name, :price, :rating, :image, :description, :delivery_time, NOW(), NOW())
                        RETURNING id
                    """),
                    {
                        "url": new_url,
                        "name": product.get("Product Name"),
                        "price": clean_price(product.get("Price")),
                        "rating": product.get("Rating"),
                        "image": product.get("Image URL"),
                        "description": product.get("Description", ""),
                        "delivery_time": product.get("Delivery Time", "")
                    }
                ).fetchone()
                new_product_id = result[0]
            
            # Update comparison
            conn.execute(
                text("""
                    UPDATE comparisons
                    SET product_ids = array_replace(product_ids, :old_id, :new_id)
                    WHERE id = :comparison_id
                """),
                {
                    "old_id": product_id,
                    "new_id": new_product_id,
                    "comparison_id": comparison_id
                }
            )
            
            # Get updated product data
            updated_product = conn.execute(
                text("""
                    SELECT id, name, price, rating, image_link
                    FROM products WHERE id = :id
                """),
                {"id": new_product_id}
            ).fetchone()
            
            return jsonify({
                'status': 'success',
                'product': {
                    'id': updated_product.id,
                    'name': updated_product.name,
                    'price': f"₹{int(updated_product.price):,}" if updated_product.price else "N/A",
                    'rating': str(updated_product.rating) if updated_product.rating else "N/A",
                    'image': updated_product.image_link or ""
                }
            })
            
    except Exception as e:
        log_error("Failed to update comparison", e)
        return jsonify({'status': 'error', 'message': 'Failed to update comparison'}), 500
    
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

@main.route('/get_products_by_category/<int:category_id>', methods=['GET'])
def get_products_by_category(category_id):
    try:
        with engine.connect() as conn:
            # Get category name
            category = conn.execute(
                text("SELECT name FROM categories WHERE id = :id"),
                {"id": category_id}
            ).fetchone()
            
            if not category:
                return jsonify({'status': 'error', 'message': 'Category not found'}), 404
            
            # Get products in this category
            products = conn.execute(
                text("""
                    SELECT id, name, price, rating, image_link 
                    FROM products 
                    WHERE category_id = :category_id
                    ORDER BY last_updated DESC
                    LIMIT 20
                """),
                {"category_id": category_id}
            ).fetchall()
            
            products_list = []
            for product in products:
                products_list.append({
                    'id': product.id,
                    'name': product.name,
                    'price': f"₹{int(product.price):,}" if product.price else "N/A",
                    'rating': str(product.rating) if product.rating else "N/A",
                    'imageUrl': product.image_link or "",
                    'redirect': f'/product_display?id={product.id}'
                })
            
            return jsonify({
                'status': 'success',
                'category': category[0],
                'products': products_list
            })
            
    except Exception as e:
        log_error(f"Failed to get products for category {category_id}", e)
        return jsonify({"status": "error", "message": "Internal server error"}), 500
    

@main.route('/test_db_write')
def test_db_write():
    try:
        with engine.begin() as conn:
            # Test writing to description and delivery_time
            test_data = {
                "description": "This is a test description",
                "delivery_time": "Test delivery time"
            }
            
            # Update first product
            conn.execute(text("""
                UPDATE products 
                SET description = :desc, 
                    delivery_time = :delivery,
                    last_updated = NOW()
                WHERE id = 1
                RETURNING description, delivery_time
            """), {
                "desc": test_data["description"],
                "delivery": test_data["delivery_time"]
            })
            
            # Verify update
            result = conn.execute(text("""
                SELECT description, delivery_time 
                FROM products 
                WHERE id = 1
            """)).fetchone()
            
            return jsonify({
                "status": "success",
                "written_data": test_data,
                "stored_data": {
                    "description": result.description,
                    "delivery_time": result.delivery_time
                }
            })
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500