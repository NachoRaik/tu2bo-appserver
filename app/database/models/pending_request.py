from database.db import db

class PendingRequest(db.Document):
    user_id = db.IntField(primary_key=True)
    requests = db.ListField(db.IntField(), required=False)
