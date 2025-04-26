-- Create the database (only works if executed by a superuser)
CREATE DATABASE "CompareKart";

-- Switch to the newly created database
\c "CompareKart"

-- Create the 'products' table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    original_url TEXT NOT NULL,
    modified_url TEXT,
    name VARCHAR(512),
    price NUMERIC(10,2),
    rating NUMERIC(3,2),
    image_link TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE,
    CONSTRAINT unique_original_url UNIQUE (original_url)
);

-- Create the 'price_alerts' table
CREATE TABLE IF NOT EXISTS price_alerts (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    desired_price NUMERIC(10,2) NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_alert UNIQUE (product_id, email),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_products_last_updated ON products(last_updated);
CREATE INDEX IF NOT EXISTS idx_price_alerts_product_id ON price_alerts(product_id);

-- Ensure sequences are properly set
SELECT setval('products_id_seq', COALESCE((SELECT MAX(id) FROM products), 0) + 1);
SELECT setval('price_alerts_id_seq', COALESCE((SELECT MAX(id) FROM price_alerts), 0) + 1);
