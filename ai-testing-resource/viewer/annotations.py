"""Annotation utilities for trace analysis"""

from typing import List, Dict, Optional


def create_annotation(
    ann_type: str,
    severity: str,
    text: str,
    span_start: Optional[int] = None,
    span_end: Optional[int] = None
) -> Dict:
    """Create an annotation dict"""
    return {
        'type': ann_type,
        'severity': severity,
        'text': text,
        'span_start': span_start,
        'span_end': span_end
    }


# Predefined annotation types
ANNOTATION_TYPES = {
    'length_violation': {
        'description': 'Response exceeds target length',
        'default_severity': 'warning'
    },
    'hallucination': {
        'description': 'Response contains fabricated information',
        'default_severity': 'error'
    },
    'missing_source': {
        'description': 'Claim made without source citation',
        'default_severity': 'warning'
    },
    'correct_retrieval': {
        'description': 'Relevant document was retrieved',
        'default_severity': 'success'
    },
    'accurate_answer': {
        'description': 'Response matches ground truth',
        'default_severity': 'success'
    },
    'prompt_issue': {
        'description': 'Problem with the system prompt',
        'default_severity': 'info'
    }
}


def annotate_length_violation(response: str, target_words: int = 80, tolerance: float = 0.25) -> Optional[Dict]:
    """Check if response violates length target"""
    word_count = len(response.split())
    min_words = int(target_words * (1 - tolerance))
    max_words = int(target_words * (1 + tolerance))

    if word_count > max_words:
        return create_annotation(
            'length_violation',
            'warning',
            f'Response is {word_count} words (target: {min_words}-{max_words})'
        )
    elif word_count < min_words:
        return create_annotation(
            'length_violation',
            'info',
            f'Response is {word_count} words (target: {min_words}-{max_words})'
        )
    return None


def annotate_hallucination(response: str, fact: str, expected_value: str) -> Optional[Dict]:
    """Check if response contains a hallucinated fact"""
    if expected_value.lower() not in response.lower():
        # Find where the fact might be mentioned
        fact_lower = fact.lower()
        response_lower = response.lower()

        span_start = response_lower.find(fact_lower)
        if span_start >= 0:
            span_end = span_start + len(fact_lower) + 20  # Include some context

            return create_annotation(
                'hallucination',
                'error',
                f'Expected "{expected_value}" for {fact}, but response may contain incorrect information',
                span_start,
                min(span_end, len(response))
            )

    return None


def annotate_missing_source(response: str, sources: List[Dict]) -> Optional[Dict]:
    """Check if response should cite sources but doesn't"""
    if not sources:
        return create_annotation(
            'missing_source',
            'warning',
            'Response makes claims without citing sources'
        )
    return None


def annotate_correct_retrieval(sources: List[Dict], expected_doc_id: str) -> Optional[Dict]:
    """Check if the expected document was retrieved"""
    source_ids = [s.get('id', '') for s in sources]

    if expected_doc_id in source_ids:
        return create_annotation(
            'correct_retrieval',
            'success',
            f'Retrieved relevant document: {expected_doc_id}'
        )
    return None


def annotate_accurate_answer(response: str, ground_truth: str) -> Optional[Dict]:
    """Check if response contains the ground truth"""
    if ground_truth.lower() in response.lower():
        # Find the position
        span_start = response.lower().find(ground_truth.lower())
        span_end = span_start + len(ground_truth)

        return create_annotation(
            'accurate_answer',
            'success',
            f'Response correctly includes: {ground_truth}',
            span_start,
            span_end
        )
    return None
