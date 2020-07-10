
import pytest
from mongoengine import connect, disconnect
from mongoengine.connection import _get_db
from tests.utils import *
import json

USER_1 = 1
USER_2 = 2
USER_3 = 3

class TestUserDeletion:
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
        db.drop_collection('video_info')
        disconnect(alias='test')

    def test_user_deleted_from_user_profile_successfully(self, client):
        """ DELETE /users/user_id
        Should: return 204 """

        token = login_and_token_user(client, USER_1)
        res = delete_user_profile(client, token, USER_1)
        assert res.status_code == 204

        other_token = login_and_token_user(client, USER_2)
        res = get_user_profile(client, other_token, USER_1)
        assert res.status_code == 404

    def test_videos_deleted_from_user_profile_successfully(self, client):
        """ DELETE /users/user_id
        Should: return 204 """

        token = login_and_token_user(client, USER_1)
        other_token = login_and_token_user(client, USER_2)

        # Adding videos
        res = add_video(client, token, USER_1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res = add_video(client, token, USER_1, 'otherUrl', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201

        # Check that videos were added correctly
        res = get_videos_from_user_id(client, other_token, USER_1)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        video_ids = [video['id'] for video in res_json]
        assert len(video_ids) == 2

        # Delete user and its videos
        res = delete_user_profile(client, token, USER_1)
        assert res.status_code == 204

        # Videos no longer exist
        res = get_videos_from_user_id(client, other_token, USER_1)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        video_ids = [video['id'] for video in res_json]
        assert len(video_ids) == 0

    def test_video_comments_deleted_from_user_profile_successfully(self, client):
        """ DELETE /users/user_id
        Should: return 204 """

        token = login_and_token_user(client, USER_1)
        other_token = login_and_token_user(client, USER_2)

        # Adding video with comment
        res = add_video(client, other_token, USER_2, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = res_json['id']
        res = add_comment_to_video(client, token, video_id, author='author', content='aComment', timestamp='06/14/20 16:39:33')
        assert res.status_code == 201

        # Check that videos were added correctly with its comment
        res = get_comments_from_video(client, token, video_id)
        res_json = json.loads(res.get_data())
        comment_ids = [comment['comment_id'] for comment in res_json]
        assert len(comment_ids) == 1

        # Delete user and its comments
        res = delete_user_profile(client, token, USER_1)
        assert res.status_code == 204

        # Comments no longer exist
        res = get_comments_from_video(client, other_token, video_id)
        res_json = json.loads(res.get_data())
        comment_ids = [comment['comment_id'] for comment in res_json]
        assert len(comment_ids) == 0

    def test_video_likes_deleted_from_user_profile_successfully(self, client):
        """ DELETE /users/user_id
        Should: return 204 """

        token_user_1 = login_and_token_user(client, USER_1)
        token_user_2 = login_and_token_user(client, USER_2)
        token_user_3 = login_and_token_user(client, USER_3)

        # Adding video with like
        res = add_video(client, token_user_2, USER_2, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = res_json['id']
        res = like_video(client, token_user_1, video_id, True)
        assert res.status_code == 200
        res = like_video(client, token_user_3, video_id, True)
        assert res.status_code == 200

        # Check that videos were added correctly with its like
        res = get_video(client, token_user_2, video_id)
        res_json = json.loads(res.get_data())
        likes = res_json['likes']
        assert likes == 2

        # Delete user and its likes
        res = delete_user_profile(client, token_user_1, USER_1)
        assert res.status_code == 204

        # Likes no longer exist
        res = get_video(client, token_user_2, video_id)
        res_json = json.loads(res.get_data())
        likes = res_json['likes']
        assert likes == 1

    def test_friends_deleted_from_user_profile_successfully(self, client):
        """ DELETE /users/user_id
        Should: return 204 """

        token_user_1 = login_and_token_user(client, USER_1)
        token_user_2 = login_and_token_user(client, USER_2)
        token_user_3 = login_and_token_user(client, USER_3)

        # Making friends
        send_friend_request(client, token_user_1, USER_2)
        accept_friend_request(client, token_user_2, USER_1)
        send_friend_request(client, token_user_1, USER_3)
        accept_friend_request(client, token_user_3, USER_1)

        # Check that they are friends
        res = get_user_friends(client, token_user_2, USER_2)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        friend_ids = [int(friend['id']) for friend in res_json]
        assert friend_ids == [USER_1]

        res = get_user_friends(client, token_user_3, USER_3)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        friend_ids = [int(friend['id']) for friend in res_json]
        assert friend_ids == [USER_1]

        # Delete user and its friends
        res = delete_user_profile(client, token_user_1, USER_1)
        assert res.status_code == 204

        # Friends no longer exist
        res = get_user_friends(client, token_user_2, USER_2)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        friend_ids = [int(friend['id']) for friend in res_json]
        assert len(friend_ids) == 0

        res = get_user_friends(client, token_user_3, USER_3)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        friend_ids = [int(friend['id']) for friend in res_json]
        assert len(friend_ids) == 0

        res = get_user_friends(client, token_user_1, USER_1)
        assert res.status_code == 401

    def test_friend_requests_deleted_from_user_profile_successfully(self, client):
        """ DELETE /users/user_id
        Should: return 204 """

        token_user_1 = login_and_token_user(client, USER_1)
        token_user_2 = login_and_token_user(client, USER_2)
        token_user_3 = login_and_token_user(client, USER_3)

        # Sending requests
        send_friend_request(client, token_user_1, USER_2)
        send_friend_request(client, token_user_1, USER_3)

        # Check that they have the request
        res = my_requests(client, token_user_2)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        request_ids = [int(request['id']) for request in res_json]
        assert request_ids == [USER_1]

        res = my_requests(client, token_user_3)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        request_ids = [int(request['id']) for request in res_json]
        assert request_ids == [USER_1]

        # Delete user and its requests
        res = delete_user_profile(client, token_user_1, USER_1)
        assert res.status_code == 204

        # Friends no longer exist
        res = my_requests(client, token_user_2)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        request_ids = [int(request['id']) for request in res_json]
        assert len(request_ids) == 0

        res = my_requests(client, token_user_3)
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        request_ids = [int(request['id']) for request in res_json]
        assert len(request_ids) == 0

        res = my_requests(client, token_user_1)
        assert res.status_code == 401

    def test_delete_unauthorized_user_profile(self, client):
        """ DELETE /users/user_id
        Should: return 401 """

        res = delete_user_profile(client, 'invalidToken', USER_1)
        assert res.status_code == 401

    def test_delete_forbidden_user_profile(self, client):
        """ DELETE /users/user_id
        Should: return 403 """

        token = login_and_token_user(client, USER_1)
        res = delete_user_profile(client, token, USER_2)
        assert res.status_code == 403
