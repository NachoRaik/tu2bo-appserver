import pytest
from mongoengine import connect, disconnect
from mongoengine.connection import _get_db
from tests.utils import *
import json

USER_1 = 1
USER_2 = 2

class TestRequestFriend:
 
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


    # -- Sending friend requests 

    def test_send_friend_request_successfully(self, client):
        """ POST /users/<user_id>/friend_request
        Should: return 200"""
        token = login_and_token_user(client, USER_1)
        res = send_friend_request(client, token, USER_2)
        assert res.status_code == 200

    def test_send_friend_request_inexistent_user(self, client):
        """ POST /users/<user_id>/friend_request
        Should: return 404"""
        token = login_and_token_user(client, USER_1)
        res = send_friend_request(client, token, 200)
        res_json = json.loads(res.get_data())
        assert res.status_code == 404
        assert res_json["reason"] == "Can't send friend request to inexistent user"

    def test_send_friend_request_changes_requester_friendship_status(self, client):
        """ GET /users/<user_id>
        Should: return 200"""
        token = login_and_token_user(client, USER_1)

        res = get_user_profile(client, token, USER_2)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        assert res_json["friendship_status"] == "no-friends"
        
        res = send_friend_request(client, token, USER_2)

        res = get_user_profile(client, token, USER_2)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        assert res_json["friendship_status"] == "pending"

    def test_send_friend_request_changes_requested_friendship_status(self, client):
        """ GET /users/<user_id>
        Should: return 200"""
        token_user_1 = login_and_token_user(client, USER_1)
        token_user_2 = login_and_token_user(client, USER_2)
        
        res = get_user_profile(client, token_user_2, USER_1)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        assert res_json["friendship_status"] == "no-friends"
        
        res = send_friend_request(client, token_user_1, USER_2)

        res = get_user_profile(client, token_user_2, USER_1)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        assert res_json["friendship_status"] == "waiting-acceptance"

    def test_user_already_pending(self, client):
        """ POST /users/<user_id>/friend_request
        Should: return 400"""
        token = login_and_token_user(client, USER_1)

        send_friend_request(client, token, USER_2)
        res = send_friend_request(client, token, USER_2)
        res_json = json.loads(res.get_data())
        assert res.status_code == 400
        assert res_json["reason"] == "Can't send friend request to user who is friend, pending or awaiting for acceptance"

    def test_user_already_friends(self, client):
        """ POST /users/<user_id>/friend_request
        Should: return 400"""
        token_user_1 = login_and_token_user(client, USER_1)
        token_user_2 = login_and_token_user(client, USER_2)

        send_friend_request(client, token_user_1, USER_2)
        accept_friend_request(client, token_user_2, USER_1)

        res = send_friend_request(client, token_user_1, USER_2)
        res_json = json.loads(res.get_data())
        assert res.status_code == 400
        assert res_json["reason"] == "Can't send friend request to user who is friend, pending or awaiting for acceptance"

    
    # -- My requests

    def test_check_my_requests_empty(self, client):
        """ GET /users/my_requests
        Should: return 200"""
        token = login_and_token_user(client, USER_1)
        res = my_requests(client, token)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        assert res_json == []

    def test_check_my_requests_with_requests(self, client):
        """ GET /users/my_requests
        Should: return 200"""
        token_user_1 = login_and_token_user(client, USER_1)
        token_user_2 = login_and_token_user(client, USER_2)
        send_friend_request(client, token_user_2, USER_1)
        
        res = my_requests(client, token_user_1)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        assert len(res_json) == 1
        assert int(res_json[0]["id"]) == USER_2
