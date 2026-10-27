from app.database import get_db

def test_profile_update_and_currency(client, auth, app):
    """Test updating user profile name and currency symbol."""
    auth.register(full_name='Original Name', currency='$')

    # Update profile
    res = client.post('/auth/profile', data={
        'action': 'update_profile',
        'full_name': 'Updated Name',
        'currency': '₹'
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b"Profile details updated successfully" in res.data
    assert b"Updated Name" in res.data

    # Verify that in transactions page, the currency is now displayed as ₹
    client.post('/transactions/add', data={
        'type': 'income', 'amount': '500.00', 'category': 'Salary',
        'date': '2026-10-20', 'description': 'Salary in INR'
    })
    res_dash = client.get('/dashboard')
    assert b"\xe2\x82\xb9" in res_dash.data or "₹".encode('utf-8') in res_dash.data

def test_change_password(client, auth):
    """Test user changing their password."""
    auth.register(username='secuser', password='oldpassword123')

    # Try with wrong current password
    res_bad = client.post('/auth/profile', data={
        'action': 'change_password',
        'current_password': 'wrongpassword',
        'new_password': 'newpassword456',
        'confirm_new_password': 'newpassword456'
    }, follow_redirects=True)
    assert b"Current password is incorrect" in res_bad.data

    # Try with mismatched confirmation
    res_mismatch = client.post('/auth/profile', data={
        'action': 'change_password',
        'current_password': 'oldpassword123',
        'new_password': 'newpassword456',
        'confirm_new_password': 'differentnew'
    }, follow_redirects=True)
    assert b"New passwords do not match" in res_mismatch.data

    # Successful password change
    res_ok = client.post('/auth/profile', data={
        'action': 'change_password',
        'current_password': 'oldpassword123',
        'new_password': 'newpassword456',
        'confirm_new_password': 'newpassword456'
    }, follow_redirects=True)
    assert b"Password changed successfully" in res_ok.data

    # Logout and verify login with new password works
    auth.logout()
    res_login_new = auth.login(login_input='secuser', password='newpassword456')
    assert res_login_new.status_code == 200
    assert b"Welcome back" in res_login_new.data

def test_budget_upsert_on_duplicate(client, auth, app):
    """Test setting a budget for an existing category/month updates instead of erroring."""
    auth.register()

    # Initial budget $300
    client.post('/budgets/add', data={
        'category': 'Entertainment',
        'month': '2026-11',
        'amount': '300.00'
    })

    # Add again for same category and month with $450
    res = client.post('/budgets/add', data={
        'category': 'Entertainment',
        'month': '2026-11',
        'amount': '450.00'
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b"450.00" in res.data

    # Verify only ONE row exists in database for this user, category, month
    with app.app_context():
        db = get_db()
        count = db.execute(
            "SELECT COUNT(*) FROM budgets WHERE category = 'Entertainment' AND month = '2026-11'"
        ).fetchone()[0]
        assert count == 1

def test_long_description_rejected(client, auth):
    """Test that overly long descriptions (> 255 chars) are rejected."""
    auth.register()

    long_desc = "X" * 300
    res = client.post('/transactions/add', data={
        'type': 'expense',
        'amount': '50.00',
        'category': 'Shopping',
        'date': '2026-10-20',
        'description': long_desc
    }, follow_redirects=True)

    assert res.status_code == 400
    assert b"Description must be 255 characters or fewer" in res.data

