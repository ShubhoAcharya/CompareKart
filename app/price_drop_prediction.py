import json
import sys
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract_price_drop_data(url):
    result = {
        "status": "error",
        "message": "Initialization failed",
        "price_drop_data": {
            "chance_of_drop": 0,
            "recommendation": "Data not available",
            "buy_link": "",
            "pointer_rotation": 0,
            "time_frame": "1",  # Default to "2-3 days"
            "store_name": ""    # Will be extracted from buy link
        }
    }
    
    try:
        # Set up Chrome options
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")

        # Initialize Chrome driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)

        try:
            driver.get(url)

            # Wait for page to load
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "section.border-2"))
            )

            price_drop_data = {
                "chance_of_drop": 0,
                "recommendation": "This is the best time to buy right away.",
                "buy_link": "",
                "pointer_rotation": 0
            }

            # Extract chance of price drop
            try:
                chance_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "span[style*='color:#00A80B']"))
                )
                price_drop_data["chance_of_drop"] = int(chance_element.text.replace('%', '').strip())
            except Exception as e:
                print(f"Could not extract chance of drop: {e}", file=sys.stderr)

            # Extract recommendation text
            try:
                recommendation_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "p.max-w-[230px], p.max-w-[380px]"))
                )
                price_drop_data["recommendation"] = recommendation_element.text.strip()
            except Exception as e:
                print(f"Could not extract recommendation: {e}", file=sys.stderr)

            # Extract buy link
            try:
                buy_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[aria-label*='Buy button']"))
                )
                price_drop_data["buy_link"] = buy_button.get_attribute("href")
            except Exception as e:
                print(f"Could not extract buy link: {e}", file=sys.stderr)

            # Extract pointer rotation
            try:
                pointer_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "g.pointer path"))
                )
                transform = pointer_element.get_attribute("transform")
                if transform and "rotate(" in transform:
                    rotation = int(transform.split("rotate(")[1].split(")")[0])
                    price_drop_data["pointer_rotation"] = rotation
            except Exception as e:
                print(f"Could not extract pointer rotation: {e}", file=sys.stderr)

            result = {
                "status": "success",
                "price_drop_data": price_drop_data
            }

        except Exception as e:
            result = {
                "status": "error",
                "message": f"Error scraping data: {str(e)}",
                "traceback": traceback.format_exc()
            }
        finally:
            driver.quit()

    except Exception as e:
        result = {
            "status": "error",
            "message": f"Browser setup failed: {str(e)}",
            "traceback": traceback.format_exc()
        }

    return result

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            result = extract_price_drop_data(sys.argv[1])
            print(json.dumps(result, ensure_ascii=False))
        else:
            print(json.dumps({
                "status": "error",
                "message": "No URL provided"
            }, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "traceback": traceback.format_exc()
        }, ensure_ascii=False))