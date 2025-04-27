from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import sys

if len(sys.argv) > 1:
    input_url = sys.argv[1]
else:
    print("No URL provided")
    sys.exit(1)

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(input_url)
driver.implicitly_wait(5)

similar_products = []

try:
    product_items = driver.find_elements(By.CSS_SELECTOR, 'ul.my-4.grid li')
    
    for item in product_items:
        try:
            store_img = item.find_element(By.CSS_SELECTOR, 'img').get_attribute('src')
            product_name = item.find_element(By.CSS_SELECTOR, 'p.capitalize').text.strip()
            price = item.find_element(By.CSS_SELECTOR, 'span.font-bold').text.strip()
            buy_link = item.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
            
            similar_products.append({
                "store_img": store_img,
                "product_name": product_name,
                "price": price,
                "buy_link": buy_link
            })
        except:
            continue
            
except Exception as e:
    print(f"Error extracting similar products: {str(e)}")
finally:
    driver.quit()

print(json.dumps({"status": "success", "products": similar_products}))