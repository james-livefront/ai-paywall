"""
Tests for ai_paywall.core module.
"""

from datetime import datetime
from unittest.mock import Mock, patch

from ai_paywall.core import AIPaywall, DetectionResult
from ai_paywall.patterns import BOT_PATTERNS


class TestDetectionResult:
    """Test DetectionResult class."""

    def test_init_with_defaults(self):
        """Test DetectionResult initialization with default values."""
        result = DetectionResult(is_bot=True)

        assert result.is_bot is True
        assert result.bot_type is None
        assert result.confidence == 0.0
        assert result.detection_method is None
        assert result.user_agent is None
        assert result.ip_address is None
        assert result.metadata == {}
        assert isinstance(result.timestamp, datetime)

    def test_init_with_custom_values(self):
        """Test DetectionResult initialization with custom values."""
        custom_time = datetime(2023, 1, 1, 12, 0, 0)
        metadata = {"test": "value"}

        result = DetectionResult(
            is_bot=True,
            bot_type="openai",
            confidence=0.95,
            detection_method="user_agent",
            user_agent="GPTBot",
            ip_address="127.0.0.1",
            metadata=metadata,
            timestamp=custom_time,
        )

        assert result.is_bot is True
        assert result.bot_type == "openai"
        assert result.confidence == 0.95
        assert result.detection_method == "user_agent"
        assert result.user_agent == "GPTBot"
        assert result.ip_address == "127.0.0.1"
        assert result.metadata == metadata
        assert result.timestamp == custom_time

    def test_post_init_sets_timestamp(self):
        """Test that __post_init__ sets timestamp if None."""
        result = DetectionResult(is_bot=False)
        assert result.timestamp is not None
        assert isinstance(result.timestamp, datetime)

    def test_post_init_sets_metadata(self):
        """Test that __post_init__ sets metadata if None."""
        result = DetectionResult(is_bot=False)
        assert result.metadata == {}


class TestAIPaywall:
    """Test AIPaywall class."""

    def test_init_with_defaults(self):
        """Test AIPaywall initialization with default values."""
        paywall = AIPaywall()

        assert paywall.mode == "detect"
        assert paywall.confidence_threshold == 0.7
        assert paywall.storage_backend is None
        assert paywall.patterns == BOT_PATTERNS
        assert paywall.request_adapter is not None

    def test_init_with_custom_values(self):
        """Test AIPaywall initialization with custom values."""
        custom_patterns = {"custom": {"confidence": 0.8}}
        storage_mock = Mock()

        paywall = AIPaywall(
            mode="block",
            patterns=custom_patterns,
            confidence_threshold=0.9,
            storage_backend=storage_mock,
        )

        assert paywall.mode == "block"
        assert paywall.confidence_threshold == 0.9
        assert paywall.storage_backend == storage_mock
        assert paywall.patterns == custom_patterns

    def test_init_with_custom_patterns(self):
        """Test AIPaywall initialization with custom patterns added."""
        custom_patterns = [{"name": "custom", "confidence": 0.8}]

        paywall = AIPaywall(custom_patterns=custom_patterns)

        assert "custom" in paywall.patterns
        assert paywall.patterns["custom"]["confidence"] == 0.8

    @patch("ai_paywall.core.RequestAdapter")
    def test_check_calls_adapter_and_detector(self, mock_adapter_class):
        """Test that check() calls the adapter and detector."""
        mock_adapter = Mock()
        mock_adapter.adapt.return_value = {
            "user_agent": "Mozilla/5.0",
            "ip_address": "127.0.0.1",
            "headers": {},
        }
        mock_adapter_class.return_value = mock_adapter

        paywall = AIPaywall()
        mock_request = Mock()

        result = paywall.check(mock_request)

        mock_adapter.adapt.assert_called_once_with(mock_request)
        assert isinstance(result, DetectionResult)

    def test_check_with_storage_backend(self):
        """Test that check() logs to storage backend when configured."""
        storage_mock = Mock()
        paywall = AIPaywall(storage_backend=storage_mock)

        # Mock the adapter to return a simple request
        with patch.object(paywall.request_adapter, "adapt") as mock_adapt:
            mock_adapt.return_value = {
                "user_agent": "Mozilla/5.0",
                "ip_address": "127.0.0.1",
                "headers": {},
            }

            mock_request = Mock()
            result = paywall.check(mock_request)

            storage_mock.log_detection.assert_called_once_with(result)

    def test_detect_bot_with_known_user_agent(self):
        """Test bot detection with known user agent."""
        paywall = AIPaywall()

        request_data = {
            "user_agent": "GPTBot/1.0",
            "ip_address": "127.0.0.1",
            "headers": {},
        }

        result = paywall._detect_bot(request_data)

        assert result.is_bot is True
        assert result.bot_type == "openai"
        assert result.detection_method == "user_agent"
        assert result.confidence >= 0.7

    def test_detect_bot_with_unknown_user_agent(self):
        """Test bot detection with unknown user agent."""
        paywall = AIPaywall()

        request_data = {
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            ),
            "ip_address": "127.0.0.1",
            "headers": {},
        }

        result = paywall._detect_bot(request_data)

        assert result.is_bot is False
        assert result.bot_type is None

    def test_detect_bot_with_known_ip(self):
        """Test bot detection with known IP range."""
        paywall = AIPaywall()

        request_data = {
            "user_agent": "Mozilla/5.0",
            "ip_address": "20.171.1.1",  # OpenAI IP range
            "headers": {},
        }

        result = paywall._detect_bot(request_data)

        assert result.is_bot is True
        assert result.bot_type == "openai"
        assert result.detection_method == "ip_range"

    def test_detect_bot_with_confidence_threshold(self):
        """Test bot detection respects confidence threshold."""
        paywall = AIPaywall(confidence_threshold=0.99)  # Very high threshold

        request_data = {
            "user_agent": "GPTBot/1.0",
            "ip_address": "127.0.0.1",
            "headers": {},
        }

        result = paywall._detect_bot(request_data)

        # Should NOT detect because OpenAI has 0.95 confidence < 0.99 threshold
        assert result.is_bot is False

    def test_check_user_agent_exact_match(self):
        """Test user agent checking with exact match."""
        paywall = AIPaywall()

        result = paywall._check_user_agent("GPTBot")

        assert result.is_bot is True
        assert result.bot_type == "openai"
        assert result.metadata is not None
        assert "GPTBot" in result.metadata["matched_pattern"]

    def test_check_user_agent_substring_match(self):
        """Test user agent checking with substring match."""
        paywall = AIPaywall()

        result = paywall._check_user_agent("Mozilla/5.0 (compatible; GPTBot/1.0)")

        assert result.is_bot is True
        assert result.bot_type == "openai"

    def test_check_user_agent_regex_match(self):
        """Test user agent checking with regex pattern."""
        paywall = AIPaywall()

        result = paywall._check_user_agent("SomeAIBot/1.0")

        assert result.is_bot is True
        assert result.bot_type == "generic_ai"

    def test_check_user_agent_no_match(self):
        """Test user agent checking with no match."""
        paywall = AIPaywall()

        result = paywall._check_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

        assert result.is_bot is False

    def test_check_user_agent_empty(self):
        """Test user agent checking with empty string."""
        paywall = AIPaywall()

        result = paywall._check_user_agent("")

        assert result.is_bot is False

    def test_check_ip_ranges_valid_ip_in_range(self):
        """Test IP range checking with valid IP in range."""
        paywall = AIPaywall()

        result = paywall._check_ip_ranges("20.171.1.1")

        assert result.is_bot is True
        assert result.bot_type == "openai"
        assert result.metadata is not None
        assert result.metadata["matched_ip_range"] == "20.171.0.0/16"

    def test_check_ip_ranges_valid_ip_not_in_range(self):
        """Test IP range checking with valid IP not in range."""
        paywall = AIPaywall()

        result = paywall._check_ip_ranges("192.168.1.1")

        assert result.is_bot is False

    def test_check_ip_ranges_invalid_ip(self):
        """Test IP range checking with invalid IP."""
        paywall = AIPaywall()

        result = paywall._check_ip_ranges("not.an.ip.address")

        assert result.is_bot is False

    def test_check_ip_ranges_empty(self):
        """Test IP range checking with empty string."""
        paywall = AIPaywall()

        result = paywall._check_ip_ranges("")

        assert result.is_bot is False

    def test_check_headers_match(self):
        """Test header checking with matching headers."""
        paywall = AIPaywall()

        headers = {"User-Agent": "GPTBot/1.0"}
        result = paywall._check_headers(headers)

        assert result.is_bot is True
        assert result.bot_type == "openai"

    def test_check_headers_case_insensitive(self):
        """Test header checking is case insensitive."""
        paywall = AIPaywall()

        headers = {"user-agent": "gptbot/1.0"}
        result = paywall._check_headers(headers)

        assert result.is_bot is True
        assert result.bot_type == "openai"

    def test_check_headers_no_match(self):
        """Test header checking with no match."""
        paywall = AIPaywall()

        headers = {"User-Agent": "Mozilla/5.0"}
        result = paywall._check_headers(headers)

        assert result.is_bot is False

    def test_check_headers_empty(self):
        """Test header checking with empty headers."""
        paywall = AIPaywall()

        result = paywall._check_headers({})

        assert result.is_bot is False

    def test_add_custom_patterns(self):
        """Test adding custom patterns."""
        paywall = AIPaywall()

        custom_patterns = [
            {"name": "custom1", "confidence": 0.8},
            {"name": "custom2", "confidence": 0.9},
        ]

        paywall._add_custom_patterns(custom_patterns)

        assert "custom1" in paywall.patterns
        assert "custom2" in paywall.patterns
        assert paywall.patterns["custom1"]["confidence"] == 0.8
        assert paywall.patterns["custom2"]["confidence"] == 0.9

    def test_add_custom_patterns_without_name(self):
        """Test adding custom patterns without name key."""
        paywall = AIPaywall()

        custom_patterns = [{"confidence": 0.8}]  # No name key

        paywall._add_custom_patterns(custom_patterns)

        # Should not add patterns without name
        assert len(paywall.patterns) == len(BOT_PATTERNS)
