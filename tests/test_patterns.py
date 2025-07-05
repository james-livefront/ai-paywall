"""
Tests for ai_paywall.patterns module.
"""

from ai_paywall.patterns import (
    BOT_PATTERNS,
    add_pattern,
    get_all_patterns,
    get_ip_ranges,
    get_pattern,
    get_user_agents,
    remove_pattern,
    validate_pattern,
)


class TestBotPatterns:
    """Test bot patterns functionality."""

    def test_bot_patterns_structure(self):
        """Test that BOT_PATTERNS has expected structure."""
        assert isinstance(BOT_PATTERNS, dict)
        assert len(BOT_PATTERNS) > 0

        # Check that all patterns have required fields
        for name, pattern in BOT_PATTERNS.items():
            assert isinstance(name, str)
            assert isinstance(pattern, dict)
            assert "confidence" in pattern
            assert isinstance(pattern["confidence"], (int, float))
            assert 0 <= pattern["confidence"] <= 1

    def test_openai_pattern(self):
        """Test OpenAI pattern specifically."""
        openai_pattern = BOT_PATTERNS["openai"]

        assert openai_pattern["confidence"] == 0.95
        assert "GPTBot" in openai_pattern["user_agents"]
        assert "ChatGPT-User" in openai_pattern["user_agents"]
        assert "20.171.0.0/16" in openai_pattern["ip_ranges"]
        assert openai_pattern["company"] == "OpenAI"

    def test_anthropic_pattern(self):
        """Test Anthropic pattern specifically."""
        anthropic_pattern = BOT_PATTERNS["anthropic"]

        assert anthropic_pattern["confidence"] == 0.95
        assert "Claude-Web" in anthropic_pattern["user_agents"]
        assert anthropic_pattern["company"] == "Anthropic"

    def test_get_pattern_existing(self):
        """Test getting an existing pattern."""
        pattern = get_pattern("openai")

        assert pattern is not None
        assert pattern["confidence"] == 0.95
        assert "GPTBot" in pattern["user_agents"]

    def test_get_pattern_nonexistent(self):
        """Test getting a non-existent pattern."""
        pattern = get_pattern("nonexistent")

        assert pattern == {}

    def test_get_all_patterns(self):
        """Test getting all patterns."""
        patterns = get_all_patterns()

        assert isinstance(patterns, dict)
        assert len(patterns) == len(BOT_PATTERNS)
        assert "openai" in patterns
        assert "anthropic" in patterns

        # Should be a copy, not the same object
        assert patterns is not BOT_PATTERNS

    def test_add_pattern(self):
        """Test adding a new pattern."""
        original_count = len(BOT_PATTERNS)

        new_pattern = {
            "user_agents": ["TestBot"],
            "confidence": 0.8,
            "description": "Test bot",
            "company": "Test Company",
        }

        add_pattern("test_bot", new_pattern)

        assert len(BOT_PATTERNS) == original_count + 1
        assert "test_bot" in BOT_PATTERNS
        assert BOT_PATTERNS["test_bot"] == new_pattern

        # Cleanup
        remove_pattern("test_bot")

    def test_remove_pattern_existing(self):
        """Test removing an existing pattern."""
        # Add a pattern first
        add_pattern("temp_bot", {"confidence": 0.5})
        assert "temp_bot" in BOT_PATTERNS

        # Remove it
        result = remove_pattern("temp_bot")

        assert result is True
        assert "temp_bot" not in BOT_PATTERNS

    def test_remove_pattern_nonexistent(self):
        """Test removing a non-existent pattern."""
        result = remove_pattern("nonexistent_bot")

        assert result is False

    def test_get_user_agents(self):
        """Test getting all user agents."""
        user_agents = get_user_agents()

        assert isinstance(user_agents, list)
        assert len(user_agents) > 0
        assert "GPTBot" in user_agents
        assert "Claude-Web" in user_agents

        # Should include regex patterns
        regex_patterns = [ua for ua in user_agents if ua.startswith(".*")]
        assert len(regex_patterns) > 0

    def test_get_ip_ranges(self):
        """Test getting all IP ranges."""
        ip_ranges = get_ip_ranges()

        assert isinstance(ip_ranges, list)
        assert "20.171.0.0/16" in ip_ranges
        assert "40.83.0.0/16" in ip_ranges

    def test_validate_pattern_valid(self):
        """Test validating a valid pattern."""
        valid_pattern = {
            "user_agents": ["TestBot"],
            "confidence": 0.8,
            "description": "Test bot",
        }

        errors = validate_pattern(valid_pattern)

        assert errors == []

    def test_validate_pattern_missing_confidence(self):
        """Test validating a pattern missing confidence."""
        invalid_pattern = {"user_agents": ["TestBot"], "description": "Test bot"}

        errors = validate_pattern(invalid_pattern)

        assert "Missing required field: confidence" in errors

    def test_validate_pattern_invalid_confidence(self):
        """Test validating a pattern with invalid confidence."""
        invalid_pattern = {
            "user_agents": ["TestBot"],
            "confidence": 1.5,  # Invalid: > 1
            "description": "Test bot",
        }

        errors = validate_pattern(invalid_pattern)

        assert "confidence must be a number between 0 and 1" in errors

    def test_validate_pattern_invalid_user_agents(self):
        """Test validating a pattern with invalid user_agents."""
        invalid_pattern = {
            "user_agents": "TestBot",  # Should be list
            "confidence": 0.8,
            "description": "Test bot",
        }

        errors = validate_pattern(invalid_pattern)

        assert "user_agents must be a list" in errors

    def test_validate_pattern_invalid_user_agents_item(self):
        """Test validating a pattern with invalid user_agents item."""
        invalid_pattern = {
            "user_agents": [123],  # Should be string or dict
            "confidence": 0.8,
            "description": "Test bot",
        }

        errors = validate_pattern(invalid_pattern)

        assert "user_agents items must be strings or dicts" in errors

    def test_validate_pattern_invalid_user_agents_dict(self):
        """Test validating a pattern with invalid user_agents dict."""
        invalid_pattern = {
            "user_agents": [{"invalid": "dict"}],  # Should have regex key
            "confidence": 0.8,
            "description": "Test bot",
        }

        errors = validate_pattern(invalid_pattern)

        assert "user_agents dict items must have 'regex' key" in errors

    def test_validate_pattern_invalid_ip_ranges(self):
        """Test validating a pattern with invalid ip_ranges."""
        invalid_pattern = {
            "ip_ranges": "192.168.1.0/24",  # Should be list
            "confidence": 0.8,
            "description": "Test bot",
        }

        errors = validate_pattern(invalid_pattern)

        assert "ip_ranges must be a list" in errors

    def test_validate_pattern_invalid_ip_ranges_item(self):
        """Test validating a pattern with invalid ip_ranges item."""
        invalid_pattern = {
            "ip_ranges": [123],  # Should be string
            "confidence": 0.8,
            "description": "Test bot",
        }

        errors = validate_pattern(invalid_pattern)

        assert "ip_ranges items must be strings" in errors

    def test_validate_pattern_invalid_headers(self):
        """Test validating a pattern with invalid headers."""
        invalid_pattern = {
            "headers": "invalid",  # Should be dict
            "confidence": 0.8,
            "description": "Test bot",
        }

        errors = validate_pattern(invalid_pattern)

        assert "headers must be a dict" in errors

    def test_validate_pattern_multiple_errors(self):
        """Test validating a pattern with multiple errors."""
        invalid_pattern = {
            "user_agents": "TestBot",  # Should be list
            "confidence": 2.0,  # Invalid: > 1
            "headers": "invalid",  # Should be dict
        }

        errors = validate_pattern(invalid_pattern)

        assert len(errors) == 3
        assert "user_agents must be a list" in errors
        assert "confidence must be a number between 0 and 1" in errors
        assert "headers must be a dict" in errors

    def test_patterns_have_descriptions(self):
        """Test that all patterns have descriptions."""
        for name, pattern in BOT_PATTERNS.items():
            assert "description" in pattern, f"Pattern {name} missing description"
            assert isinstance(
                pattern["description"], str
            ), f"Pattern {name} description not string"
            assert len(pattern["description"]) > 0, f"Pattern {name} description empty"

    def test_patterns_have_companies(self):
        """Test that all patterns have company information."""
        for name, pattern in BOT_PATTERNS.items():
            assert "company" in pattern, f"Pattern {name} missing company"
            assert isinstance(
                pattern["company"], str
            ), f"Pattern {name} company not string"
            assert len(pattern["company"]) > 0, f"Pattern {name} company empty"

    def test_regex_patterns_format(self):
        """Test that regex patterns in user_agents are properly formatted."""
        for name, pattern in BOT_PATTERNS.items():
            user_agents = pattern.get("user_agents", [])
            for ua in user_agents:
                if isinstance(ua, dict) and "regex" in ua:
                    assert isinstance(
                        ua["regex"], str
                    ), f"Pattern {name} regex not string"
                    assert len(ua["regex"]) > 0, f"Pattern {name} regex empty"
