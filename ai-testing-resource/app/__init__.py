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

    # Register blueprints
    from .routes import app_bp
    app.register_blueprint(app_bp)

    # Register viewer blueprint
    from viewer.routes import viewer_bp
    app.register_blueprint(viewer_bp)

    return app
