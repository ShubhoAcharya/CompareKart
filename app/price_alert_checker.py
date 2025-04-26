# price_alert_checker.py
import smtplib
from email.mime.text import MIMEText
from sqlalchemy import create_engine, text
import os

DATABASE_URL = "postgresql://postgres:root@localhost:5432/CompareKart"
engine = create_engine(DATABASE_URL)

def send_email_alert(to_email, product_name, current_price, desired_price, alert_id, host_url):
    subject = f"📉 Price Drop Alert: {product_name}"
    body = f"""
    Good news! The price of "{product_name}" has dropped to ₹{current_price}, which is below your alert threshold of ₹{desired_price}!

    Visit CompareKart to view the deal now: {host_url}product_display?id=123

    To remove this alert: {host_url}remove_price_alert/{alert_id}

    - Your CompareKart Team
    """

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "comparekart@example.com"
    msg["To"] = to_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("shubhojit2021@gift.edu.in", "jyuc xvhg zkrl cdxl")
            server.send_message(msg)
            print(f"✅ Alert sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send alert: {e}")

def check_price_alerts():
    with engine.connect() as conn:
        results = conn.execute(text("""
            SELECT a.id, p.name, p.price, a.email, a.desired_price
            FROM price_alerts a
            JOIN products p ON p.id = a.product_id
            WHERE p.price <= a.desired_price
        """)).fetchall()

        for row in results:
            send_email_alert(
                row.email, 
                row.name, 
                row.price, 
                row.desired_price,
                row.id,
                "https://comparekart.com"  # Replace with your actual host URL
            )

        # Delete alerts that were triggered
        conn.execute(text("""
            DELETE FROM price_alerts
            WHERE id IN (
                SELECT a.id
                FROM price_alerts a
                JOIN products p ON a.product_id = p.id
                WHERE p.price <= a.desired_price
            )
        """))