"""
Integration tests for AI Paywall.
"""

from unittest.mock import Mock

from ai_paywall import AIPaywall, DetectionResult


class TestAIPaywallIntegration:
    """Integration tests for the complete AI Paywall flow."""

    def test_end_to_end_bot_detection(self):
        """Test complete bot detection flow."""
        paywall = AIPaywall()

        # Mock Django request with bot user agent
        mock_request = Mock()
        mock_request.__class__.__module__ = "django.http.request"
        mock_request.META = {
            "HTTP_USER_AGENT": "GPTBot/1.0",
            "REMOTE_ADDR": "127.0.0.1",
        }
        mock_request.method = "GET"
        mock_request.path = "/article/test"
        mock_request.GET = Mock()
        mock_request.GET.dict.return_value = {}

        result = paywall.check(mock_request)

        assert isinstance(result, DetectionResult)
        assert result.is_bot is True
        assert result.bot_type == "openai"
        assert result.user_agent == "GPTBot/1.0"
        assert result.ip_address == "127.0.0.1"
        assert result.detection_method == "user_agent"
        assert result.confidence >= 0.7

    def test_end_to_end_human_detection(self):
        """Test complete human detection flow."""
        paywall = AIPaywall()

        # Mock Flask request with human user agent
        mock_request = Mock()
        mock_request.__class__.__module__ = "flask.wrappers"
        mock_request.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        mock_request.environ = {
            "REMOTE_ADDR": "192.168.1.100",
        }
        mock_request.method = "GET"
        mock_request.path = "/home"
        mock_request.args = Mock()
        mock_request.args.to_dict.return_value = {}

        result = paywall.check(mock_request)

        assert isinstance(result, DetectionResult)
        assert result.is_bot is False
        assert result.bot_type is None
        assert result.user_agent is not None
        assert result.user_agent.startswith("Mozilla/5.0")
        assert result.ip_address == "192.168.1.100"
        assert result.detection_method is None

    def test_end_to_end_with_storage(self):
        """Test complete flow with storage backend."""
        storage_mock = Mock()
        paywall = AIPaywall(storage_backend=storage_mock)

        # Mock FastAPI request
        mock_request = Mock()
        mock_request.__class__.__module__ = "fastapi.requests"
        mock_request.headers = {
            "user-agent": "Claude-Web/1.0",
            "accept": "text/html",
        }
        mock_request.client = Mock()
        mock_request.client.host = "203.0.113.1"
        mock_request.method = "GET"
        mock_request.url = Mock()
        mock_request.url.path = "/api/content"
        mock_request.query_params = {"id": "123"}

        paywall.check(mock_request)

        # Check that storage was called
        storage_mock.log_detection.assert_called_once()
        call_args = storage_mock.log_detection.call_args[0]
        logged_result = call_args[0]

        assert isinstance(logged_result, DetectionResult)
        assert logged_result.is_bot is True
        assert logged_result.bot_type == "anthropic"
        assert logged_result.user_agent == "Claude-Web/1.0"

    def test_end_to_end_with_custom_patterns(self):
        """Test complete flow with custom patterns."""
        custom_patterns = [
            {
                "name": "custom_bot",
                "user_agents": ["CustomBot/1.0"],
                "confidence": 0.8,
                "description": "Custom test bot",
                "company": "Test Inc",
            }
        ]

        paywall = AIPaywall(custom_patterns=custom_patterns)

        # Mock request with custom bot
        mock_request = Mock()
        mock_request.__class__.__module__ = "django.http.request"
        mock_request.META = {
            "HTTP_USER_AGENT": "CustomBot/1.0",
            "REMOTE_ADDR": "10.0.0.1",
        }
        mock_request.method = "GET"
        mock_request.path = "/test"
        mock_request.GET = Mock()
        mock_request.GET.dict.return_value = {}

        result = paywall.check(mock_request)

        assert result.is_bot is True
        assert result.bot_type == "custom_bot"
        assert result.user_agent == "CustomBot/1.0"
        assert result.confidence == 0.8

    def test_end_to_end_confidence_threshold(self):
        """Test complete flow with confidence threshold."""
        paywall = AIPaywall(confidence_threshold=0.99)  # Very high threshold

        # Mock request with lower confidence bot
        mock_request = Mock()
        mock_request.__class__.__module__ = "django.http.request"
        mock_request.META = {
            "HTTP_USER_AGENT": "SomeAIBot/1.0",  # Generic AI pattern (0.7 confidence)
            "REMOTE_ADDR": "10.0.0.1",
        }
        mock_request.method = "GET"
        mock_request.path = "/test"
        mock_request.GET = Mock()
        mock_request.GET.dict.return_value = {}

        result = paywall.check(mock_request)

        # Should not be detected as bot due to high threshold
        assert result.is_bot is False

    def test_end_to_end_ip_detection(self):
        """Test complete flow with IP-based detection."""
        paywall = AIPaywall()

        # Mock request with OpenAI IP but generic user agent
        mock_request = Mock()
        mock_request.__class__.__module__ = "flask.wrappers"
        mock_request.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; SomeBot/1.0)",
        }
        mock_request.environ = {
            "REMOTE_ADDR": "20.171.1.1",  # OpenAI IP range
        }
        mock_request.method = "GET"
        mock_request.path = "/content"
        mock_request.args = Mock()
        mock_request.args.to_dict.return_value = {}

        result = paywall.check(mock_request)

        assert result.is_bot is True
        assert result.bot_type == "openai"
        assert result.detection_method == "ip_range"
        assert result.ip_address == "20.171.1.1"

    def test_end_to_end_multiple_detection_methods(self):
        """Test that the first successful detection method is used."""
        paywall = AIPaywall()

        # Mock request with both user agent and IP matching
        mock_request = Mock()
        mock_request.__class__.__module__ = "fastapi.requests"
        mock_request.headers = {
            "user-agent": "GPTBot/1.0",  # Should match first
        }
        mock_request.client = Mock()
        mock_request.client.host = "20.171.1.1"  # Would also match
        mock_request.method = "GET"
        mock_request.url = Mock()
        mock_request.url.path = "/test"
        mock_request.query_params = {}

        result = paywall.check(mock_request)

        assert result.is_bot is True
        assert result.bot_type == "openai"
        assert result.detection_method == "user_agent"  # Should be first method
        assert result.user_agent == "GPTBot/1.0"

    def test_end_to_end_regex_pattern_matching(self):
        """Test complete flow with regex pattern matching."""
        paywall = AIPaywall()

        # Mock request with user agent matching regex pattern
        mock_request = Mock()
        mock_request.__class__.__module__ = "django.http.request"
        mock_request.META = {
            "HTTP_USER_AGENT": "MyCustomAIBot/2.0",  # Should match generic AI regex
            "REMOTE_ADDR": "192.168.1.1",
        }
        mock_request.method = "GET"
        mock_request.path = "/api/data"
        mock_request.GET = Mock()
        mock_request.GET.dict.return_value = {}

        result = paywall.check(mock_request)

        assert result.is_bot is True
        assert result.bot_type == "generic_ai"
        assert result.detection_method == "user_agent"
        assert result.user_agent == "MyCustomAIBot/2.0"

    def test_end_to_end_header_detection(self):
        """Test complete flow with header-based detection."""
        paywall = AIPaywall()

        # Mock request with headers but no user agent match
        mock_request = Mock()
        mock_request.__class__.__module__ = "flask.wrappers"
        mock_request.headers = {
            "User-Agent": "CustomClient/1.0",  # No direct match
            "Accept": "application/json",
        }
        mock_request.environ = {
            "REMOTE_ADDR": "192.168.1.1",
        }
        mock_request.method = "GET"
        mock_request.path = "/api/test"
        mock_request.args = Mock()
        mock_request.args.to_dict.return_value = {}

        result = paywall.check(mock_request)

        # Should not be detected as bot (no header patterns in default config)
        assert result.is_bot is False

    def test_end_to_end_different_frameworks(self):
        """Test that detection works consistently across frameworks."""
        paywall = AIPaywall()

        # Test with same bot user agent across different frameworks
        bot_ua = "GPTBot/1.0"

        # Django request
        django_request = Mock()
        django_request.__class__.__module__ = "django.http.request"
        django_request.META = {"HTTP_USER_AGENT": bot_ua, "REMOTE_ADDR": "127.0.0.1"}
        django_request.method = "GET"
        django_request.path = "/test"
        django_request.GET = Mock()
        django_request.GET.dict.return_value = {}

        # Flask request
        flask_request = Mock()
        flask_request.__class__.__module__ = "flask.wrappers"
        flask_request.headers = {"User-Agent": bot_ua}
        flask_request.environ = {"REMOTE_ADDR": "127.0.0.1"}
        flask_request.method = "GET"
        flask_request.path = "/test"
        flask_request.args = Mock()
        flask_request.args.to_dict.return_value = {}

        # FastAPI request
        fastapi_request = Mock()
        fastapi_request.__class__.__module__ = "fastapi.requests"
        fastapi_request.headers = {"user-agent": bot_ua}
        fastapi_request.client = Mock()
        fastapi_request.client.host = "127.0.0.1"
        fastapi_request.method = "GET"
        fastapi_request.url = Mock()
        fastapi_request.url.path = "/test"
        fastapi_request.query_params = {}

        # Test all frameworks
        django_result = paywall.check(django_request)
        flask_result = paywall.check(flask_request)
        fastapi_result = paywall.check(fastapi_request)

        # All should detect the bot
        assert django_result.is_bot is True
        assert flask_result.is_bot is True
        assert fastapi_result.is_bot is True

        # All should have same bot type
        assert django_result.bot_type == "openai"
        assert flask_result.bot_type == "openai"
        assert fastapi_result.bot_type == "openai"

        # All should have same confidence
        assert django_result.confidence == flask_result.confidence
        assert flask_result.confidence == fastapi_result.confidence
