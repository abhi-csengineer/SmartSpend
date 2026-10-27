"""
SmartSpend - Demo Data Seeder
Run this script to populate a realistic sample portfolio for teacher demonstration and viva.
Command: python seed_demo.py
"""
import sys
import secrets
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import create_app
from app.database import get_db, init_db

def seed_demo_data():
    demo_password = secrets.token_urlsafe(18)
    app = create_app('development')
    with app.app_context():
        init_db(app)
        db = get_db()

        # Check if demo user already exists
        user = db.execute("SELECT id FROM users WHERE username = ?", ('demo_student',)).fetchone()
        
        if user:
            print("Existing demo user found. Cleaning old demo data and rotating its password...")
            user_id = user['id']
            db.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (generate_password_hash(demo_password), user_id)
            )
            db.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
            db.execute("DELETE FROM budgets WHERE user_id = ?", (user_id,))
        else:
            print("Creating a new demo account with a one-time generated password.")
            pw_hash = generate_password_hash(demo_password)
            cursor = db.execute(
                """
                INSERT INTO users (username, email, password_hash, full_name, currency)
                VALUES (?, ?, ?, ?, ?)
                """,
                ('demo_student', 'demo@smartspend.edu', pw_hash, 'Aditya Sharma', '₹')
            )
            user_id = cursor.lastrowid

        today = datetime.now()
        current_month = today.strftime("%Y-%m")

        print("Populating category budgets for current month...")
        demo_budgets = [
            ('Food & Dining', current_month, 8000.00),
            ('Housing & Rent', current_month, 15000.00),
            ('Transportation', current_month, 3500.00),
            ('Entertainment', current_month, 2500.00),
            ('Utilities', current_month, 3000.00),
            ('Shopping', current_month, 5000.00),
        ]

        for cat, month, amt in demo_budgets:
            db.execute(
                """
                INSERT OR REPLACE INTO budgets (user_id, category, month, amount)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, cat, month, amt)
            )

        print("Populating realistic transactions across past 3 months...")
        
        # Helper to generate dates relative to today
        def d(days_ago):
            return (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")

        transactions = [
            # Income
            ('income', 45000.00, 'Salary', d(2), 'Software Developer Monthly Stipend / Salary'),
            ('income', 8500.00, 'Freelance & Consulting', d(12), 'Frontend UI Design for Local Business Client'),
            ('income', 45000.00, 'Salary', d(32), 'Previous Month Software Developer Stipend'),
            ('income', 5000.00, 'Gifts & Grants', d(45), 'Academic Excellence Merit Scholarship Award'),
            ('income', 45000.00, 'Salary', d(62), 'Software Developer Stipend'),
            ('income', 12000.00, 'Freelance & Consulting', d(70), 'Full Stack Python Website Development Project'),

            # Current month expenses
            ('expense', 15000.00, 'Housing & Rent', d(1), 'Monthly Apartment Rent Payment'),
            ('expense', 4200.00, 'Food & Dining', d(3), 'Supermarket Monthly Groceries & Supplies'),
            ('expense', 1250.00, 'Utilities', d(4), 'High-Speed Fiber Internet & Electricity Bill'),
            ('expense', 950.00, 'Transportation', d(6), 'Monthly Metro Transit SmartCard Recharge'),
            ('expense', 1850.00, 'Entertainment', d(7), 'Weekend Dinner & Movie with College Friends'),
            ('expense', 2300.00, 'Food & Dining', d(10), 'Departmental Team Lunch & Snacks'),
            ('expense', 3400.00, 'Shopping', d(14), 'Ergonomic Coding Keyboard & Study Desk Lamp'),
            ('expense', 850.00, 'Healthcare', d(18), 'Routine Health Checkup & Prescription Vitamins'),
            ('expense', 1200.00, 'Education', d(22), 'Cloud Computing & Python Certification Exam Fee'),

            # Previous month expenses
            ('expense', 15000.00, 'Housing & Rent', d(31), 'Monthly Apartment Rent Payment'),
            ('expense', 6200.00, 'Food & Dining', d(35), 'Groceries and Campus Dining'),
            ('expense', 2100.00, 'Utilities', d(38), 'Electricity and Water Utility Charges'),
            ('expense', 1400.00, 'Transportation', d(42), 'Train and Cab Commute'),
            ('expense', 4800.00, 'Shopping', d(48), 'College Reference Books and Winter Jacket'),
            ('expense', 1500.00, 'Entertainment', d(52), 'Music & Streaming Subscriptions'),

            # 2 months ago expenses
            ('expense', 15000.00, 'Housing & Rent', d(61), 'Monthly Apartment Rent Payment'),
            ('expense', 5800.00, 'Food & Dining', d(65), 'Dining and Grocery Supplies'),
            ('expense', 1900.00, 'Utilities', d(68), 'Electricity & Internet Service'),
            ('expense', 1100.00, 'Transportation', d(72), 'Public Transportation Passes'),
            ('expense', 2200.00, 'Education', d(78), 'Textbooks & Lab Supplies')
        ]

        for tx_type, amt, cat, tx_date, desc in transactions:
            db.execute(
                """
                INSERT INTO transactions (user_id, type, amount, category, date, description)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, tx_type, amt, cat, tx_date, desc)
            )

        db.commit()
        print("\n" + "="*60)
        print("SUCCESS: Demo data populated successfully!")
        print("Login credentials for viva presentation:")
        print("   Username: demo_student")
        print(f"   Password (generated for this run): {demo_password}")
        print("   Full Name: Aditya Sharma")
        print("   Currency: ₹")
        print("="*60 + "\n")

if __name__ == '__main__':
    seed_demo_data()

