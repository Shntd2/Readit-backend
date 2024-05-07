class Config(object):
	DEBUG = False
	TESTING = False
	SECRET_KEY = ''
	ALLOWED_EXTENSIONS = {'pdf', 'docx', 'epub'}
	MAX_CONTENT_LENGTH = 25 * 1000 * 1000


class DevelopmentConfig(Config):  # intermediate state
	DEBUG = True
	TESTING = False
	SECRET_KEY = ''
	ALLOWED_EXTENSIONS = {'pdf', 'docx', 'epub'}
	MAX_CONTENT_LENGTH = 25 * 1000 * 1000
	APPLICATION_URL = 'http://localhost:5000'
	UPLOAD_FOLDER = 'C:/Python/Projects'
	SENDER_EMAIL = '...'
	EMAIL_APP_PASSWORD = '...'
	SQLALCHEMY_DATABASE_URI = ...
	SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):  # final state
	DEBUG = False
	TESTING = False
	SECRET_KEY = ''
	ALLOWED_EXTENSIONS = {'pdf', 'docx', 'epub'}
	MAX_CONTENT_LENGTH = 25 * 1000 * 1000
	APPLICATION_URL = ...
	UPLOAD_FOLDER = ...
	SENDER_EMAIL = ...
	EMAIL_APP_PASSWORD = ...
	SQLALCHEMY_DATABASE_URI = ...
	SQLALCHEMY_TRACK_MODIFICATIONS = False
