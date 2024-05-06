"""
This utility will generate a summary of the uploaded text file
"""

import os.path
from flask import Blueprint, request, jsonify
from nltk.tokenize import sent_tokenize
import PyPDF2
from io import BytesIO
import requests

pdf_summary = Blueprint('pdf_summary', __name__, url_prefix='/summarizer')


def clean_text(text):
	"""Simplifies text extraction noise"""
	return ' '.join(text.replace('\t', ' ').replace('\n', ' ').strip().split())


def chunks(sentences, chunks_lines):
	"""Yields successive 14-sized chunks from a list of sentences"""
	for i in range(0, len(sentences), chunks_lines):
		yield ' '.join(sentences[i:i + chunks_lines])


@pdf_summary.route('/generate_summary', methods=['GET'])
def generate_summary():
	"""Forms chunks in json"""
	file_path = request.args.get('file_path')
	if not file_path or not os.path.isfile(file_path):
		return jsonify({'error': 'Invalid or missing file path', 'code': 400}), 400

	try:
		with open(file_path, 'rb') as f:
			pdf_bytes = BytesIO(f.read())
		pdf_reader = PyPDF2.PdfReader(pdf_bytes)
		summary_sentences = []
		for page in pdf_reader.pages:
			raw_text = page.extract_text()
			if raw_text:
				cleaned_text = clean_text(raw_text)
				summary_sentences.extend(sent_tokenize(cleaned_text))
		if not summary_sentences:
			return jsonify({'error': 'No meaningful text extracted', 'code': 400}), 400

		summary_chunks = list(chunks(summary_sentences, 14))
		status_code, response_message = send_summary_via_email(summary_chunks, 'recipients@mail.com')
		return jsonify({
			'summary_chunks': summary_chunks,
			'num_pages': len(pdf_reader.pages),
			'status': 'success',
			'code': status_code,
			'email_service_response': response_message
		})
	except Exception as e:
		return jsonify({'error': str(e), 'code': 500}), 500
	finally:
		os.remove(file_path)


def send_summary_via_email(summary_chunks, recipient):
	"""Creates package with chunk and sends to email_service.py"""
	url = 'http://localhost:5000/sending_email'
	data = {
		'summary': ' '.join(summary_chunks),
		'recipient': recipient,
		'chunk_number': 1
	}
	response = requests.post(url, json=data)
	return response.status_code, response.text
