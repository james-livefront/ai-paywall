"""
Tests for ai_paywall.__init__ module.
"""

from ai_paywall import AIPaywall, DetectionResult, RequestAdapter


class TestModuleInit:
    """Test module initialization and exports."""

    def test_module_exports(self):
        """Test that all expected classes are exported."""
        # Test that classes can be imported
        assert AIPaywall is not None
        assert DetectionResult is not None
        assert RequestAdapter is not None

    def test_aipaywall_class_import(self):
        """Test AIPaywall class can be imported and instantiated."""
        paywall = AIPaywall()
        assert paywall is not None
        assert hasattr(paywall, "check")
        assert hasattr(paywall, "mode")
        assert hasattr(paywall, "confidence_threshold")

    def test_detection_result_class_import(self):
        """Test DetectionResult class can be imported and instantiated."""
        result = DetectionResult(is_bot=True)
        assert result is not None
        assert result.is_bot is True
        assert hasattr(result, "bot_type")
        assert hasattr(result, "confidence")
        assert hasattr(result, "timestamp")

    def test_request_adapter_class_import(self):
        """Test RequestAdapter class can be imported and instantiated."""
        adapter = RequestAdapter()
        assert adapter is not None
        assert hasattr(adapter, "adapt")

    def test_module_version(self):
        """Test that module version is defined."""
        import ai_paywall

        assert hasattr(ai_paywall, "__version__")
        assert ai_paywall.__version__ == "0.1.0"

    def test_module_all_attribute(self):
        """Test that __all__ attribute is defined."""
        import ai_paywall

        assert hasattr(ai_paywall, "__all__")
        assert isinstance(ai_paywall.__all__, list)
        assert "AIPaywall" in ai_paywall.__all__
        assert "DetectionResult" in ai_paywall.__all__
        assert "RequestAdapter" in ai_paywall.__all__

    def test_public_api_classes_work_together(self):
        """Test that public API classes work together."""
        # Test creating paywall and checking a mock request
        paywall = AIPaywall()

        # Create a mock request-like object
        class MockRequest:
            def __init__(self):
                self.__class__.__module__ = "test.module"
                self.headers = {"User-Agent": "GPTBot/1.0"}
                self.method = "GET"
                self.path = "/test"

        mock_request = MockRequest()
        result = paywall.check(mock_request)

        assert isinstance(result, DetectionResult)
        assert result.is_bot is True
        assert result.bot_type == "openai"
