# Unit Tests

Unit tests verify that individual functions work correctly in isolation. For example, a unit test checks that the input sanitizer strips dangerous characters before they reach the AI model. They catch bugs early, make refactoring safe, and pinpoint exactly which function broke.

## Relationship to AI
**These test the code *around* your AI, not the AI itself.** Unit tests cover deterministic operations like input preprocessing, output formatting, and token counting. AI responses are non-deterministic, so AI behavior is validated separately through evals.
