"""
AI Paywall - A universal Python module for charging AI crawlers.

Keeps content free for humans while monetizing AI crawler access.
"""

from .adapters.request import RequestAdapter
from .core import AIPaywall, DetectionResult

__version__ = "0.1.0"
__all__ = ["AIPaywall", "DetectionResult", "RequestAdapter"]
