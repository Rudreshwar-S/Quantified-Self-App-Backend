from qs_app import db
import qs_app.models
db.create_all()

# from qs_app import redis_client
# redis_client.delete('user_count')