# Contributing to AI Paywall

Thank you for your interest in contributing to AI Paywall! This project aims to help content creators get paid for their work while keeping the web free for humans.

## Ways to Contribute

### 1. Bot Detection Patterns

Help identify new AI crawlers by submitting bot patterns:

```python
# Example: Add to ai_paywall/patterns.py
'new_bot': {
    'user_agents': ['NewAIBot/1.0', 'ResearchCrawler'],
    'ip_ranges': ['192.168.1.0/24'],
    'confidence': 0.8,
    'description': 'New AI company crawler',
    'docs_url': 'https://example.com/bot-docs'
}
```

### 2. Framework Integrations

Add support for new Python web frameworks by creating adapters.

### 3. Payment Providers

Integrate new payment providers (PayPal, crypto, etc.).

### 4. Bug Reports and Features

Use GitHub issues for bugs and feature requests.

## Development Setup

```bash
# Clone and setup
git clone https://github.com/jamesfishwick/ai-paywall.git
cd ai-paywall
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Code formatting
black ai_paywall tests
isort ai_paywall tests
```

## Code Standards

- **Python 3.8+** compatibility required
- **Black** for code formatting
- **Type hints** for all public APIs
- **Tests** for all new features
- **Documentation** for public methods

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure tests pass (`pytest`)
6. Format code (`black . && isort .`)
7. Commit changes (`git commit -m 'Add amazing feature'`)
8. Push to branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## Bot Pattern Guidelines

When submitting new bot patterns:

1. **Verify accuracy**: Test with real traffic if possible
2. **Include metadata**: Company, description, confidence level
3. **Provide documentation**: Link to official bot documentation
4. **Avoid false positives**: Ensure patterns don't match legitimate tools

## Testing

- Add unit tests for new functionality
- Test with multiple Python versions
- Include integration tests for framework adapters
- Verify performance impact is minimal

## Documentation

- Update README.md for new features
- Add docstrings to public methods
- Include examples in documentation
- Update CHANGELOG.md

## Community Guidelines

- Be respectful and constructive
- Help others learn and contribute
- Share knowledge about AI crawler detection
- Collaborate on improving the detection algorithms

## Questions?

- Open a GitHub Discussion for questions
- Check existing issues before creating new ones
- Join our community Discord (coming soon)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
