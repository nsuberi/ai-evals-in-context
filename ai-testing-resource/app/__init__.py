"""Acme Support Bot - Sample Application"""

from flask import Flask
import os
from pathlib import Path


def create_app(testing=False):
    """Create and configure the Flask application"""
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    template_folder = project_root / 'templates'
    static_folder = project_root / 'static'

    app = Flask(__name__,
                template_folder=str(template_folder),
                static_folder=str(static_folder))

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['TESTING'] = testing

    # Register blueprints first (before session setup)
    from tsr.api import tsr_api
    from viewer.governance import governance
    app.register_blueprint(tsr_api)
    app.register_blueprint(governance)

    # Register existing blueprints
    from .routes import app_bp
    app.register_blueprint(app_bp)

    # Register viewer blueprint
    from viewer.routes import viewer_bp
    app.register_blueprint(viewer_bp)

    # Setup lazy database session initialization
    setup_database_session(app)

    return app


def setup_database_session(app):
    """Setup database session lifecycle using Flask's application context"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, scoped_session
    from config import TSR_DATABASE_URL

    # Create engine once at app startup (reuse across requests)
    engine = create_engine(
        TSR_DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,   # Recycle connections after 1 hour
    )

    # Create scoped session factory
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)

    # Store Session factory on app for access
    app.tsr_session_factory = Session

    @app.before_request
    def create_session():
        """Create session before each request"""
        from flask import g
        from tsr.repository import TSRRepository
        from tsr.api import init_tsr_api
        from viewer.governance import init_governance

        # Create session for this request
        session = Session()
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
        Session.remove()  # Remove scoped session
