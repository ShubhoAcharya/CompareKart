import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

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

        def safe_get_text(by, value):
            try:
                return driver.find_element(by, value).text.strip()
            except:
                return "Not found"

        # Product name
        product_name = safe_get_text(By.ID, "productTitle")

        # ✅ More robust price extractor from aok-offscreen spans using regex
        def extract_price(driver):
            try:
                offscreen_spans = driver.find_elements(By.CLASS_NAME, "aok-offscreen")
                for span in offscreen_spans:
                    text = span.text.strip()
                    match = re.search(r'₹[\s]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?', text)
                    if match:
                        return match.group().replace(" ", "")
                return "Not found"
            except:
                return "Not found"

        price = extract_price(driver)

        # Description
        try:
            bullets = driver.find_element(By.ID, "feature-bullets").text
            description = "\n".join(
                [line.strip() for line in bullets.splitlines() if "See more" not in line]
            )
        except:
            description = "Not found"

        # Rating
        rating = safe_get_text(By.CSS_SELECTOR, "span[data-hook='rating-out-of-text']")

        # Delivery Time
        try:
            delivery_block = driver.find_element(By.ID, "mir-layout-DELIVERY_BLOCK").text.strip()
            delivery = delivery_block.replace("\n", " ")
        except:
            delivery = "Not found"

        return {
            "Product Name": product_name,
            "Price": price,
            "Description": description,
            "Rating": rating,
            "Delivery Time": delivery
        }

    except Exception as e:
        print(f"Error occurred: {e}")
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
