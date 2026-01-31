"""Line selection utilities for code canvas viewer"""

from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlencode


@dataclass
class LineSelection:
    """Represents selected lines in a code file"""
    file_path: str
    start_line: int
    end_line: int
    commit_sha: Optional[str] = None

    def to_url_params(self) -> str:
        """Generate URL parameters for this selection"""
        params = {
            'file': self.file_path,
            'L': f"{self.start_line}-{self.end_line}" if self.start_line != self.end_line
                 else str(self.start_line)
        }
        if self.commit_sha:
            params['ref'] = self.commit_sha
        return urlencode(params)

    @classmethod
    def from_url_params(cls, params: dict) -> Optional['LineSelection']:
        """Parse selection from URL query parameters"""
        if 'file' not in params or 'L' not in params:
            return None

        file_path = params['file'][0] if isinstance(params['file'], list) else params['file']
        line_spec = params['L'][0] if isinstance(params['L'], list) else params['L']

        if '-' in line_spec:
            start, end = map(int, line_spec.split('-'))
        else:
            start = end = int(line_spec)

        commit_sha = params.get('ref')
        if isinstance(commit_sha, list):
            commit_sha = commit_sha[0] if commit_sha else None

        return cls(file_path=file_path, start_line=start, end_line=end,
                   commit_sha=commit_sha)


def get_line_content(file_path: str, start_line: int, end_line: int) -> str:
    """Extract specific lines from a file

    Args:
        file_path: Path to the file
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (1-indexed, inclusive)

    Returns:
        String containing the selected lines
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()
    return ''.join(lines[start_line - 1:end_line])


def add_line_numbers(code: str, start_line: int = 1) -> str:
    """Add line numbers to code for display

    Args:
        code: The code string
        start_line: Starting line number (default: 1)

    Returns:
        HTML string with line numbers in a gutter
    """
    lines = code.split('\n')
    gutter_html = []
    code_html = []

    for i, line in enumerate(lines, start=start_line):
        gutter_html.append(f'<div class="gutter__line" data-line="{i}">{i}</div>')
        code_html.append(line)

    return {
        'gutter': '\n'.join(gutter_html),
        'code': '\n'.join(code_html)
    }
