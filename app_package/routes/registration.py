from flask import jsonify, request
from app_package import db
from app_package.models.models import User, user_schema
from app_package.forms.registration import RegistrationForm
from werkzeug.security import generate_password_hash
from . import routes


@routes.route('/register', methods=['POST'])
def register():
    json_data = request.get_json()
    if not json_data:
        return jsonify({'error': 'No input data provided'}), 400

    form = RegistrationForm(meta={'csrf': False})

    form.username.data = json_data.get('username')
    form.email.data = json_data.get('email')
    form.password.data = json_data.get('password')
    form.confirm_password.data = json_data.get('confirm_password')

    if form.validate():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already exists"}), 400

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        return user_schema.jsonify(new_user), 201
    else:
        return jsonify({"error": form.errors}), 400


@routes.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify(user_schema.dump(users, many=True)), 200
