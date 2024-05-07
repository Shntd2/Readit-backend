"""
This utility handles sending emails
"""

from flask import Blueprint, request, jsonify
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl
import logging
from ..config import DevelopmentConfig
from ..models import db, AIResponse

logging.basicConfig(level=logging.INFO)
email_service = Blueprint('email_service', __name__)


@email_service.route('/sending_email', methods=['POST'])
def send_email():
	"""Fetches stored AI responses from the database and sends them as emails"""
	responses = AIResponse.query.all()
	context = ssl.create_default_context()
	sender_email = DevelopmentConfig.SENDER_EMAIL
	app_password = DevelopmentConfig.EMAIL_APP_PASSWORD

	for response in responses:
		msg = MIMEMultipart()
		msg['From'] = sender_email
		msg['To'] = response.user_email
		msg['Subject'] = 'Your Text Summary'
		body = f"Hello {response.username},\n\nHere is uploaded text's summary:\n\n{response.ai_response}"
		msg.attach(MIMEText(body, 'plain'))

		try:
			with smtplib.SMTP('smtp.gmail.com', 587) as server:
				server.starttls(context=context)
				server.login(sender_email, app_password)
				server.sendmail(sender_email, response.user_email, msg.as_string())
				logging.info(f'Email sent successfully to {response.user_email}')
		except smtplib.SMTPException as e:
			logging.error(f'Error sending email to {response.user_email}: {e}')
		except Exception as e:
			logging.error(f'Unexpected error when sending email to {response.user_email}: {e}')
	return jsonify({'message': 'Email sent', 'code': 200}), 200
