from flask import Blueprint

routes = Blueprint('routes', __name__)


def init_app(app):
	from . import registration
	from . import login_logout

	app.register_blueprint(routes)
