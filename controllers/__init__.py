"""
Controllers Package
Web routes and API endpoint handlers
"""

from .web_routes import web_bp
from .api_routes import api_bp

__all__ = ['web_bp', 'api_bp']