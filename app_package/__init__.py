"""
Initializes Flask application
"""


import logging
from logging.handlers import RotatingFileHandler
from flask_cors import CORS
from flask import Flask
from flask_compress import Compress

# Import blueprints
# from .blueprints.ai_summarizer import ai_summarizer
# from .blueprints.config_switcher import config_switcher
# from .blueprints.email_service import email_service
# from .blueprints.pdf_summary import pdf_summary
from mds_core.routes import routes_app

# Import the development configuration
from config import DevelopmentConfig


# Function to create the Flask app
def create_app():
    app = Flask(__name__)

    # Configure the app
    app.config.from_object(DevelopmentConfig)

    # Configure logging
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
    log_handler.setFormatter(log_formatter)
    app.logger.addHandler(log_handler)

    # Log the app's configuration to help with debugging
    app.logger.info('App configuration loaded')

    CORS(app)

    # Register blueprints
    app.register_blueprint(routes_app, url_prefix='routes')
    # app.register_blueprint(config_switcher)
    # app.register_blueprint(pdf_summary)
    # app.register_blueprint(ai_summarizer)
    # app.register_blueprint(email_service)

    Compress(app)
    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        app.run(debug=True)
