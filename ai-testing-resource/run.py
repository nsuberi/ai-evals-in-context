#!/usr/bin/env python
"""Run the AI Testing Resource application"""

import sys
print("run.py: Starting...", flush=True)

import os
from pathlib import Path
print("run.py: Basic imports done", flush=True)

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
    print("run.py: dotenv imported", flush=True)
except Exception as e:
    print(f"run.py: dotenv import failed: {e}", flush=True)
    sys.exit(1)

# Load environment variables
load_dotenv()
print("run.py: Environment loaded", flush=True)

try:
    from app import create_app
    print("run.py: create_app imported", flush=True)
except Exception as e:
    print(f"run.py: create_app import failed: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from app.rag import initialize_knowledge_base
    print("run.py: initialize_knowledge_base imported", flush=True)
except Exception as e:
    print(f"run.py: RAG import failed: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)


def main():
    """Main entry point"""
    # Initialize knowledge base on startup (non-critical)
    try:
        print("Initializing knowledge base...")
        initialize_knowledge_base()
        print("Knowledge base initialized successfully")
    except Exception as e:
        print(f"Warning: Knowledge base initialization failed: {e}")
        print("Continuing without knowledge base (app will still function)")

    # Create and run the app
    print("Creating Flask application...")
    try:
        app = create_app()
        print("Flask application created successfully")
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to create Flask app: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    print(f"\nStarting AI Testing Resource...")
    print(f"Open http://{host}:{port}/viewer/tests in your browser")
    print(f"Demo available at http://{host}:{port}/ask")
    print(f"\nPress Ctrl+C to stop\n")

    try:
        print(f"Starting Flask on {host}:{port} (debug={debug})...")
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        print(f"CRITICAL ERROR: Flask failed to start: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
