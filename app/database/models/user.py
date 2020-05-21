from database.db import db

class User(db.Document):
    id = db.SequenceField(primary_key=True)
    username = db.StringField(required=True, unique=True)
    videos = db.ListField(db.StringField(), required=False)
