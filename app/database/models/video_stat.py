from database.db import db

class VideoStat(db.Document):
    id = db.SequenceField(primary_key=True)
    timestamp = db.StringField(required=True)
    videos_sorted_by_likes = db.ListField(db.IntField(), required=False)
    videos_sorted_by_comments = db.ListField(db.IntField(), required=False)
