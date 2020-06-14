from database.db import db
from database.models.comment import Comment

class VideoInfo(db.Document):
    video_id = db.IntField(required=True, primary_key=True)
    comments = db.ListField(db.EmbeddedDocumentField(Comment), required=False)
    likes = db.ListField(db.IntField(), required=False)
