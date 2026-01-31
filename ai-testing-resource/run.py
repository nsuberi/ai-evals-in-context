#!/usr/bin/env python
"""Run the AI Testing Resource application"""

import os
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import create_app
from app.rag import initialize_knowledge_base


def main():
    """Main entry point"""
    # Initialize knowledge base on startup
    print("Initializing knowledge base...")
    initialize_knowledge_base()

    # Create and run the app
    app = create_app()

    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    print(f"\nStarting AI Testing Resource...")
    print(f"Open http://{host}:{port}/viewer/tests in your browser")
    print(f"Demo available at http://{host}:{port}/ask")
    print(f"\nPress Ctrl+C to stop\n")

    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
