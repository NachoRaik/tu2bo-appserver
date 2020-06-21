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
        db.drop_collection('friends')
        db.drop_collection('pending_request')
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

    def test_check_same_user_requested(self, client):
        """ GET /users/<user_id_request>
        Should: return 200"""
        ANOTHER_USER_ID = 1
        token = login_and_token_user(client)
        res = get_user_profile(client,token,ANOTHER_USER_ID)

        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert res_json.get("friendship_status",None) == None

    def test_send_friend_request_successfully(self, client):
        """ POST /users/<user_id_request>/friend_request
        Should: return 200"""
        ANOTHER_USER_ID = 2
        token = login_and_token_user(client)
        res = send_friend_request(client,token,ANOTHER_USER_ID)

        assert res.status_code == 200

    def test_send_friend_request_invalid(self, client):
        """ POST /users/<user_id_request>/friend_request
        Should: return 400"""
        ANOTHER_USER_ID = 200
        token = login_and_token_user(client)
        res = send_friend_request(client,token,ANOTHER_USER_ID)

        assert res.status_code == 400
        res_json = json.loads(res.get_data())
        assert res_json["reason"] == "Cant send friend request"

    def test_send_friend_request_check_pending(self, client):
        """ GET /users/<user_id_request>
        Should: return 200"""
        ANOTHER_USER_ID = 2
        token = login_and_token_user(client)
        res = send_friend_request(client,token,ANOTHER_USER_ID)
        res = get_user_profile(client,token,ANOTHER_USER_ID)

        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert res_json["friendship_status"] == "pending"

    def test_no_request_check_my_requests(self, client):
        """ GET /users/<user_id_request>
        Should: return 200"""
        token = login_and_token_user(client)
        res = my_requests(client,token)

        assert res.status_code == 404
        res_json = json.loads(res.get_data())
        assert res_json["reason"] == "User pending requests not found"

    def test_add_request_check_my_requests(self, client):
        """ GET /users/<user_id_request>
        Should: return 200"""
        ANOTHER_USER_ID = 2
        token = login_and_token_user(client,ANOTHER_USER_ID)
        send_friend_request(client,token,1)
        token = login_and_token_user(client)
        res = my_requests(client,token)

        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert res_json[0]["id"] == "2"

    def test_pending_and_not_friend_status(self, client):
        """ GET /users/<user_id_request>
        Should: return 200"""
        ANOTHER_USER_ID = 2
        token = login_and_token_user(client)
        res = send_friend_request(client,token,ANOTHER_USER_ID)
        res = get_user_profile(client,token,ANOTHER_USER_ID)

        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert res_json["friendship_status"] == "pending"

        token  = login_and_token_user(client,2)
        res = get_user_profile(client,token,1)

        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert res_json["friendship_status"] == "no-friends"

    def test_pending_and_my_request_status(self, client):
        """ GET /users/<user_id_request>
        Should: return 200"""
        ANOTHER_USER_ID = 2
        token = login_and_token_user(client)
        res = send_friend_request(client,token,ANOTHER_USER_ID)
        res = get_user_profile(client,token,ANOTHER_USER_ID)

        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert res_json["friendship_status"] == "pending"

        token  = login_and_token_user(client,2)
        res = my_requests(client,token)

        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert res_json[0]["id"] == "1"
