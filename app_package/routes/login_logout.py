from flask import jsonify, request, make_response
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt,
    set_access_cookies, set_refresh_cookies,
    unset_jwt_cookies
)
from app_package.models.models import User, db
from app_package.forms.login_logout import LoginForm, ChangePasswordForm
from werkzeug.security import check_password_hash, generate_password_hash
from app_package import redis_client, jwt
from datetime import timedelta
from . import routes


REVOKED_TOKEN_PREFIX = "revoked_token:"


@routes.route('/user/login', methods=['POST'])
def login():
    json_data = request.get_json()
    print(f"Received login data: {json_data}")
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400

    form = LoginForm(meta={'csrf': False})
    form.email.data = json_data.get('email')
    form.client_hashed_password.data = json_data.get('password')

    if form.validate():
        email = form.email.data
        client_hashed_password = form.client_hashed_password.data
        user = User.query.filter_by(email=email).first()

        print(f"User found: {user is not None}")
        if user:
            print(f"Stored password hash: {user.password}")
            print(f"Received password hash: {client_hashed_password}")
            print(f"Password check result: {user.check_password(client_hashed_password)}")

        if user and user.check_password(client_hashed_password):
            access_token = create_access_token(identity=email)
            refresh_token = create_refresh_token(identity=email)

            response = make_response(jsonify({
                "message": "Login successful",
                "accessToken": access_token,
                "refreshToken": refresh_token,
                "userId": user.id,
                "username": user.username
            }))

            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)

            print(f"Login successful for user: {email}")
            return response
        else:
            print(f"Login failed for user: {email}")
            if user:
                print("User exists but password check failed")
            else:
                print("User does not exist")
            return jsonify({"error": "Invalid email or password"}), 401
    else:
        print(f"Form validation failed: {form.errors}")
        return jsonify({"error": form.errors}), 400


@routes.route('/user/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    if user:
        return jsonify({"email": user.email, "username": user.username}), 200
    else:
        return jsonify({"error": "User not found"}), 404


@routes.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_email = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_email)

    response = make_response(jsonify({"access_token": new_access_token}))
    set_access_cookies(response, new_access_token)

    return response


@routes.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    redis_key = f"{REVOKED_TOKEN_PREFIX}{jti}"
    redis_client.setex(redis_key, timedelta(hours=1), "revoked")

    response = make_response(jsonify({"message": "Successfully logged out"}))
    unset_jwt_cookies(response)
    return response


@routes.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_email = get_jwt_identity()
    return jsonify(logged_in_as=current_user_email), 200


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


@routes.route('/change_password', methods=['POST'])
@jwt_required()
def change_password():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    form = ChangePasswordForm(meta={'csrf': False})
    form.current_client_hashed_password.data = request.json.get('current_password')
    form.new_client_hashed_password.data = request.json.get('new_password')
    form.confirm_client_hashed_password.data = request.json.get('confirm_password')

    if form.validate():
        if not user.check_password(form.current_client_hashed_password.data):
            return jsonify({"error": "Current password is incorrect"}), 400

        user.password = form.new_client_hashed_password.data
        db.session.commit()

        jti = get_jwt()["jti"]
        redis_key = f"{REVOKED_TOKEN_PREFIX}{jti}"
        redis_client.setex(redis_key, timedelta(hours=1), "revoked")

        access_token = create_access_token(identity=current_user_email)
        refresh_token = create_refresh_token(identity=current_user_email)

        response = make_response(jsonify({
            "message": "Password changed successfully",
            "accessToken": access_token,
            "refreshToken": refresh_token
        }))
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)

        return response
    else:
        return jsonify({"error": form.errors}), 400
