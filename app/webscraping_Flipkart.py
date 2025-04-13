import json
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
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract the product name
        product_name_tag = soup.find('span', class_='VU-ZEz')
        product_name = product_name_tag.get_text(strip=True) if product_name_tag else "No product name found"
        
        # Extract the product price
        product_price_tag = soup.find('div', class_='Nx9bqj')
        product_price = product_price_tag.get_text(strip=True) if product_price_tag else "No price found"
        
        # Extract the product description (if available)
        description_tag = soup.find('div', class_='_4gvKMe')
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
        
        # Returning the extracted data as a dictionary
        return {
            'Product Name': product_name,
            'Price': product_price,
            'Description': product_description,
            'Rating': product_rating,
            'Delivery Time': delivery_time
        }

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except AttributeError as e:
        print(f"Failed to parse the HTML: {e}")
        return None

def save_to_file(data, filename='flipkart_product.txt'):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(f"Product Name: {data['Product Name']}\n")
            file.write(f"Price: {data['Price']}\n")
            file.write(f"Description: {data['Description']}\n")
            file.write(f"Rating: {data['Rating']}\n")
            file.write(f"Delivery Time: {data['Delivery Time']}\n")
        print(f"Data saved to {filename}")
    except IOError as e:
        print(f"Failed to write to file: {e}")

# URL of the Flipkart product
if __name__ == "__main__":
    with open('product_urls.json', 'r') as f:
        product_urls = json.load(f)
    url = product_urls.get('flipkart_link', '')
    
    # Scrape the product data
    product_data = scrape_flipkart_product(url)

    # Save the extracted data to a file
    if product_data:
        save_to_file(product_data, filename='flipkart_product.txt')
