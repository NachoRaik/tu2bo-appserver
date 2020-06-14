from database.db import db

class Comment(db.EmbeddedDocument):
    author = db.StringField(required=True)
    comment_id = db.SequenceField(primary_key=True)
    user_id = db.IntField(required=True)
    content = db.StringField(required=True)
    timestamp = db.StringField(required=True)
