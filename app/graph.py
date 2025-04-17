import os
import json
import time
from urllib.parse import urlparse, unquote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import sys

def extract_graph_data_selenium(url, output_file='graph_data.json'):
    print("[1/6] Setting up Chrome options...")
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")

    print("[2/6] Launching browser...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        print(f"[3/6] Opening URL: {url}")
        driver.get(url)
        wait = WebDriverWait(driver, 30)

        # Get product name from <h1> or fallback
        try:
            product_name = driver.find_element(By.TAG_NAME, "h1").text.strip()
        except Exception:
            print(" Could not extract product name, deriving from URL...")
            parsed_url = urlparse(url)
            product_name = unquote(parsed_url.path.split('/')[-1].split('-price')[0].strip().replace(" ", "_"))

        # Extract chart data
        try:
            graph_path = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "div#chart-container svg.highcharts-root g.highcharts-series path.highcharts-graph"
            )))
            path_data = graph_path.get_attribute("d")
        except Exception:
            path_data = ""
            print(" Could not extract path data.")

        try:
            y_labels = [label.text for label in driver.find_elements(
                By.CSS_SELECTOR, "g.highcharts-axis-labels.highcharts-yaxis-labels text") if label.text]
        except:
            y_labels = []

        try:
            x_labels = [label.text for label in driver.find_elements(
                By.CSS_SELECTOR, "g.highcharts-axis-labels.highcharts-xaxis-labels text") if label.text]
        except:
            x_labels = []

        try:
            title = driver.find_element(By.CSS_SELECTOR, "text.highcharts-title").text
        except:
            title = "Price History"

        try:
            subtitle = driver.find_element(By.CSS_SELECTOR, "text.highcharts-subtitle").text
        except:
            subtitle = "Historical price trends"

        try:
            lowest_price_element = driver.find_element(By.XPATH, "//div[@class='flex items-center justify-between']/following-sibling::div/p[1]")
            average_price_element = driver.find_element(By.XPATH, "//div[@class='flex items-center justify-between']/following-sibling::div/p[2]")

            lowest_price = float(lowest_price_element.text.replace("₹", "").replace(",", ""))
            average_price = float(average_price_element.text.replace("₹", "").replace(",", ""))
        except:
            lowest_price = 0
            average_price = 0

        graph_data = {
            "title": title,
            "subtitle": subtitle,
            "path_data": path_data,
            "x_axis_labels": x_labels,
            "y_axis_labels": y_labels,
            "average_price": average_price,
            "lowest_price": lowest_price
        }

        # Always save to the specified output_file (default: graph_data.json in project root)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=4, ensure_ascii=False)

        print(f"[6/6] Graph data saved to '{output_file}'.")

    except Exception as e:
        print(" An error occurred:", e)

    finally:
        driver.quit()

    return output_file

# === CLI Usage ===
if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_url = sys.argv[1]
        # If a second argument is provided, use it as output_file, else default to graph_data.json
        output_file = sys.argv[2] if len(sys.argv) > 2 else "graph_data.json"
        result_file = extract_graph_data_selenium(user_url, output_file)
        if result_file:
            print(result_file)
        else:
            print(" Failed to save graph data.")
    else:
        print(" No URL provided.")
