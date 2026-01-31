"""Iteration Timeline - Compare versions and show evolution"""

from typing import Dict, List
from .trace_inspector import get_trace_summary

VERSIONS = [
    {
        'id': 'v1',
        'name': 'Version 1',
        'subtitle': 'Verbose',
        'color': 'warning',
        'problem': 'Responses are too long (~300 words instead of ~80)',
        'fix': 'Updated prompt to request concise 80-word responses',
        'prompt_change': 'Changed "at least 300 words" to "approximately 80 words"'
    },
    {
        'id': 'v2',
        'name': 'Version 2',
        'subtitle': 'Hallucinating',
        'color': 'error',
        'problem': 'Model fabricates specific facts (prices, policies)',
        'fix': 'Added RAG with Chroma to ground responses in actual data',
        'prompt_change': 'Added context injection with retrieved documents'
    },
    {
        'id': 'v3',
        'name': 'Version 3',
        'subtitle': 'Accurate',
        'color': 'success',
        'problem': 'N/A - This version passes all evals',
        'fix': 'Production-ready with concise, accurate responses',
        'prompt_change': 'Using V3_SYSTEM_PROMPT with RAG context'
    }
]


def get_iteration_summary() -> List[Dict]:
    """Get summary for each version"""
    summaries = []

    for version in VERSIONS:
        stats = get_trace_summary(version['id'])
        summaries.append({
            **version,
            'stats': stats
        })

    return summaries


def get_comparison_data() -> Dict:
    """Get data for side-by-side comparison"""
    return {
        'versions': VERSIONS,
        'metrics': [
            {
                'name': 'Response Length',
                'v1': '~300 words',
                'v2': '~80 words',
                'v3': '~80 words',
                'target': '~80 words'
            },
            {
                'name': 'Factual Accuracy',
                'v1': 'N/A (too verbose)',
                'v2': 'Low (hallucinations)',
                'v3': 'High (grounded)',
                'target': 'High'
            },
            {
                'name': 'Sources Cited',
                'v1': 'None',
                'v2': 'None',
                'v3': 'Yes',
                'target': 'Yes'
            },
            {
                'name': 'Eval Pass Rate',
                'v1': '0%',
                'v2': '33%',
                'v3': '100%',
                'target': '100%'
            }
        ],
        'key_lessons': [
            {
                'title': 'Prompt Engineering Matters',
                'description': 'V1 to V2 shows how a simple prompt change can fix behavioral issues like response length.'
            },
            {
                'title': 'LLMs Hallucinate Without Grounding',
                'description': 'V2 demonstrates that LLMs will confidently make up facts. RAG provides the grounding needed for accuracy.'
            },
            {
                'title': 'Evals Guide Iteration',
                'description': 'Each version was improved based on eval failures. Evals are your acceptance tests for AI behavior.'
            }
        ]
    }


def get_version_diff(from_version: str, to_version: str) -> Dict:
    """Get the differences between two versions"""
    version_map = {v['id']: v for v in VERSIONS}

    from_v = version_map.get(from_version)
    to_v = version_map.get(to_version)

    if not from_v or not to_v:
        return {}

    return {
        'from': from_v,
        'to': to_v,
        'problem_fixed': from_v['problem'],
        'solution': to_v['fix'] if to_v['fix'] != from_v['fix'] else 'Same approach',
        'prompt_diff': to_v['prompt_change']
    }
