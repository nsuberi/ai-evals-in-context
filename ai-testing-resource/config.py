"""Configuration settings for AI Testing Resource"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Flask settings
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Anthropic settings
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')

# Embedding settings (using local sentence-transformers)
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')

# Chroma settings
CHROMA_PATH = os.getenv('CHROMA_PATH', str(BASE_DIR / 'chroma_db'))

# Knowledge base
KNOWLEDGE_BASE_DIR = BASE_DIR / 'data' / 'knowledge_base'

# Traces
TRACES_DIR = BASE_DIR / 'data' / 'traces'

# Test settings
TESTS_DIR = BASE_DIR / 'tests'

# Response settings
TARGET_WORD_COUNT = 80
WORD_COUNT_TOLERANCE = 0.25  # 25% tolerance

# Token limits
MAX_PROMPT_TOKENS = 2000
MAX_COMPLETION_TOKENS = 500

# Latency thresholds (milliseconds)
LATENCY_THRESHOLD_P50 = 2000
LATENCY_THRESHOLD_P95 = 5000
LATENCY_THRESHOLD_MAX = 10000

# Phase 2: TSR Database (PostgreSQL)
# For development, you can use SQLite: sqlite:///tsr.db
# For production, construct URL from individual components or use TSR_DATABASE_URL directly
def get_database_url():
    """Get database URL from environment variables"""
    direct_url = os.getenv('TSR_DATABASE_URL')
    if direct_url:
        return direct_url

    # Construct from individual components (for ECS deployment)
    db_host = os.getenv('TSR_DB_HOST')
    if db_host:
        db_port = os.getenv('TSR_DB_PORT', '5432')
        db_name = os.getenv('TSR_DB_NAME', 'tsr_db')
        db_user = os.getenv('TSR_DB_USER', 'tsr_user')
        db_password = os.getenv('TSR_DB_PASSWORD', '')
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    # Default to SQLite for local development
    return 'sqlite:///tsr.db'

TSR_DATABASE_URL = get_database_url()

# Phase 2: WebSocket settings
SOCKETIO_MESSAGE_QUEUE = os.getenv('SOCKETIO_MESSAGE_QUEUE', None)  # Redis URL for production
SOCKETIO_ASYNC_MODE = 'threading'  # Use 'gevent' or 'eventlet' in production

# Phase 2: Monitoring settings
MONITORING_ENABLED = os.getenv('MONITORING_ENABLED', 'True').lower() == 'true'
MONITORING_WINDOW_MINUTES = int(os.getenv('MONITORING_WINDOW_MINUTES', '15'))
TRACE_RETENTION_HOURS = int(os.getenv('TRACE_RETENTION_HOURS', '24'))
