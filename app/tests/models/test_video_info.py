import pytest
from mongoengine import connect, disconnect, get_connection
from mongoengine.connection import _get_db
from database.models.video_info import VideoInfo
from database.models.comment import Comment

class TestVideoInfo:
    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class. setup_method is invoked for every test method of a class.
        """
        connect('appserver-db-test', host='mongomock://localhost', alias='test_video')

    def teardown_method(self, method):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        db = _get_db()
        db.drop_collection('video_info')
        disconnect(alias='test_video')

    def test_create_video_info(self):
        """ Create video_info in db
        Should: return save video_info in db """
        video_id = 1
        video_info = VideoInfo(video_id=video_id)
        video_info.save()

        author, user_id, content, timestamp = 'author', 1, 'beautiful video', '2020-01-01 00:00:00'
        comment = Comment(author=author, user_id=user_id, content=content, timestamp=timestamp)
 
        video_info.comments.append(comment)
        video_info.save()

        added_video_info = VideoInfo.objects.get(video_id=video_id)
        assert added_video_info.video_id ==  video_id
        comment = added_video_info.comments[0]

        assert comment.author == author
        assert comment.user_id == user_id
        assert comment.content == content
        assert comment.timestamp == timestamp

