#!/bin/bash
set -e

echo "=== AI Testing Resource - Starting ==="

# Step 1: Initialize TSR database tables
echo "Initializing TSR database..."
python3 scripts/init_database.py || {
  echo "Warning: Database initialization failed (may already exist)"
}

# Step 2: Seed sample TSR data (idempotent - only seeds if empty)
echo "Seeding sample TSR data..."
python3 scripts/seed_test_data.py || {
  echo "Warning: TSR seeding failed (may already exist)"
}

# Step 3: Start the Flask application
# Note: run.py already calls initialize_knowledge_base() which seeds ChromaDB
echo "Starting Flask application..."
exec python3 run.py
