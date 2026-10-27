import os
import tempfile
import pytest
from app import create_app
from app.database import init_db

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    db_fd, db_path = tempfile.mkstemp(suffix='.db')

    app = create_app('testing')
    app.config.update({
        'DATABASE_PATH': db_path,
        'TESTING': True,
        'CSRF_ENABLED': False
    })

    with app.app_context():
        init_db(app)

    yield app

    # Cleanup temporary test database
    try:
        os.close(db_fd)
        if os.path.exists(db_path):
            os.unlink(db_path)
    except OSError:
        pass

@pytest.fixture
def client(app):
    """Test client for issuing HTTP requests."""
    return app.test_client()

@pytest.fixture
def auth(client):
    """Authentication helper for tests."""
    class AuthActions:
        def register(self, username='student1', email='student1@example.com', password='password123', full_name='Student One', currency='$'):
            return client.post('/auth/register', data={
                'username': username,
                'email': email,
                'password': password,
                'confirm_password': password,
                'full_name': full_name,
                'currency': currency
            }, follow_redirects=True)

        def login(self, login_input='student1', password='password123'):
            return client.post('/auth/login', data={
                'login_input': login_input,
                'password': password
            }, follow_redirects=True)

        def logout(self):
            return client.post('/auth/logout', follow_redirects=True)

    return AuthActions()

