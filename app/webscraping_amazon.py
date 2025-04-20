import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_amazon_product_selenium(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0')

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(3)

        # Wait until the page content is fully loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "productTitle"))
        )

        def safe_get_text(by, value):
            try:
                return driver.find_element(by, value).text.strip()
            except Exception as e:
                print(f"❌ Error getting text for {value}: {e}")
                return "Not found"

        # Product name
        product_name = safe_get_text(By.ID, "productTitle")

        # Improved price extraction
        def extract_price(driver):
            price_selectors = [
                (By.ID, "priceblock_ourprice"),
                (By.ID, "priceblock_dealprice"),
                (By.CSS_SELECTOR, "span.a-price-whole"),
                (By.CLASS_NAME, "a-price-whole"),
                (By.CSS_SELECTOR, "span.a-offscreen"),
                (By.CSS_SELECTOR, ".a-price.a-text-price span"),
                (By.CSS_SELECTOR, "span.a-color-price")
            ]
            
            for selector_type, selector_value in price_selectors:
                try:
                    elements = driver.find_elements(selector_type, selector_value)
                    for element in elements:
                        price_text = element.text.strip()
                        if price_text:
                            # Extract price using regex
                            match = re.search(r'₹\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?', price_text)
                            if match:
                                return match.group().replace(" ", "")
                            # If no currency symbol found, look for just numbers
                            match = re.search(r'\d{1,3}(?:,\d{3})*(?:\.\d{2})?', price_text)
                            if match:
                                return "₹" + match.group()
                except:
                    continue
            
            # If no price found in standard locations, try more aggressive search
            try:
                page_text = driver.page_source
                price_match = re.search(r'₹\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?', page_text)
                if price_match:
                    return price_match.group().replace(" ", "")
            except Exception as e:
                print(f"❌ Error in aggressive price search: {e}")
            
            return "Not found"

        price = extract_price(driver)

        # Description
        try:
            bullets = driver.find_element(By.ID, "feature-bullets").text
            description = "\n".join(
                [line.strip() for line in bullets.splitlines() if "See more" not in line]
            )
        except Exception as e:
            print(f"❌ Error extracting description: {e}")
            description = "Not found"

        # Rating
        rating = safe_get_text(By.CSS_SELECTOR, "span[data-hook='rating-out-of-text']")

        # Delivery Time
        try:
            delivery_block = driver.find_element(By.ID, "mir-layout-DELIVERY_BLOCK").text.strip()
            delivery = delivery_block.replace("\n", " ")
        except Exception as e:
            print(f"❌ Error extracting delivery time: {e}")
            delivery = "Not found"

        return {
            "Product Name": product_name,
            "Price": price,
            "Description": description,
            "Rating": rating,
            "Delivery Time": delivery
        }

    except Exception as e:
        print(f"❌ Error occurred: {e}")
        return None
    finally:
        driver.quit()

def save_to_file(data):
    try:
        safe_name = re.sub(r'[\\/*?:"<>|]', "_", data["Product Name"]).strip()[:100]
        filename = f"{safe_name}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            for key, value in data.items():
                f.write(f"{key}: {value}\n")
        print(f"✅ Data saved to {filename}")
    except Exception as e:
        print(f"❌ File save failed: {e}")

if __name__ == "__main__":
    url = input("Enter Amazon Product URL: ").strip()
    product_data = scrape_amazon_product_selenium(url)
    if product_data:
        save_to_file(product_data)