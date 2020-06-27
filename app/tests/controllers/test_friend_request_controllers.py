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
        assert res_json.get("friendship_status", None) == None

    def test_send_friend_request_successfully(self, client):
        """ POST /users/<user_id_request>/friend_request
        Should: return 200"""
        ANOTHER_USER_ID = 2
        token = login_and_token_user(client)
        res = send_friend_request(client,token,ANOTHER_USER_ID)

        assert res.status_code == 200

    def test_send_friend_request_invalid(self, client):
        """ POST /users/<user_id_request>/friend_request
        Should: return 404"""
        ANOTHER_USER_ID = 200
        token = login_and_token_user(client)
        res = send_friend_request(client,token,ANOTHER_USER_ID)

        assert res.status_code == 404
        res_json = json.loads(res.get_data())
        assert res_json["reason"] == "Can't send friend request to inexistent user"

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

        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert res_json == []

    def test_add_request_check_my_requests(self, client):
        """ GET /users/<user_id_request>
        Should: return 200"""

        MY_USER_ID = 1
        ANOTHER_USER_ID = 2
        token = login_and_token_user(client,ANOTHER_USER_ID)
        send_friend_request(client,token,MY_USER_ID)
        token = login_and_token_user(client)
        res = my_requests(client,token)

        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert res_json[0]["id"] == "2"

    def test_pending_and_not_friend_status(self, client):
        """ GET /users/<user_id_request>
        Should: return 200"""

        MY_USER_ID = 1
        ANOTHER_USER_ID = 2
        token = login_and_token_user(client)
        res = send_friend_request(client,token,ANOTHER_USER_ID)
        res = get_user_profile(client,token,ANOTHER_USER_ID)

        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert res_json["friendship_status"] == "pending"

        token  = login_and_token_user(client,ANOTHER_USER_ID)
        res = get_user_profile(client,token,MY_USER_ID)

        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert res_json["friendship_status"] == "waiting-acceptance"

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

        token  = login_and_token_user(client,ANOTHER_USER_ID)
        res = my_requests(client,token)

        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert res_json[0]["id"] == "1"

    def test_accept_friend_request(self, client):
        """ POST /users/<user_id_request>/friends
        Should: return 200"""

        MY_USER_ID = 1
        ANOTHER_USER_ID = 2
        token = login_and_token_user(client)
        send_friend_request(client,token,ANOTHER_USER_ID)
        token = login_and_token_user(client,ANOTHER_USER_ID)
        res = accept_friend_request(client,token,MY_USER_ID)
        assert res.status_code == 200

    def test_accept_and_check_status_for_both(self, client):
        """ GET /users/<user_id_request>
        Should: return 200"""

        MY_USER_ID = 1
        ANOTHER_USER_ID = 2
        token = login_and_token_user(client)
        send_friend_request(client,token,ANOTHER_USER_ID)
        token = login_and_token_user(client,ANOTHER_USER_ID)
        accept_friend_request(client,token,MY_USER_ID)

        #User 1
        token = login_and_token_user(client)
        res = get_user_profile(client,token,ANOTHER_USER_ID)

        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert res_json["friendship_status"] == "friends"

        #User 2
        token = login_and_token_user(client,ANOTHER_USER_ID)
        res = get_user_profile(client,token,MY_USER_ID)

        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert res_json["friendship_status"] == "friends"

    def test_accept_and_remove_request(self, client):
        """ GET /users/my_requests
        Should: return 200"""
        MY_USER_ID = 1
        ANOTHER_USER_ID = 2
        token = login_and_token_user(client)
        send_friend_request(client,token,ANOTHER_USER_ID)
        token = login_and_token_user(client,ANOTHER_USER_ID)
        accept_friend_request(client,token,MY_USER_ID)
        res = my_requests(client,token)
        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert res_json == []


    def test_list_of_friends(self, client):
        """ GET /users/<user_id_request>/friends
        Should: return 200"""
        MY_USER_ID = 1
        FRIEND_2 = 2
        FRIEND_3 = 3
        token = login_and_token_user(client)
        send_friend_request(client,token,FRIEND_2)
        send_friend_request(client,token,FRIEND_3)
        token = login_and_token_user(client,FRIEND_2)
        accept_friend_request(client,token,MY_USER_ID)
        token = login_and_token_user(client,FRIEND_3)
        accept_friend_request(client,token,MY_USER_ID)

        #Friends User1
        token = login_and_token_user(client)
        res = get_user_friends(client,token,MY_USER_ID)
        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert res_json == [{'id': '2', 'username': 'user2'}, {'id': '3', 'username': 'user3'}]


        #Friends User2
        token = login_and_token_user(client,FRIEND_2)
        res = get_user_friends(client,token,FRIEND_2)
        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert res_json == [{'id': '1', 'username': 'user1'}]


        #Friends User3
        token = login_and_token_user(client,FRIEND_3)
        res = get_user_friends(client,token,FRIEND_3)
        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert res_json == [{'id': '1', 'username': 'user1'}]


    def test_user_has_no_request(self, client):
        """ GET /users/my_requests
        Should: return 200"""

        token = login_and_token_user(client)
        res = my_requests(client,token)
        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert res_json == []



    def test_accept_any_request_fail(self, client):
        """ POST /users/<user_id_request>/friends
        Should: return 400"""

        MY_USER_ID = 1
        token = login_and_token_user(client)
        res = accept_friend_request(client,token,MY_USER_ID)
        assert res.status_code == 400
        res_json = json.loads(res.get_data())
        assert res_json["reason"] == "Can't accept friendship without request"

    def test_accept_no_request(self, client):
        """ POST /users/<user_id_request>/friends
        Should: return 404"""

        MY_USER_ID = 1
        FRIEND_2 = 2
        FRIEND_3 = 3
        token = login_and_token_user(client)
        send_friend_request(client,token,FRIEND_2)

        token = login_and_token_user(client,FRIEND_2)
        res = accept_friend_request(client,token,FRIEND_3)

        assert res.status_code == 400
        res_json = json.loads(res.get_data())
        assert res_json["reason"] == "Can't accept friendship without request"


    def test_user_has_not_friends(self, client):
        """ GET /users/<user_id_request>/friends
        Should: return 404"""

        MY_USER_ID = 1
        token = login_and_token_user(client)
        res = get_user_friends(client,token,MY_USER_ID)
        assert res.status_code == 404
        res_json = json.loads(res.get_data())
        assert res_json["reason"] == "User has not friends"

    def test_user_already_friends(self, client):
        """ POST /users/<user_id_request>/friend_request
        Should: return 400"""

        MY_USER_ID = 1
        FRIEND_2 = 2
        token = login_and_token_user(client)
        send_friend_request(client,token,FRIEND_2)

        token = login_and_token_user(client,FRIEND_2)
        accept_friend_request(client,token,MY_USER_ID)

        token = login_and_token_user(client)
        res = send_friend_request(client,token,FRIEND_2)

        assert res.status_code == 400
        res_json = json.loads(res.get_data())
        assert res_json["reason"] == "Already friends"

    def test_user_already_friends(self, client):
        """ POST /users/<user_id_request>/friend_request
        Should: return 400"""

        MY_USER_ID = 1
        FRIEND_2 = 2
        token = login_and_token_user(client)
        send_friend_request(client,token,FRIEND_2)

        token = login_and_token_user(client, FRIEND_2)
        res = send_friend_request(client,token,MY_USER_ID)

        assert res.status_code == 400
        res_json = json.loads(res.get_data())
        assert res_json["reason"] == "Already pending"
