from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def search_amazon(product_name):
    # Initialize the WebDriver with Chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)  # Keep the browser open after script execution
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()  # Maximize the browser window for better visibility

    try:
        # Open Amazon
        driver.get("https://www.amazon.in/")

        # Search for the product
        search_box = driver.find_element(By.ID, "twotabsearchtextbox")
        search_box.send_keys(product_name)
        search_box.send_keys(Keys.RETURN)

        # Wait for the search results to load
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot")))

        # Get all product links excluding sponsored ones
        products = driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")

        # Display the list of products with their indices
        print("Please click on the product you want to select in the browser.")

        # Wait for the user to click on a product
        selected_product = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-component-type='s-search-result']")))
        # Click on the selected product
        selected_product.click()
        
        # Wait for the new tab to open
        WebDriverWait(driver, 20).until(EC.number_of_windows_to_be(2))
        
        # Switch to the newly opened tab
        driver.switch_to.window(driver.window_handles[1])

        # Get the URL of the selected product
        product_url = driver.current_url
        return product_url

    finally:
        # Close the driver
        driver.quit()
