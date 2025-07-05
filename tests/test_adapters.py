"""
Tests for ai_paywall.adapters module.
"""

from unittest.mock import Mock

from ai_paywall.adapters.request import RequestAdapter


class TestRequestAdapter:
    """Test RequestAdapter class."""

    def test_init(self):
        """Test RequestAdapter initialization."""
        adapter = RequestAdapter()
        assert adapter is not None

    def test_detect_framework_django(self):
        """Test framework detection for Django."""
        adapter = RequestAdapter()

        # Mock Django request
        mock_request = Mock()
        mock_request.__class__.__name__ = "HttpRequest"
        mock_request.__class__.__module__ = "django.http.request"

        framework = adapter._detect_framework(mock_request)
        assert framework == "django"

    def test_detect_framework_flask(self):
        """Test framework detection for Flask."""
        adapter = RequestAdapter()

        # Mock Flask request
        mock_request = Mock()
        mock_request.__class__.__name__ = "Request"
        mock_request.__class__.__module__ = "flask.wrappers"

        framework = adapter._detect_framework(mock_request)
        assert framework == "flask"

    def test_detect_framework_fastapi(self):
        """Test framework detection for FastAPI."""
        adapter = RequestAdapter()

        # Mock FastAPI request
        mock_request = Mock()
        mock_request.__class__.__name__ = "Request"
        mock_request.__class__.__module__ = "fastapi.requests"

        framework = adapter._detect_framework(mock_request)
        assert framework == "fastapi"

    def test_detect_framework_starlette(self):
        """Test framework detection for Starlette."""
        adapter = RequestAdapter()

        # Mock Starlette request
        mock_request = Mock()
        mock_request.__class__.__name__ = "Request"
        mock_request.__class__.__module__ = "starlette.requests"

        framework = adapter._detect_framework(mock_request)
        assert framework == "starlette"

    def test_detect_framework_generic(self):
        """Test framework detection for unknown framework."""
        adapter = RequestAdapter()

        # Mock unknown request
        mock_request = Mock()
        mock_request.__class__.__name__ = "SomeRequest"
        mock_request.__class__.__module__ = "unknown.module"

        framework = adapter._detect_framework(mock_request)
        assert framework == "generic"

    def test_adapt_django_request(self):
        """Test adapting Django request."""
        adapter = RequestAdapter()

        # Mock Django request
        mock_request = Mock()
        mock_request.__class__.__module__ = "django.http.request"
        mock_request.META = {
            "HTTP_USER_AGENT": "Mozilla/5.0",
            "HTTP_X_FORWARDED_FOR": "192.168.1.1",
            "REMOTE_ADDR": "127.0.0.1",
            "HTTP_ACCEPT": "text/html",
        }
        mock_request.method = "GET"
        mock_request.path = "/test"
        mock_request.GET = Mock()
        mock_request.GET.dict.return_value = {"q": "test"}

        result = adapter.adapt(mock_request)

        assert result["user_agent"] == "Mozilla/5.0"
        assert result["ip_address"] == "192.168.1.1"
        assert result["method"] == "GET"
        assert result["path"] == "/test"
        assert result["query_string"] == {"q": "test"}
        assert result["framework"] == "django"
        assert "User-Agent" in result["headers"]
        assert "Accept" in result["headers"]

    def test_adapt_flask_request(self):
        """Test adapting Flask request."""
        adapter = RequestAdapter()

        # Mock Flask request
        mock_request = Mock()
        mock_request.__class__.__module__ = "flask.wrappers"
        mock_request.headers = {
            "User-Agent": "Mozilla/5.0",
            "X-Forwarded-For": "192.168.1.1",
            "Accept": "text/html",
        }
        mock_request.environ = {
            "HTTP_X_FORWARDED_FOR": "192.168.1.1",
            "REMOTE_ADDR": "127.0.0.1",
        }
        mock_request.method = "POST"
        mock_request.path = "/api/test"
        mock_request.args = Mock()
        mock_request.args.to_dict.return_value = {"param": "value"}

        result = adapter.adapt(mock_request)

        assert result["user_agent"] == "Mozilla/5.0"
        assert result["ip_address"] == "192.168.1.1"
        assert result["method"] == "POST"
        assert result["path"] == "/api/test"
        assert result["query_string"] == {"param": "value"}
        assert result["framework"] == "flask"
        assert result["headers"]["User-Agent"] == "Mozilla/5.0"

    def test_adapt_fastapi_request(self):
        """Test adapting FastAPI request."""
        adapter = RequestAdapter()

        # Mock FastAPI request
        mock_request = Mock()
        mock_request.__class__.__module__ = "fastapi.requests"
        mock_request.headers = {
            "user-agent": "Mozilla/5.0",
            "x-forwarded-for": "192.168.1.1",
        }
        mock_request.client = Mock()
        mock_request.client.host = "127.0.0.1"
        mock_request.method = "PUT"
        mock_request.url = Mock()
        mock_request.url.path = "/api/v1/test"
        mock_request.query_params = {"filter": "active"}

        result = adapter.adapt(mock_request)

        assert result["user_agent"] == "Mozilla/5.0"
        assert result["ip_address"] == "127.0.0.1"
        assert result["method"] == "PUT"
        assert result["path"] == "/api/v1/test"
        assert result["query_string"] == {"filter": "active"}
        assert result["framework"] == "fastapi"

    def test_adapt_generic_request(self):
        """Test adapting generic request."""
        adapter = RequestAdapter()

        # Mock generic request
        mock_request = Mock()
        mock_request.__class__.__module__ = "unknown.module"
        mock_request.headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        }
        mock_request.method = "DELETE"
        mock_request.path = "/resource/123"

        result = adapter.adapt(mock_request)

        assert result["user_agent"] == "Mozilla/5.0"
        assert result["method"] == "DELETE"
        assert result["path"] == "/resource/123"
        assert result["framework"] == "generic"
        assert result["headers"]["User-Agent"] == "Mozilla/5.0"

    def test_adapt_generic_request_minimal(self):
        """Test adapting minimal generic request."""
        adapter = RequestAdapter()

        # Mock minimal request with only essential attributes
        mock_request = Mock()
        mock_request.__class__.__module__ = "unknown.module"

        # Remove all optional attributes that would be checked
        if hasattr(mock_request, "headers"):
            del mock_request.headers
        if hasattr(mock_request, "method"):
            del mock_request.method
        if hasattr(mock_request, "path"):
            del mock_request.path
        if hasattr(mock_request, "url"):
            del mock_request.url

        result = adapter.adapt(mock_request)

        assert result["user_agent"] == ""
        assert result["ip_address"] == ""
        assert result["headers"] == {}
        assert result["method"] == "GET"
        assert result["path"] == "/"
        assert result["framework"] == "generic"

    def test_get_client_ip_django_forwarded(self):
        """Test getting client IP from Django with X-Forwarded-For."""
        adapter = RequestAdapter()

        mock_request = Mock()
        mock_request.META = {
            "HTTP_X_FORWARDED_FOR": "192.168.1.1, 10.0.0.1",
            "REMOTE_ADDR": "127.0.0.1",
        }

        ip = adapter._get_client_ip_django(mock_request)
        assert ip == "192.168.1.1"

    def test_get_client_ip_django_remote_addr(self):
        """Test getting client IP from Django with REMOTE_ADDR."""
        adapter = RequestAdapter()

        mock_request = Mock()
        mock_request.META = {
            "REMOTE_ADDR": "127.0.0.1",
        }

        ip = adapter._get_client_ip_django(mock_request)
        assert ip == "127.0.0.1"

    def test_get_client_ip_flask_environ(self):
        """Test getting client IP from Flask environ."""
        adapter = RequestAdapter()

        mock_request = Mock()
        mock_request.environ = {
            "HTTP_X_FORWARDED_FOR": "192.168.1.1, 10.0.0.1",
            "REMOTE_ADDR": "127.0.0.1",
        }
        mock_request.headers = {}

        ip = adapter._get_client_ip_flask(mock_request)
        assert ip == "192.168.1.1"

    def test_get_client_ip_flask_headers(self):
        """Test getting client IP from Flask headers."""
        adapter = RequestAdapter()

        mock_request = Mock()
        mock_request.environ = {}
        mock_request.headers = {
            "X-Forwarded-For": "192.168.1.1",
            "X-Real-IP": "10.0.0.1",
        }

        ip = adapter._get_client_ip_flask(mock_request)
        assert ip == "192.168.1.1"

    def test_get_client_ip_fastapi_client(self):
        """Test getting client IP from FastAPI client."""
        adapter = RequestAdapter()

        mock_request = Mock()
        mock_request.client = Mock()
        mock_request.client.host = "192.168.1.1"
        mock_request.headers = {}

        ip = adapter._get_client_ip_fastapi(mock_request)
        assert ip == "192.168.1.1"

    def test_get_client_ip_fastapi_headers(self):
        """Test getting client IP from FastAPI headers."""
        adapter = RequestAdapter()

        mock_request = Mock()
        mock_request.client = None
        mock_request.headers = {
            "x-forwarded-for": "192.168.1.1, 10.0.0.1",
            "x-real-ip": "10.0.0.1",
        }

        ip = adapter._get_client_ip_fastapi(mock_request)
        assert ip == "192.168.1.1"

    def test_extract_headers_django(self):
        """Test extracting headers from Django request."""
        adapter = RequestAdapter()

        mock_request = Mock()
        mock_request.META = {
            "HTTP_USER_AGENT": "Mozilla/5.0",
            "HTTP_ACCEPT": "text/html",
            "HTTP_X_FORWARDED_FOR": "192.168.1.1",
            "CONTENT_TYPE": "application/json",  # Not HTTP_ prefixed
            "REMOTE_ADDR": "127.0.0.1",  # Not HTTP_ prefixed
        }

        headers = adapter._extract_headers_django(mock_request)

        assert headers["User-Agent"] == "Mozilla/5.0"
        assert headers["Accept"] == "text/html"
        assert headers["X-Forwarded-For"] == "192.168.1.1"
        assert "Content-Type" not in headers  # Should not include non-HTTP_ headers
        assert "Remote-Addr" not in headers

    def test_adapt_with_empty_headers(self):
        """Test adapting request with empty headers."""
        adapter = RequestAdapter()

        mock_request = Mock()
        mock_request.__class__.__module__ = "flask.wrappers"
        mock_request.headers = {}
        mock_request.environ = {}
        mock_request.method = "GET"
        mock_request.path = "/"
        mock_request.args = Mock()
        mock_request.args.to_dict.return_value = {}

        result = adapter.adapt(mock_request)

        assert result["user_agent"] == ""
        assert result["ip_address"] == ""
        assert result["headers"] == {}
        assert result["framework"] == "flask"

    def test_adapt_starlette_request(self):
        """Test adapting Starlette request."""
        adapter = RequestAdapter()

        mock_request = Mock()
        mock_request.__class__.__module__ = "starlette.requests"
        mock_request.headers = {
            "user-agent": "Mozilla/5.0",
            "accept": "text/html",
        }
        mock_request.client = Mock()
        mock_request.client.host = "192.168.1.1"
        mock_request.method = "GET"
        mock_request.url = Mock()
        mock_request.url.path = "/test"
        mock_request.query_params = {"q": "search"}

        result = adapter.adapt(mock_request)

        assert result["user_agent"] == "Mozilla/5.0"
        assert result["ip_address"] == "192.168.1.1"
        assert result["method"] == "GET"
        assert result["path"] == "/test"
        assert result["query_string"] == {"q": "search"}
        assert result["framework"] == "starlette"
