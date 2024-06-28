from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize the WebDriver with Chrome options
driver = webdriver.Chrome(options=chrome_options)

try:
    # Open Amazon
    driver.get("https://www.amazon.in/")

    # Search for a product
    search_box = driver.find_element(By.ID, "twotabsearchtextbox")
    search_box.send_keys("narzo 70")
    search_box.send_keys(Keys.RETURN)

    # Wait for the search results to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot")))

    # Get all product links excluding sponsored ones
    products = driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
    non_sponsored_product = None

    for product in products:
        # Check if the product is sponsored
        sponsored = product.find_elements(By.CSS_SELECTOR, "span.puis-label-popover-default")
        
        # If not sponsored, get the first link and break the loop
        if not sponsored:
            link_element = product.find_element(By.CSS_SELECTOR, "h2 a")
            product_url = link_element.get_attribute("href")
            print("Product URL:", product_url)
            break

    # If no non-sponsored product is found, handle accordingly
    if not non_sponsored_product:
        print("No non-sponsored products found")

finally:
    # Close the driver after some time
    time.sleep(5)
    driver.quit()
