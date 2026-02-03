"""Utility functions for Acme Support Bot"""

import re
import tiktoken
import markdown


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


def convert_markdown_to_html(text: str) -> str:
    """
    Convert markdown text to HTML.

    Supports common markdown features:
    - Headers, bold, italic
    - Code blocks and inline code
    - Lists (ordered and unordered)
    - Blockquotes
    - Links
    """
    if not text:
        return ""

    # Convert markdown to HTML with common extensions
    html = markdown.markdown(
        text,
        extensions=['fenced_code', 'tables', 'nl2br']
    )

    return html


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
    tokens: dict = None,
    trace: dict = None
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
            },
            'trace': {
                'version': str,
                'query': str,
                'not_in_use': bool (for v1/v2),
                'reason': str (for v1/v2),
                'retrieved_docs': [...] (for v3),
                'formatted_context': str (for v3),
                'system_prompt': str (for v3),
                'user_message': str (for v3)
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
        },
        'trace': trace or {}
    }
