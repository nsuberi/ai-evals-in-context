"""Utility functions for Acme Support Bot"""

import re
import tiktoken


def sanitize_input(text: str) -> str:
    """
    Clean user input to prevent injection and normalize text.

    - Strip whitespace
    - Remove HTML tags
    - Limit length
    - Normalize unicode
    """
    if not text:
        return ""

    # Strip whitespace
    text = text.strip()

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Remove null bytes
    text = text.replace('\x00', '')

    # Limit length (max 500 chars for a question)
    text = text[:500]

    # Normalize whitespace
    text = ' '.join(text.split())

    return text


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Count tokens in text using tiktoken"""
    if not text:
        return 0

    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    return len(encoding.encode(text))


def format_response(
    text: str,
    sources: list = None,
    latency_ms: int = 0,
    tokens: dict = None
) -> dict:
    """
    Structure AI output for display.

    Returns:
        {
            'text': str,
            'sources': [{'id': str, 'title': str}],
            'metadata': {
                'latency_ms': int,
                'prompt_tokens': int,
                'completion_tokens': int,
                'total_tokens': int
            }
        }
    """
    tokens = tokens or {}

    return {
        'text': text.strip(),
        'sources': sources or [],
        'metadata': {
            'latency_ms': latency_ms,
            'prompt_tokens': tokens.get('prompt', 0),
            'completion_tokens': tokens.get('completion', 0),
            'total_tokens': tokens.get('prompt', 0) + tokens.get('completion', 0)
        }
    }
