import pytest
from mongoengine import connect, disconnect
from mongoengine.connection import _get_db
from tests.utils import *
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

    # -- Video management

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

    def test_add_video_forbidden(self, client):
        """ POST /users/user_id/videos
        Should: return 403 """

        token = login_and_token_user(client)
        res = add_video(client, token, 2, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 403

    
    # -- Video Info logic

    def test_add_comment_to_video_succesful(self, client):
        """ POST /videos/video_id/comments
        Should: return 200"""

        token = login_and_token_user(client)
        res = add_video(client, token, 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = res_json['id']

        author, content, timestamp = 'anotherAuthor', 'this video sucks', '06/18/20 10:39:33'
        res = add_comment_to_video(client, token, video_id, author=author, content=content, timestamp=timestamp)
        assert res.status_code == 201
        res_json = json.loads(res.get_data())

        assert res_json['user_id'] == 1
        assert res_json['author'] == author
        assert res_json['content'] == content
        assert res_json['timestamp'] == timestamp

    def test_add_comment_to_inexistent_video(self, client):
        """ POST /videos/video_id/comments
        Should: return 404"""

        token = login_and_token_user(client)
        author, content, timestamp, inexistent_video_id = 'anotherAuthor', 'this video sucks', '06/18/20 10:39:33', 1000
        res = add_comment_to_video(client, token, inexistent_video_id, author=author, content=content, timestamp=timestamp)
        assert res.status_code == 404
        res_json = json.loads(res.get_data())
        assert res_json['reason'] == 'Video not found'

    def test_add_comment_with_not_enough_fields(self, client):
        """ POST /videos/video_id/comments
        Should: return 400"""

        token = login_and_token_user(client)
        res = add_video(client, token, 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = res_json['id']

        author, content, timestamp = 'someAuthor', 'content', '06/14/20 16:39:33'

        res = add_comment_to_video(client, token, video_id, author=author, content=content)
        assert res.status_code == 400

        res = add_comment_to_video(client, token, video_id, author=author, timestamp=timestamp)
        assert res.status_code == 400

        res = add_comment_to_video(client, token, video_id, content=content, timestamp=timestamp)
        assert res.status_code == 400

        res = add_comment_to_video(client, token, video_id, author=author)
        assert res.status_code == 400

        res = add_comment_to_video(client, token, video_id, content=content)
        assert res.status_code == 400

        res = add_comment_to_video(client, token, video_id, timestamp=timestamp)
        assert res.status_code == 400

        res = add_comment_to_video(client, token, video_id)
        assert res.status_code == 400

    def test_get_comment_from_video_successful(self, client):
        """ GET /videos/video_id/comments
        Should: return 200"""

        token = login_and_token_user(client)
        res = add_video(client, token, 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = res_json['id']

        author, content, timestamp = 'anotherAuthor', 'this video sucks', '06/18/20 10:39:33'
        res = add_comment_to_video(client, token, video_id, author=author, content=content, timestamp=timestamp)
        assert res.status_code == 201

        res = get_comments_from_video(client, token, video_id)
        res_json = json.loads(res.get_data())[0]

        #TODO: change this harcoded number
        assert res_json['user_id'] == 1
        assert res_json['author'] == author
        assert res_json['content'] == content
        assert res_json['timestamp'] == timestamp

    def test_get_multiple_comments_from_video_successful(self, client):
        """ GET /videos/video_id/comments
        Should: return 200"""

        token = login_and_token_user(client)
        res = add_video(client, token, 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = res_json['id']

        second_author, second_content, second_timestamp = 'anotherAuthor', 'this video sucks', '06/20/20 10:39:33'
        res = add_comment_to_video(client, token, video_id, author=second_author, content=second_content, timestamp=second_timestamp)
        assert res.status_code == 201

        first_author, first_content, first_timestamp = 'otherAuthor', 'this video rocks', '06/18/20 10:39:33'
        res = add_comment_to_video(client, token, video_id, author=first_author, content=first_content, timestamp=first_timestamp)
        assert res.status_code == 201

        res = get_comments_from_video(client, token,  video_id)
        assert res.status_code == 200
        res_json = json.loads(res.get_data())

        first_comment = res_json[0]
        assert first_comment['author'] == first_author
        assert first_comment['content'] == first_content
        assert first_comment['timestamp'] == first_timestamp

        second_comment = res_json[1]
        assert second_comment['author'] == second_author
        assert second_comment['content'] == second_content
        assert second_comment['timestamp'] == second_timestamp

    def test_get_comment_from_inexistent_video(self, client):
        """ GET /videos/video_id/comments
        Should: return 404"""

        token = login_and_token_user(client)
        res = get_comments_from_video(client, token, 100)
        assert res.status_code == 404
        res_json = json.loads(res.get_data())
        assert res_json['reason'] == 'Video not found'

    def test_like_video_successfully(self, client):
        """ PUT /videos/video_id/likes
        Should: return 200"""

        token = login_and_token_user(client)
        res = add_video(client, token, 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = res_json['id']

        liked = True
        res = like_video(client, token, video_id, liked)
        assert res.status_code == 200

    def test_dislike_video_successfully(self, client):
        """ PUT /videos/video_id/likes
        Should: return 200"""

        token = login_and_token_user(client)
        res = add_video(client, token, 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = res_json['id']

        liked = True
        res = like_video(client, token, video_id, liked)

        liked = False
        res = like_video(client, token, video_id, liked)
        assert res.status_code == 200

    def test_dislike_video_not_liked_doesnt_return_error(self, client):
        """ PUT /videos/video_id/likes
        Should: return 200"""

        token = login_and_token_user(client)
        res = add_video(client, token, 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = res_json['id']

        liked = False
        res = like_video(client, token, video_id, liked)
        assert res.status_code == 200

    def test_like_inexistent_video(self, client):
        """ PUT /videos/video_id/likes
        Should: return 404"""

        token = login_and_token_user(client)
        liked = True
        res = like_video(client, token, 100, liked)
        assert res.status_code == 404
        res_json = json.loads(res.get_data())
        assert res_json['reason'] == 'Video not found'

    def test_add_like_with_not_enough_fields(self, client):
        """ PUT /videos/video_id/likes
        Should: return 404"""

        token = login_and_token_user(client)
        res = add_video(client, token, 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = res_json['id']

        res = client.put('/videos/{}/likes'.format(video_id),headers={"access-token": token}, json={})
        assert res.status_code == 400

    def test_get_videos_with_zero_likes(self, client):
        """ GET /videos
        Should: return 200"""

        token = login_and_token_user(client)
        user_id, url, author, title, visibility, timestamp = 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33'
        res = add_video(client, token, user_id, url, author, title, visibility, timestamp)
        assert res.status_code == 201

        res = get_videos(client)
        res_json = json.loads(res.get_data())[0]
        assert res_json['likes'] == 0


    def test_get_videos_with_one_like(self, client):
        """ GET /videos
        Should: return 200"""

        token = login_and_token_user(client)
        user_id, url, author, title, visibility, timestamp = 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33'
        res = add_video(client, token, user_id, url, author, title, visibility, timestamp)
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = res_json['id']

        liked = True
        res = like_video(client, token, video_id, liked)
        assert res.status_code == 200

        res = get_videos(client)
        res_json = json.loads(res.get_data())[0]
        assert res_json['likes'] == 1

    def test_get_video_with_one_like_and_then_zero(self, client):
        """ GET /video/video_id
        Should: return 200"""

        token = login_and_token_user(client)
        user_id, url, author, title, visibility, timestamp = 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33'
        res = add_video(client, token, user_id, url, author, title, visibility, timestamp)
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = res_json['id']

        liked = True
        res = like_video(client, token, video_id, liked)
        assert res.status_code == 200

        res = get_video(client, token, video_id)
        res_json = json.loads(res.get_data())
        assert res_json['likes'] == 1
        assert res_json['user_related_info']['is_liked'] == True

        liked = False
        res = like_video(client, token, video_id, liked)
        assert res.status_code == 200

        res = get_video(client, token, video_id)
        res_json = json.loads(res.get_data())
        assert res_json['likes'] == 0
        assert res_json['user_related_info']['is_liked'] == False

    def test_get_inexistent_video(self, client):
        """ GET /videos/video_id
        Should: return 404"""

        token = login_and_token_user(client)
        res = get_video(client, token, 100)
        assert res.status_code == 404
        assert b'Video not found' in res.get_data()

    def test_get_video_with_zero_likes(self, client):
        """ GET /videos/video_id
        Should: return 200"""

        token = login_and_token_user(client)
        user_id, url, author, title, visibility, timestamp = 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33'
        res = add_video(client, token, user_id, url, author, title, visibility, timestamp)
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = res_json['id']

        res = get_video(client, token, video_id)
        res_json = json.loads(res.get_data())
        assert res_json['likes'] == 0
        assert res_json['user_related_info']['is_liked'] == False

    def test_liked_by_other_user(self, client):
        """ GET /videos/video_id
        Should: return 200"""

        token = login_and_token_user(client)
        user_id, url, author, title, visibility, timestamp = 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33'
        res = add_video(client, token, user_id, url, author, title, visibility, timestamp)
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = res_json['id']

        res = get_video(client, token, video_id)
        res_json = json.loads(res.get_data())
        assert res_json['likes'] == 0
        assert res_json['user_related_info']['is_liked'] == False

        token2 = login_and_token_user(client, 2)
        liked = True
        res = like_video(client, token2, video_id, liked)
        assert res.status_code == 200

        res = get_video(client, token, video_id)
        res_json = json.loads(res.get_data())
        assert res_json['likes'] == 1
        assert res_json['user_related_info']['is_liked'] == False

        res = get_video(client, token2, video_id)
        res_json = json.loads(res.get_data())
        assert res_json['likes'] == 1
        assert res_json['user_related_info']['is_liked'] == True
