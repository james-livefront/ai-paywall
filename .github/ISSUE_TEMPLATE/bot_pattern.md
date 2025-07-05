---
name: New Bot Pattern
about: Submit a new AI bot detection pattern
title: 'Add pattern for [Bot Name]'
labels: 'bot-pattern'
assignees: ''

---

**Bot Information**
- Bot Name:
- Company:
- Official Documentation:

**Detection Pattern**
```python
'bot_name': {
    'user_agents': ['BotName/1.0', 'BotName-Crawler'],
    'ip_ranges': ['192.168.1.0/24'],  # if known
    'confidence': 0.9,  # 0.0 to 1.0
    'description': 'Description of what this bot does',
    'docs_url': 'https://example.com/bot-docs'  # if available
}
```

**Evidence**
How did you identify this bot? Include:
- Log entries showing the user agent
- Official announcements
- Documentation links
- Traffic analysis

**Testing**
Have you tested this pattern? How many requests did it catch?

**Additional Notes**
Any other relevant information about this bot's behavior.
