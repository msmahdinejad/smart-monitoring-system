"""
Flask Application Factory
Creates and configures the Flask application instance
"""

from flask import Flask
from controllers.web_routes import web_bp
from controllers.api_routes import api_bp

try:
    from config import SECURITY_CONFIG, SERVER_CONFIG
except ImportError:
    print("❌ ERROR: config.py not found!")
    exit(1)


def create_app():
    """
    Flask application factory
    Returns configured Flask application instance
    """
    app = Flask(__name__)
    
    # Configure Flask app
    app.secret_key = SECURITY_CONFIG['secret_key']
    app.config['MAX_CONTENT_LENGTH'] = SERVER_CONFIG['max_content_length']
    
    # Register blueprints
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app