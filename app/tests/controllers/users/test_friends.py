import json
import pytest
from mongoengine import connect, disconnect
from mongoengine.connection import _get_db
from tests.utils import *
from database.models.pending_request import PendingRequest
from database.models.friends import Friends

USER_1 = 1
USER_2 = 2
USER_3 = 3

class TestFriends:
    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        connect('appserver-db-test', host='mongomock://localhost', alias='test')
        PendingRequest(user_id=USER_1, requests=[USER_2]).save()
        Friends(user_id=USER_2, friends=[USER_3]).save()
        Friends(user_id=USER_3, friends=[USER_2]).save()

    def teardown_method(self, method):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        db = _get_db()
        db.drop_collection('friends')
        db.drop_collection('pending_request')
        disconnect(alias='test')


    # -- Accept friend requests 

    def test_accept_friend_request(self, client):
        """ POST /users/<user_id_request>/friends
        Should: return 200"""
        token = login_and_token_user(client, USER_1)
        res = accept_friend_request(client, token, USER_2)
        assert res.status_code == 200

    def test_accept_changes_status_for_both(self, client):
        """ POST /users/<user_id_request>/friends
        Should: return 200"""
        token_user_1 = login_and_token_user(client, USER_1)
        token_user_2 = login_and_token_user(client, USER_2)

        #User 1
        res = get_user_profile(client, token_user_1, USER_2)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        assert res_json["friendship_status"] == "waiting-acceptance"
        #User 2
        res = get_user_profile(client, token_user_2, USER_1)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        assert res_json["friendship_status"] == "pending"

        accept_friend_request(client, token_user_1, USER_2)

        #User 1
        res = get_user_profile(client, token_user_1, USER_2)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        assert res_json["friendship_status"] == "friends"
        #User 2
        res = get_user_profile(client, token_user_2, USER_1)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        assert res_json["friendship_status"] == "friends"

    def test_accept_removes_request(self, client):
        """ POST /users/<user_id_request>/friends
        Should: return 200"""
        token = login_and_token_user(client, USER_1)
        
        res = my_requests(client, token)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        assert len(res_json) == 1

        res = accept_friend_request(client, token, USER_2)
        
        res = my_requests(client, token)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        assert len(res_json) == 0

    def test_accept_inexistent_user(self, client):
        """ POST /users/<user_id_request>/friends
        Should: return 404"""
        token = login_and_token_user(client, USER_1)
        res = accept_friend_request(client, token, 999)
        res_json = json.loads(res.get_data())
        assert res.status_code == 404
        assert res_json["reason"] == "Can't befriend inexistent user"

    def test_accept_inexistent_request(self, client):
        """ POST /users/<user_id_request>/friends
        Should: return 400"""
        token = login_and_token_user(client, USER_1)
        res = accept_friend_request(client, token, USER_3)
        res_json = json.loads(res.get_data())
        assert res.status_code == 400
        assert res_json["reason"] == "Can't accept friendship without request from the other user"

    def test_accept_pending_request_user(self, client):
        """ POST /users/<user_id_request>/friends
        Should: return 400"""
        token = login_and_token_user(client, USER_2)
        res = accept_friend_request(client, token, USER_1)
        res_json = json.loads(res.get_data())
        assert res.status_code == 400
        assert res_json["reason"] == "Can't accept friendship without request from the other user"


    # -- Friends list
    
    def test_user_with_no_friends(self, client):
        """ GET /users/<user_id_request>/friends
        Should: return 404"""
        token = login_and_token_user(client, USER_1)
        res = get_user_friends(client, token, USER_1)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        assert res_json == []
    
    def test_user_with_existent_friends(self, client):
        """ GET /users/<user_id_request>/friends
        Should: return 404"""
        token_user_2 = login_and_token_user(client, USER_2)
        token_user_3 = login_and_token_user(client, USER_3)
        
        res = get_user_friends(client, token_user_2, USER_2)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        assert res_json == [{'id': '3', 'username': 'user3'}]
        
        res = get_user_friends(client, token_user_3, USER_3)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        assert res_json == [{'id': '2', 'username': 'user2'}]

    def test_user_friends_seen_by_others(self, client):
        """ GET /users/<user_id_request>/friends
        Should: return 404"""
        token = login_and_token_user(client, USER_1)
        res = get_user_friends(client, token, USER_2)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        assert res_json == [{'id': '3', 'username': 'user3'}]

    def test_list_of_multiple_friends(self, client):
        """ GET /users/<user_id_request>/friends
        Should: return 200"""
        token_user_1 = login_and_token_user(client, USER_1)
        token_user_2 = login_and_token_user(client, USER_2)
        token_user_3 = login_and_token_user(client, USER_3)

        friends_user_1 = get_user_friends(client, token_user_1, USER_1).get_json()
        friends_user_2 = get_user_friends(client, token_user_2, USER_2).get_json()
        friends_user_3 = get_user_friends(client, token_user_3, USER_3).get_json()
        assert friends_user_1 == []
        assert friends_user_2 == [{'id': '3', 'username': 'user3'}]
        assert friends_user_3 == [{'id': '2', 'username': 'user2'}]
        
        accept_friend_request(client, token_user_1, USER_2)

        friends_user_1 = get_user_friends(client, token_user_1, USER_1).get_json()
        friends_user_2 = get_user_friends(client, token_user_2, USER_2).get_json()
        friends_user_3 = get_user_friends(client, token_user_3, USER_3).get_json()
        assert friends_user_1 == [{'id': '2', 'username': 'user2'}]
        assert friends_user_2 == [{'id': '3', 'username': 'user3'}, {'id': '1', 'username': 'user1'}]
        assert friends_user_3 == [{'id': '2', 'username': 'user2'}]
