"""
Universal request adapter for different web frameworks.
"""

from typing import Any, Dict


class RequestAdapter:
    """
    Universal request adapter that normalizes requests.

    Supports Django, Flask, FastAPI, and generic WSGI/ASGI requests.
    """

    def adapt(self, request: Any) -> Dict[str, Any]:
        """
        Adapt a request object to a normalized format.

        Args:
            request: HTTP request object from any supported framework

        Returns:
            Dict containing normalized request data
        """
        # Determine framework and adapt accordingly
        framework = self._detect_framework(request)

        if framework == "django":
            return self._adapt_django(request)
        elif framework == "flask":
            return self._adapt_flask(request)
        elif framework == "fastapi":
            return self._adapt_fastapi(request)
        elif framework == "starlette":
            return self._adapt_starlette(request)
        else:
            # Try generic adaptation
            return self._adapt_generic(request)

    def _detect_framework(self, request: Any) -> str:
        """Detect which web framework the request is from."""
        module_name = request.__class__.__module__

        if "django" in module_name.lower():
            return "django"
        elif "flask" in module_name.lower():
            return "flask"
        elif "fastapi" in module_name.lower() or "starlette" in module_name.lower():
            if "fastapi" in module_name.lower():
                return "fastapi"
            else:
                return "starlette"
        else:
            return "generic"

    def _adapt_django(self, request: Any) -> Dict[str, Any]:
        """Adapt Django HttpRequest."""
        return {
            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            "ip_address": self._get_client_ip_django(request),
            "headers": self._extract_headers_django(request),
            "method": request.method,
            "path": request.path,
            "query_string": request.GET.dict(),
            "framework": "django",
        }

    def _adapt_flask(self, request: Any) -> Dict[str, Any]:
        """Adapt Flask Request."""
        return {
            "user_agent": request.headers.get("User-Agent", ""),
            "ip_address": self._get_client_ip_flask(request),
            "headers": dict(request.headers),
            "method": request.method,
            "path": request.path,
            "query_string": request.args.to_dict(),
            "framework": "flask",
        }

    def _adapt_fastapi(self, request: Any) -> Dict[str, Any]:
        """Adapt FastAPI Request."""
        return {
            "user_agent": request.headers.get("user-agent", ""),
            "ip_address": self._get_client_ip_fastapi(request),
            "headers": dict(request.headers),
            "method": request.method,
            "path": request.url.path,
            "query_string": dict(request.query_params),
            "framework": "fastapi",
        }

    def _adapt_starlette(self, request: Any) -> Dict[str, Any]:
        """Adapt Starlette Request."""
        return {
            "user_agent": request.headers.get("user-agent", ""),
            "ip_address": self._get_client_ip_starlette(request),
            "headers": dict(request.headers),
            "method": request.method,
            "path": request.url.path,
            "query_string": dict(request.query_params),
            "framework": "starlette",
        }

    def _adapt_generic(self, request: Any) -> Dict[str, Any]:
        """Generic adaptation for unknown request types."""
        adapted = {
            "user_agent": "",
            "ip_address": "",
            "headers": {},
            "method": "GET",
            "path": "/",
            "query_string": {},
            "framework": "generic",
        }

        # Try to extract common attributes
        if hasattr(request, "headers"):
            if hasattr(request.headers, "get"):
                adapted["user_agent"] = request.headers.get(
                    "User-Agent", ""
                ) or request.headers.get("user-agent", "")
                adapted["headers"] = dict(request.headers)
            elif isinstance(request.headers, dict):
                adapted["user_agent"] = request.headers.get(
                    "User-Agent", ""
                ) or request.headers.get("user-agent", "")
                adapted["headers"] = request.headers

        if hasattr(request, "method"):
            adapted["method"] = request.method

        if hasattr(request, "path"):
            adapted["path"] = request.path
        elif hasattr(request, "url") and hasattr(request.url, "path"):
            adapted["path"] = request.url.path

        return adapted

    def _get_client_ip_django(self, request: Any) -> str:
        """Get client IP from Django request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = str(x_forwarded_for).split(",")[0].strip()
        else:
            ip = str(request.META.get("REMOTE_ADDR", ""))
        return ip

    def _get_client_ip_flask(self, request: Any) -> str:
        """Get client IP from Flask request."""
        if hasattr(request, "environ") and request.environ:
            x_forwarded_for = request.environ.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                ip = str(x_forwarded_for).split(",")[0].strip()
            else:
                ip = str(request.environ.get("REMOTE_ADDR", ""))
        else:
            # Fallback to headers
            x_forwarded_for = request.headers.get("X-Forwarded-For")
            if x_forwarded_for:
                ip = str(x_forwarded_for).split(",")[0].strip()
            else:
                ip = str(request.headers.get("X-Real-IP", ""))
        return ip

    def _get_client_ip_fastapi(self, request: Any) -> str:
        """Get client IP from FastAPI request."""
        if hasattr(request, "client") and hasattr(request.client, "host"):
            return str(request.client.host)

        # Fallback to headers
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            return str(x_forwarded_for).split(",")[0].strip()

        return str(request.headers.get("x-real-ip", ""))

    def _get_client_ip_starlette(self, request: Any) -> str:
        """Get client IP from Starlette request."""
        if hasattr(request, "client") and hasattr(request.client, "host"):
            return str(request.client.host)

        # Fallback to headers
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            return str(x_forwarded_for).split(",")[0].strip()

        return str(request.headers.get("x-real-ip", ""))

    def _extract_headers_django(self, request: Any) -> Dict[str, str]:
        """Extract HTTP headers from Django request."""
        headers = {}
        for key, value in request.META.items():
            if key.startswith("HTTP_"):
                # Convert HTTP_USER_AGENT to User-Agent
                header_name = key[5:].replace("_", "-").title()
                headers[header_name] = value
        return headers
