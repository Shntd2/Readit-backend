from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt,
    set_access_cookies, set_refresh_cookies,
    unset_jwt_cookies
)
from app_package.models.models import User
from app_package.forms.login_logout import LoginForm
from werkzeug.security import check_password_hash
from app_package import redis_client, jwt
from datetime import timedelta
from . import routes


REVOKED_TOKEN_PREFIX = "revoked_token:"


@routes.route('/login', methods=['POST'])
def login():
    json_data = request.get_json()
    print(f"Received login data: {json_data}")
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400

    form = LoginForm(meta={'csrf': False})

    form.username.data = json_data.get('username')
    form.password.data = json_data.get('password')

    if form.validate():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            access_token = create_access_token(identity=username)
            refresh_token = create_refresh_token(identity=username)

            response = jsonify({
                "message": "Login successful",
                "access_token": access_token,
                "refresh_token": refresh_token
            })

            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)

            print(f"Login successful for user: {username}")
            return response, 200
        else:
            print(f"Login failed for user: {username}")
            return jsonify({"error": "Invalid username or password"}), 401
    else:
        return jsonify({"error": form.errors}), 400


@routes.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)

    response = jsonify({"access_token": new_access_token})
    set_access_cookies(response, new_access_token)

    return response, 200


@routes.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    redis_key = f"{REVOKED_TOKEN_PREFIX}{jti}"
    redis_client.setex(redis_key, timedelta(hours=1), "revoked")

    response = jsonify({"message": "Successfully logged out"})
    unset_jwt_cookies(response)
    return response, 200


@routes.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


# checks if JWT exists in the Redis blocklist
@jwt.token_in_blocklist_loader
def check_if_token_revoked(_, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    redis_key = f"{REVOKED_TOKEN_PREFIX}{jti}"
    token_in_redis = redis_client.get(redis_key)
    return token_in_redis is not None


# lists JWT in Redis blocklist
@routes.route('/revoked_tokens', methods=['GET'])
def list_revoked_tokens():
    pattern = f"{REVOKED_TOKEN_PREFIX}*"
    revoked_tokens = redis_client.keys(pattern)
    return jsonify({"revoked_tokens": revoked_tokens}), 200
