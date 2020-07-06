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

    def test_get_videos_from_user(self, client):
        """ GET /users/user_id/videos
        Should: return 200 """

        token = login_and_token_user(client)
        user_id = 1
        res = add_video(client, token, user_id, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = res_json['id']

        res = get_videos_from_user_id(client, token, user_id)
        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert len(res_json) == 1
        assert res_json[0]['id'] == video_id

    def test_get_videos_from_inexistent_user(self, client):
        """ GET /users/user_id/videos
        Should: return 200 and empty json"""

        token = login_and_token_user(client)
        res = get_videos_from_user_id(client, token, 100)
        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert len(res_json) == 0

    def test_get_video_from_user_no_friend(self, client):
        """ GET /users/user_id/videos
        Should: return 200 """

        user_id_video = 1
        user_id_viewer = 2
        token_user_video = login_and_token_user(client, user_id_video)
        token_user_viewer = login_and_token_user(client, user_id_viewer)

        res = add_video(client, token_user_video, user_id_video, 'url', 'someAuthor', 'someTitle', 'private', '06/14/20 16:39:33')
        assert res.status_code == 201

        res = get_videos_from_user_id(client, token_user_viewer, user_id_video)
        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert len(res_json) == 0

    def test_get_videos_from_user_no_friend(self, client):
        """ GET /users/user_id/videos
        Should: return 200 """

        user_id_video = 1
        user_id_viewer = 2
        token_user_video = login_and_token_user(client, user_id_video)
        token_user_viewer = login_and_token_user(client, user_id_viewer)

        # Adding private video
        res = add_video(client, token_user_video, user_id_video, 'url', 'someAuthor', 'someTitle', 'private', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        private_video_id = res_json['id']

        # Adding public video
        res = add_video(client, token_user_video, user_id_video, 'url2', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        public_video_id = res_json['id']

        res = get_videos_from_user_id(client, token_user_viewer, user_id_video)
        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert len(res_json) == 1
        assert public_video_id == res_json[0]['id']

    def test_get_videos_from_no_friend(self, client):
        """ GET /videos
        Should: return 200 """

        user_id_video = 1
        user_id_viewer = 2
        token_user_video = login_and_token_user(client, user_id_video)
        token_user_viewer = login_and_token_user(client, user_id_viewer)

        # Adding private video
        res = add_video(client, token_user_video, user_id_video, 'url', 'someAuthor', 'someTitle', 'private', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        private_video_id = res_json['id']

        # Adding public video
        res = add_video(client, token_user_video, user_id_video, 'url2', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        public_video_id = res_json['id']

        res = get_videos(client, token_user_viewer)
        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert len(res_json) == 1
        assert public_video_id == res_json[0]['id']

    def test_get_video_from_user_yourself(self, client):
        """ GET /users/user_id/videos
        Should: return 200 """

        token = login_and_token_user(client)
        user_id = 1

        res = add_video(client, token, user_id, 'url', 'someAuthor', 'someTitle', 'private', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = res_json['id']

        res = get_videos_from_user_id(client, token, user_id)
        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert len(res_json) == 1
        assert video_id == res_json[0]['id']

    def test_get_videos_from_user_yourself(self, client):
        """ GET /users/user_id/videos
        Should: return 200 """

        token = login_and_token_user(client)
        user_id = 1

        # Adding private video
        res = add_video(client, token, user_id, 'url', 'someAuthor', 'someTitle', 'private', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        private_video_id = res_json['id']

        # Adding public video
        res = add_video(client, token, user_id, 'url2', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        public_video_id = res_json['id']

        res = get_videos_from_user_id(client, token, user_id)
        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert len(res_json) == 2
        assert any(video['id'] == private_video_id for video in res_json)
        assert any(video['id'] == public_video_id for video in res_json)

    def test_get_videos_from_yourself(self, client):
        """ GET /videos
        Should: return 200 """

        token = login_and_token_user(client)
        user_id = 1

        # Adding private video
        res = add_video(client, token, user_id, 'url', 'someAuthor', 'someTitle', 'private', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        private_video_id = res_json['id']

        # Adding public video
        res = add_video(client, token, user_id, 'url2', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        public_video_id = res_json['id']

        res = get_videos(client, token)
        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert len(res_json) == 2
        assert any(video['id'] == private_video_id for video in res_json)
        assert any(video['id'] == public_video_id for video in res_json)

    def test_get_video_from_user_friend(self, client):
        """ GET /users/user_id/videos
        Should: return 200 """

        user_id_video = 1
        user_id_viewer = 2
        token_user_video = login_and_token_user(client, user_id_video)
        token_user_viewer = login_and_token_user(client, user_id_viewer)

        send_friend_request(client, token_user_video, user_id_viewer)
        accept_friend_request(client, token_user_viewer, user_id_video)

        res = add_video(client, token_user_video, user_id_video, 'url', 'someAuthor', 'someTitle', 'private', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = res_json['id']

        res = get_videos_from_user_id(client, token_user_viewer, user_id_video)
        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert len(res_json) == 1
        assert video_id == res_json[0]['id']

    def test_get_videos_from_user_friend(self, client):
        """ GET /users/user_id/videos
        Should: return 200 """

        user_id_video = 1
        user_id_viewer = 2
        token_user_video = login_and_token_user(client, user_id_video)
        token_user_viewer = login_and_token_user(client, user_id_viewer)

        send_friend_request(client, token_user_video, user_id_viewer)
        accept_friend_request(client, token_user_viewer, user_id_video)

        res = add_video(client, token_user_video, user_id_video, 'url', 'someAuthor', 'someTitle', 'private', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        private_video_id = res_json['id']

        res = add_video(client, token_user_video, user_id_video, 'url2', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        public_video_id = res_json['id']        

        res = get_videos_from_user_id(client, token_user_viewer, user_id_video)
        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert len(res_json) == 2
        assert any(video['id'] == private_video_id for video in res_json)
        assert any(video['id'] == public_video_id for video in res_json)

    def test_get_videos_from_friend(self, client):
        """ GET /videos
        Should: return 200 """

        user_id_video = 1
        user_id_viewer = 2
        token_user_video = login_and_token_user(client, user_id_video)
        token_user_viewer = login_and_token_user(client, user_id_viewer)

        send_friend_request(client, token_user_video, user_id_viewer)
        accept_friend_request(client, token_user_viewer, user_id_video)

        res = add_video(client, token_user_video, user_id_video, 'url', 'someAuthor', 'someTitle', 'private', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        private_video_id = res_json['id']

        res = add_video(client, token_user_video, user_id_video, 'url2', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        public_video_id = res_json['id']        

        res = get_videos(client, token_user_viewer)
        assert res.status_code == 200
        res_json = json.loads(res.get_data())
        assert len(res_json) == 2
        assert any(video['id'] == private_video_id for video in res_json)
        assert any(video['id'] == public_video_id for video in res_json)

    def test_delete_video_successfully(self, client):
        """ DELETE /videos/video_id
        Should: return 204 """

        token = login_and_token_user(client)
        res = add_video(client, token, 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')

        res = delete_video(client, token, 1)
        assert res.status_code == 204

        res_not_found = get_video(client, token, 1)
        assert res_not_found.status_code == 404

    def test_delete_video_with_comment(self, client):
        """ DELETE /videos/video_id
        Should: return 204 """

        token = login_and_token_user(client)
        res = add_video(client, token, 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = res_json['id']        
        author, content, timestamp = 'anotherAuthor', 'this video sucks', '06/18/20 10:39:33'
        res = add_comment_to_video(client, token, video_id, author=author, content=content, timestamp=timestamp)

        res = delete_video(client, token, 1)
        assert res.status_code == 204

        res_not_found = get_video(client, token, 1)
        assert res_not_found.status_code == 404

    def test_delete_video_forbidden(self, client):
        """ DELETE /videos/video_id
        Should: return 403 """

        token = login_and_token_user(client)
        anotherToken = login_and_token_user(client, id=2)
        add_video(client, token, 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')

        res = delete_video(client, anotherToken, 1)

        assert res.status_code == 403

    def test_delete_video_not_found(self, client):
        """ DELETE /videos/video_id
        Should: return 404 """

        token = login_and_token_user(client)

        res = delete_video(client, token, 1)

        assert res.status_code == 404

    def test_edit_video_successfully(self, client):
        """ PATCH /videos/video_id
        Should: return 200 with updated video """

        token = login_and_token_user(client)
        add_video(client, token, 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')

        res = edit_video(client, token, 1 , {'title': 'anotherTitle', 'visibility': 'private', 'description': 'newDescription'})
        res_json = json.loads(res.get_data())
        assert res.status_code == 200
        assert res_json['title'] == 'anotherTitle'
        assert res_json['visibility'] == 'private'
        assert res_json['description'] == 'newDescription'

    def test_edit_video_forbidden(self, client):
        """ PATCH /videos/video_id
        Should: return 403 """

        token = login_and_token_user(client)
        anotherToken = login_and_token_user(client, id=2)
        add_video(client, token, 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')

        res = edit_video(client, anotherToken, 1 , {'title': 'anotherTitle', 'visibility': 'private', 'description': 'newDescription'})
        res_json = json.loads(res.get_data())
        assert res.status_code == 403

    def test_edit_video_not_found(self, client):
        """ PATCH /videos/video_id
        Should: return 404 """

        token = login_and_token_user(client)

        res = delete_video(client, token, 1)

        assert res.status_code == 404
    
    def test_edit_video_invalid_values(self, client):
        """ PATCH /videos/video_id
        Should: return 400 """

        token = login_and_token_user(client)
        add_video(client, token, 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')

        res = edit_video(client, token, 1 , {'author': 'anotherAuthor'})
        res_json = json.loads(res.get_data())
        assert res.status_code == 400
        assert res_json['reason'] == 'Invalid values'

    def test_edit_video_invalid_visibility(self, client):
        """ PATCH /videos/video_id
        Should: return 400 """

        token = login_and_token_user(client)
        add_video(client, token, 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')

        res = edit_video(client, token, 1 , {'visibility': 'invalidVisibility'})
        res_json = json.loads(res.get_data())
        assert res.status_code == 400
        assert res_json['reason'] == 'Invalid visibility'

    
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

        assert 'comment_id' in res_json
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

        assert 'comment_id' in res_json
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
        assert 'comment_id' in first_comment
        assert first_comment['author'] == first_author
        assert first_comment['content'] == first_content
        assert first_comment['timestamp'] == first_timestamp

        second_comment = res_json[1]
        assert 'comment_id' in second_comment
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

        res = get_videos(client, token)
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

        res = get_videos(client, token)
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
