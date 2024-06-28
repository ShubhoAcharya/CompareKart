import requests
from bs4 import BeautifulSoup
import time

def scrape_flipkart_product(url):
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
        
        # Log the response content for debugging
        with open("page_content.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract the product name
        product_name_tag = soup.find('span', class_='VU-ZEz')
        product_name = product_name_tag.get_text(strip=True) if product_name_tag else "No product name found"
        
        # Extract the product price
        product_price_tag = soup.find('div', class_='Nx9bqj')
        product_price = product_price_tag.get_text(strip=True) if product_price_tag else "No price found"
        
        # Extract the product description (if available)
        description_tag = soup.find('div', class_='_4gvKMe')  # Adjust the class as needed based on actual HTML
        product_description = description_tag.get_text(strip=True) if description_tag else "No description available"
        
        # Extract the product rating
        rating_section = soup.find('div', class_='ISksQ2')
        if rating_section:
            rating_tag = rating_section.find('div', class_='XQDdHH')
            rating_value = rating_tag.get_text(strip=True) if rating_tag else "No rating value found"
            
            rating_details_tag = rating_section.find('span', class_='Wphh3N')
            rating_details = rating_details_tag.get_text(strip=True) if rating_details_tag else "No rating details found"
            
            product_rating = f"{rating_value} ({rating_details})"
        else:
            product_rating = "No rating found"
        
        # Extract the delivery time
        delivery_section = soup.find('div', class_='hVvnXm')
        if delivery_section:
            delivery_time_tag = delivery_section.find('span', class_='Y8v7Fl')
            delivery_time = delivery_time_tag.get_text(strip=True) if delivery_time_tag else "No delivery time found"
        else:
            delivery_time = "No delivery time found"
        
        # Extract specifications
        specifications = {}
        spec_sections = soup.find_all('div', class_='GNDEQ-')
        for section in spec_sections:
            section_title = section.find('div', class_='_4BJ2V+').get_text(strip=True)
            spec_rows = section.find_all('tr', class_='WJdYP6 row')
            for row in spec_rows:
                cols = row.find_all('td')
                if len(cols) == 2:
                    key = cols[0].get_text(strip=True)
                    value = cols[1].get_text(strip=True)
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

# URL of the Flipkart product
url = 'https://www.flipkart.com/realme-narzo-70-pro-5g-glass-gold-128-gb/p/itm5f12ccbe8d955?pid=MOBGZ5M6PATZHMTP&lid=LSTMOBGZ5M6PATZHMTPRDHNL5&marketplace=FLIPKART&q=realme%20narzo%2070%20pro&sattr[]=color&sattr[]=storage&st=color'

# Scrape the product data
product_data = scrape_flipkart_product(url)

# Print the extracted data
if product_data:
    print("Product Data:")
    for key, value in product_data.items():
        print(f"{key}: {value}")
