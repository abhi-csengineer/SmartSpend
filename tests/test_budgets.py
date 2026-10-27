from app.database import get_db

def test_create_and_view_budget(client, auth):
    """Test creating a category budget for a month."""
    auth.register()

    res = client.post('/budgets/add', data={
        'category': 'Food & Dining',
        'month': '2026-10',
        'amount': '400.00'
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b"Budget for Food &amp; Dining set to" in res.data or b"Budget for Food & Dining set to" in res.data
    assert b"400.00" in res.data

def test_budget_rejects_non_finite_and_sub_cent_amounts(client, auth):
    auth.register()
    for value in ('NaN', 'Infinity', '0.001'):
        response = client.post('/budgets/add', data={
            'category': 'Food & Dining', 'month': '2026-10', 'amount': value
        })
        assert response.status_code == 302
        assert b'Food &amp; Dining' not in response.data

def test_budget_utilization_and_warning_badges(client, auth):
    """
    Test budget status calculations:
    - Normal when < 80%
    - Warning when >= 80% and < 100%
    - Danger when >= 100%
    """
    auth.register()

    # Create budget of $500 for Food & Dining in 2026-10
    client.post('/budgets/add', data={
        'category': 'Food & Dining',
        'month': '2026-10',
        'amount': '500.00'
    })

    # Initial check: 0 spent -> On Track
    res_init = client.get('/budgets?month=2026-10')
    assert b"On Track (0.0%)" in res_init.data

    # Spend $420 (84% of 500) -> Near Limit Warning
    client.post('/transactions/add', data={
        'type': 'expense',
        'amount': '420.00',
        'category': 'Food & Dining',
        'date': '2026-10-10',
        'description': 'Groceries'
    })

    res_warn = client.get('/budgets?month=2026-10')
    assert b"Near Limit (84.0%)" in res_warn.data

    # Spend another $100 -> Total $520 (104%) -> Over Budget Alert
    client.post('/transactions/add', data={
        'type': 'expense',
        'amount': '100.00',
        'category': 'Food & Dining',
        'date': '2026-10-15',
        'description': 'Dinner out'
    })

    res_over = client.get('/budgets?month=2026-10')
    assert b"Over Budget" in res_over.data

def test_edit_budget(client, auth, app):
    """Test editing a budget limit."""
    auth.register()

    client.post('/budgets/add', data={
        'category': 'Transportation',
        'month': '2026-10',
        'amount': '150.00'
    })

    with app.app_context():
        db = get_db()
        b_id = db.execute("SELECT id FROM budgets WHERE category = 'Transportation'").fetchone()['id']

    # Update to $200
    res = client.post(f'/budgets/edit/{b_id}', data={
        'amount': '200.00',
        'month': '2026-10'
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b"Budget updated successfully" in res.data
    assert b"200.00" in res.data

def test_delete_budget(client, auth, app):
    """Test deleting a budget."""
    auth.register()

    client.post('/budgets/add', data={
        'category': 'Healthcare',
        'month': '2026-10',
        'amount': '250.00'
    })

    with app.app_context():
        db = get_db()
        b_id = db.execute("SELECT id FROM budgets WHERE category = 'Healthcare'").fetchone()['id']

    res = client.post(f'/budgets/delete/{b_id}', data={'month': '2026-10'}, follow_redirects=True)
    assert res.status_code == 200
    assert b"Budget removed successfully" in res.data

def test_user_isolation_for_budgets(client, auth, app):
    """
    CRITICAL SECURITY TEST:
    Ensure User B cannot modify or delete User A's budget.
    """
    auth.register(username='user1', email='user1@example.com')
    client.post('/budgets/add', data={
        'category': 'Utilities',
        'month': '2026-10',
        'amount': '300.00'
    })

    with app.app_context():
        db = get_db()
        b_id = db.execute("SELECT id FROM budgets WHERE category = 'Utilities'").fetchone()['id']

    auth.logout()

    # User 2 logs in
    auth.register(username='user2', email='user2@example.com')

    # User 2 tries to edit User 1's budget
    res_edit = client.post(f'/budgets/edit/{b_id}', data={'amount': '999.00', 'month': '2026-10'}, follow_redirects=True)
    assert b"Budget not found or access denied" in res_edit.data

    # User 2 tries to delete User 1's budget
    res_del = client.post(f'/budgets/delete/{b_id}', data={'month': '2026-10'}, follow_redirects=True)
    assert b"Budget not found or access denied" in res_del.data

    # Verify User 1's budget remains intact
    with app.app_context():
        db = get_db()
        b_still = db.execute("SELECT amount FROM budgets WHERE id = ?", (b_id,)).fetchone()
        assert b_still['amount'] == 300.00

