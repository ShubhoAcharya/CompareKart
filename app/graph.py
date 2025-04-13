import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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

        print("[4/6] Waiting for Highcharts graph to load...")
        wait = WebDriverWait(driver, 30)

        # Extract path data
        try:
            graph_path = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "div#chart-container svg.highcharts-root g.highcharts-series path.highcharts-graph"
            )))
            path_data = graph_path.get_attribute("d")
        except Exception:
            path_data = ""
            print("⚠️ Could not extract path data.")

        # Extract Y-axis labels
        try:
            y_axis_labels = driver.find_elements(By.CSS_SELECTOR, "g.highcharts-axis-labels.highcharts-yaxis-labels text")
            y_labels = [label.text for label in y_axis_labels if label.text]
        except Exception:
            y_labels = []
            print("⚠️ Could not extract Y-axis labels.")

        # Extract X-axis labels
        try:
            x_axis_labels = driver.find_elements(By.CSS_SELECTOR, "g.highcharts-axis-labels.highcharts-xaxis-labels text")
            x_labels = [label.text for label in x_axis_labels if label.text]
        except Exception:
            x_labels = []
            print("⚠️ Could not extract X-axis labels.")

        # Extract title
        try:
            title = driver.find_element(By.CSS_SELECTOR, "text.highcharts-title").text
        except Exception:
            title = "Price History"
            print("⚠️ Could not extract title, using default.")

        # Extract subtitle
        try:
            subtitle = driver.find_element(By.CSS_SELECTOR, "text.highcharts-subtitle").text
        except Exception:
            subtitle = "Historical price trends"
            print("⚠️ Could not extract subtitle, using default.")

        # Extract Lowest Price and Average Price from the HTML structure
        try:
            # Corrected XPath for Lowest Price and Average Price
            lowest_price_element = driver.find_element(By.XPATH, "//div[@class='flex items-center justify-between']/following-sibling::div/p[1]")
            average_price_element = driver.find_element(By.XPATH, "//div[@class='flex items-center justify-between']/following-sibling::div/p[2]")

            lowest_price = float(lowest_price_element.text.replace("₹", "").replace(",", ""))
            average_price = float(average_price_element.text.replace("₹", "").replace(",", ""))
        except Exception:
            lowest_price = 0
            average_price = 0
            print("⚠️ Could not extract Lowest Price or Average Price.")

        # Prepare and save data
        graph_data = {
            "title": title,
            "subtitle": subtitle,
            "path_data": path_data,
            "x_axis_labels": x_labels,
            "y_axis_labels": y_labels,
            "average_price": average_price,
            "lowest_price": lowest_price
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=4, ensure_ascii=False)

        print(f"[6/6] Graph data saved to '{output_file}'.")

    except Exception as e:
        print("❌ An error occurred:", e)
    finally:
        driver.quit()

# === Usage ===
if __name__ == "__main__":
    user_url = input("Enter the URL of the page with the graph: ")
    extract_graph_data_selenium(user_url)
