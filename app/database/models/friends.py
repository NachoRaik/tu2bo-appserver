from database.db import db

class Friends(db.Document):
    user_id = db.IntField(primary_key=True)
    friends = db.ListField(db.IntField(), required=False)
