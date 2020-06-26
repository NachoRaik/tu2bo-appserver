import pytest
from mongoengine import connect, disconnect
from mongoengine.connection import _get_db
from tests.utils import *
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

        token = login_and_token_user(client)
        res = add_video(client, token, 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        res_json = json.loads(res.get_data())
        assert res.status_code == 201
        assert res_json['id'] == 1

    def test_add_video_already_uploaded(self, client):
        """ POST /users/user_id/videos
        Should: return 409 """

        token = login_and_token_user(client)
        res = add_video(client, token, 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res = add_video(client, token, 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 409

    def test_add_video_with_invalid_date(self, client):
        """ POST /users/user_id/videos
        Should: return 400 """

        token = login_and_token_user(client)
        res = add_video(client, token, 1, 'url', 'someAuthor', 'someTitle', 'public', '09/19/50 13:55:26')
        assert b'Invalid date' in res.get_data()
        assert res.status_code == 400

    def test_add_video_with_invalid_visibility(self, client):
        """ POST /users/user_id/videos
        Should: return 400 """

        token = login_and_token_user(client)
        res = add_video(client, token, 1, 'url', 'someAuthor', 'someTitle', 'invalidVisibility', '09/19/18 13:55:26')
        assert b'Invalid visibility' in res.get_data()
        assert res.status_code == 400

    def test_edit_user_profile_successully(self, client):
        """ PUT /users/user_id
        Should: return 200 """

        new_profile_pic = 'myNewProfilePic'
        token = login_and_token_user(client)
        res = edit_user_profile(client, token, 1, new_profile_pic)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        assert res_json['profile']['picture'] == new_profile_pic
    
    def test_edit_forbidden_user_profile(self, client):
        """ PUT /users/user_id
        Should: return 403 """

        new_profile_pic = 'myNewProfilePic'
        token = login_and_token_user(client)
        res = edit_user_profile(client, token, 2, new_profile_pic)
        res_json = json.loads(res.get_data())
        assert res.status_code == 403
