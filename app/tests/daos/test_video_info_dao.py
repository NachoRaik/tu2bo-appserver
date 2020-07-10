import pytest
from mongoengine import connect, disconnect, get_connection
from mongoengine.connection import _get_db
from database.daos.VideoInfoDAO import VideoInfoDAO

class TestVideoInfoDAO:
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

    def test_delete_video_info_correctly(self):
        video_id = 1
        handler = VideoInfoDAO()
        
        handler.new_video_registered(video_id)
        assert handler.get_video_comments(video_id) == []

        handler.delete_video_info(video_id)
        assert handler.get_video_comments(video_id) == None

    def test_delete_comment_correctly(self):
        video_id = 1
        user_id = 1
        handler = VideoInfoDAO()
        
        handler.new_video_registered(video_id)
        handler.add_video_comment(video_id, user_id, {'author': 'author', 'content': 'content', 'timestamp': '06/14/20 16:39:33'})
        comments = handler.get_video_comments(video_id)
        assert len(comments) == 1
        comment_id = comments[0].comment_id

        handler.delete_comment(video_id, comment_id)        
        comments = handler.get_video_comments(video_id)
        assert len(comments) == 0