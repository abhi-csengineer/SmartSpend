import csv
import io

def test_dashboard_calculations(client, auth):
    """Test that dashboard balance is exactly income minus expenses."""
    auth.register()

    # Add 4000 income
    client.post('/transactions/add', data={
        'type': 'income', 'amount': '4000.00', 'category': 'Salary',
        'date': '2026-10-01', 'description': 'Monthly Pay'
    })

    # Add 1500 expense
    client.post('/transactions/add', data={
        'type': 'expense', 'amount': '1500.00', 'category': 'Housing & Rent',
        'date': '2026-10-02', 'description': 'Apartment Rent'
    })

    # Add 250 expense
    client.post('/transactions/add', data={
        'type': 'expense', 'amount': '250.00', 'category': 'Food & Dining',
        'date': '2026-10-05', 'description': 'Groceries'
    })

    # Balance should be 4000 - 1750 = 2250
    res = client.get('/dashboard?month=2026-10')
    assert res.status_code == 200
    assert b"2,250.00" in res.data
    assert b"4,000.00" in res.data
    assert b"1,750.00" in res.data

def test_reports_page_and_kpis(client, auth):
    """Test reports page renders KPIs and charts."""
    auth.register()

    client.post('/transactions/add', data={
        'type': 'income', 'amount': '2000.00', 'category': 'Salary',
        'date': '2026-10-01', 'description': 'Salary'
    })
    client.post('/transactions/add', data={
        'type': 'expense', 'amount': '600.00', 'category': 'Shopping',
        'date': '2026-10-04', 'description': 'Electronics'
    })

    res = client.get('/reports?months=6')
    assert res.status_code == 200
    assert b"Financial Reports &amp; Analytics" in res.data or b"Financial Reports & Analytics" in res.data
    assert b"2,000.00" in res.data
    assert b"600.00" in res.data
    assert b"1,400.00" in res.data
    assert b"Shopping" in res.data

def test_csv_export_format_and_headers(client, auth):
    """Test downloading transactions as CSV."""
    auth.register(currency='$')

    client.post('/transactions/add', data={
        'type': 'expense', 'amount': '89.99', 'category': 'Shopping',
        'date': '2026-10-18', 'description': 'New Keyboard'
    })

    res = client.get('/transactions/export')
    assert res.status_code == 200
    assert 'text/csv' in res.headers['Content-Type']
    assert 'attachment;' in res.headers['Content-Disposition']
    assert 'smartspend_transactions_' in res.headers['Content-Disposition']

    # Parse CSV content
    csv_file = io.StringIO(res.data.decode('utf-8'))
    reader = csv.reader(csv_file)
    rows = list(reader)

    header = rows[0]
    assert header == ['Transaction ID', 'Type', 'Category', 'Amount ($)', 'Date', 'Description', 'Created At']

    data_row = rows[1]
    assert data_row[1] == 'Expense'
    assert data_row[2] == 'Shopping'
    assert data_row[3] == '89.99'
    assert data_row[4] == '2026-10-18'
    assert data_row[5] == 'New Keyboard'

def test_404_error_page(client, auth):
    """Test 404 custom error page."""
    auth.register()
    res = client.get('/nonexistent-page-url')
    assert res.status_code == 404
    assert b"Page Not Found" in res.data

