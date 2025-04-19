# price_alert_checker.py
import smtplib
from email.mime.text import MIMEText
from sqlalchemy import create_engine, text
import os

DATABASE_URL = "postgresql://postgres:root@localhost:5432/CompareKart"
engine = create_engine(DATABASE_URL)

def send_email_alert(to_email, product_name, current_price, desired_price):
    subject = f"📉 Price Drop Alert: {product_name}"
    body = f"""
    Good news! The price of "{product_name}" has dropped to ₹{current_price}, which is below your alert threshold of ₹{desired_price}!

    Visit CompareKart to view the deal now: https://comparekart.com/product_display?id=123

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
            SELECT p.id, p.name, p.price, a.email, a.desired_price
            FROM price_alerts a
            JOIN products p ON p.id = a.product_id
            WHERE p.price <= a.desired_price
        """)).fetchall()

        for row in results:
            send_email_alert(row.email, row.name, row.price, row.desired_price)

        # Optional: delete alerts that were triggered
        conn.execute(text("""
            DELETE FROM price_alerts
            WHERE product_id IN (
                SELECT p.id
                FROM products p
                JOIN price_alerts a ON a.product_id = p.id
                WHERE p.price <= a.desired_price
            )
        """))

if __name__ == "__main__":
    check_price_alerts()
