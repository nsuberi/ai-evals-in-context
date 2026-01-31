"""Syntax highlighting utilities using Pygments"""

from pygments import highlight
from pygments.lexers import PythonLexer, get_lexer_by_name
from pygments.formatters import HtmlFormatter


def get_syntax_css():
    """Generate CSS for Pygments syntax highlighting (light theme)"""
    formatter = HtmlFormatter(style='github')
    return formatter.get_style_defs('.highlight')


def syntax_highlight(code: str, language: str = 'python', muted: bool = False) -> str:
    """
    Apply syntax highlighting to code.

    Args:
        code: Source code to highlight
        language: Programming language
        muted: If True, use muted colors for secondary display

    Returns:
        HTML string with syntax highlighting
    """
    try:
        lexer = get_lexer_by_name(language)
    except Exception:
        lexer = PythonLexer()

    css_class = 'highlight-muted' if muted else 'highlight'
    formatter = HtmlFormatter(
        nowrap=True,
        cssclass=css_class
    )

    return highlight(code, lexer, formatter)


def highlight_with_line_numbers(code: str, language: str = 'python', start_line: int = 1) -> str:
    """Highlight code with line numbers"""
    try:
        lexer = get_lexer_by_name(language)
    except Exception:
        lexer = PythonLexer()

    formatter = HtmlFormatter(
        linenos='table',
        linenostart=start_line,
        cssclass='highlight'
    )

    return highlight(code, lexer, formatter)
