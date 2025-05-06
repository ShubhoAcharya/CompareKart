# price_alert_checker.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy import create_engine, text
import os
from datetime import datetime
from jinja2 import Template

DATABASE_URL = "postgresql://postgres:root@localhost:5432/CompareKart"
engine = create_engine(DATABASE_URL)

def send_email_alert(to_email, product_name, current_price, desired_price, alert_id, host_url, product_image=None):
    subject = f"📉 Price Drop Alert: {product_name}"
    
    # HTML email template
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background-color: #4f46e5; color: white; padding: 20px; text-align: center; }
            .product-card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 20px 0; }
            .price-container { display: flex; justify-content: space-between; margin: 15px 0; }
            .price-box { padding: 10px; border-radius: 5px; width: 48%; }
            .current-price { background-color: #f3f4f6; }
            .alert-price { background-color: #ecfdf5; color: #065f46; }
            .cta-button {
                display: inline-block;
                background-color: #4f46e5;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                margin-top: 15px;
            }
            .footer { margin-top: 30px; font-size: 12px; color: #6b7280; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Price Drop Alert!</h1>
            </div>
            
            <p>Hello,</p>
            <p>The price of <strong>{{ product_name }}</strong> has dropped below your alert price!</p>
            
            <div class="product-card">
                {% if product_image %}
                <img src="{{ product_image }}" alt="{{ product_name }}" style="max-width: 100%; height: auto; margin-bottom: 15px;">
                {% endif %}
                
                <div class="price-container">
                    <div class="price-box current-price">
                        <div>Current Price</div>
                        <div style="font-size: 18px; font-weight: bold;">₹{{ current_price }}</div>
                    </div>
                    <div class="price-box alert-price">
                        <div>Your Alert Price</div>
                        <div style="font-size: 18px; font-weight: bold;">₹{{ desired_price }}</div>
                    </div>
                </div>
                
                <a href="{{ product_url }}" class="cta-button">View Product Now</a>
            </div>
            
            <p>To stop receiving alerts for this product, <a href="{{ remove_url }}">click here</a>.</p>
            
            <div class="footer">
                <p>© {{ year }} CompareKart. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Render the template
    template = Template(html_template)
    html_content = template.render(
        product_name=product_name,
        current_price=current_price,
        desired_price=desired_price,
        product_image=product_image,
        product_url=f"{host_url}/product_display?id={alert_id}",
        remove_url=f"{host_url}/remove_price_alert/{alert_id}",
        year=datetime.now().year
    )

    # Create message container
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = "comparekart@example.com"
    msg['To'] = to_email

    # Attach HTML content
    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("shubhojit2021@gift.edu.in", "jyuc xvhg zkrl cdxl")
            server.send_message(msg)
            print(f"✅ Alert sent to {to_email}")
            return True
    except Exception as e:
        print(f"❌ Failed to send alert: {e}")
        return False

def check_price_alerts():
    with engine.connect() as conn:
        # Get active alerts where price has dropped below desired price
        results = conn.execute(text("""
            SELECT a.id, p.name, p.price, a.desired_price, a.email, p.image_link
            FROM price_alerts a
            JOIN products p ON p.id = a.product_id
            WHERE a.is_active = TRUE 
            AND p.price <= a.desired_price
            AND (a.triggered_at IS NULL OR a.triggered_at < NOW() - INTERVAL '1 hour')
        """)).fetchall()

        for row in results:
            alert_id, product_name, current_price, desired_price, email, image_link = row
            
            # Send email notification
            email_sent = send_email_alert(
                email,
                product_name,
                current_price,
                desired_price,
                alert_id,
                "https://comparekart.com",  # Replace with your actual domain
                image_link
            )
            
            if email_sent:
                # Mark alert as triggered
                conn.execute(text("""
                    UPDATE price_alerts
                    SET triggered_at = NOW(),
                        is_active = FALSE
                    WHERE id = :alert_id
                """), {"alert_id": alert_id})
                
                print(f"✅ Alert {alert_id} processed and marked as triggered")

if __name__ == "__main__":
    check_price_alerts()