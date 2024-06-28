from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def search_flipkart(product_name):
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize the WebDriver with Chrome options
    
    # Set up the WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service,options=chrome_options)
    
    # Open Flipkart
    driver.get('https://www.flipkart.com/')
    
    # Close the login popup if it appears
    try:
        close_button = driver.find_element(By.XPATH, '//button[text()="✕"]')
        close_button.click()
    except:
        pass

    # Find the search input box
    search_input = driver.find_element(By.NAME, 'q')
    
    # Enter the product name
    search_input.send_keys(product_name)
    
    # Submit the search form
    search_input.send_keys(Keys.RETURN)
    
    # Wait for some time to let the results load
    time.sleep(5)  # Adjust the sleep time if necessary
    
    # Find the first product link and get its URL
    try:
        first_product = driver.find_element(By.CSS_SELECTOR, 'a[class="CGtC98"]')
        product_url = first_product.get_attribute('href')
        print(f"URL of the first product: {product_url}")
        
        # Click on the first product
        first_product.click()
        
        # Optionally, you can perform actions on the product page here
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Close the browser
    driver.quit()

if __name__ == "__main__":
    product_name = input("Enter the product name to search: ")
    search_flipkart(product_name)
