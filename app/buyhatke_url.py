import time
import pyautogui
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def open_buyhatke_and_paste(url):
    # Setup Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    try:
        print("🌐 Opening BuyHatke...")
        driver.get("https://buyhatke.com/")

        # Wait for input field to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "product-search-bar"))
        )
        input_element = driver.find_element(By.ID, "product-search-bar")
        print("✅ Input field located.")

        # Click on the input field to focus
        input_element.click()
        time.sleep(1)

        # Copy URL to clipboard and paste it using Ctrl+V
        pyperclip.copy(url)
        pyautogui.hotkey("ctrl", "v")
        print("📋 URL pasted via Ctrl+V.")

        # Press Enter to trigger search/redirect
        time.sleep(1)
        pyautogui.press("enter")
        print("↩️ Enter key pressed.")

        # Wait for redirection
        WebDriverWait(driver, 10).until(lambda d: d.current_url != "https://buyhatke.com/")
        print("✅ Redirected to:", driver.current_url)

    except Exception as e:
        print("❌ Error:", e)
        print("🌐 Final URL:", driver.current_url)

    finally:
        driver.quit()

if __name__ == "__main__":
    product_url = "https://www.flipkart.com/noise-icon-4-stunning-1-96-amoled-display-metallic-finish-bt-calling-smartwatch/p/itmb7800093c5c95?pid=SMWGWZVPQWQSG2UH&lid=LSTSMWGWZVPQWQSG2UHVIFBFI&marketplace=FLIPKART&store=ajy%2Fbuh&srno=b_1_2&otracker=browse&fm=organic&iid=en_AETJp3g4iofnF_7jxebttz3FmmSyhxAez3Ueryr7j9jLf6a5vbgCufa6UvAKlhsjwhrQd0HH0h0zg5bxejR5pg%3D%3D&ppt=hp&ppn=homepage&ssid=54ko982xts0000001744350079894"
    open_buyhatke_and_paste(product_url)
