"""
This utility will send JSON chunks of uploaded PDF from MongoDB to AI API
Is under development
"""

from flask import Blueprint, request, jsonify, session
import requests
from app_package.mds_core.models import db, AIResponse

ai_summarizer = Blueprint('ai_summarizer', __name__, url_prefix='/ai_summarizer')


@ai_summarizer.route('/process_chunks', methods=['POST'])
def process_chunks():
	chunks = request.json.get('chunks', [])
	user_email = session.get('email')
	username = session.get('username')
	# place here URL for an external AI API service
	url = 'https://ai/api'
	headers = {'Content-Type': 'application/json'}

	for chunk in chunks:
		payload = {'text': chunk}
		response = requests.post(url, json=payload, headers=headers)
		if response.status_code == 200:
			ai_response = AIResponse(chunk_text=chunk, user_email=user_email, username=username)
			db.session.add(ai_response)
		else:
			# add logging and saving error handling
			pass
	db.session.commit()
	return jsonify({'message': 'Processing complete', 'email': user_email, 'username': username})
