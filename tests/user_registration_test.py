import requests
import json
from dotenv import load_dotenv
import os
import hashlib

load_dotenv()

APPLICATION_URL = os.getenv('APPLICATION_URL')


def hash_password(password):
    hash_object = hashlib.sha256(password.encode('utf-8'))
    hex_dig = hash_object.hexdigest()
    return hex_dig


def test_user_registration():
    url = f"{APPLICATION_URL}/register"

    plain_password = "123456789"
    hashed_password = hash_password(plain_password)

    user_data = {
        "username": "test6",
        "email": "shant@test4.com",
        "password": hashed_password,
        "confirm_password": hashed_password
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
