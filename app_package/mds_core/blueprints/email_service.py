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

logging.basicConfig(level=logging.INFO)
email_service = Blueprint('email_service', __name__)


@email_service.route('/sending_email', methods=['POST'])
def send_email():
	"""Sends summaries to recipients email"""
	summary_chunk = request.json.get('summary', '')
	recipient = request.json.get('recipient', '')
	if not summary_chunk or not recipient:
		return jsonify({'error': 'Missing summary or recipient', 'code': 400}), 400

	msg = MIMEMultipart()
	sender_email = DevelopmentConfig.SENDER_EMAIL
	app_password = DevelopmentConfig.EMAIL_APP_PASSWORD
	msg['From'] = sender_email
	msg['To'] = recipient
	chunk_number = request.json.get('chunk_number', 'unknown')
	msg['Subject'] = f'Summary Part {chunk_number}: Uploaded Text File'
	body = f"This email contains part {chunk_number} of the summary for your uploaded text file:\n\n{summary_chunk}"
	msg.attach(MIMEText(body, 'plain'))

	context = ssl.create_default_context()
	try:
		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls(context=context)
		server.login(sender_email, app_password)
		server.sendmail(sender_email, recipient, msg.as_string())
		server.quit()
		logging.info('Email sent successfully')
	except smtplib.SMTPException as e:
		logging.error(f'Error sending email: {e}')
		return jsonify({'error': str(e), 'code': 500}), 500
	except Exception as e:
		logging.error(f'Unexpected error: {e}')
		return jsonify({'error': str(e), 'code': 500}), 500
	return jsonify({'message': 'Email sent', 'code': 200}), 200
