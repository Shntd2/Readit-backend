"""
Defines the routes for uploading PDF files and displaying the upload form
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from .config import DevelopmentConfig
from werkzeug.utils import secure_filename
import os

routes_app = Blueprint('routes', __name__)


def allowed_file(filename):
	"""Checks if the uploaded file matches the required extension"""
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in DevelopmentConfig.ALLOWED_EXTENSIONS


@routes_app.route('/')
@routes_app.route('/upload', methods=['GET', 'POST'])
def upload_file():
	"""Handles PDF file upload. Sends file to pdf_summary.py for further processing"""
	if request.method == 'POST':
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			file_path = os.path.join(DevelopmentConfig.UPLOAD_FOLDER, secure_filename(file.filename))
			file.save(file_path)
			return redirect(url_for('pdf_summary.generate_summary', file_path=file_path))
	return render_template('upload.html')
