from multiprocessing.resource_tracker import main
from flask import Blueprint, jsonify, request
from ..models import Tracker, User, Card
from qs_app import app, db, redis_client
from flask_swagger import swagger
from ..utils import token_required
def serialize_tracker(l):
    dic={}
    for i in range(len(l)):
        dic2 = {}
        dic2["id"]= l[i].id
        dic2["name"]= l[i].name
        dic2["description"]= l[i].description
        dic2["tracker_type"]= l[i].tracker_type
        dic[i]=dic2
    return dic

def serialize_a_tracker(l):
    dic={}
    dic["id"]= l.id
    dic["name"]= l.name
    dic["description"]= l.description
    dic["tracker_type"]= l.tracker_type
    dic["user_id"]=l.user_id
    return dic

def serialize_cards(l):
    dic={}
    for i in range(len(l)):
        dic2 = {}
        dic2["id"]= l[i].id
        dic2["value"]= l[i].value
        dic2["note"]= l[i].note
        dic2["tracker_id"]= l[i].tracker_id
        dic2["time_stamp"]= l[i].time_stamp
        dic[i]=dic2
    return dic

main = Blueprint('main', __name__)


@main.route("/", methods=['GET'])
def home():
    """
    Home Route
    ---
    tags:
        - main
    responses:
        200:
            description: API is Running!
    """
    return jsonify(message="Welcome to QS API!"), 200

@main.route("/user-count", methods=['GET'])
def get_user_count():
    user_count = redis_client.get('user_count')
    if redis_client.get('user_count'):
        return jsonify(message=f"We have {int(user_count)} users and counting - from Redis")
    else:
        user_count = User.query.count()
        redis_client.set('user_count', user_count)
        return jsonify(message=f"We have {int(user_count)} users and counting - from database")

@main.route("/swagger")
def get_swagger_docs():
    """
    Swagger Docs
    ---
    tags:
        - main
    responses:
        200:
            description: Swagger API Documentation.
    """
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "QS API"
    return jsonify(swag)

@main.route("/trackers", methods=['GET'])
@token_required
def get_tracker(user):
    """
    Get Trackers List
    ---
    tags:
        - main
    responses:
        200:
            description: All Trackers Fetched
    """
    user_id = user["user_id"]
    tracker = Tracker.query.filter_by(user_id=user['user_id']).all()
    dic_tracker = serialize_tracker(tracker)
    return jsonify(dic_tracker), 200

@main.route("/trackers/<tracker_id>", methods=['GET'])
@token_required
def get_a_tracker(user, tracker_id):
    """
    Get Tracker by ID
    ---
    tags:
        - main
    responses:
        200:
            description:  Tracker Fetched
    """
    tracker = Tracker.query.filter_by(id=tracker_id).first()
    if user["user_id"]!=tracker.user_id:
        return "Unauthorized", 401
    ser_tracker = serialize_a_tracker(tracker)
    return jsonify(ser_tracker), 200

@main.route("/trackers/<tracker_id>", methods=['PUT'])
@token_required
def update_tracker(user, tracker_id):
    """
    Update Tracker by ID
    ---
    tags:
        - main
    responses:
        200:
            description: Tracker Updated
    """
    request_data = request.get_json()
    tracker = Tracker.query.filter_by(id=tracker_id).first()
    if user["user_id"]!=tracker.user_id:
        return "Unauthorized", 401
    tracker.name = request_data['name']
    tracker.description = request_data['description']
    ser_tracker = serialize_a_tracker(tracker)
    db.session.commit()
    return jsonify(ser_tracker), 200


@main.route("/trackers", methods=['POST'])
@token_required
def create_tracker(current_user):
    """
    Create a New Tracker
    ---
    tags:
        - main
    responses:
        200:
            description: New Tracker Created
    """
    request_data = request.get_json()
    tracker_name = request_data['name']
    tracker_desc = request_data['description']
    tracker_type = request_data['tracker_type']
    user = User.query.filter_by(id=current_user['user_id']).first()
    tracker = Tracker(name = tracker_name, description = tracker_desc, tracker_type = tracker_type, user = user)
    db.session.add(tracker)
    db.session.commit()
    return jsonify(message="success"), 200

@main.route("/trackers", methods=['DELETE'])
@token_required
def del_tracker(user):
    """
    Delete a Tracker by ID
    ---
    tags:
        - main
    responses:
        200:
            description: Tracker Deleted
    """
    request_data = request.get_json()
    tracker_id = request_data['id']
    tracker = Tracker.query.filter_by(id=tracker_id).first()
    db.session.delete(tracker)
    db.session.commit()
    return jsonify(message="success"), 200

@main.route("/tracker/<tracker_id>", methods=['POST'])
@token_required
def create_card(user, tracker_id):
    """
    Create a Card Using Tracker ID
    ---
    tags:
        - main
    responses:
        200:
            description: Card Created
    """
    tracker = Tracker.query.filter_by(id=tracker_id).first()
    if user["user_id"]!=tracker.user_id:
        return "Unauthorized", 401
    request_data = request.get_json()  
    card_time = request_data['time_stamp']
    card_value = request_data['value']
    card_note = request_data['note']
    tracker = Tracker.query.filter_by(id=tracker_id).first()
    card = Card(time_stamp = card_time, value = card_value, note = card_note, tracker = tracker)
    db.session.add(card)
    db.session.commit()
    return jsonify(message="success"), 200


@main.route("/tracker/<tracker_id>", methods=['GET'])
@token_required
def get_card(user, tracker_id):
    """
    Get all Cards Using Tracker ID
    ---
    tags:
        - main
    responses:
        200:
            description: Cards Fetched
    """
    tracker = Tracker.query.filter_by(id=tracker_id).first()
    if user["user_id"]!=tracker.user_id:
        return "Unauthorized", 401
    
    cards =  Card.query.filter_by(tracker_id=tracker.id).all()
    serialized_cards = serialize_cards(cards)
    return jsonify(serialized_cards), 200

@main.route("/tracker/<tracker_id>", methods=['DELETE'])
@token_required
def delete_card(user, tracker_id):
    """
    Delete a Card Using Card ID
    ---
    tags:
        - main
    responses:
        200:
            description: Card Deleted
    """
    tracker = Tracker.query.filter_by(id=tracker_id).first()
    if user["user_id"]!=tracker.user_id:
        return "Unauthorized", 401
    request_data = request.get_json()
    card_id = request_data['id']
    cards =  Card.query.filter_by(id=card_id).first()
    db.session.delete(cards)
    db.session.commit()
    return jsonify(message="success"), 200