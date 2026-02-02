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

    # Initialize TSR database connection and repository
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from config import TSR_DATABASE_URL
    from tsr.repository import TSRRepository
    from tsr.api import tsr_api, init_tsr_api
    from viewer.governance import governance, init_governance

    # Create database session
    engine = create_engine(TSR_DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Initialize TSR repository
    tsr_repository = TSRRepository(session)

    # Initialize TSR API and governance with repository
    init_tsr_api(tsr_repository)
    init_governance(tsr_repository)

    # Register TSR API blueprint
    app.register_blueprint(tsr_api)

    # Register governance blueprint
    app.register_blueprint(governance)

    # Register existing blueprints
    from .routes import app_bp
    app.register_blueprint(app_bp)

    # Register viewer blueprint
    from viewer.routes import viewer_bp
    app.register_blueprint(viewer_bp)

    return app
