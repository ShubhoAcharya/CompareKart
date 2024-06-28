from flask import Blueprint, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data['query']
    
    flipkart_link = search_flipkart(query)
    amazon_link = search_amazon(query)
    
    return jsonify({
        'flipkart_link': flipkart_link,
        'amazon_link': amazon_link
    })

def create_driver():
    options = Options()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def search_flipkart(product_name):
    driver = create_driver()
    driver.get('https://www.flipkart.com/')
    
    try:
        close_button = driver.find_element(By.XPATH, '//button[text()="✕"]')
        close_button.click()
    except:
        pass

    search_input = driver.find_element(By.NAME, 'q')
    search_input.send_keys(product_name)
    search_input.send_keys(Keys.RETURN)
    
    time.sleep(5)
    product_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/p/"]')
    product_link = None
    for link in product_links:
        if "sponsored" not in link.get_attribute('href'):
            product_link = link.get_attribute('href')
            break
    
    driver.quit()
    return product_link

def search_amazon(product_name):
    driver = create_driver()
    driver.get('https://www.amazon.in/')
    
    search_input = driver.find_element(By.ID, 'twotabsearchtextbox')
    search_input.send_keys(product_name)
    search_input.send_keys(Keys.RETURN)
    
    time.sleep(5)
    product_links = driver.find_elements(By.CSS_SELECTOR, 'a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal')
    product_link = None
    for link in product_links:
        if "sponsored" not in link.get_attribute('href'):
            product_link = link.get_attribute('href')
            break
    
    driver.quit()
    return product_link
