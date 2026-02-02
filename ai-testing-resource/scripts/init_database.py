#!/usr/bin/env python3
"""
Initialize TSR database tables and ChromaDB knowledge base
Run this before starting the application for the first time
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
import time

from tsr.database import create_tables, drop_tables, Base
from app.rag import initialize_knowledge_base, get_chroma_client
from config import TSR_DATABASE_URL, KNOWLEDGE_BASE_DIR, CHROMA_PATH


def wait_for_database(max_retries=30, retry_interval=2):
    """Wait for database to be ready"""
    print(f"Waiting for database at {TSR_DATABASE_URL}...")

    for attempt in range(max_retries):
        try:
            engine = create_engine(TSR_DATABASE_URL)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✓ Database is ready!")
            return engine
        except OperationalError as e:
            if attempt < max_retries - 1:
                print(f"  Database not ready (attempt {attempt + 1}/{max_retries}), retrying...")
                time.sleep(retry_interval)
            else:
                print(f"✗ Database connection failed after {max_retries} attempts")
                raise


def initialize_tsr_database():
    """Create TSR database tables"""
    print("\n=== Initializing TSR Database ===")

    try:
        engine = wait_for_database()

        # Check if tables already exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        if 'test_summary_reports' in existing_tables:
            print("⚠ TSR tables already exist")
            response = os.getenv('FORCE_RECREATE_TABLES', 'no').lower()

            if response == 'yes':
                print("  Dropping existing tables...")
                drop_tables(engine)
                print("  Creating fresh tables...")
                create_tables(engine)
                print("✓ TSR tables recreated")
            else:
                print("  Skipping table creation (set FORCE_RECREATE_TABLES=yes to recreate)")
        else:
            print("Creating TSR tables...")
            create_tables(engine)
            print("✓ TSR tables created successfully")

            # Print table summary
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print(f"\nCreated {len(tables)} tables:")
            for table in sorted(tables):
                print(f"  - {table}")

    except Exception as e:
        print(f"✗ Failed to initialize TSR database: {e}")
        raise


def initialize_chroma_database():
    """Initialize ChromaDB and load knowledge base"""
    print("\n=== Initializing ChromaDB Knowledge Base ===")

    try:
        # Ensure chroma directory exists
        os.makedirs(CHROMA_PATH, exist_ok=True)
        print(f"ChromaDB path: {CHROMA_PATH}")

        # Initialize client
        client = get_chroma_client()

        # Check if collection exists
        collections = [c.name for c in client.list_collections()]

        if 'acme_knowledge_base' in collections:
            print("⚠ Knowledge base collection already exists")

            # Check document count
            collection = client.get_collection("acme_knowledge_base")
            count = collection.count()
            print(f"  Current document count: {count}")

            if count > 0:
                print("  Skipping knowledge base initialization")
                return

        # Load knowledge base documents
        print("Loading knowledge base documents...")

        if not KNOWLEDGE_BASE_DIR.exists():
            print(f"⚠ Knowledge base directory not found: {KNOWLEDGE_BASE_DIR}")
            print("  Creating empty directory...")
            os.makedirs(KNOWLEDGE_BASE_DIR, exist_ok=True)
            return

        # Count markdown files
        md_files = list(KNOWLEDGE_BASE_DIR.glob("*.md"))
        print(f"Found {len(md_files)} markdown documents")

        if len(md_files) == 0:
            print("⚠ No markdown files found in knowledge base directory")
            return

        # Initialize knowledge base
        initialize_knowledge_base()

        # Verify loaded documents
        collection = client.get_collection("acme_knowledge_base")
        count = collection.count()
        print(f"✓ Knowledge base initialized with {count} documents")

    except Exception as e:
        print(f"✗ Failed to initialize ChromaDB: {e}")
        raise


def main():
    """Main initialization routine"""
    print("=" * 60)
    print("AI Testing Resource - Database Initialization")
    print("=" * 60)

    try:
        # Initialize TSR database
        initialize_tsr_database()

        # Initialize ChromaDB
        initialize_chroma_database()

        print("\n" + "=" * 60)
        print("✓ Initialization complete!")
        print("=" * 60)
        return 0

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ Initialization failed: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
