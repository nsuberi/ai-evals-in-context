"""Acme Support Bot - Sample Application"""

from flask import Flask, jsonify
from jinja2 import FileSystemLoader, ChoiceLoader
import os
from pathlib import Path


def combine_prefix(base, suffix):
    """Combine APPLICATION_ROOT with blueprint's own prefix.

    Args:
        base: The APPLICATION_ROOT prefix (e.g., '/ai-evals')
        suffix: The blueprint's internal prefix (e.g., '/governance')

    Returns:
        Combined prefix or None if both are empty
    """
    if base and suffix:
        return f"{base}{suffix}"
    return base or suffix or None


def create_app(testing=False):
    """Create and configure the Flask application"""
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    template_folder = project_root / 'templates'
    viewer_template_folder = project_root / 'viewer' / 'templates'
    static_folder = project_root / 'static'

    # URL prefix for all routes (used when behind CloudFront at /ai-evals/*)
    # Flask requires url_prefix to be None or start with '/', empty string is invalid
    url_prefix = os.getenv('APPLICATION_ROOT', '') or None

    # Set static_url_path to include the prefix so url_for('static', ...) generates correct URLs
    static_url_path = f"{url_prefix}/static" if url_prefix else '/static'

    app = Flask(__name__,
                template_folder=str(template_folder),
                static_folder=str(static_folder),
                static_url_path=static_url_path)

    # Add viewer templates as additional search path
    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(str(template_folder)),
        FileSystemLoader(str(viewer_template_folder))
    ])

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['TESTING'] = testing
    if url_prefix:
        app.config['APPLICATION_ROOT'] = url_prefix

    # Register blueprints with URL prefix (for CloudFront routing)
    # Each blueprint's internal prefix is combined with APPLICATION_ROOT
    from tsr.api import tsr_api
    from viewer.governance import governance

    # tsr_api has internal prefix '/api/tsr'
    app.register_blueprint(tsr_api, url_prefix=combine_prefix(url_prefix, '/api/tsr'))

    # governance has internal prefix '/governance'
    app.register_blueprint(governance, url_prefix=combine_prefix(url_prefix, '/governance'))

    # Register existing blueprints
    # app_bp has no internal prefix (root routes)
    from .routes import app_bp
    app.register_blueprint(app_bp, url_prefix=url_prefix)

    # Register viewer blueprint
    # viewer_bp has internal prefix '/viewer'
    from viewer.routes import viewer_bp
    app.register_blueprint(viewer_bp, url_prefix=combine_prefix(url_prefix, '/viewer'))

    # Simple health check endpoint (no database dependency)
    # Register both with and without prefix for ALB health checks
    health_route = '/health'
    prefixed_health = f"{url_prefix}/health" if url_prefix else '/health'

    @app.route(health_route)
    @app.route(prefixed_health)
    def health_check():
        return jsonify({'status': 'healthy', 'service': 'ai-testing-resource'}), 200

    # Setup lazy database session initialization
    setup_database_session(app)

    return app


def setup_database_session(app):
    """Setup database session lifecycle using Flask's application context"""

    @app.before_request
    def create_session():
        """Create session before each request"""
        from flask import g
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker, scoped_session
        from config import TSR_DATABASE_URL
        from tsr.repository import TSRRepository
        from tsr.api import init_tsr_api
        from viewer.governance import init_governance

        # Create engine and session factory lazily on first request
        if not hasattr(app, '_tsr_session_factory'):
            engine = create_engine(
                TSR_DATABASE_URL,
                pool_pre_ping=True,  # Verify connections before using
                pool_recycle=3600,   # Recycle connections after 1 hour
            )
            # Create database tables if they don't exist
            from tsr.database import create_tables
            create_tables(engine)

            session_factory = sessionmaker(bind=engine)
            app._tsr_session_factory = scoped_session(session_factory)

        # Create session for this request
        session = app._tsr_session_factory()
        g.tsr_session = session

        # Create repository for this request
        repository = TSRRepository(session)
        g.tsr_repository = repository

        # Initialize blueprints with repository
        init_tsr_api(repository)
        init_governance(repository)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Close session after request"""
        if hasattr(app, '_tsr_session_factory'):
            app._tsr_session_factory.remove()  # Remove scoped session
