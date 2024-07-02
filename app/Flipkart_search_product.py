import time
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def search_flipkart_product(product_name):
    # Initialize the WebDriver
    driver = webdriver.Chrome()  # Make sure you have the ChromeDriver installed and added to PATH
    driver.get("https://www.flipkart.com")

    # Close the login popup if it appears
    try:
        close_login_popup = WebDriverWait(driver).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'✕')]"))
        )
        close_login_popup.click()
    except Exception as e:
        print("Login popup did not appear or could not be closed.")
    
    # Find the search bar and enter the product name
    search_bar = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "q"))
    )
    search_bar.clear()
    search_bar.send_keys(product_name)
    search_bar.send_keys(Keys.RETURN)

    # Wait for the search results to load
    WebDriverWait(driver, 10)

    # Display the search results to the user
    print("Please select a product from the search results on the webpage.")
    print("The script will continue once you have clicked on a product.")

    # Wait for the user to select a product and open it in a new tab
    original_window = driver.current_window_handle
    while len(driver.window_handles) == 1:
        time.sleep(1)

    # Switch to the new tab
    new_tab = [window for window in driver.window_handles if window != original_window][0]
    driver.switch_to.window(new_tab)

    # Get the URL of the selected product
    product_url = driver.current_url
    return product_url

    # Clean up
    driver.quit()


