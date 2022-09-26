from multiprocessing.resource_tracker import main
from flask import Blueprint, jsonify, request
from ..models import Tracker, User
from qs_app import db

from ..utils import token_required


main = Blueprint('main', __name__)


@main.route("/", methods=['GET'])
def home():
    return jsonify(message="Welcome to QS API!"), 200

@main.route("/trackers", methods=['GET'])
@token_required
def get_tracker(user):
    return jsonify(message=""), 200

@main.route("/trackers", methods=['POST'])
@token_required
def create_tracker(current_user):
    request_data = request.get_json()
    tracker_name = request_data['name']
    tracker_desc = request_data['description']
    tracker_type = request_data['tracker_type']
    user = User.query.filter_by(id=current_user['user_id']).first()
    tracker = Tracker(name = tracker_name, description = tracker_desc, tracker_type = tracker_type, user = user)
    db.session.add(tracker)
    db.session.commit()
    print("Hello")
    return jsonify(message="success"), 200