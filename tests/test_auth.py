def test_register_success(client, auth):
    """Test successful user registration and auto-login."""
    response = auth.register(username='alice', email='alice@example.com', full_name='Alice Smith')
    assert response.status_code == 200
    assert b"Welcome to SmartSpend, Alice Smith" in response.data
    assert b"Financial Dashboard" in response.data

def test_register_duplicate_username(client, auth):
    """Test that duplicate username is rejected."""
    auth.register(username='bob', email='bob1@example.com')
    auth.logout()

    response = auth.register(username='bob', email='bob2@example.com')
    assert b"Username is already taken" in response.data

def test_register_duplicate_email(client, auth):
    """Test that duplicate email is rejected."""
    auth.register(username='charlie1', email='charlie@example.com')
    auth.logout()

    response = auth.register(username='charlie2', email='charlie@example.com')
    assert b"Email is already registered" in response.data

def test_register_password_mismatch(client):
    """Test that mismatched passwords fail registration."""
    response = client.post('/auth/register', data={
        'username': 'david',
        'email': 'david@example.com',
        'full_name': 'David Jones',
        'password': 'password123',
        'confirm_password': 'different_password',
        'currency': '$'
    }, follow_redirects=True)
    assert b"Passwords do not match" in response.data

def test_login_success(client, auth):
    """Test login with valid credentials."""
    auth.register(username='emma', email='emma@example.com', password='secretpassword')
    auth.logout()

    response = auth.login(login_input='emma', password='secretpassword')
    assert response.status_code == 200
    assert b"Welcome back" in response.data
    assert b"Financial Dashboard" in response.data

def test_login_with_email(client, auth):
    """Test login using email instead of username."""
    auth.register(username='felix', email='felix@example.com', password='secretpassword')
    auth.logout()

    response = auth.login(login_input='felix@example.com', password='secretpassword')
    assert response.status_code == 200
    assert b"Welcome back" in response.data

def test_login_invalid_password(client, auth):
    """Test login with wrong password."""
    auth.register(username='grace', email='grace@example.com', password='correct_password')
    auth.logout()

    response = auth.login(login_input='grace', password='wrong_password')
    assert b"Invalid username/email or password" in response.data

def test_logout(client, auth):
    """Test user logout."""
    auth.register()
    response = auth.logout()
    assert b"You have been securely logged out" in response.data
    
    # Verify protected page requires login now
    dash_response = client.get('/', follow_redirects=True)
    assert b"Please log in to access this page" in dash_response.data

def test_protected_routes_redirect(client):
    """Ensure unauthenticated access to protected routes redirects to login."""
    routes = ['/', '/dashboard', '/transactions', '/transactions/add', '/budgets', '/reports']
    for r in routes:
        res = client.get(r, follow_redirects=False)
        assert res.status_code == 302
        assert '/auth/login' in res.headers['Location']

def test_login_rejects_network_path_redirect(client, auth):
    auth.register()
    auth.logout()
    response = client.post('/auth/login?next=//example.com', data={
        'login_input': 'student1', 'password': 'password123'
    })
    assert response.status_code == 302
    assert response.headers['Location'] == '/dashboard'

def test_logout_is_post_only(client, auth):
    auth.register()
    response = client.get('/auth/logout')
    assert response.status_code == 405
    assert client.get('/dashboard').status_code == 200

def test_csrf_rejects_missing_token(app):
    app.config['CSRF_ENABLED'] = True
    client = app.test_client()
    response = client.post('/auth/register', data={
        'username': 'csrfuser', 'email': 'csrf@example.com',
        'password': 'password123', 'confirm_password': 'password123',
        'full_name': 'CSRF User'
    })
    assert response.status_code == 400

