import pytest
from mongoengine import connect, disconnect
from mongoengine.connection import _get_db
from tests.utils import *
import json

class TestFriendsRequestController:
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

    def test_check_no_friends(self, client):
        """ GET /users/<user_id_request>
        Should: return 200"""
        ANOTHER_USER_ID = 2
        token = login_and_token_user(client)
        res = get_user_profile(client,token,ANOTHER_USER_ID)

        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert res_json["friendship_status"] == "no-friends"

    def test_check_no_friends(self, client):
        """ GET /users/<user_id_request>
        Should: return 200"""
        ANOTHER_USER_ID = 1
        token = login_and_token_user(client)
        res = get_user_profile(client,token,ANOTHER_USER_ID)

        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert res_json.get("friendship_status",None) == None
