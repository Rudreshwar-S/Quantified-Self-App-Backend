from functools import wraps
from http.client import ImproperConnectionState
from flask import request
from qs_app import app, celery, mail
from flask_mail import Message
from .models import Tracker, User, Card
from datetime import datetime

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        data, status = get_logged_in_user(request)
        token = data.get('data')

        if not token:
            return data, status
        
        return f(data['data'] ,*args, **kwargs)

    return decorated


def get_logged_in_user(new_request):
    auth_token = new_request.headers.get('Authorization')
    if auth_token:
        resp = User.decode_auth_token(auth_token)
        if not isinstance(resp, str):
            user = User.query.filter_by(id=resp).first()
            response_object = {
                'status': 'success',
                'data': {
                    'user_id': user.id,
                    'email': user.email,
                    'name': user.name,
                }
            }
            return response_object, 200
        response_object = {
            'status': 'fail',
            'message': resp
        }
        return response_object, 401
    else:
        response_object = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }
        return response_object, 401


@celery.task
def send_async_email(email_data):
    msg = Message(email_data['subject'],
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[email_data['to']])
    msg.body = email_data['body']
    with app.app_context():
        mail.send(msg)

def send_reminder_emails():
    trakers = Tracker.query.all()
    for tracker in trakers:
        last_card = Card.query.filter_by(tracker_id=tracker.id).order_by(Card.id.desc()).first()

        if not last_card:
            continue

        time_gap = datetime.now() - datetime.fromtimestamp(int(last_card.time_stamp)/1000.0)
        if time_gap.days > 0:
            user = User.query.filter_by(id=tracker.user_id).first()
            email_data = {
                'subject': 'Time to create today\'s Tracker log!',
                'to': user.email,
                'body': f"Please visit Quantified Self webapp to create today\'s log for {tracker.name}"
            }
            send_async_email(email_data)