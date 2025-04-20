import requests
from bs4 import BeautifulSoup
import re

def scrape_flipkart_product(url):
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to load page. Status: {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        product_name_tag = soup.find('span', class_='VU-ZEz')
        product_name = product_name_tag.get_text(strip=True) if product_name_tag else "No product name"

        product_price_tag = soup.find('div', class_='Nx9bqj')
        product_price = product_price_tag.get_text(strip=True) if product_price_tag else "No price"

        description_tag = soup.find('div', class_='_4gvKMe')
        product_description = description_tag.get_text(strip=True) if description_tag else "No description"

        rating_section = soup.find('div', class_='ISksQ2')
        if rating_section:
            rating_value = rating_section.find('div', class_='XQDdHH')
            rating_details = rating_section.find('span', class_='Wphh3N')
            product_rating = f"{rating_value.text.strip()} ({rating_details.text.strip()})" if rating_value and rating_details else "No rating"
        else:
            product_rating = "No rating"

        delivery_section = soup.find('div', class_='hVvnXm')
        delivery_time = delivery_section.find('span', class_='Y8v7Fl').text.strip() if delivery_section else "No delivery time"

        return {
            "Product Name": product_name,
            "Price": product_price,
            "Description": product_description,
            "Rating": product_rating,
            "Delivery Time": delivery_time
        }

    except Exception as e:
        print(f"Scraping failed: {e}")
        return None

def save_to_file(data):
    try:
        # Clean and truncate filename to max 100 characters
        safe_name = re.sub(r'[\\/*?:"<>|]', "_", data["Product Name"])
        safe_name = safe_name.strip()[:100]
        filename = f"{safe_name}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            for key, value in data.items():
                f.write(f"{key}: {value}\n")
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"File save failed: {e}")

if __name__ == "__main__":
    url = input("Enter Flipkart Product URL: ").strip()
    product_data = scrape_flipkart_product(url)
    if product_data:
        save_to_file(product_data)
