"""
Defines the routes for uploading PDF files and displaying the upload form
"""

import requests
from flask import Blueprint, render_template, request, redirect, flash, jsonify, session
# from app_package.config import DevelopmentConfig

routes_app = Blueprint('routes', __name__, template_folder='templates')


def allowed_file(filename):
	"""Checks if the uploaded file matches the required extension"""
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in DevelopmentConfig.ALLOWED_EXTENSIONS


@routes_app.route('/')
def main_page():
	"""Renders the main page"""
	return render_template('index.html')


@routes_app.route('/upload', methods=['GET', 'POST'])
def upload_file():
	"""Handles PDF file upload. Sends file to pdf_summary.py for further processing"""
	if request.method == 'POST':
		file = request.files['file']
		if not file or file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			file_content = file.read()
			# here function will retrieve 'email' and 'username' value from authorized user -
			# which will be retrieved from registered users database
			user_email = session.get('email')
			username = session.get('username')

			response = requests.post('http://localhost:5000/pdf_summary/generate_summary', json={
				'file_content': file_content,
				'username': username,
				'email': user_email
			})
			return jsonify(response.json()), response.status_code
	return render_template('index.html')
