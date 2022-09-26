from flask import Blueprint, jsonify, request
from qs_app import db
from qs_app.models import User
auth = Blueprint('auth', __name__)


@auth.route("/register", methods=['POST'])
def register():
    request_data = request.get_json()
    user_name = request_data['name']
    user_email = request_data['email']
    password = request_data['password']

    user = User.query.filter_by(email=user_email).first()
    if user:
        return jsonify(message='Email already in use!'), 400
    
    user = User(name=user_name, email=user_email, password=password)
    db.session.add(user)
    db.session.commit()

    jwt_token = User.encode_auth_token(user.id)

    return jsonify(jwt=jwt_token), 200

@auth.route("/login", methods=['POST'])
def login():
    request_data = request.get_json()
    user_email = request_data['email']
    password = request_data['password']

    user = User.query.filter_by(email=user_email).first()

    if not user:
        return jsonify(message='User not found!'), 400
    
    if not user.check_password(password):
        return jsonify(message='Password incorrect!'), 400

    jwt_token = User.encode_auth_token(user.id)

    return jsonify(jwt=jwt_token), 200