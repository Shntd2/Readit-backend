from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Class Users(db.Model):

Class AIResponse(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	ai_response = db.Column(db.JSON, nullable=False)
	username = db.Column(db.Text, nullable=False)
	user_email = db.Column(db.Text, nullable=False)

	def __init__(self, ai_response, username, user_email):
		self.ai_response = ai_response
		self.username = username
		self.user_email = user_email