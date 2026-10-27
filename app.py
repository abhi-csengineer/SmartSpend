import os
from app import create_app

# Create application instance with environment or development settings
env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    # Bind to localhost; debug mode is controlled by the selected configuration.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port, debug=app.config.get('DEBUG', False))

