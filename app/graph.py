import json
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract_graph_data_selenium(url):
    try:
        # Set up Chrome options
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        
        # Initialize Chrome driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        try:
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div#chart-container"))
            )
            
            graph_data = {
                "title": "",
                "subtitle": "",
                "path_data": "",
                "x_axis_labels": [],
                "y_axis_labels": [],
                "average_price": 0,
                "lowest_price": 0
            }

            # Extract chart data
            try:
                graph_path = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR,
                        "div#chart-container svg.highcharts-root g.highcharts-series path.highcharts-graph"
                    )))
                graph_data["path_data"] = graph_path.get_attribute("d")
            except Exception as e:
                print(f"Could not extract path data: {e}")

            try:
                graph_data["y_axis_labels"] = [label.text for label in driver.find_elements(
                    By.CSS_SELECTOR, "g.highcharts-axis-labels.highcharts-yaxis-labels text") if label.text]
            except Exception as e:
                print(f"Could not extract y-axis labels: {e}")

            try:
                graph_data["x_axis_labels"] = [label.text for label in driver.find_elements(
                    By.CSS_SELECTOR, "g.highcharts-axis-labels.highcharts-xaxis-labels text") if label.text]
            except Exception as e:
                print(f"Could not extract x-axis labels: {e}")

            try:
                graph_data["title"] = driver.find_element(
                    By.CSS_SELECTOR, "text.highcharts-title").text
            except:
                graph_data["title"] = "Price History"

            try:
                graph_data["subtitle"] = driver.find_element(
                    By.CSS_SELECTOR, "text.highcharts-subtitle").text
            except:
                graph_data["subtitle"] = "Historical price trends"

            # Extract lowest and average price
            try:
                price_parent = driver.find_element(
                    By.CSS_SELECTOR, 
                    "div.mt-4 > div.flex.items-center.justify-between + div.flex.items-center.justify-between"
                )
                price_ps = price_parent.find_elements(By.TAG_NAME, "p")
                if len(price_ps) >= 2:
                    lowest_price_text = price_ps[0].text.replace("₹", "").replace(",", "").strip()
                    avg_price_text = price_ps[1].text.replace("₹", "").replace(",", "").strip()
                    graph_data["lowest_price"] = float(lowest_price_text)
                    graph_data["average_price"] = float(avg_price_text)
            except Exception as e:
                print(f"Could not extract lowest/average price: {e}")

            return {
                "status": "success",
                "graph_data": graph_data
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error scraping data: {str(e)}"
            }
        finally:
            driver.quit()
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Browser setup failed: {str(e)}"
        }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        result = extract_graph_data_selenium(sys.argv[1])
        print(json.dumps(result))
    else:
        print(json.dumps({
            "status": "error",
            "message": "No URL provided"
        }))