import time
import pyautogui
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def open_buyhatke_and_paste(url):
    # Setup Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    try:
        print(" Opening BuyHatke...")
        driver.get("https://buyhatke.com/")

        # Wait for input field to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "product-search-bar"))
        )
        input_element = driver.find_element(By.ID, "product-search-bar")
        print(" Input field located.")

        # Click on the input field to focus
        input_element.click()
        time.sleep(1)

        # Copy URL to clipboard and paste it using Ctrl+V
        pyperclip.copy(url)
        pyautogui.hotkey("ctrl", "v")
        print(" URL pasted via Ctrl+V.")

        # Press Enter to trigger search/redirect
        time.sleep(1)
        pyautogui.press("enter")
        print(" Enter key pressed.")

        # Wait for redirection
        WebDriverWait(driver, 10).until(lambda d: d.current_url != "https://buyhatke.com/")
        print(" Redirected to:", driver.current_url)

        with open("temp.txt", "w") as f:
            f.write(driver.current_url)


    except Exception as e:
        print(" Error:", e)
        print(" Final URL:", driver.current_url)

    finally:
        driver.quit()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://www.flipkart.com/noise-icon-4-stunning-1-96-amoled-display-metallic-finish-bt-calling-smartwatch/p/..."

    open_buyhatke_and_paste(url)
    print(" Process completed.")