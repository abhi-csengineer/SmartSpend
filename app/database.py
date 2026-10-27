import sqlite3
import os
from flask import g, current_app

DEFAULT_EXPENSE_CATEGORIES = [
    ('Food & Dining', 'expense', 'utensils', '#f97316'),
    ('Housing & Rent', 'expense', 'home', '#3b82f6'),
    ('Transportation', 'expense', 'car', '#06b6d4'),
    ('Utilities', 'expense', 'zap', '#eab308'),
    ('Entertainment', 'expense', 'film', '#a855f7'),
    ('Healthcare', 'expense', 'activity', '#ec4899'),
    ('Shopping', 'expense', 'shopping-bag', '#14b8a6'),
    ('Education', 'expense', 'book-open', '#6366f1'),
    ('Personal Care', 'expense', 'smile', '#f43f5e'),
    ('Investments', 'expense', 'trending-up', '#10b981'),
    ('Other Expense', 'expense', 'more-horizontal', '#64748b'),
]

DEFAULT_INCOME_CATEGORIES = [
    ('Salary', 'income', 'briefcase', '#10b981'),
    ('Freelance & Consulting', 'income', 'laptop', '#06b6d4'),
    ('Investments & Dividends', 'income', 'trending-up', '#3b82f6'),
    ('Gifts & Grants', 'income', 'gift', '#a855f7'),
    ('Rental Income', 'income', 'key', '#eab308'),
    ('Other Income', 'income', 'plus-circle', '#64748b'),
]

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT '$',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
    icon TEXT DEFAULT 'tag',
    color TEXT DEFAULT '#64748b',
    is_default INTEGER DEFAULT 1,
    user_id INTEGER DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_cat_default_unique ON categories(name, type) WHERE user_id IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_cat_user_unique ON categories(name, type, user_id) WHERE user_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
    category TEXT NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    date TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON transactions(user_id, date);
CREATE INDEX IF NOT EXISTS idx_transactions_user_type ON transactions(user_id, type);
CREATE INDEX IF NOT EXISTS idx_transactions_user_cat ON transactions(user_id, category);

CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    month TEXT NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, category, month)
);

CREATE INDEX IF NOT EXISTS idx_budgets_user_month ON budgets(user_id, month);
"""

def get_db():
    """Open or return existing SQLite database connection for the current request."""
    if 'db' not in g:
        db_path = current_app.config['DATABASE_PATH']
        # Ensure parent directory exists for file-based sqlite databases
        if db_path != ':memory:':
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
            
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        # Enable SQLite foreign key constraints
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db

def close_db(e=None):
    """Close the database connection if open."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app=None):
    """Initialize database tables and default categories."""
    if app:
        with app.app_context():
            _init_db_context()
    else:
        _init_db_context()

def _init_db_context():
    db = get_db()
    db.executescript(SCHEMA_SQL)
    
    # Insert default categories if not already present
    for name, cat_type, icon, color in DEFAULT_EXPENSE_CATEGORIES:
        db.execute(
            """
            INSERT OR IGNORE INTO categories (name, type, icon, color, is_default, user_id)
            VALUES (?, ?, ?, ?, 1, NULL)
            """,
            (name, cat_type, icon, color)
        )
        
    for name, cat_type, icon, color in DEFAULT_INCOME_CATEGORIES:
        db.execute(
            """
            INSERT OR IGNORE INTO categories (name, type, icon, color, is_default, user_id)
            VALUES (?, ?, ?, ?, 1, NULL)
            """,
            (name, cat_type, icon, color)
        )
    db.commit()

