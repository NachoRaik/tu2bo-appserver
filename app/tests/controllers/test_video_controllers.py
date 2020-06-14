import pytest
from mongoengine import connect, disconnect
from mongoengine.connection import _get_db
from tests.utils import add_video, add_comment_to_video, get_comments_from_video, like_video
import json

class TestVideoController:
    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """

        connect('appserver-db-test', host='mongomock://localhost', alias='test')

    def teardown_method(self, method):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        db = _get_db()
        db.drop_collection('video_info')
        disconnect(alias='test')

    def test_add_video(self, client):
        """ POST /users/user_id/videos
        Should: return 201 with video id """

        res = add_video(client, 1, 'someUrl','someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        res_json = json.loads(res.get_data())
        assert res_json['id'] == 5
        assert res.status_code == 201

    def test_add_comment_to_video_succesful(self, client):
        """ POST /videos/video_id/comments
        Should: return 200"""
        
        res = add_video(client, 1, 'anotherUrl','someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = int(res_json['id'])

        author, content, timestamp = 'anotherAuthor', 'this video sucks', '06/18/20 10:39:33'
        res = add_comment_to_video(client, video_id, author, content, timestamp)
        assert res.status_code == 200
        res_json = json.loads(res.get_data())

        #TODO: change this harcoded number
        assert res_json['user_id'] == 1
        assert res_json['author'] == author
        assert res_json['content'] == content
        assert res_json['timestamp'] == timestamp
        

    def test_add_comment_to_inexistent_video(self, client):
        """ POST /videos/video_id/comments
        Should: return 404"""

        author, content, timestamp, inexistent_video_id = 'anotherAuthor', 'this video sucks', '06/18/20 10:39:33', 1000
        res = add_comment_to_video(client, inexistent_video_id, author, content, timestamp)
        assert res.status_code == 404
        res_json = json.loads(res.get_data())
        assert res_json['reason'] == 'Video not found'
     

