import pytest
from mongoengine import connect, disconnect
from mongoengine.connection import _get_db
from tests.utils import add_video
import json

class TestUsersController:
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

    def test_add_video_successfully(self, client):
        """ POST /users/user_id/videos
        Should: return 201 with video id """

        res = add_video(client, 1, 'url1', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        res_json = json.loads(res.get_data())
        assert res_json['id'] == 5
        assert res.status_code == 201

    def test_add_video_already_uploaded(self, client):
        """ POST /users/user_id/videos
        Should: return 409 """

        res = add_video(client, 1, 'url2', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        res = add_video(client, 1, 'url2', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 409