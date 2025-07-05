"""
Community bot patterns database for AI Paywall.

This module contains patterns for detecting known AI crawlers and bots.
"""

from typing import Any, Dict, List

# Known AI bot patterns
BOT_PATTERNS: Dict[str, Dict[str, Any]] = {
    "openai": {
        "user_agents": [
            "GPTBot",
            "ChatGPT-User",
            "GPTBot/1.0",
            "ChatGPT-User/1.0",
        ],
        "ip_ranges": [
            "20.171.0.0/16",  # OpenAI IP range
            "40.83.0.0/16",  # Additional OpenAI range
        ],
        "headers": {"User-Agent": ["GPTBot", "ChatGPT-User"]},
        "confidence": 0.95,
        "description": "OpenAI crawlers (GPTBot, ChatGPT-User)",
        "docs_url": "https://platform.openai.com/docs/gptbot",
        "company": "OpenAI",
    },
    "anthropic": {
        "user_agents": [
            "Claude-Web",
            "Claude-Web/1.0",
            "ClaudeBot",
            "ClaudeBot/1.0",
        ],
        "confidence": 0.95,
        "description": "Anthropic Claude crawlers",
        "docs_url": "https://docs.anthropic.com/claude/docs/web-search",
        "company": "Anthropic",
    },
    "google": {
        "user_agents": [
            "Google-Extended",
            "GoogleBot-Extended",
            "Bard",
            "GoogleBot-AI",
            {"regex": r"Google.*AI"},
        ],
        "confidence": 0.90,
        "description": "Google AI crawlers (Bard, Google-Extended)",
        "docs_url": "https://developers.google.com/search/docs/"
        "crawling-indexing/overview-google-crawlers",
        "company": "Google",
    },
    "microsoft": {
        "user_agents": [
            "Bing-AI",
            "BingBot-AI",
            "EdgeBot",
            "MSNBot-AI",
            {"regex": r"Bing.*AI"},
        ],
        "confidence": 0.90,
        "description": "Microsoft AI crawlers (Bing AI, Edge AI)",
        "company": "Microsoft",
    },
    "cohere": {
        "user_agents": [
            "Cohere-AI",
            "CohereBot",
            "CoBot",
        ],
        "confidence": 0.90,
        "description": "Cohere AI crawlers",
        "company": "Cohere",
    },
    "perplexity": {
        "user_agents": [
            "PerplexityBot",
            "Perplexity-AI",
            "PerplexityBot/1.0",
        ],
        "confidence": 0.90,
        "description": "Perplexity AI crawlers",
        "company": "Perplexity",
    },
    "common_crawl": {
        "user_agents": [
            "CCBot",
            "CCBot/2.0",
            "Common Crawl",
            {"regex": r"CCBot/\d+\.\d+"},
        ],
        "confidence": 0.85,
        "description": "Common Crawl bot (often used for AI training)",
        "docs_url": "https://commoncrawl.org/big-picture/frequently-asked-questions/",
        "company": "Common Crawl",
    },
    "meta": {
        "user_agents": [
            "FacebookBot",
            "facebookexternalhit",
            "Meta-ExternalAgent",
            "Meta-AI",
            {"regex": r"Facebook.*AI"},
        ],
        "confidence": 0.85,
        "description": "Meta/Facebook AI crawlers",
        "company": "Meta",
    },
    "bytedance": {
        "user_agents": [
            "Bytespider",
            "Bytespider/1.0",
            "ByteDance",
            "TikTokBot",
        ],
        "confidence": 0.85,
        "description": "ByteDance crawlers (TikTok parent company)",
        "company": "ByteDance",
    },
    "generic_ai": {
        "user_agents": [
            {"regex": r".*AI.*Bot"},
            {"regex": r".*AI.*Crawler"},
            {"regex": r".*AI.*Spider"},
            {"regex": r".*ML.*Bot"},
            {"regex": r".*LLM.*Bot"},
            {"regex": r".*GPT.*Bot"},
            {"regex": r".*Language.*Model"},
        ],
        "confidence": 0.70,
        "description": "Generic AI bot patterns",
        "company": "Various",
    },
}


def get_pattern(bot_name: str) -> Dict[str, Any]:
    """
    Get bot pattern by name.

    Args:
        bot_name: Name of the bot pattern

    Returns:
        Bot pattern dict or empty dict if not found
    """
    return BOT_PATTERNS.get(bot_name, {})


def get_all_patterns() -> Dict[str, Dict[str, Any]]:
    """
    Get all bot patterns.

    Returns:
        Dictionary of all bot patterns
    """
    return BOT_PATTERNS.copy()


def add_pattern(name: str, pattern: Dict[str, Any]) -> None:
    """
    Add a new bot pattern.

    Args:
        name: Name of the bot pattern
        pattern: Pattern dictionary
    """
    BOT_PATTERNS[name] = pattern


def remove_pattern(name: str) -> bool:
    """
    Remove a bot pattern.

    Args:
        name: Name of the bot pattern to remove

    Returns:
        True if pattern was removed, False if not found
    """
    if name in BOT_PATTERNS:
        del BOT_PATTERNS[name]
        return True
    return False


def get_user_agents() -> List[str]:
    """
    Get all user agent strings from patterns.

    Returns:
        List of user agent strings
    """
    user_agents = []
    for pattern in BOT_PATTERNS.values():
        for ua in pattern.get("user_agents", []):
            if isinstance(ua, str):
                user_agents.append(ua)
            elif isinstance(ua, dict) and "regex" in ua:
                user_agents.append(ua["regex"])
    return user_agents


def get_ip_ranges() -> List[str]:
    """
    Get all IP ranges from patterns.

    Returns:
        List of IP ranges
    """
    ip_ranges = []
    for pattern in BOT_PATTERNS.values():
        ip_ranges.extend(pattern.get("ip_ranges", []))
    return ip_ranges


def validate_pattern(pattern: Dict[str, Any]) -> List[str]:
    """
    Validate a bot pattern.

    Args:
        pattern: Pattern dictionary to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check required fields
    if "confidence" not in pattern:
        errors.append("Missing required field: confidence")
    elif not isinstance(pattern["confidence"], (int, float)) or not (
        0 <= pattern["confidence"] <= 1
    ):
        errors.append("confidence must be a number between 0 and 1")

    # Check user_agents format
    if "user_agents" in pattern:
        if not isinstance(pattern["user_agents"], list):
            errors.append("user_agents must be a list")
        else:
            for ua in pattern["user_agents"]:
                if not isinstance(ua, (str, dict)):
                    errors.append("user_agents items must be strings or dicts")
                elif isinstance(ua, dict) and "regex" not in ua:
                    errors.append("user_agents dict items must have 'regex' key")

    # Check ip_ranges format
    if "ip_ranges" in pattern:
        if not isinstance(pattern["ip_ranges"], list):
            errors.append("ip_ranges must be a list")
        else:
            for ip_range in pattern["ip_ranges"]:
                if not isinstance(ip_range, str):
                    errors.append("ip_ranges items must be strings")

    # Check headers format
    if "headers" in pattern:
        if not isinstance(pattern["headers"], dict):
            errors.append("headers must be a dict")

    return errors
