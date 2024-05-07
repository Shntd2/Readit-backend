"""
Initializes Flask application
"""

from flask import Flask
from flask_compress import Compress
from ..mds_core.config import DevelopmentConfig
from models import db


def create_app():
	app = Flask(__name__)
	app.config.from_object(DevelopmentConfig)

	db.init_app(app)

	from .routes import routes_app
	app.register_blueprint(routes_app)

	from .blueprints.config_switcher import config_switcher
	app.register_blueprint(config_switcher)

	from .blueprints.pdf_summary import pdf_summary
	app.register_blueprint(pdf_summary)

	from .blueprints.ai_summarizer import ai_summarizer
	app.register_blueprint(ai_summarizer)

	from .blueprints.email_service import email_service
	app.register_blueprint(email_service)

	Compress(app)
	return app


if __name__ == '__main__':
	app = create_app()
	with app.app_context():
		db.create_all()  # create database tables
	app.run(debug=True)
