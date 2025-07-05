# AI Paywall

A universal Python module that enables content creators to detect AI crawlers accessing their content. Currently in **Phase 1: Detection and Logging** - perfect for understanding which AI bots are accessing your site before implementing payment features.

## Why?

AI companies are training billion-dollar models on freely available web content. This module gives content creators visibility into which AI crawlers are accessing their content, with future plans for monetization while preserving the open web for humans.

## Current Features (Phase 1)

- ✅ **AI Bot Detection**: Detects major AI crawlers (OpenAI, Anthropic, Google, Meta, etc.)
- ✅ **Universal Framework Support**: Works with Django, Flask, FastAPI, and any Python web framework
- ✅ **Zero Configuration**: Works out of the box with sensible defaults
- ✅ **Community Bot Database**: Shared patterns for 10+ AI companies
- ✅ **Detailed Logging**: Get insights on bot type, confidence, detection method
- ✅ **Privacy-Focused**: Only logs bot activity, respects human privacy

## Quick Start

```bash
pip install ai-paywall
```

```python
from ai_paywall import AIPaywall

# Phase 1: Detection only (current functionality)
paywall = AIPaywall()

# Works with any request object
result = paywall.check(request)
if result.is_bot:
    print(f"AI bot detected: {result.bot_type}")
    print(f"Confidence: {result.confidence}")
    print(f"Detection method: {result.detection_method}")
```

## Framework Setup Guides

### Django (5 minutes)

**Step 1**: Install

```bash
pip install ai-paywall
```

**Step 2**: Create middleware file `ai_middleware.py`:

```python
from ai_paywall import AIPaywall
import logging

logger = logging.getLogger(__name__)

class AIDetectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.paywall = AIPaywall()

    def __call__(self, request):
        result = self.paywall.check(request)
        if result.is_bot:
            logger.info(f"AI Bot detected: {result.bot_type} (confidence: {result.confidence})")
            # Add to request for use in views
            request.ai_detection = result

        return self.get_response(request)
```

**Step 3**: Add to `settings.py`:

```python
MIDDLEWARE = [
    # ... your existing middleware
    'your_app.ai_middleware.AIDetectionMiddleware',
]

# Optional: Configure logging
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'ai_bots.log',
        },
    },
    'loggers': {
        'your_app.ai_middleware': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

**Step 4**: Use in views (optional):

```python
def my_view(request):
    if hasattr(request, 'ai_detection') and request.ai_detection.is_bot:
        # Handle AI bot access
        return HttpResponse("AI bot detected", status=200)
    # Normal response for humans
    return render(request, 'template.html')
```

**Done!** Check `ai_bots.log` to see detected AI crawlers.

### Flask (3 minutes)

**Step 1**: Install

```bash
pip install ai-paywall
```

**Step 2**: Add to your Flask app:

```python
from flask import Flask, request, g
from ai_paywall import AIPaywall
import logging

app = Flask(__name__)
paywall = AIPaywall()

# Setup logging
logging.basicConfig(
    filename='ai_bots.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

@app.before_request
def detect_ai_bots():
    result = paywall.check(request)
    g.ai_detection = result

    if result.is_bot:
        app.logger.info(f"AI Bot: {result.bot_type} (confidence: {result.confidence})")

@app.route('/')
def home():
    if g.ai_detection.is_bot:
        return f"AI bot detected: {g.ai_detection.bot_type}", 200
    return "Welcome, human visitor!"

if __name__ == '__main__':
    app.run()
```

**Done!** Check `ai_bots.log` to see detected AI crawlers.

### FastAPI (3 minutes)

**Step 1**: Install

```bash
pip install ai-paywall
```

**Step 2**: Add to your FastAPI app:

```python
from fastapi import FastAPI, Request
from ai_paywall import AIPaywall
import logging

app = FastAPI()
paywall = AIPaywall()

# Setup logging
logging.basicConfig(
    filename='ai_bots.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def ai_detection_middleware(request: Request, call_next):
    result = paywall.check(request)
    request.state.ai_detection = result

    if result.is_bot:
        logger.info(f"AI Bot: {result.bot_type} (confidence: {result.confidence})")

    response = await call_next(request)
    return response

@app.get("/")
async def home(request: Request):
    ai_result = request.state.ai_detection
    if ai_result.is_bot:
        return {"message": f"AI bot detected: {ai_result.bot_type}"}
    return {"message": "Welcome, human visitor!"}
```

**Done!** Check `ai_bots.log` to see detected AI crawlers.

### Any Other Python Web Framework

**Step 1**: Install

```bash
pip install ai-paywall
```

**Step 2**: Add anywhere in your request handling:

```python
from ai_paywall import AIPaywall

paywall = AIPaywall()

# In your request handler
def handle_request(request):
    result = paywall.check(request)

    if result.is_bot:
        print(f"AI Bot: {result.bot_type}")
        # Log, track, or handle as needed

    # Continue with normal request handling
```

## What You'll See

Once set up, you'll start logging entries like:

```
2024-01-15 10:30:22 - AI Bot: openai (confidence: 0.95)
2024-01-15 11:15:33 - AI Bot: anthropic (confidence: 0.95)
2024-01-15 14:22:44 - AI Bot: google (confidence: 0.90)
```

## Configuration Options

### Custom Confidence Threshold

```python
# Only detect bots we're very confident about
paywall = AIPaywall(confidence_threshold=0.9)
```

### Add Custom Bot Patterns

```python
paywall = AIPaywall(custom_patterns=[
    {
        "name": "my_custom_bot",
        "user_agents": ["MyBot/1.0", "CustomCrawler"],
        "confidence": 0.8,
        "description": "My custom bot pattern",
        "company": "My Company"
    }
])
```

### Storage Backend (for analytics)

```python
# Built-in memory storage
paywall = AIPaywall(storage_backend=memory_storage)

# Or implement your own storage
class MyStorage:
    def log_detection(self, result):
        # Save to database, send to analytics, etc.
        pass

paywall = AIPaywall(storage_backend=MyStorage())
```

## Detection Patterns

The module includes community-maintained patterns for:

- **OpenAI**: GPTBot, ChatGPT-User
- **Anthropic**: Claude-Web, ClaudeBot
- **Google**: Google-Extended, Bard-related bots
- **Microsoft**: Bing-AI, EdgeBot
- **Meta**: facebookexternalhit (AI training mode)
- **Common Crawl**: CCBot (used by many AI companies)
- **Cohere**: CohereBot
- **Perplexity**: PerplexityBot
- **ByteDance**: Bytespider
- **Generic AI**: Pattern-based detection for unknown AI bots

## Roadmap

- ✅ **Phase 1**: Detection and logging (CURRENT)
- 🚧 **Phase 2**: Manual payment processing (coming next)
- 📋 **Phase 3**: Automated payment flows
- 📋 **Phase 4**: ML-based bot detection
- 📋 **Phase 5**: Content-based pricing
- 📋 **Phase 6**: Enterprise features

## Future Features (Not Yet Implemented)

These features are planned but not yet available:

### Payment Integration (Phase 2+)

```python
# FUTURE - Not yet implemented
paywall = AIPaywall(
    mode='paywall',  # Will be available in Phase 2
    pricing={'monthly': 50},
    payment_provider='stripe'
)
```

### Block Mode (Phase 2+)

```python
# FUTURE - Not yet implemented
paywall = AIPaywall(mode='block')  # Will return 403 to bots
```

### Analytics Dashboard (Phase 3+)

```python
# FUTURE - Not yet implemented
stats = paywall.get_stats()  # Will provide analytics
paywall.export_logs('bot_activity.csv')  # Will export data
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/jamesfishwick/ai-paywall.git
cd ai-paywall

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=ai_paywall --cov-report=html

# Run specific test file
pytest tests/test_core.py

# Run tests with verbose output
pytest -v

# Run tests and generate coverage report
pytest --cov=ai_paywall --cov-report=term-missing
```

### Code Quality

This project enforces high code quality standards:

```bash
# Format code with black
black ai_paywall tests

# Sort imports with isort
isort ai_paywall tests

# Lint with flake8
flake8 ai_paywall tests

# Type check with mypy
mypy ai_paywall --ignore-missing-imports

# Run all quality checks
python -m pytest && black ai_paywall tests && isort ai_paywall tests && flake8 ai_paywall tests && mypy ai_paywall --ignore-missing-imports
```

### Pre-commit Hooks

Install pre-commit hooks to automatically run quality checks:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### Project Structure

```
ai-paywall/
├── ai_paywall/              # Main package
│   ├── __init__.py          # Public API
│   ├── core.py              # Core AIPaywall class
│   ├── patterns.py          # Bot detection patterns
│   └── adapters/            # Framework adapters
│       ├── __init__.py
│       └── request.py       # Universal request adapter
├── tests/                   # Test suite
│   ├── test_core.py         # Core functionality tests
│   ├── test_patterns.py     # Pattern management tests
│   ├── test_adapters.py     # Request adapter tests
│   ├── test_integration.py  # End-to-end tests
│   └── test_init.py         # Module initialization tests
├── docs/                    # Documentation
├── examples/                # Usage examples
├── pyproject.toml           # Project configuration
├── CLAUDE.md               # Development guidance
└── README.md               # This file
```

## Philosophy

This project is inspired by the belief that:

1. **Content creators deserve compensation** when their work trains AI systems
2. **The open web should remain free** for human readers and researchers
3. **Fair use applies to humans**, not corporate AI training
4. **Technology should serve creators**, not just consumers

## Contributing

We welcome contributions to bot detection patterns, payment integrations, and framework adapters. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Legal

This module helps enforce your existing rights as a content creator. Consult your local laws regarding web scraping, terms of service, and payment processing.

## License

MIT License - Use it to protect your content and get paid for your work.
