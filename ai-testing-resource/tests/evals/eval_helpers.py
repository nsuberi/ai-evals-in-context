"""
Eval Helpers: Utility functions for AI evaluations

Provides common evaluation functions used across different eval suites.
"""
from typing import List, Dict, Optional, Tuple


def count_words(text: str) -> int:
    """Count words in text"""
    return len(text.split())


def check_contains_any(text: str, keywords: List[str], case_sensitive: bool = False) -> Tuple[bool, List[str]]:
    """
    Check if text contains any of the keywords.

    Returns:
        Tuple of (contains_any, list_of_found_keywords)
    """
    if not case_sensitive:
        text = text.lower()
        keywords = [k.lower() for k in keywords]

    found = [k for k in keywords if k in text]
    return len(found) > 0, found


def check_contains_all(text: str, keywords: List[str], case_sensitive: bool = False) -> Tuple[bool, List[str]]:
    """
    Check if text contains all of the keywords.

    Returns:
        Tuple of (contains_all, list_of_missing_keywords)
    """
    if not case_sensitive:
        text = text.lower()
        keywords = [k.lower() for k in keywords]

    missing = [k for k in keywords if k not in text]
    return len(missing) == 0, missing


def evaluate_length(text: str, target: int, tolerance: float = 0.25) -> Dict:
    """
    Evaluate if text length is within acceptable range.

    Args:
        text: Text to evaluate
        target: Target word count
        tolerance: Acceptable deviation (0.25 = 25%)

    Returns:
        Dict with pass/fail, word_count, and target_range
    """
    word_count = count_words(text)
    min_words = int(target * (1 - tolerance))
    max_words = int(target * (1 + tolerance))

    return {
        'passed': min_words <= word_count <= max_words,
        'word_count': word_count,
        'target': target,
        'min': min_words,
        'max': max_words,
        'deviation': abs(word_count - target) / target
    }


def evaluate_accuracy(response: str, ground_truth: str, fuzzy: bool = True) -> Dict:
    """
    Evaluate if response contains the ground truth.

    Args:
        response: AI response text
        ground_truth: Expected value/fact
        fuzzy: If True, check for partial matches

    Returns:
        Dict with pass/fail and details
    """
    response_lower = response.lower()
    truth_lower = ground_truth.lower()

    if fuzzy:
        # Extract numeric parts for comparison
        import re
        truth_numbers = re.findall(r'\d+\.?\d*', ground_truth)
        found_numbers = [n for n in truth_numbers if n in response_lower]

        return {
            'passed': len(found_numbers) > 0 or truth_lower in response_lower,
            'ground_truth': ground_truth,
            'found_numbers': found_numbers,
            'exact_match': truth_lower in response_lower
        }
    else:
        return {
            'passed': truth_lower in response_lower,
            'ground_truth': ground_truth,
            'exact_match': truth_lower in response_lower
        }


def evaluate_sources(sources: List[Dict], expected_topic: str) -> Dict:
    """
    Evaluate if sources are relevant to the expected topic.

    Args:
        sources: List of source dicts with 'id' and 'title'
        expected_topic: Topic keyword to look for

    Returns:
        Dict with pass/fail and relevance details
    """
    if not sources:
        return {
            'passed': False,
            'reason': 'No sources provided',
            'relevant_sources': []
        }

    topic_lower = expected_topic.lower()
    relevant = []

    for source in sources:
        source_id = source.get('id', '').lower()
        source_title = source.get('title', '').lower()

        if topic_lower in source_id or topic_lower in source_title:
            relevant.append(source)

    return {
        'passed': len(relevant) > 0,
        'total_sources': len(sources),
        'relevant_sources': relevant,
        'expected_topic': expected_topic
    }


def evaluate_hedging(response: str) -> Dict:
    """
    Check if response contains appropriate hedging language
    when expressing uncertainty.

    Returns:
        Dict with hedging analysis
    """
    hedging_phrases = [
        "i don't have",
        "i'm not sure",
        "i cannot find",
        "no information",
        "contact support",
        "contact our team",
        "i don't know",
        "unable to find",
        "not available",
        "beyond my knowledge"
    ]

    response_lower = response.lower()
    found_hedging = [p for p in hedging_phrases if p in response_lower]

    return {
        'has_hedging': len(found_hedging) > 0,
        'hedging_phrases_found': found_hedging,
        'hedging_count': len(found_hedging)
    }
