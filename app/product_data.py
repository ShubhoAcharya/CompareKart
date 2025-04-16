from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
import os
import re
import sys
import json

# === Check if input URL is provided ===
if len(sys.argv) > 1:
    input_url = sys.argv[1]
else:
    print(" No URL provided. Please pass a product URL as a command-line argument.")
    sys.exit(1)

# === Setup headless browser ===
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(input_url)
driver.implicitly_wait(5)

# === Extract Image ===
try:
    product_img = driver.find_element(By.CSS_SELECTOR, 'img.product_image')
    product_img_url = product_img.get_attribute("src")
except:
    product_img_url = None

# === Extract Product Name ===
try:
    product_name = driver.find_element(By.TAG_NAME, "h1").text.strip()
except:
    product_name = "Unknown Product"

# === Sanitize product name for saving ===
safe_product_name = re.sub(r'[\\/*?:"<>|]', "_", product_name)

# === Extract Price ===
try:
    price = driver.find_element(By.CLASS_NAME, "font-bold").text.strip()
except:
    price = "N/A"

# === Extract Rating ===
try:
    rating = driver.find_element(By.CLASS_NAME, "text-primary").text.strip()
except:
    rating = "N/A"

driver.quit()

# === Output JSON for use in backend ===
product_info = {
    "Product Name": product_name,
    "Price": price,
    "Rating": rating,
    "Image URL": product_img_url or "N/A"
}

print(json.dumps(product_info))  # 👈 Print so it can be read by subprocess
