from database.db import db

class User(db.Document):
    user_id = db.IntField(required=True, primary_key=True)
    username = db.StringField(required=True)
    videos = db.ListField(db.StringField(), required=False)
