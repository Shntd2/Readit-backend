import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

APPLICATION_URL = os.getenv('APPLICATION_URL')


def test_user_registration():
	url = f"{APPLICATION_URL}/register"

	user_data = {
		"username": "test",
		"email": "test@example.com",
		"password": "12345678",
		"confirm_password": "12345678"
	}

	headers = {
		'Content-Type': 'application/json'
	}

	response = requests.post(url, data=json.dumps(user_data), headers=headers)

	if response.status_code == 201:
		print("User created successfully")
		print("Response:", response.json())
	else:
		print("Failed to create user")
		print("Status Code:", response.status_code)
		print("Response:", response.text)


if __name__ == "__main__":
	test_user_registration()
