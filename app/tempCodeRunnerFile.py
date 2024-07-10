import pandas as pd

# Function to read product data from file
def read_product_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        product_data = {}
        specifications = {}
        current_key = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('Product Name:'):
                product_data['Product Name'] = line.split(': ', 1)[1]
            elif line.startswith('Price:'):
                product_data['Price'] = line.split(': ', 1)[1]
            elif line.startswith('Description:'):
                product_data['Description'] = line.split(': ', 1)[1]
            elif line.startswith('Rating:'):
                product_data['Rating'] = line.split(': ', 1)[1]
            elif line.startswith('Delivery Time:'):
                product_data['Delivery Time'] = line.split(': ', 1)[1]
            elif line.startswith('Specifications:'):
                current_key = 'Specifications'
            elif current_key == 'Specifications' and line.startswith('  - '):
                key, value = map(str.strip, line.lstrip('  - ').split(':', 1))
                specifications[key] = value
        
        product_data['Specifications'] = specifications
        return product_data

# Load Amazon and Flipkart product data from files
amazon_product_data = read_product_data('./amazon_product.txt')
flipkart_product_data = read_product_data('./flipkart_product.txt')

# Define the features to compare (excluding Specifications)
features = [
    'Product Name',
    'Price',
    'Description',
    'Rating',
    'Delivery Time'
]

# Initialize lists to store data
data = {'Feature': features}
amazon_values = []
flipkart_values = []

# Add Amazon data to lists
for feature in features:
    amazon_values.append(amazon_product_data.get(feature, None))

# Add Flipkart data to lists
for feature in features:
    flipkart_values.append(flipkart_product_data.get(feature, None))

# Create a DataFrame from the collected data
df = pd.DataFrame({
    'Feature': features,
    'Amazon': amazon_values,
    'Flipkart': flipkart_values
})

# Display the final DataFrame
print("\nFinal DataFrame:")
print(df)

# Save the DataFrame to a CSV file
df.to_csv('product_comparison.csv', index=False)
