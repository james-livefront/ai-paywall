# AI Paywall

A universal Python module that enables content creators to charge AI crawlers for access to their content while keeping it free for human visitors.

## Why?

AI companies are training billion-dollar models on freely available web content. This module gives content creators control over their intellectual property by requiring AI crawlers to pay for access while preserving the open web for humans.

## Features

- **Universal**: Works with Django, Flask, FastAPI, and any Python web framework
- **Simple**: One import, one function call to get started
- **Flexible**: Start with detection, add payments later
- **Community-driven**: Shared database of AI bot patterns
- **Privacy-focused**: Minimal data collection, respects human privacy

## Quick Start

```bash
pip install ai-paywall
```

```python
from ai_paywall import AIPaywall

# Phase 1: Detection only
paywall = AIPaywall(mode='detect')

# Works with any request object
result = paywall.check(request)
if result.is_bot:
    print(f"AI bot detected: {result.bot_type}")
```

## Framework Integration

### Django
```python
class AIDetectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.paywall = AIPaywall(mode='detect')
    
    def __call__(self, request):
        result = self.paywall.check(request)
        if result.is_bot:
            # Log or block as needed
            request.ai_bot_detected = result
        return self.get_response(request)
```

### Flask
```python
from flask import Flask, request
from ai_paywall import AIPaywall

app = Flask(__name__)
paywall = AIPaywall(mode='detect')

@app.before_request
def check_ai_bots():
    result = paywall.check(request)
    if result.is_bot:
        print(f"Bot detected: {result.bot_type}")
```

### FastAPI
```python
from fastapi import FastAPI, Request
from ai_paywall import AIPaywall

app = FastAPI()
paywall = AIPaywall(mode='detect')

@app.middleware("http")
async def ai_detection_middleware(request: Request, call_next):
    result = paywall.check(request)
    if result.is_bot:
        print(f"Bot detected: {result.bot_type}")
    return await call_next(request)
```

## Modes

### Detection Mode (Phase 1)
```python
paywall = AIPaywall(mode='detect')
# Detects and logs AI bots, no blocking
```

### Block Mode
```python
paywall = AIPaywall(mode='block')
# Returns 403 Forbidden to detected AI bots
```

### Paywall Mode
```python
paywall = AIPaywall(
    mode='paywall',
    pricing={'weekly': 10, 'monthly': 50, 'yearly': 500},
    payment_provider='stripe'
)
# Returns 402 Payment Required with payment flow
```

## Configuration

### Environment Variables
```bash
export AI_PAYWALL_MODE=detect
export AI_PAYWALL_STORAGE=file://./ai_access.db
export AI_PAYWALL_STRIPE_KEY=sk_...
```

### Configuration File
```yaml
# ai-paywall.yaml
mode: paywall
storage: redis://localhost:6379
pricing:
  weekly: 10
  monthly: 50
  yearly: 500
custom_patterns:
  - MyCustomBot/1.0
  - ResearchCrawler
```

### Programmatic Configuration
```python
paywall = AIPaywall(
    mode='paywall',
    storage='redis://localhost:6379',
    pricing={'monthly': 50},
    custom_patterns=['MyBot/1.0']
)
```

## Detection Patterns

The module includes community-maintained patterns for known AI crawlers:

- **OpenAI**: GPTBot, ChatGPT-User
- **Anthropic**: Claude-Web, anthropic-ai
- **Google**: Google-Extended, Bard-related bots
- **Meta**: facebookexternalhit (AI training mode)
- **Common Crawl**: CCBot (used by many AI companies)
- And more...

### Adding Custom Patterns
```python
paywall.add_patterns([
    'MyCustomBot/1.0',
    'ResearchCrawler',
    'UniversityBot'
])
```

## Payment Integration

### Stripe (Automated)
```python
paywall = AIPaywall(
    mode='paywall',
    payment_provider='stripe',
    stripe_key='sk_...'
)
```

### Manual Payment
```python
paywall = AIPaywall(
    mode='paywall',
    payment_provider='manual',
    payment_info={
        'venmo': '@yourusername',
        'paypal': 'you@example.com',
        'contact': 'ai-access@yourdomain.com'
    }
)
```

## Analytics

```python
# Get detection statistics
stats = paywall.get_stats()
print(f"Total requests: {stats['total_requests']}")
print(f"Bot requests: {stats['bot_requests']}")
print(f"Revenue potential: ${stats['revenue_potential']}")

# Export logs
paywall.export_logs('bot_activity.csv')
```

## Philosophy

This project is inspired by the belief that:

1. **Content creators deserve compensation** when their work trains AI systems
2. **The open web should remain free** for human readers and researchers
3. **Fair use applies to humans**, not corporate AI training
4. **Technology should serve creators**, not just consumers

## Roadmap

- [x] **Phase 1**: Detection and logging
- [ ] **Phase 2**: Manual payment processing
- [ ] **Phase 3**: Automated payment flows
- [ ] **Phase 4**: ML-based bot detection
- [ ] **Phase 5**: Content-based pricing
- [ ] **Phase 6**: Enterprise features

## Contributing

We welcome contributions to bot detection patterns, payment integrations, and framework adapters. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Legal

This module helps enforce your existing rights as a content creator. Consult your local laws regarding web scraping, terms of service, and payment processing.

## License

MIT License - Use it to protect your content and get paid for your work.

---

*"The best time to plant a tree was 20 years ago. The second best time is now. The same applies to charging AI companies for your content."*