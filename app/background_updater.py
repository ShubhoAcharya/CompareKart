import threading
import time
import logging
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://postgres:root@localhost:5432/CompareKart"

def create_db_engine():
    return create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,  # Reduced pool size for background tasks
        max_overflow=5,
        pool_timeout=30,
        connect_args={
            'connect_timeout': 10,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5
        }
    )

def update_product(product_id, original_url, engine):
    try:
        with engine.begin() as conn:
            # Scrape product based on URL domain
            if "flipkart.com" in original_url:
                from app.webscraping_Flipkart import scrape_flipkart_product
                product_data = scrape_flipkart_product(original_url)
            elif "amazon.in" in original_url:
                from app.tempCodeRunnerFile import scrape_amazon_product_selenium
                product_data = scrape_amazon_product_selenium(original_url)
            else:
                return False

            if not product_data:
                logger.warning(f"Failed to scrape product {product_id}")
                return False

            # Clean and prepare data
            cleaned_price = clean_price(product_data.get("Price"))
            cleaned_rating = clean_rating(product_data.get("Rating"))
            description = (product_data.get("Description") or "No description available")[:2000]
            delivery_time = (product_data.get("Delivery Time") or "Delivery time not specified")[:255]

            # Update product
            conn.execute(text("""
                UPDATE products
                SET 
                    name = COALESCE(:name, name),
                    price = COALESCE(:price, price),
                    rating = COALESCE(:rating, rating),
                    description = :description,
                    delivery_time = :delivery_time,
                    last_updated = NOW()
                WHERE id = :id
            """), {
                "id": product_id,
                "name": product_data.get("Product Name"),
                "price": cleaned_price,
                "rating": cleaned_rating,
                "description": description,
                "delivery_time": delivery_time
            })

            logger.info(f"Updated product ID: {product_id}")
            return True

    except Exception as e:
        logger.error(f"Error updating product {product_id}: {str(e)}")
        return False

def clean_price(price_str):
    if not price_str:
        return 0.0
    try:
        return float(price_str.replace('₹', '').replace(',', '').strip())
    except ValueError:
        return 0.0

def clean_rating(rating_str):
    if not rating_str:
        return None
    try:
        import re
        match = re.search(r'(\d+\.\d+)', rating_str)
        return float(match.group(1)) if match else None
    except (ValueError, AttributeError):
        return None

def start_background_updater(app):
    engine = create_db_engine()
    
    def updater():
        with app.app_context():
            while True:
                try:
                    # Get products that need updating
                    with engine.connect() as conn:
                        products = conn.execute(text("""
                            SELECT id, original_url FROM products 
                            WHERE last_updated < NOW() - INTERVAL '12 hours' 
                            OR last_updated IS NULL
                            ORDER BY last_updated ASC NULLS FIRST
                            LIMIT 5
                        """)).fetchall()

                    if not products:
                        time.sleep(3600)  # Sleep longer if no products to update
                        continue

                    # Process each product
                    for product in products:
                        update_product(product.id, product.original_url, engine)
                        time.sleep(30)  # Add delay between product updates

                    time.sleep(600)  # Sleep between batches

                except SQLAlchemyError as e:
                    logger.error(f"Database error in update loop: {str(e)}")
                    time.sleep(60)
                except Exception as e:
                    logger.error(f"Unexpected error in update loop: {str(e)}")
                    time.sleep(60)

    # Start the background thread
    thread = threading.Thread(target=updater, daemon=True)
    thread.start()