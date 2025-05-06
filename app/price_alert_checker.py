import os
from datetime import datetime
from flask_mail import Message
from sqlalchemy import create_engine, text
from flask import current_app
from jinja2 import Template

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:root@localhost:5432/CompareKart")
engine = create_engine(DATABASE_URL)

def send_price_alert_email(to_email, product_name, current_price, alert_price, product_id, product_image=None):
    try:
        msg = Message(
            f"📉 Price Drop Alert: {product_name}",
            recipients=[to_email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # Load HTML template
        template_path = os.path.join(current_app.root_path, 'templates', 'price_alert_notification.html')
        with open(template_path, 'r') as f:
            html_template = f.read()
        
        # Render the template
        template = Template(html_template)
        html_content = template.render(
            product_name=product_name,
            current_price=f"₹{current_price:,.2f}",
            alert_price=f"₹{alert_price:,.2f}",
            product_image=product_image,
            product_url=f"{current_app.config['BASE_URL']}/product_display?id={product_id}",
            remove_alert_url=f"{current_app.config['BASE_URL']}/remove_price_alert/{product_id}",
            unsubscribe_url=f"{current_app.config['BASE_URL']}/unsubscribe?email={to_email}",
            year=datetime.now().year,
            request={'host_url': current_app.config['BASE_URL']}
        )

        msg.html = html_content
        current_app.extensions['mail'].send(msg)
        print(f"✅ Price alert email sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send price alert email: {str(e)}")
        return False

def check_price_alerts(app):
    """Check all active price alerts and send notifications if prices have dropped"""
    with app.app_context():
        with engine.begin() as conn:
            # Get all active alerts where price is now <= desired price
            alerts = conn.execute(text("""
                SELECT a.id, p.name, p.price, a.desired_price, a.email, p.image_link, p.id as product_id
                FROM price_alerts a
                JOIN products p ON p.id = a.product_id
                WHERE a.is_active = TRUE 
                AND p.price <= a.desired_price
                AND (a.triggered_at IS NULL OR p.last_updated > a.triggered_at)
            """)).fetchall()

            for alert in alerts:
                success = send_price_alert_email(
                    alert.email,
                    alert.name,
                    alert.price,
                    alert.desired_price,
                    alert.product_id,
                    alert.image_link
                )
                
                if success:
                    # Mark alert as triggered only if email was sent successfully
                    conn.execute(text("""
                        UPDATE price_alerts
                        SET triggered_at = NOW(),
                            is_active = FALSE
                        WHERE id = :alert_id
                    """), {"alert_id": alert.id})
                    print(f"✅ Alert {alert.id} processed and marked as triggered")

def check_price_alert_immediately(product_id):
    """Check alerts for a specific product immediately after price update"""
    from flask import current_app
    with current_app.app_context():
        with engine.begin() as conn:
            # Check all alerts for this product
            alerts = conn.execute(text("""
                SELECT a.id, p.name, p.price, a.desired_price, a.email, p.image_link, p.id as product_id
                FROM price_alerts a
                JOIN products p ON p.id = a.product_id
                WHERE a.is_active = TRUE 
                AND p.id = :product_id
                AND p.price <= a.desired_price
            """), {"product_id": product_id}).fetchall()

            for alert in alerts:
                success = send_price_alert_email(
                    alert.email,
                    alert.name,
                    alert.price,
                    alert.desired_price,
                    alert.product_id,
                    alert.image_link
                )
                
                if success:
                    conn.execute(text("""
                        UPDATE price_alerts
                        SET triggered_at = NOW(),
                            is_active = FALSE
                        WHERE id = :alert_id
                    """), {"alert_id": alert.id})
                    print(f"✅ Alert {alert.id} processed and marked as triggered")

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        check_price_alerts(app)