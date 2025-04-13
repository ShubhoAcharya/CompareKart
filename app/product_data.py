from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
import os
import re

# Setup headless browser
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://buyhatke.com/flipkart-noise-icon-4-with-stunning-1-96-amoled-display-metallic-finish-bt-calling-smartwatch-price-in-india-2-142848250")

# Wait a bit if needed (you can use WebDriverWait if more stability is needed)
driver.implicitly_wait(5)

# === Extract Image ===
try:
    product_img = driver.find_element(By.CSS_SELECTOR, 'img.product_image')
    product_img_url = product_img.get_attribute("src")
    print("✅ Image URL:", product_img_url)
except:
    product_img_url = None
    print("⚠️ Product image not found.")

# === Extract Product Name ===
product_name = driver.find_element(By.TAG_NAME, "h1").text.strip()

# Sanitize product name for file saving
safe_product_name = re.sub(r'[\\/*?:"<>|]', "_", product_name)

# === Extract Price ===
price = driver.find_element(By.CLASS_NAME, "font-bold").text.strip()

# === Extract Rating (optional) ===
try:
    rating = driver.find_element(By.CLASS_NAME, "text-primary").text.strip()
except:
    rating = "N/A"

driver.quit()

# === Save Data ===
os.makedirs("product_data", exist_ok=True)

# Save image
if product_img_url:
    img_data = requests.get(product_img_url).content
    img_filename = os.path.join("product_data", f"{safe_product_name}_image.jpg")
    with open(img_filename, "wb") as f:
        f.write(img_data)
    print(f"✅ Image saved to {img_filename}")
else:
    print("⚠️ Image not found.")

# Save product info
info_filename = os.path.join("product_data", f"{safe_product_name}_info.txt")
with open(info_filename, "w", encoding="utf-8") as f:
    f.write(f"Product Name: {product_name}\n")
    f.write(f"Price: {price}\n")
    f.write(f"Rating: {rating}\n")
    f.write(f"Image URL: {product_img_url or 'N/A'}\n")

print(f"✅ Product data saved to {info_filename}")
