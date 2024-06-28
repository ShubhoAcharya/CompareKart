import pandas as pd

def read_data_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()
    return data

def parse_amazon_data(data):
    product_data = {}
    lines = data.split('\n')
    
    try:
        product_data['Website'] = 'Amazon'
        product_data['Product Name'] = lines[0].split(': ', 1)[1] if len(lines) > 0 else 'N/A'
        product_data['Price'] = lines[1].split(': ', 1)[1] if len(lines) > 1 else 'N/A'
        product_data['Description'] = lines[2].split(': ', 1)[1] if len(lines) > 2 else 'N/A'
        product_data['Rating'] = lines[3].split(': ', 1)[1] if len(lines) > 3 else 'N/A'
        product_data['Delivery Time'] = lines[4].split(': ', 1)[1] if len(lines) > 4 else 'N/A'
        
        specs = {}
        spec_lines = lines[6:]
        for line in spec_lines:
            if line.strip() and ': ' in line:
                key, value = line.split(': ', 1)
                specs[key.strip()] = value.strip()
        product_data['Specifications'] = specs
    except IndexError as e:
        print(f"Error parsing Amazon data: {e}")
    
    return product_data

def parse_flipkart_data(data):
    product_data = {}
    lines = data.split('\n')
    
    try:
        product_data['Website'] = 'Flipkart'
        product_data['Product Name'] = lines[0].split(': ', 1)[1] if len(lines) > 0 else 'N/A'
        product_data['Price'] = lines[1].split(': ', 1)[1] if len(lines) > 1 else 'N/A'
        product_data['Description'] = lines[2].split(': ', 1)[1] if len(lines) > 2 else 'N/A'
        product_data['Rating'] = lines[3].split(': ', 1)[1] if len(lines) > 3 else 'N/A'
        product_data['Delivery Time'] = lines[4].split(': ', 1)[1] if len(lines) > 4 else 'N/A'
        
        specs = {}
        spec_lines = lines[6:]
        for line in spec_lines:
            if line.strip() and ': ' in line:
                key, value = line.split(': ', 1)
                specs[key.strip()] = value.strip()
        product_data['Specifications'] = specs
    except IndexError as e:
        print(f"Error parsing Flipkart data: {e}")
    
    return product_data

# Reading data from text files
amazon_data = read_data_from_file('amazon_product.txt')
flipkart_data = read_data_from_file('flipkart_product.txt')

# Parsing data
amazon_product = parse_amazon_data(amazon_data)
flipkart_product = parse_flipkart_data(flipkart_data)

# Extracting relevant fields to create a DataFrame
data = {
    'Feature': [
        'Product Name', 'Price', 'Description', 'Rating', 'Delivery Time',
        'OS', 'RAM', 'Product Dimensions', 'Batteries', 'Item model number',
        'Wireless communication technologies', 'Connectivity technologies',
        'Special features', 'Other display features', 'Other camera features',
        'Form factor', 'Colour', 'Battery Power Rating', 'Whats in the box',
        'Manufacturer', 'Country of Origin', 'Item Weight'
    ],
    'Amazon': [
        amazon_product.get('Product Name', 'N/A'), amazon_product.get('Price', 'N/A'), amazon_product.get('Description', 'N/A'), amazon_product.get('Rating', 'N/A'), amazon_product.get('Delivery Time', 'N/A'),
        amazon_product['Specifications'].get('OS', 'N/A'), amazon_product['Specifications'].get('RAM', 'N/A'), amazon_product['Specifications'].get('Product Dimensions', 'N/A'),
        amazon_product['Specifications'].get('Batteries', 'N/A'), amazon_product['Specifications'].get('Item model number', 'N/A'),
        amazon_product['Specifications'].get('Wireless communication technologies', 'N/A'), amazon_product['Specifications'].get('Connectivity technologies', 'N/A'),
        amazon_product['Specifications'].get('Special features', 'N/A'), amazon_product['Specifications'].get('Other display features', 'N/A'),
        amazon_product['Specifications'].get('Other camera features', 'N/A'), amazon_product['Specifications'].get('Form factor', 'N/A'),
        amazon_product['Specifications'].get('Colour', 'N/A'), amazon_product['Specifications'].get('Battery Power Rating', 'N/A'),
        amazon_product['Specifications'].get('Whats in the box', 'N/A'), amazon_product['Specifications'].get('Manufacturer', 'N/A'),
        amazon_product['Specifications'].get('Country of Origin', 'N/A'), amazon_product['Specifications'].get('Item Weight', 'N/A')
    ],
    'Flipkart': [
        flipkart_product.get('Product Name', 'N/A'), flipkart_product.get('Price', 'N/A'), flipkart_product.get('Description', 'N/A'), flipkart_product.get('Rating', 'N/A'), flipkart_product.get('Delivery Time', 'N/A'),
        flipkart_product['Specifications'].get('Operating System', 'N/A'), flipkart_product['Specifications'].get('RAM', 'N/A'), flipkart_product['Specifications'].get('Display Size', 'N/A'),
        flipkart_product['Specifications'].get('Battery Capacity', 'N/A'), flipkart_product['Specifications'].get('Model Number', 'N/A'),
        flipkart_product['Specifications'].get('Wi-Fi', 'N/A'), flipkart_product['Specifications'].get('Bluetooth Support', 'N/A'),
        flipkart_product['Specifications'].get('Special features', 'N/A'), flipkart_product['Specifications'].get('Display Type', 'N/A'),
        flipkart_product['Specifications'].get('Dual Camera Lens', 'N/A'), flipkart_product['Specifications'].get('Form factor', 'N/A'),
        flipkart_product['Specifications'].get('Color', 'N/A'), flipkart_product['Specifications'].get('Battery Type', 'N/A'),
        flipkart_product['Specifications'].get('In The Box', 'N/A'), flipkart_product['Specifications'].get('Manufacturer', 'N/A'),
        flipkart_product['Specifications'].get('Country of Origin', 'N/A'), flipkart_product['Specifications'].get('Item Weight', 'N/A')
    ]
}

# Creating DataFrame
df = pd.DataFrame(data)

# Displaying DataFrame as a table
print(df)

# Optionally, save the DataFrame to a CSV file
df.to_csv('product_comparison.csv', index=False)
