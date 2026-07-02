"""
order_processing.py
--------------------
Simulated e-commerce order processing module.

!! INTENTIONALLY VIOLATES multiple software design principles !!
   - Single Responsibility Principle (SRP)
   - Dependency Inversion Principle (DIP)

This file is intended to be used as an evaluation target for the
Autonomous Co-Architect agent to detect and report architectural violations.
"""

import json
import hashlib
import datetime


# =============================================================================
# VIOLATION 1 — SRP + DIP
# Class name "Manager" is a red flag (SRP_Naming_AntiPattern).
# The class handles: user validation, password hashing, DB writes, and email
# sending — far too many responsibilities for a single class.
# It also directly instantiates concrete dependencies (DIP_Hardcoded_Dependency).
# =============================================================================
class UserManager:
    def __init__(self):
        # DIP VIOLATION: directly instantiating concrete infrastructure classes
        self.db = DatabaseClient()
        self.mailer = SMTPMailer()
        self.logger = FileLogger()

    def register_user(self, username: str, email: str, password: str) -> dict:
        """Register a new user — validates, hashes password, saves, and sends welcome email."""
        # Responsibility 1: input validation
        if not username or len(username) < 3:
            raise ValueError("Username must be at least 3 characters.")
        if "@" not in email:
            raise ValueError("Invalid email address.")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters.")

        # Responsibility 2: password hashing
        hashed = hashlib.sha256(password.encode()).hexdigest()

        # Responsibility 3: database persistence
        user_record = {"username": username, "email": email, "password": hashed}
        self.db.insert("users", user_record)

        # Responsibility 4: send welcome email (should not be here!)
        self.mailer.send(
            to=email,
            subject="Welcome!",
            body=f"Hi {username}, your account has been created."
        )

        # Responsibility 5: audit logging
        self.logger.log(f"[{datetime.datetime.now()}] User '{username}' registered.")
        return user_record

    def update_password(self, username: str, new_password: str) -> bool:
        """Update a user's password — directly re-hashes and talks to DB."""
        hashed = hashlib.sha256(new_password.encode()).hexdigest()
        self.db.update("users", {"username": username}, {"password": hashed})
        self.logger.log(f"Password updated for '{username}'.")
        return True

    def delete_user(self, username: str) -> bool:
        self.db.delete("users", {"username": username})
        self.logger.log(f"User '{username}' deleted.")
        return True

    def get_user(self, username: str) -> dict:
        return self.db.find_one("users", {"username": username})

    def list_users(self) -> list:
        return self.db.find_all("users")

    def deactivate_user(self, username: str) -> bool:
        self.db.update("users", {"username": username}, {"active": False})
        return True

    def send_password_reset(self, email: str) -> None:
        """Send a password reset email — another responsibility lumped in."""
        reset_token = hashlib.md5(email.encode()).hexdigest()
        self.mailer.send(
            to=email,
            subject="Password Reset",
            body=f"Your reset token is: {reset_token}"
        )
        self.logger.log(f"Password reset sent to '{email}'.")


# =============================================================================
# VIOLATION 2 — SRP + DIP
# "OrderHandler" is another generic catch-all name (SRP_Naming_AntiPattern).
# It manages order creation, payment processing, inventory checks, shipping
# label generation, and notification — all in one class.
# Every infrastructure object is hardcoded (DIP_Hardcoded_Dependency).
# =============================================================================
class OrderHandler:
    def __init__(self):
        # DIP VIOLATIONS: all concrete dependencies are hardcoded
        self.inventory = WarehouseInventorySystem()
        self.payment = StripePaymentGateway()
        self.notifier = TwilioSMSNotifier()
        self.shipping = FedExShippingClient()
        self.db = DatabaseClient()
        self.logger = FileLogger()

    def place_order(self, user_id: str, items: list, card_token: str) -> dict:
        """
        Place a new order.
        Responsibilities: inventory check, payment, order save, shipping, notification.
        """
        # Responsibility 1: inventory validation
        for item in items:
            stock = self.inventory.check_stock(item["sku"])
            if stock < item["quantity"]:
                raise RuntimeError(f"Insufficient stock for SKU {item['sku']}.")

        # Responsibility 2: calculate total
        total = sum(item["price"] * item["quantity"] for item in items)

        # Responsibility 3: charge the customer
        charge_result = self.payment.charge(card_token, total)
        if not charge_result.get("success"):
            raise RuntimeError("Payment failed.")

        # Responsibility 4: persist the order
        order = {
            "user_id": user_id,
            "items": items,
            "total": total,
            "status": "confirmed",
            "created_at": str(datetime.datetime.now()),
        }
        self.db.insert("orders", order)

        # Responsibility 5: generate shipping label
        label = self.shipping.create_label(user_id, items)
        order["shipping_label"] = label

        # Responsibility 6: send SMS notification
        self.notifier.send_sms(user_id, f"Your order of ${total:.2f} has been placed!")

        # Responsibility 7: audit log
        self.logger.log(f"Order placed for user '{user_id}', total=${total:.2f}.")
        return order

    def cancel_order(self, order_id: str) -> bool:
        order = self.db.find_one("orders", {"id": order_id})
        if order:
            # Responsibility: refund through payment gateway
            self.payment.refund(order["charge_id"])
            # Responsibility: update inventory
            for item in order["items"]:
                self.inventory.restock(item["sku"], item["quantity"])
            self.db.update("orders", {"id": order_id}, {"status": "cancelled"})
            self.notifier.send_sms(order["user_id"], "Your order has been cancelled.")
            self.logger.log(f"Order '{order_id}' cancelled.")
        return True

    def get_order_history(self, user_id: str) -> list:
        return self.db.find_all("orders", {"user_id": user_id})

    def generate_invoice(self, order_id: str) -> str:
        """Generate a plain-text invoice — yet another concern mixed in."""
        order = self.db.find_one("orders", {"id": order_id})
        lines = [f"INVOICE — Order {order_id}", "-" * 40]
        for item in order.get("items", []):
            lines.append(f"  {item['name']} x{item['quantity']}  ${item['price']:.2f}")
        lines.append(f"  TOTAL: ${order['total']:.2f}")
        return "\n".join(lines)

    def export_orders_to_json(self, user_id: str) -> str:
        """Export all orders to JSON — data serialisation is a separate responsibility."""
        orders = self.db.find_all("orders", {"user_id": user_id})
        return json.dumps(orders, indent=2)


# =============================================================================
# VIOLATION 3 — SRP + DIP
# "ReportingUtility" (SRP_Naming_AntiPattern on 'utility').
# Mixes analytics, CSV export, PDF generation, and emailing reports.
# Also exceeds the 7-method threshold (SRP_Too_Many_Methods).
# =============================================================================
class ReportingUtility:
    def __init__(self):
        # DIP VIOLATIONS: all concrete
        self.db = DatabaseClient()
        self.mailer = SMTPMailer()
        self.logger = FileLogger()

    def get_daily_sales(self, date: str) -> list:
        return self.db.find_all("orders", {"date": date})

    def get_monthly_revenue(self, month: int, year: int) -> float:
        orders = self.db.find_all("orders", {"month": month, "year": year})
        return sum(o.get("total", 0) for o in orders)

    def get_top_products(self, limit: int = 10) -> list:
        orders = self.db.find_all("orders")
        product_counts: dict = {}
        for order in orders:
            for item in order.get("items", []):
                sku = item["sku"]
                product_counts[sku] = product_counts.get(sku, 0) + item["quantity"]
        sorted_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_products[:limit]

    def export_to_csv(self, data: list, filename: str) -> str:
        """CSV export — a completely separate responsibility."""
        rows = [",".join(str(v) for v in row.values()) for row in data]
        csv_content = "\n".join(rows)
        with open(filename, "w") as f:
            f.write(csv_content)
        self.logger.log(f"Exported {len(data)} rows to '{filename}'.")
        return filename

    def generate_pdf_report(self, title: str, data: list) -> bytes:
        """PDF generation — another responsibility shoved in."""
        # DIP VIOLATION: instantiating a concrete PDF renderer inside the method
        renderer = WeasyPrintPDFRenderer()
        html = f"<h1>{title}</h1><pre>{json.dumps(data, indent=2)}</pre>"
        return renderer.render(html)

    def email_report(self, recipient: str, subject: str, report_bytes: bytes) -> None:
        """Email a report — yet another concern (SRP violation)."""
        self.mailer.send(
            to=recipient,
            subject=subject,
            body="Please find the attached report.",
            attachment=report_bytes
        )

    def archive_old_reports(self, older_than_days: int) -> int:
        """Archive stale records — storage management mixed with reporting."""
        cutoff = datetime.datetime.now() - datetime.timedelta(days=older_than_days)
        old_orders = self.db.find_all("orders", {"before": str(cutoff)})
        for order in old_orders:
            self.db.update("orders", {"id": order["id"]}, {"archived": True})
        self.logger.log(f"Archived {len(old_orders)} orders older than {older_than_days} days.")
        return len(old_orders)

    def get_user_lifetime_value(self, user_id: str) -> float:
        """Calculates CLV — mixing financial analytics into a reporting class."""
        orders = self.db.find_all("orders", {"user_id": user_id})
        return sum(o.get("total", 0) for o in orders)


# =============================================================================
# Stub infrastructure classes — the concrete implementations that should be
# injected via abstractions/interfaces, but are instead hardcoded above.
# =============================================================================

class DatabaseClient:
    def insert(self, collection: str, record: dict): pass
    def update(self, collection: str, query: dict, update: dict): pass
    def delete(self, collection: str, query: dict): pass
    def find_one(self, collection: str, query: dict) -> dict: return {}
    def find_all(self, collection: str, query: dict = None) -> list: return []

class SMTPMailer:
    def send(self, to: str, subject: str, body: str, attachment: bytes = None): pass

class FileLogger:
    def log(self, message: str): print(message)

class WarehouseInventorySystem:
    def check_stock(self, sku: str) -> int: return 100
    def restock(self, sku: str, quantity: int): pass

class StripePaymentGateway:
    def charge(self, token: str, amount: float) -> dict: return {"success": True, "charge_id": "ch_123"}
    def refund(self, charge_id: str): pass

class TwilioSMSNotifier:
    def send_sms(self, user_id: str, message: str): pass

class FedExShippingClient:
    def create_label(self, user_id: str, items: list) -> str: return "LABEL-XYZ"

class WeasyPrintPDFRenderer:
    def render(self, html: str) -> bytes: return html.encode()
