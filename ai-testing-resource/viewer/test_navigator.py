"""Test Navigator - Browse and run tests by type"""

import os
from pathlib import Path
from typing import List, Dict, Optional
import markdown
import html

TEST_TYPES = [
    {'id': 'unit', 'name': 'Unit', 'description': 'Test individual functions'},
    {'id': 'integration', 'name': 'Integration', 'description': 'Test component interactions'},
    {'id': 'e2e', 'name': 'E2E', 'description': 'Test full user flows'},
    {'id': 'acceptance', 'name': 'Acceptance', 'description': 'Verify requirements'},
    {'id': 'evals', 'name': 'AI Evals', 'description': 'Evaluate AI behavior'},
    {'id': 'security', 'name': 'Security', 'description': 'Test security measures'},
    {'id': 'performance', 'name': 'Performance', 'description': 'Test speed and efficiency'},
]

# Get the base directory
BASE_DIR = Path(__file__).parent.parent
TESTS_DIR = BASE_DIR / 'tests'
EXPLANATIONS_DIR = BASE_DIR / 'data' / 'explanations'


def get_tests_by_type(test_type: str) -> List[Dict]:
    """Get list of tests for a given type"""
    type_dir = TESTS_DIR / test_type
    if not type_dir.exists():
        return []

    tests = []
    for test_file in sorted(type_dir.glob('*.py')):
        if test_file.name.startswith('__'):
            continue

        tests.append({
            'id': f"{test_type}/{test_file.stem}",
            'name': format_test_name(test_file.stem),
            'filename': test_file.name,
            'path': str(test_file)
        })

    return tests


def format_test_name(stem: str) -> str:
    """Convert test_sanitize to 'Sanitize'"""
    name = stem.replace('test_', '').replace('eval_', '')
    return name.replace('_', ' ').title()


def get_test_code(test_id: str) -> Dict:
    """Get test code and related app code"""
    parts = test_id.split('/')
    if len(parts) != 2:
        return {'code': '# Test not found', 'related_app_code': None, 'filename': 'unknown.py'}

    type_name, test_name = parts
    test_path = TESTS_DIR / type_name / f"{test_name}.py"

    if not test_path.exists():
        return {'code': '# Test not found', 'related_app_code': None, 'filename': 'unknown.py'}

    code = test_path.read_text()

    # Try to find related app code based on test name
    related_app_code = find_related_app_code(test_name)

    return {
        'code': code,
        'related_app_code': related_app_code,
        'filename': test_path.name
    }


def get_test_path(test_id: str) -> str:
    """Get the file path for a test"""
    parts = test_id.split('/')
    if len(parts) != 2:
        return ''

    type_name, test_name = parts
    test_path = TESTS_DIR / type_name / f"{test_name}.py"
    return str(test_path)


def find_related_app_code(test_name: str) -> Optional[str]:
    """Find app code related to a test"""
    # Map test names to app files
    mappings = {
        'sanitize': 'app/utils.py',
        'tokens': 'app/utils.py',
        'format': 'app/utils.py',
        'chroma': 'app/rag.py',
        'rag_pipeline': 'app/rag.py',
        'ai_service': 'app/ai_service.py',
        'v1': 'app/ai_service.py',
        'v2': 'app/ai_service.py',
        'v3': 'app/ai_service.py',
    }

    for key, path in mappings.items():
        if key in test_name.lower():
            app_path = BASE_DIR / path
            if app_path.exists():
                return app_path.read_text()

    return None


def get_explanation(test_type: str) -> Dict:
    """Get educational explanation for test type"""
    explanation_path = EXPLANATIONS_DIR / f"{test_type}.md"

    if not explanation_path.exists():
        return {
            'title': test_type.title(),
            'content': 'No explanation available.',
            'relationship_to_ai': ''
        }

    content = explanation_path.read_text()

    # Parse markdown for title and content
    lines = content.strip().split('\n')
    title = lines[0].lstrip('#').strip() if lines else test_type.title()
    body = '\n'.join(lines[1:]).strip()

    # Convert markdown to HTML (this properly escapes code blocks)
    md = markdown.Markdown(extensions=['fenced_code', 'codehilite'])
    body_html = md.convert(body)

    return {
        'title': title,
        'content': body_html,
        'relationship_to_ai': extract_ai_relationship_html(body_html)
    }


def extract_ai_relationship(content: str) -> str:
    """Extract the AI relationship section from explanation"""
    # Look for section about AI
    if '## Relationship to AI' in content:
        parts = content.split('## Relationship to AI')
        if len(parts) > 1:
            return parts[1].split('##')[0].strip()
    return ''


def extract_ai_relationship_html(html_content: str) -> str:
    """Extract the AI relationship section from HTML content"""
    # Look for h2 with "Relationship to AI" and get content until next h2
    if 'Relationship to AI' in html_content:
        import re
        # Find the h2 tag and extract content until next h2 or end
        match = re.search(r'<h2>Relationship to AI</h2>(.*?)(?=<h2>|$)', html_content, re.DOTALL)
        if match:
            return match.group(1).strip()
    return ''
