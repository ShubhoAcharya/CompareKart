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

        # Returning the extracted data as a dictionary
        return {
            'Product Name': product_name,
            'Price': product_price,
            'Description': product_description,
            'Rating': product_rating,
            'Delivery Time': delivery_time,
            'Specifications': specifications
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
            file.write("Specifications:\n")
            file.write(f"  - Whats in the box: {data['Specifications'].get('In The Box', 'N/A')}\n")
            file.write(f"  - Colour: {data['Specifications'].get('Color', 'N/A')}\n")
            file.write(f"  - OS: {data['Specifications'].get('Operating System', 'N/A')}\n")
            file.write(f"  - RAM: {data['Specifications'].get('RAM', 'N/A')}\n")
            file.write(f"  - Battery Power Rating: {data['Specifications'].get('Battery Capacity', 'N/A')}\n")
        print(f"Data saved to {filename}")
    except IOError as e:
        print(f"Failed to write to file: {e}")

# URL of the Flipkart product
url = 'https://www.flipkart.com/realme-narzo-70x-5g-ice-blue-128-gb/p/itm4ef66169ea11b?pid=MOBHYCWQUSWGF6FT&lid=LSTMOBHYCWQUSWGF6FTEN3MHN&marketplace=FLIPKART&q=narzo+70+5g&store=tyy%2F4io&srno=s_1_1&otracker=search&otracker1=search&fm=organic&iid=76f11829-a833-44c9-9969-20b3f845bdc0.MOBHYCWQUSWGF6FT.SEARCH&ppt=hp&ppn=homepage&ssid=ru3j7r785c0000001719549384529&qH=a972efa0bd6da8dd'

# Scrape the product data
product_data = scrape_flipkart_product(url)

# Save the extracted data to a file
if product_data:
    save_to_file(product_data, filename='flipkart_product.txt')
