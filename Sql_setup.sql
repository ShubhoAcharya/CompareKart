-- Create the database (only works if executed by a superuser)
CREATE DATABASE comparekart;

-- Switch to the newly created database
\c comparekart

-- Create the 'products' table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    original_url TEXT NOT NULL,
    modified_url TEXT,
    name VARCHAR(512),
    price NUMERIC(10,2),
    rating NUMERIC(3,2),
    image_link TEXT,
    graph_data_link TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Optional: Insert sample data for testing
INSERT INTO products (
    original_url, modified_url, name, price, rating, image_link, graph_data_link
) VALUES (
    'https://www.amazon.in/dp/exampleproduct',
    'https://www.amazon.in/exampleproduct',
    'Sample Product Name',
    999.99,
    4.5,
    'https://images.example.com/sample.jpg',
    'https://yourdomain.com/graphs/sample_product_graph.json'
);