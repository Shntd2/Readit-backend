"""
This utility provides a route to display specific configuration settings of the application
"""

from flask import Blueprint, current_app

config_switcher = Blueprint('config_switcher', __name__, url_prefix='/config')


@config_switcher.route('/')
def config_route():
	secret_key = current_app.config['SECRET_KEY']
	allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
	max_content_length = current_app.config['MAX_CONTENT_LENGTH']

	return f'Secret Key: {secret_key}, Max Content Length: {max_content_length}, Allowed Extensions: {allowed_extensions}'
