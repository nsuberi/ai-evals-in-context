"""Data models for Acme Support Bot"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Question:
    """Represents a user question"""
    id: str
    text: str
    version: str  # v1, v2, v3
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Response:
    """Represents an AI response"""
    id: str
    question_id: str
    text: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int
    sources: List[str] = field(default_factory=list)  # doc IDs for V3


@dataclass
class KnowledgeDoc:
    """Represents a knowledge base document"""
    id: str
    title: str
    content: str
    category: str  # pricing, returns, products, shipping
