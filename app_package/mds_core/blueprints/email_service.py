"""
This utility handles sending emails

Flow:
1. Fetch all AI responses from the database
2. Establish an SMTP connection using the sender's email and app password
3. Loop through each AI response, format the email content, and send the email
4. Log success or error messages for each email sent
5. Handle any unexpected errors during the process
"""

import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Blueprint, jsonify

from app_package.config import DevelopmentConfig
from ..models import AIResponse

logging.basicConfig(level=logging.INFO)
email_service = Blueprint('email_service', __name__)


@email_service.route('/sending_email', methods=['POST'])
def send_email():
	"""
	Fetches stored AI responses from the database and sends them as emails
	"""
	responses = AIResponse.query.all()
	context = ssl.create_default_context()
	sender_email = DevelopmentConfig.SENDER_EMAIL
	app_password = DevelopmentConfig.EMAIL_APP_PASSWORD

	try:
		with smtplib.SMTP('smtp.gmail.com', 587) as server:
			server.starttls(context=context)
			server.login(sender_email, app_password)

			for response in responses:
				msg = MIMEMultipart()
				msg['From'] = sender_email
				msg['To'] = response.user_email
				msg['Subject'] = 'Your Text Summary'
				body = f"Hello {response.username},\n\nHere is uploaded text's summary:\n\n{response.ai_response}"
				msg.attach(MIMEText(body, 'plain'))

				try:
					server.sendmail(sender_email, response.user_email, msg.as_string())
					logging.info(f'Email sent successfully to {response.user_email}')
				except smtplib.SMTPException as e:
					logging.error(f'Error sending email to {response.user_email}: {e}')
					# Optionally handle the error (e.g., continue or exit the loop)

	except Exception as e:
		logging.error(f'Unexpected error when sending emails: {e}')
		return jsonify({'message': 'Error sending emails', 'code': 500}), 500

	return jsonify({'message': 'Emails sent successfully', 'code': 200}), 200
