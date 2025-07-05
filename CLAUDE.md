# CLAUDE.md

This file provides guidance to Claude Code when working with the AI Paywall project.

## Project Overview

AI Paywall is a universal Python module that enables content creators to charge AI crawlers for access while keeping content free for humans. The project aims to be framework-agnostic and easy to integrate.

## Development Philosophy

### Core Principles
- **Universal compatibility**: Must work with Django, Flask, FastAPI, and any Python web framework
- **Zero-config default**: Should work out of the box with sensible defaults
- **Progressive enhancement**: Start simple, add features as needed
- **Community-driven**: Patterns and integrations should be crowd-sourced
- **Privacy-first**: Minimal data collection, respect human privacy

### Code Quality Standards
- **Simplicity over cleverness**: Prefer readable code over optimized code
- **Comprehensive testing**: Every public method needs tests
- **Documentation-driven**: Write docs first, then implement
- **Backward compatibility**: Don't break existing integrations
- **Security-conscious**: Never trust user input, validate everything

## Project Structure

```
ai-paywall/
├── ai_paywall/              # Main package
│   ├── __init__.py          # Public API
│   ├── core.py              # Core AIPaywall class
│   ├── detectors.py         # Bot detection logic
│   ├── patterns.py          # Known bot patterns
│   ├── storage.py           # Storage backends
│   ├── payments.py          # Payment providers
│   ├── config.py            # Configuration handling
│   └── adapters/            # Framework adapters
│       ├── __init__.py
│       ├── django.py
│       ├── flask.py
│       └── fastapi.py
├── tests/                   # Test suite
├── examples/                # Integration examples
├── docs/                    # Documentation
├── setup.py                 # Package configuration
└── pyproject.toml          # Modern packaging
```

## Development Commands

### Environment Setup
```bash
# Development environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -e .
pip install -r requirements-dev.txt

# Testing
pytest
pytest --cov=ai_paywall --cov-report=html

# Code quality
black ai_paywall tests
isort ai_paywall tests
flake8 ai_paywall tests
mypy ai_paywall
```

### Packaging
```bash
# Build package
python -m build

# Test upload
python -m twine upload --repository testpypi dist/*

# Production upload
python -m twine upload dist/*
```

## API Design Guidelines

### Public API
Keep the public API minimal and stable:
```python
# These should rarely change
from ai_paywall import AIPaywall, DetectionResult

paywall = AIPaywall(mode='detect')
result = paywall.check(request)
```

### Request Adaptation
The `RequestAdapter` should handle differences between frameworks transparently:
```python
# Should work the same regardless of framework
result = paywall.check(django_request)
result = paywall.check(flask_request) 
result = paywall.check(fastapi_request)
```

### Storage Interface
Storage backends should be pluggable:
```python
# All storage backends implement the same interface
storage = MemoryStorage()
storage = FileStorage('bot_logs.db')
storage = RedisStorage('redis://localhost')
```

## Testing Strategy

### Test Categories
1. **Unit tests**: Individual functions and classes
2. **Integration tests**: Framework adapters with mock requests
3. **End-to-end tests**: Full workflow from detection to payment
4. **Performance tests**: Ensure minimal overhead
5. **Security tests**: Validate input sanitization

### Test Data
Create realistic test scenarios:
- Known bot user agents
- Human browser user agents
- Edge cases and malformed requests
- Different framework request objects

## Bot Detection Patterns

### Pattern Management
- Keep patterns in `patterns.py` as structured data
- Include metadata: company, description, confidence level
- Support regular expressions and exact matches
- Allow easy updates from community contributions

### Pattern Format
```python
PATTERNS = {
    'openai': {
        'user_agents': ['GPTBot', 'ChatGPT-User'],
        'ip_ranges': ['20.171.0.0/16'],
        'confidence': 0.9,
        'description': 'OpenAI crawlers',
        'docs_url': 'https://platform.openai.com/docs/gptbot'
    }
}
```

## Important Guidelines

### Security Considerations
- Never log sensitive data (IPs can be sensitive)
- Validate all configuration inputs
- Use secure token generation for payments
- Implement rate limiting to prevent abuse
- Sanitize all user-provided patterns

### Performance Requirements
- Detection should add <10ms overhead per request
- Memory usage should be minimal and bounded
- Support high-traffic sites (1000+ requests/second)
- Lazy-load expensive operations

### Error Handling
- Graceful degradation: if detection fails, allow request through
- Clear error messages for configuration issues
- Log errors for debugging but don't crash the application
- Provide helpful suggestions for common problems

## Integration Testing

### Test with Real Applications
Before any major release:
1. Test with James's minimalwave-blog (Django)
2. Create test Flask app
3. Create test FastAPI app
4. Verify performance with load testing

### Compatibility Testing
- Python 3.8+ support
- Major framework versions
- Different deployment environments (Docker, cloud, etc.)

## Documentation Standards

### Code Documentation
- Docstrings for all public methods
- Type hints for better IDE support
- Inline comments for complex logic
- Examples in docstrings

### User Documentation
- README with quick start
- Framework-specific guides
- Configuration reference
- Troubleshooting guide

## Release Process

### Version Management
- Semantic versioning (MAJOR.MINOR.PATCH)
- Clear changelog for each release
- Beta releases for major changes
- LTS versions for stability

### Quality Gates
Before any release:
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Performance benchmarks run
- [ ] Security review completed
- [ ] Integration tests with real apps

## Community Guidelines

### Contributing
- Welcome pattern contributions from community
- Require tests for new features
- Code review for all changes
- Clear contribution guidelines

### Support
- GitHub issues for bug reports
- Discussions for questions
- Clear issue templates
- Response within 48 hours

---

## Important Reminders

- **Start simple**: Get basic detection working before adding complexity
- **Test early**: Every feature should be tested with real applications
- **Document everything**: Good docs are as important as good code
- **Security first**: This module handles payments, security is critical
- **Community-driven**: Success depends on community adoption and contributions

## Current Focus

**Phase 1 Goal**: Create a working detection module that can be tested with the minimalwave-blog Django application.

**Success Criteria**:
- Zero-config integration with Django
- Detects major AI bots (GPTBot, Claude-Web, CCBot)
- Logs useful metadata for analysis
- No false positives on human traffic
- Performance overhead < 10ms per request