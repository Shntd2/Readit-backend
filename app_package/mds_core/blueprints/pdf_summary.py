"""
This utility will generate a summary of the uploaded text file
"""

from flask import Blueprint, request, jsonify, session
import PyPDF2
from io import BytesIO
from nltk.tokenize import sent_tokenize
import requests

pdf_summary = Blueprint('pdf_summary', __name__, url_prefix='/pdf_summary')


def clean_text(text):
	"""Simplifies text extraction noise"""
	return ' '.join(text.replace('\t', ' ').replace('\n', ' ').strip().split())


def chunks(sentences, chunk_size=14):
	"""Yields successive 14-sized chunks from a list of sentences"""
	for i in range(0, len(sentences), chunk_size):
		yield ' '.join(sentences[i:i + chunk_size])


@pdf_summary.route('/generate_summary', methods=['POST'])
def generate_summary():
	"""Forms chunks in json"""
	file = request.files.get('file_content')
	if not file:
		return jsonify({'error': 'Missing file content', 'code': 400}), 400

	try:
		file_content = file.read()
		pdf_bytes = BytesIO(file_content)
		pdf_reader = PyPDF2.PdfReader(pdf_bytes)
		summary_sentences = []

		for page in pdf_reader.pages:
			raw_text = page.extract_text()
			if raw_text:
				cleaned_text = clean_text(raw_text)
				summary_sentences.extend(sent_tokenize(cleaned_text))
		if not summary_sentences:
			return jsonify({'error': 'No meaningful text extracted from file', 'code': 400}), 400

		user_email = session.get('email')
		username = session.get('username')
		summary_chunks = list(chunks(summary_sentences))
		for chunk in summary_chunks:
			requests.post('http://localhost:5000/ai_summarizer/process_chunks', json={
				'chunks': [chunk], 'username': username, 'email': user_email
			})

		return jsonify({
			'message': 'Chunks sent for processing',
			'num_pages': len(pdf_reader.pages),
			'status': 'success'
		})
	except Exception as e:
		return jsonify({'error': str(e), 'code': 500}), 500

# This function was used to send raw chunks of uploaded PDF file directly to recipient
# Now is needed to move this function. Destination yet is unidentified
# def send_summary_via_email(summary_chunks, recipient):
# 	"""Creates package with chunk and sends to email_service.py"""
# 	url = 'http://localhost:5000/sending_email'
# 	data = {
# 		'summary': ' '.join(summary_chunks),
# 		'recipient': recipient,
# 		'chunk_number': 1
# 	}
# 	response = requests.post(url, json=data)
# 	return response.status_code, response.text
