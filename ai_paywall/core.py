"""
Core AI Paywall functionality.
"""

import ipaddress
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .adapters.request import RequestAdapter
from .patterns import BOT_PATTERNS


@dataclass
class DetectionResult:
    """Result of bot detection analysis."""

    is_bot: bool
    bot_type: Optional[str] = None
    confidence: float = 0.0
    detection_method: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        if self.metadata is None:
            self.metadata = {}


class AIPaywall:
    """
    Universal AI Paywall for detecting and managing AI crawler access.

    This class provides bot detection capabilities that work across different
    web frameworks while maintaining a consistent interface.
    """

    def __init__(
        self,
        mode: str = "detect",
        patterns: Optional[Dict[str, Any]] = None,
        confidence_threshold: float = 0.7,
        storage_backend: Optional[Any] = None,
        custom_patterns: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Initialize AIPaywall instance.

        Args:
            mode: Operation mode ("detect", "block", "charge")
            patterns: Custom bot patterns (uses defaults if None)
            confidence_threshold: Minimum confidence to classify as bot
            storage_backend: Storage backend for logging/analytics
            custom_patterns: Additional patterns to include
        """
        self.mode = mode
        self.confidence_threshold = confidence_threshold
        self.storage_backend = storage_backend

        # Initialize patterns
        self.patterns = patterns or BOT_PATTERNS.copy()
        if custom_patterns:
            self._add_custom_patterns(custom_patterns)

        # Initialize request adapter
        self.request_adapter = RequestAdapter()

    def check(self, request: Any) -> DetectionResult:
        """
        Check if a request is from a bot.

        Args:
            request: HTTP request object (Django, Flask, FastAPI, etc.)

        Returns:
            DetectionResult with bot detection information
        """
        # Adapt request to unified format
        adapted_request = self.request_adapter.adapt(request)

        # Perform detection
        result = self._detect_bot(adapted_request)

        # Log if storage backend is configured
        if self.storage_backend:
            self.storage_backend.log_detection(result)

        return result

    def _detect_bot(self, request_data: Dict[str, Any]) -> DetectionResult:
        """
        Internal bot detection logic.

        Args:
            request_data: Adapted request data

        Returns:
            DetectionResult
        """
        user_agent = request_data.get("user_agent", "")
        ip_address = request_data.get("ip_address", "")
        headers = request_data.get("headers", {})

        # Check user agent patterns
        ua_result = self._check_user_agent(user_agent)
        if ua_result.is_bot and ua_result.confidence >= self.confidence_threshold:
            return DetectionResult(
                is_bot=True,
                bot_type=ua_result.bot_type,
                confidence=ua_result.confidence,
                detection_method="user_agent",
                user_agent=user_agent,
                ip_address=ip_address,
                metadata=ua_result.metadata,
            )

        # Check IP ranges
        ip_result = self._check_ip_ranges(ip_address)
        if ip_result.is_bot and ip_result.confidence >= self.confidence_threshold:
            return DetectionResult(
                is_bot=True,
                bot_type=ip_result.bot_type,
                confidence=ip_result.confidence,
                detection_method="ip_range",
                user_agent=user_agent,
                ip_address=ip_address,
                metadata=ip_result.metadata,
            )

        # Check headers
        header_result = self._check_headers(headers)
        if (
            header_result.is_bot
            and header_result.confidence >= self.confidence_threshold
        ):
            return DetectionResult(
                is_bot=True,
                bot_type=header_result.bot_type,
                confidence=header_result.confidence,
                detection_method="headers",
                user_agent=user_agent,
                ip_address=ip_address,
                metadata=header_result.metadata,
            )

        # Default to human
        return DetectionResult(
            is_bot=False,
            user_agent=user_agent,
            ip_address=ip_address,
            metadata={"detection_methods_tried": ["user_agent", "ip_range", "headers"]},
        )

    def _check_user_agent(self, user_agent: str) -> DetectionResult:
        """Check user agent against known bot patterns."""
        if not user_agent:
            return DetectionResult(is_bot=False)

        # Normalize user agent for comparison
        user_agent_lower = user_agent.lower()

        for bot_name, pattern_data in self.patterns.items():
            user_agents = pattern_data.get("user_agents", [])

            for pattern in user_agents:
                if isinstance(pattern, str):
                    # Exact match or substring match
                    if pattern.lower() in user_agent_lower:
                        return DetectionResult(
                            is_bot=True,
                            bot_type=bot_name,
                            confidence=pattern_data.get("confidence", 0.9),
                            metadata={
                                "matched_pattern": pattern,
                                "full_user_agent": user_agent,
                                "description": pattern_data.get("description", ""),
                            },
                        )
                elif isinstance(pattern, dict) and pattern.get("regex"):
                    # Regex pattern
                    if re.search(pattern["regex"], user_agent, re.IGNORECASE):
                        return DetectionResult(
                            is_bot=True,
                            bot_type=bot_name,
                            confidence=pattern_data.get("confidence", 0.9),
                            metadata={
                                "matched_pattern": pattern["regex"],
                                "full_user_agent": user_agent,
                                "description": pattern_data.get("description", ""),
                            },
                        )

        return DetectionResult(is_bot=False)

    def _check_ip_ranges(self, ip_address: str) -> DetectionResult:
        """Check IP address against known bot IP ranges."""
        if not ip_address:
            return DetectionResult(is_bot=False)

        try:
            ip = ipaddress.ip_address(ip_address)

            for bot_name, pattern_data in self.patterns.items():
                ip_ranges = pattern_data.get("ip_ranges", [])

                for ip_range in ip_ranges:
                    try:
                        network = ipaddress.ip_network(ip_range, strict=False)
                        if ip in network:
                            return DetectionResult(
                                is_bot=True,
                                bot_type=bot_name,
                                confidence=pattern_data.get("confidence", 0.8),
                                metadata={
                                    "matched_ip_range": ip_range,
                                    "ip_address": ip_address,
                                    "description": pattern_data.get("description", ""),
                                },
                            )
                    except ValueError:
                        # Invalid IP range in patterns
                        continue

        except ValueError:
            # Invalid IP address
            return DetectionResult(is_bot=False)

        return DetectionResult(is_bot=False)

    def _check_headers(self, headers: Dict[str, str]) -> DetectionResult:
        """Check HTTP headers for bot indicators."""
        if not headers:
            return DetectionResult(is_bot=False)

        # Normalize headers to lowercase
        headers_lower = {k.lower(): v for k, v in headers.items()}

        for bot_name, pattern_data in self.patterns.items():
            header_patterns = pattern_data.get("headers", {})

            for header_name, expected_values in header_patterns.items():
                header_value = headers_lower.get(header_name.lower(), "")

                if isinstance(expected_values, list):
                    for expected_value in expected_values:
                        if expected_value.lower() in header_value.lower():
                            return DetectionResult(
                                is_bot=True,
                                bot_type=bot_name,
                                confidence=pattern_data.get("confidence", 0.7),
                                metadata={
                                    "matched_header": header_name,
                                    "matched_value": expected_value,
                                    "actual_value": header_value,
                                    "description": pattern_data.get("description", ""),
                                },
                            )
                elif isinstance(expected_values, str):
                    if expected_values.lower() in header_value.lower():
                        return DetectionResult(
                            is_bot=True,
                            bot_type=bot_name,
                            confidence=pattern_data.get("confidence", 0.7),
                            metadata={
                                "matched_header": header_name,
                                "matched_value": expected_values,
                                "actual_value": header_value,
                                "description": pattern_data.get("description", ""),
                            },
                        )

        return DetectionResult(is_bot=False)

    def _add_custom_patterns(self, custom_patterns: List[Dict[str, Any]]) -> None:
        """Add custom bot patterns to the existing patterns."""
        for pattern in custom_patterns:
            if "name" in pattern:
                self.patterns[pattern["name"]] = pattern
