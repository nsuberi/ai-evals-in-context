"""Playwright test fixtures and CLI options."""

import os
import pytest


def pytest_addoption(parser):
    """Add CLI options for steel thread tests."""
    parser.addoption(
        "--portfolio-url",
        action="store",
        default="https://portfolio.cookinupideas.com",
        help="Portfolio URL for steel thread tests",
    )
    # Note: --base-url is provided by pytest-base-url plugin


@pytest.fixture(scope="session")
def portfolio_url(request):
    """Portfolio URL from CLI option."""
    return request.config.getoption("--portfolio-url")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for HTTPS handling."""
    return {
        **browser_context_args,
        "ignore_https_errors": True,
    }
