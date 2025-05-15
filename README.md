CompareKart - Price Comparison Tool
![Screenshot](.app/static/images/Screenshot 2025-05-10 204151.png)


CompareKart is a web application that helps users compare product prices across different e-commerce platforms like Amazon and Flipkart. It also provides price history tracking and alert features.

Features
🛒 Real-time price comparison between Amazon and Flipkart
📈 Price history tracking with interactive graphs
🔔 Price drop alerts via email
📊 Product specifications comparison
📤 Export comparison data to CSV
🔄 Automatic price updates (every 12 hours)

Technology Stack
Backend: Python with Flask
Frontend: HTML, CSS, JavaScript
Database: PostgreSQL
Web Scraping: Selenium
Email: Flask-Mail
Scheduling: APScheduler
Deployment: (Configure as needed)


Configuration
The following environment variables need to be configured:

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER=comparekart@example.com
BASE_URL=http://localhost:5000
DATABASE_URL=postgresql://username:password@localhost:5432/CompareKart


Usage
Visit http://localhost:5000 in your browser
Enter a product URL from Amazon or Flipkart
View price comparison and historical data
Set price alerts for products


API Endpoints
POST /process_url - Process a product URL
GET /get_product_details/<id> - Get product details
GET /get_graph_data - Get price history graph data
POST /set_price_alert - Set a price alert
GET /compare_page - View comparison page
GET /export_comparison - Export comparison data as CSV
