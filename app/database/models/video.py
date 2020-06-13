from database.db import db
from comment import Comment

class VideoInfo(db.Document):
    video_info_id = db.IntField(required=True, primary_key=True)
    comments = db.EmbeddedDocumentListField(Comment, required=False)
    likes = db.ListField(db.IntField(), required=False)
