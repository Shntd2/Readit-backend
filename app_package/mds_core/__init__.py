"""
Initializes Flask application
"""

from flask import Flask
from flask_compress import Compress
from ..mds_core.config import DevelopmentConfig


def create_app():
	app = Flask(__name__)
	app.config.from_object(DevelopmentConfig)

	from .routes import routes_app
	app.register_blueprint(routes_app)

	from .blueprints.config_switcher import config_switcher
	app.register_blueprint(config_switcher)

	from .blueprints.pdf_summary import pdf_summary
	app.register_blueprint(pdf_summary)

	from .blueprints.email_service import email_service
	app.register_blueprint(email_service)

	Compress(app)
	return app
