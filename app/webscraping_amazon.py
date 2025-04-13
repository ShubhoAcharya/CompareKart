import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def scrape_amazon_product_selenium(url):
    # Set up headless Chrome browser
    options = Options()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36')

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(3)  # Wait for JavaScript to load content

        # Safe element extractor
        def safe_get_text(by, value):
            try:
                return driver.find_element(by, value).text.strip()
            except:
                return "Not found"

        # Extract product details
        product_name = safe_get_text(By.ID, "productTitle")
        product_price = safe_get_text(By.CLASS_NAME, "a-price-whole")
        description = safe_get_text(By.ID, "feature-bullets")
        rating = safe_get_text(By.CSS_SELECTOR, "span[data-hook='rating-out-of-text']")
        delivery = safe_get_text(By.ID, "mir-layout-DELIVERY_BLOCK")

        product_data = {
            "Product Name": product_name,
            "Price": product_price,
            "Description": description,
            "Rating": rating,
            "Delivery Time": delivery
        }

        return product_data

    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    finally:
        driver.quit()

def save_to_file(data, filename='amazon_product.txt'):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(f"Product Name: {data['Product Name']}\n")
            file.write(f"Price: {data['Price']}\n")
            file.write(f"Description: {data['Description']}\n")
            file.write(f"Rating: {data['Rating']}\n")
            file.write(f"Delivery Time: {data['Delivery Time']}\n")
        print(f"Data saved to {filename}")
    except IOError as e:
        print(f"Failed to write to file: {e}")

if __name__ == "__main__":
    # Load product URL from JSON file
    try:
        with open('product_urls.json', 'r') as f:
            product_urls = json.load(f)
        url = product_urls.get('amazon_link', '')
    except Exception as e:
        print(f"Failed to load URL from JSON: {e}")
        url = ''

    if url:
        product_data = scrape_amazon_product_selenium(url)
        if product_data:
            save_to_file(product_data)
        else:
            print("Failed to extract product data.")
    else:
        print("Amazon URL not found in product_urls.json.")
