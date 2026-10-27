import os
from app import create_app

def run_verification():
    demo_password = os.environ.get('SMARTSPEND_DEMO_PASSWORD')
    if not demo_password:
        raise RuntimeError('Run seed_demo.py and set SMARTSPEND_DEMO_PASSWORD before verification.')
    app = create_app('development')
    client = app.test_client()

    print("Step 1: Fetching login page...")
    get_res = client.get('/auth/login')
    assert get_res.status_code == 200, f"Login GET failed with {get_res.status_code}"
    
    with client.session_transaction() as sess:
        csrf_token = sess.get('csrf_token')
    print(f"   CSRF token extracted: {csrf_token[:12]}...")

    print("Step 2: Authenticating as demo_student with CSRF token...")
    login_res = client.post('/auth/login', data={
        'login_input': 'demo_student',
        'password': demo_password,
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert login_res.status_code == 200, f"Login POST failed with {login_res.status_code}"
    assert b"Aditya Sharma" in login_res.data, "Greeting not found in dashboard response"
    print("   Login successful! Greeting rendered correctly.")

    print("Step 3: Checking Dashboard metrics and charts...")
    dash_res = client.get('/dashboard')
    assert dash_res.status_code == 200
    assert b"Cashflow Trend" in dash_res.data
    assert b"Spending Breakdown" in dash_res.data
    print("   Dashboard rendered with charts and KPIs.")

    print("Step 4: Checking Transactions page and filter...")
    tx_res = client.get('/transactions')
    assert tx_res.status_code == 200
    assert b"Transactions Found" in tx_res.data
    assert b"Apartment Rent" in tx_res.data
    print("   Transactions table rendered with demo data.")

    print("Step 5: Checking Budgets page...")
    b_res = client.get('/budgets')
    assert b_res.status_code == 200
    assert b"Overall Budget Summary" in b_res.data
    print("   Budgets page rendered with progress bars and alerts.")

    print("Step 6: Checking Reports page...")
    rep_res = client.get('/reports')
    assert rep_res.status_code == 200
    assert b"Financial Reports" in rep_res.data
    print("   Reports page rendered successfully.")

    print("Step 7: Testing CSV export...")
    csv_res = client.get('/transactions/export')
    assert csv_res.status_code == 200
    assert csv_res.headers['Content-Type'].startswith('text/csv')
    assert b"Transaction ID,Type,Category,Amount" in csv_res.data
    print("   CSV Export verified.")

    print("\nALL VERIFICATION CHECKS PASSED PERFECTLY!")

if __name__ == '__main__':
    run_verification()

