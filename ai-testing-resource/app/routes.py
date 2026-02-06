"""Routes for Acme Support Bot demo"""

import logging
from flask import Blueprint, render_template, request, jsonify
from .ai_service import ask, AIServiceError
from .utils import sanitize_input

logger = logging.getLogger(__name__)

app_bp = Blueprint('app', __name__)


# Root route is now handled by narrative blueprint
# @app_bp.route('/')
# def index():
#     """Redirect to the viewer"""
#     return render_template('ask.html', active_nav='demo')


@app_bp.route('/ask', methods=['GET', 'POST'])
def ask_route():
    """Handle questions to the support bot"""
    if request.method == 'GET':
        return render_template('ask.html', active_nav='demo')

    # Handle POST request
    data = request.get_json() if request.is_json else request.form

    question = data.get('question', '')
    version = data.get('version', 'v3')

    # Sanitize input
    question = sanitize_input(question)

    if not question:
        return jsonify({'error': 'Please provide a question'}), 400

    try:
        response = ask(question, version=version)
        return jsonify(response)
    except AIServiceError as e:
        return jsonify({'error': e.message}), 503  # Service Unavailable
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({'error': 'An unexpected error occurred'}), 500
