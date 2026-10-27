import os
import click
from flask import Flask, render_template, request, session, g
from config import config_by_name
from app.database import init_db, close_db
from app.utils import (
    generate_csrf_token,
    validate_csrf,
    load_logged_in_user,
    format_currency,
    format_date,
    format_month
)

def create_app(config_name=None):
    """Application factory for SmartSpend."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    config_obj = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(config_obj)

    if config_name == 'production' and not app.config.get('SECRET_KEY'):
        raise RuntimeError('SECRET_KEY must be set when running in production.')

    # Disable strict slashes so /transactions and /transactions/ both resolve directly
    app.url_map.strict_slashes = False

    # Ensure instance directory exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Database teardown hook
    app.teardown_appcontext(close_db)

    # CLI command: flask init-db
    @app.cli.command('init-db')
    def init_db_command():
        """Initialize SQLite database with schema and default categories."""
        init_db(app)
        click.echo("SmartSpend database initialized successfully.")

    # Auto-initialize database on startup if database file doesn't exist
    with app.app_context():
        db_path = app.config.get('DATABASE_PATH')
        if db_path and db_path != ':memory:' and not os.path.exists(db_path):
            init_db(app)

    # Authentication & User Context
    @app.before_request
    def before_request_handler():
        # Ensure CSRF token is in session
        generate_csrf_token()
        # Verify CSRF for state-changing HTTP requests unless CSRF is disabled (e.g. in test suite)
        if app.config.get('CSRF_ENABLED', True):
            validate_csrf()
        # Populate g.current_user
        load_logged_in_user()

    # Context Processors for Templates
    @app.context_processor
    def inject_template_globals():
        return {
            'csrf_token': generate_csrf_token,
            'current_user': g.current_user if hasattr(g, 'current_user') else None
        }

    # Custom Jinja Filters
    app.jinja_env.filters['currency'] = format_currency
    app.jinja_env.filters['format_date'] = format_date
    app.jinja_env.filters['format_month'] = format_month

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.transactions import transactions_bp
    from app.routes.budgets import budgets_bp
    from app.routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(reports_bp)

    # Error Handlers
    @app.errorhandler(400)
    def bad_request_error(error):
        return render_template(
            'errors/400.html',
            error_title="400 Bad Request",
            error_message=str(error.description or "The request was invalid or could not be verified.")
        ), 400

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template(
            'errors/404.html',
            error_title="404 Page Not Found",
            error_message="The financial page or resource you requested does not exist."
        ), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template(
            'errors/500.html',
            error_title="500 Server Error",
            error_message="An unexpected system error occurred. Please try again later."
        ), 500

    return app

