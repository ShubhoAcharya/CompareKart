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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

