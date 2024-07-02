import requests
from bs4 import BeautifulSoup
import time

def scrape_amazon_product(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Connection': 'keep-alive'
    }
    
    try:
        for attempt in range(3):  # Retry mechanism
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                break
            else:
                print(f"Attempt {attempt + 1}: Failed to retrieve the webpage. Status code: {response.status_code}")
                time.sleep(2 ** attempt)  # Exponential backoff

        if response.status_code != 200:
            print("Failed to retrieve the webpage after multiple attempts.")
            return None
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract the product name
        product_name_tag = soup.find('span', id='productTitle')
        product_name = product_name_tag.get_text(strip=True) if product_name_tag else "No product name found"
        
        # Extract the product price
        product_price_tag = soup.find('span', class_='a-price-whole')
        product_price = product_price_tag.get_text(strip=True) if product_price_tag else "No price found"
        
        # Extract the product description (if available)
        description_tag = soup.find('div', id='feature-bullets')
        product_description = description_tag.get_text(strip=True) if description_tag else "No description available"
        
        # Extract the product rating
        rating_tag = soup.find('span', {'data-hook': 'rating-out-of-text'})
        product_rating = rating_tag.get_text(strip=True) if rating_tag else "No rating found"
        
        # Extract the delivery time
        delivery_tag = soup.find('div', id='mir-layout-DELIVERY_BLOCK')
        primary_delivery_time_tag = delivery_tag.find('span', class_='a-text-bold') if delivery_tag else None
        primary_delivery_time = primary_delivery_time_tag.get_text(strip=True) if primary_delivery_time_tag else "No delivery time found"
        delivery_time = primary_delivery_time
        
        # Extract specifications
        specifications = {
            'OS': None,
            'RAM': None,
            'Colour': None,
            'Battery Power Rating': None,
            'Whats in the box': None
        }
        
        tech_details_section = soup.find(id='productDetails_techSpec_section_1')
        if tech_details_section:
            spec_rows = tech_details_section.find_all('tr')
            for row in spec_rows:
                key_elem = row.find('th', class_='a-color-secondary')
                value_elem = row.find('td', class_='a-size-base')
                if key_elem and value_elem:
                    key = key_elem.get_text(strip=True)
                    value = value_elem.get_text(strip=True)
                    if key in specifications:
                        specifications[key] = value
        
        # Returning the extracted data
        product_data = {
            'Product Name': product_name,
            'Price': product_price,
            'Description': product_description,
            'Rating': product_rating,
            'Delivery Time': delivery_time,
            'Specifications': specifications
        }
        
        return product_data

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except AttributeError as e:
        print(f"Failed to parse the HTML: {e}")
        return None

def save_to_file(data, filename='amazon_product.txt'):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(f"Product Name: {data['Product Name']}\n")
            file.write(f"Price: {data['Price']}\n")
            file.write(f"Description: {data['Description']}\n")
            file.write(f"Rating: {data['Rating']}\n")
            file.write(f"Delivery Time: {data['Delivery Time']}\n")
            file.write("Specifications:\n")
            for key, value in data['Specifications'].items():
                file.write(f"  - {key}: {value}\n")
        print(f"Data saved to {filename}")
    except IOError as e:
        print(f"Failed to write to file: {e}")

# URL of the Amazon product
url = 'https://www.amazon.in/Acer-i3-1215U-Premium-Windows-AL15-52/dp/B0CKLN7PSZ/ref=sr_1_3?crid=DX4S7Q2DSZUJ&dib=eyJ2IjoiMSJ9.OEYfzYNd95GjvreCKceOJ008dur1IM5JPY5FZYdz6VS3CDDxRMH-Ju8J9yE9h7-Kf18OCXnNTUV-N2huc0s6pPJFacUOFK3od3T6ZGs_zvlo8OO9Q2xsZPn8AeW0T5NMppKj2CWoaXO2XtYzSfN7FLnnrb4jQo_O3qxrRCHCR_gvxqVqU0_ZPV3ssSlVDNv7OOcmNuJgCRHow6aNh_4fjFQNkzb15YkTvGHycGd0L2k.5Gcsn15ZzxJzIZQKIjZ7SNjdhGjSTVFLXLwebN6gQzo&dib_tag=se&keywords=acer%2Blaptop&qid=1719638112&sprefix=acer%2Caps%2C230&sr=8-3&th=1'  # Example URL, replace with actual product URL

# Scrape the product data
product_data = scrape_amazon_product(url)

# Save the extracted data to a file
if product_data:
    save_to_file(product_data)
