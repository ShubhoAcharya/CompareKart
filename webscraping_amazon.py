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
        rating_section = soup.find('div', id='cm_cr_dp_d_rating_histogram')
        if (rating_section and 
            (rating_value_tag := rating_section.find('span', {'data-hook': 'rating-out-of-text'})) and 
            (total_reviews_tag := rating_section.find('span', {'data-hook': 'total-review-count'}))):
            rating_value = rating_value_tag.get_text(strip=True)
            total_reviews = total_reviews_tag.get_text(strip=True)
            product_rating = f"{rating_value} ({total_reviews})"
        else:
            product_rating = "No rating found"
        
        # Extract the delivery time
        delivery_section = soup.find('div', id='mir-layout-DELIVERY_BLOCK')
        if (delivery_section and 
            (primary_delivery_time_tag := delivery_section.find('span', class_='a-text-bold'))):
            primary_delivery_time = primary_delivery_time_tag.get_text(strip=True)
            secondary_delivery_time_tag = delivery_section.find_all('span', class_='a-text-bold')
            secondary_delivery_time = secondary_delivery_time_tag[1].get_text(strip=True) if len(secondary_delivery_time_tag) > 1 else "No secondary delivery time found"
            delivery_time = f"Primary: {primary_delivery_time}, Secondary: {secondary_delivery_time}"
        else:
            delivery_time = "No delivery time found"
        
        # Extract specifications
        specifications = {}
        
        # Attempt to find specifications in the product details section
        tech_details_section = soup.find(id='productDetails_techSpec_section_1')
        if tech_details_section:
            spec_rows = tech_details_section.find_all('tr')
            for row in spec_rows:
                key_elem = row.find('th', class_='a-color-secondary')
                value_elem = row.find('td', class_='a-size-base')
                if key_elem and value_elem:
                    key = key_elem.get_text(strip=True)
                    value = value_elem.get_text(strip=True)
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
            for key, value in data.items():
                if key == 'Specifications':
                    file.write(f"{key}:\n")
                    for spec_key, spec_value in value.items():
                        file.write(f"  - {spec_key}: {spec_value}\n")
                else:
                    file.write(f"{key}: {value}\n")
        print(f"Data saved to {filename}")
    except IOError as e:
        print(f"Failed to write to file: {e}")

# URL of the Amazon product
url = 'https://www.amazon.in/realme-Storage-Dimensity-Chipset-Display/dp/B0CZS4VHP4/ref=sr_1_1?dib=eyJ2IjoiMSJ9.Frbg-b9fdxf85CYVeYMwDHMoB44TzH_7bPEmyCSpjyO33YYUqJT2lyHRaAQDFKE_5z4ILxZ0aemHBJvv0p1-zZXIt6lo8kgFgVfsKHPSGKsaEcT1xnYAgfh1gK3kaKmrc0P1BDTpYoeky5foyeQo_ps4Lsqvff7OLqbY4IxslK26_XN63pjGpSWcP-uaSAJOFKVc_dkTNbGYx8C7yOsE7CXx8CeUa6oG2CTxdNQzLRQ.ITE6s6JSq5VTCB_Zh0xX57w8tzAXMI10pNhUzLup3xA&dib_tag=se&keywords=narzo+70&qid=1719490998&sr=8-1'  # Example URL, replace with actual product URL

# Scrape the product data
product_data = scrape_amazon_product(url)

# Save the extracted data to a file
if product_data:
    save_to_file(product_data)
