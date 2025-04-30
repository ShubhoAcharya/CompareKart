-- Updated Sql_setup.sql
CREATE DATABASE "CompareKart";

\c "CompareKart"

-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    icon VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create the 'products' table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    original_url TEXT NOT NULL,
    modified_url TEXT,
    name VARCHAR(512),
    price NUMERIC(10,2),
    rating NUMERIC(3,2),
    image_link TEXT,
    category_id INTEGER REFERENCES categories(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE,
    CONSTRAINT unique_original_url UNIQUE (original_url)
);

-- Create the 'price_alerts' table with improved structure
CREATE TABLE IF NOT EXISTS price_alerts (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    desired_price NUMERIC(10,2) NOT NULL,
    email VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    triggered_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_alert UNIQUE (product_id, email),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_products_last_updated ON products(last_updated);
CREATE INDEX IF NOT EXISTS idx_price_alerts_product_id ON price_alerts(product_id);
CREATE INDEX IF NOT EXISTS idx_price_alerts_is_active ON price_alerts(is_active);

-- Insert default categories
INSERT INTO categories (name, icon) VALUES 
('Electronics', 'fas fa-laptop'),
('TVs & Appliances', 'fas fa-tv'),
('Men', 'fas fa-male'),
('Women', 'fas fa-female'),
('Baby & Kids', 'fas fa-baby'),
('Home & Furniture', 'fas fa-couch'),
('Sports, Books & More', 'fas fa-football-ball'),
('Flights', 'fas fa-plane'),
('Offer Zone', 'fas fa-tags'),
('Grocery', 'fas fa-shopping-basket');

-- Ensure sequences are properly set
SELECT setval('products_id_seq', COALESCE((SELECT MAX(id) FROM products), 0) + 1);
SELECT setval('price_alerts_id_seq', COALESCE((SELECT MAX(id) FROM price_alerts), 0) + 1);