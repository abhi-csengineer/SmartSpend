import sqlite3
from app.database import get_db

def test_create_income_and_expense_transactions(client, auth, app):
    """Test creating income and expense transactions."""
    auth.register()

    # Add income
    res_inc = client.post('/transactions/add', data={
        'type': 'income',
        'amount': '3500.00',
        'category': 'Salary',
        'date': '2026-10-15',
        'description': 'Monthly CS Developer salary'
    }, follow_redirects=True)
    assert res_inc.status_code == 200
    assert b"Salary" in res_inc.data
    assert b"3,500.00" in res_inc.data

    # Add expense
    res_exp = client.post('/transactions/add', data={
        'type': 'expense',
        'amount': '45.50',
        'category': 'Food & Dining',
        'date': '2026-10-16',
        'description': 'Lunch at cafe'
    }, follow_redirects=True)
    assert res_exp.status_code == 200
    assert b"Food &amp; Dining" in res_exp.data or b"Food & Dining" in res_exp.data
    assert b"45.50" in res_exp.data

def test_validation_rejects_negative_or_zero_amount(client, auth):
    """Ensure negative and 0 amounts are rejected."""
    auth.register()

    # Negative amount
    res_neg = client.post('/transactions/add', data={
        'type': 'expense',
        'amount': '-100.00',
        'category': 'Food & Dining',
        'date': '2026-10-16',
        'description': 'Invalid negative amount'
    }, follow_redirects=True)
    assert res_neg.status_code == 400
    assert b"Amount must be a positive number" in res_neg.data

    # Zero amount
    res_zero = client.post('/transactions/add', data={
        'type': 'expense',
        'amount': '0.00',
        'category': 'Food & Dining',
        'date': '2026-10-16',
        'description': 'Invalid zero amount'
    }, follow_redirects=True)
    assert res_zero.status_code == 400
    assert b"Amount must be a positive number" in res_zero.data

def test_validation_rejects_non_finite_and_sub_cent_amounts(client, auth):
    auth.register()
    for value in ('NaN', 'Infinity', '0.001'):
        response = client.post('/transactions/add', data={
            'type': 'expense', 'amount': value, 'category': 'Food & Dining',
            'date': '2026-10-16', 'description': 'Invalid amount'
        })
        assert response.status_code == 400

def test_edit_transaction(client, auth, app):
    """Test editing an existing transaction."""
    auth.register()

    # Add transaction
    client.post('/transactions/add', data={
        'type': 'expense',
        'amount': '120.00',
        'category': 'Shopping',
        'date': '2026-10-10',
        'description': 'Initial purchase'
    }, follow_redirects=True)

    with app.app_context():
        db = get_db()
        tx = db.execute("SELECT id FROM transactions WHERE description = 'Initial purchase'").fetchone()
        tx_id = tx['id']

    # Edit transaction
    res = client.post(f'/transactions/edit/{tx_id}', data={
        'type': 'expense',
        'amount': '150.00',
        'category': 'Shopping',
        'date': '2026-10-10',
        'description': 'Updated purchase'
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b"Transaction updated successfully" in res.data
    assert b"150.00" in res.data
    assert b"Updated purchase" in res.data

def test_delete_transaction(client, auth, app):
    """Test deleting an existing transaction."""
    auth.register()

    client.post('/transactions/add', data={
        'type': 'expense',
        'amount': '80.00',
        'category': 'Entertainment',
        'date': '2026-10-12',
        'description': 'Movie night'
    }, follow_redirects=True)

    with app.app_context():
        db = get_db()
        tx = db.execute("SELECT id FROM transactions WHERE description = 'Movie night'").fetchone()
        tx_id = tx['id']

    # Delete
    res = client.post(f'/transactions/delete/{tx_id}', follow_redirects=True)
    assert res.status_code == 200
    assert b"Transaction deleted successfully" in res.data
    assert b"Movie night" not in res.data

def test_user_isolation_for_transactions(client, auth, app):
    """
    CRITICAL SECURITY TEST:
    Verify User B cannot view, edit, or delete User A's transactions.
    """
    # User A registers and creates a transaction
    auth.register(username='usera', email='usera@example.com', full_name='User Alpha')
    client.post('/transactions/add', data={
        'type': 'income',
        'amount': '5000.00',
        'category': 'Salary',
        'date': '2026-10-01',
        'description': 'User A Secret Bonus'
    }, follow_redirects=True)

    with app.app_context():
        db = get_db()
        tx_a = db.execute("SELECT id FROM transactions WHERE description = 'User A Secret Bonus'").fetchone()
        tx_a_id = tx_a['id']

    auth.logout()

    # User B registers and checks their transactions
    auth.register(username='userb', email='userb@example.com', full_name='User Beta')
    res_b_index = client.get('/transactions')
    assert b"User A Secret Bonus" not in res_b_index.data

    # User B attempts to edit User A's transaction
    res_b_edit = client.post(f'/transactions/edit/{tx_a_id}', data={
        'type': 'expense',
        'amount': '10.00',
        'category': 'Food & Dining',
        'date': '2026-10-01',
        'description': 'Hacked'
    }, follow_redirects=True)
    assert b"Transaction not found or access denied" in res_b_edit.data

    # User B attempts to delete User A's transaction
    res_b_del = client.post(f'/transactions/delete/{tx_a_id}', follow_redirects=True)
    assert b"Transaction not found or could not be deleted" in res_b_del.data

    # Verify transaction was NOT modified or deleted in database
    with app.app_context():
        db = get_db()
        tx_still_exists = db.execute("SELECT amount, description FROM transactions WHERE id = ?", (tx_a_id,)).fetchone()
        assert tx_still_exists is not None
        assert tx_still_exists['amount'] == 5000.00
        assert tx_still_exists['description'] == 'User A Secret Bonus'

def test_transaction_filters_and_search(client, auth):
    """Test filtering transactions by category, type, date range, and search."""
    auth.register()

    # Add 3 transactions
    client.post('/transactions/add', data={
        'type': 'expense', 'amount': '25.00', 'category': 'Food & Dining',
        'date': '2026-10-05', 'description': 'Breakfast bagel'
    })
    client.post('/transactions/add', data={
        'type': 'expense', 'amount': '75.00', 'category': 'Utilities',
        'date': '2026-10-10', 'description': 'Electric bill'
    })
    client.post('/transactions/add', data={
        'type': 'income', 'amount': '1200.00', 'category': 'Freelance & Consulting',
        'date': '2026-10-15', 'description': 'Web design client'
    })

    # Filter by type=income
    res_inc = client.get('/transactions?type=income')
    assert b"Web design client" in res_inc.data
    assert b"Breakfast bagel" not in res_inc.data

    # Filter by category='Utilities'
    res_cat = client.get('/transactions?category=Utilities')
    assert b"Electric bill" in res_cat.data
    assert b"Breakfast bagel" not in res_cat.data

    # Filter by search='bagel'
    res_search = client.get('/transactions?search=bagel')
    assert b"Breakfast bagel" in res_search.data
    assert b"Electric bill" not in res_search.data

    # Filter by date range: 2026-10-08 to 2026-10-12
    res_date = client.get('/transactions?start_date=2026-10-08&end_date=2026-10-12')
    assert b"Electric bill" in res_date.data
    assert b"Breakfast bagel" not in res_date.data
    assert b"Web design client" not in res_date.data

