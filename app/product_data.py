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
from urllib.parse import urlparse, unquote
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

# === Extract Product Data ===
try:
    product_img = driver.find_element(By.CSS_SELECTOR, 'img.product_image')
    product_img_url = product_img.get_attribute("src")
except:
    product_img_url = None

try:
    product_name = driver.find_element(By.TAG_NAME, "h1").text.strip()
except:
    product_name = "Unknown Product"

safe_product_name = re.sub(r'[\\/*?:"<>|]', "_", product_name)

try:
    price = driver.find_element(By.CLASS_NAME, "font-bold").text.strip()
except:
    price = "N/A"

try:
    rating = driver.find_element(By.CLASS_NAME, "text-primary").text.strip()
except:
    rating = "N/A"

# === Extract Graph Data ===
graph_data = {
    "title": "",
    "subtitle": "",
    "path_data": "",
    "x_axis_labels": [],
    "y_axis_labels": [],
    "average_price": 0,
    "lowest_price": 0
}

try:
    # Extract chart data
    try:
        graph_path = WebDriverWait(driver, 10).until(EC.presence_of_element_located((
            By.CSS_SELECTOR,
            "div#chart-container svg.highcharts-root g.highcharts-series path.highcharts-graph"
        )))
        graph_data["path_data"] = graph_path.get_attribute("d")
    except Exception:
        print(" Could not extract path data.")

    try:
        graph_data["y_axis_labels"] = [label.text for label in driver.find_elements(
            By.CSS_SELECTOR, "g.highcharts-axis-labels.highcharts-yaxis-labels text") if label.text]
    except:
        pass

    try:
        graph_data["x_axis_labels"] = [label.text for label in driver.find_elements(
            By.CSS_SELECTOR, "g.highcharts-axis-labels.highcharts-xaxis-labels text") if label.text]
    except:
        pass

    try:
        graph_data["title"] = driver.find_element(By.CSS_SELECTOR, "text.highcharts-title").text
    except:
        graph_data["title"] = "Price History"

    try:
        graph_data["subtitle"] = driver.find_element(By.CSS_SELECTOR, "text.highcharts-subtitle").text
    except:
        graph_data["subtitle"] = "Historical price trends"

    # Extract lowest and average price using the correct selectors
    try:
        # Find the parent div containing both prices
        price_parent = driver.find_element(By.CSS_SELECTOR, "div.mt-4 > div.flex.items-center.justify-between + div.flex.items-center.justify-between")
        price_ps = price_parent.find_elements(By.TAG_NAME, "p")
        if len(price_ps) >= 2:
            # Remove currency symbols and commas, then convert to float
            lowest_price_text = price_ps[0].text.replace("₹", "").replace(",", "").strip()
            avg_price_text = price_ps[1].text.replace("₹", "").replace(",", "").strip()
            graph_data["lowest_price"] = float(lowest_price_text)
            graph_data["average_price"] = float(avg_price_text)
    except Exception as e:
        print(f"Could not extract lowest/average price: {e}")

    # Save graph data to JSON file
    with open('graph_data.json', 'w', encoding='utf-8') as f:
        json.dump(graph_data, f, indent=4, ensure_ascii=False)

except Exception as e:
    print(f" Error extracting graph data: {e}")

finally:
    driver.quit()

# === Output JSON for use in backend ===
output = {
    "product": {
        "Product Name": product_name,
        "Price": price,
        "Rating": rating,
        "Image URL": product_img_url or "N/A"
    },
    "graph_data": graph_data
}

print(json.dumps(output))