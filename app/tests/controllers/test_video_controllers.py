import pytest
from mongoengine import connect, disconnect
from mongoengine.connection import _get_db
from tests.utils import add_video, add_comment_to_video, get_comments_from_video, like_video
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

    def test_add_video(self, client):
        """ POST /users/user_id/videos
        Should: return 201 with video id """

        res = add_video(client, 1, 'url1', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        res_json = json.loads(res.get_data())
        assert res_json['id'] == 5
        assert res.status_code == 201

    def test_add_comment_to_video_succesful(self, client):
        """ POST /videos/video_id/comments
        Should: return 200"""
        
        res = add_video(client, 1, 'url2', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = int(res_json['id'])

        author, content, timestamp = 'anotherAuthor', 'this video sucks', '06/18/20 10:39:33'
        res = add_comment_to_video(client, video_id, author, content, timestamp)
        assert res.status_code == 201
        res_json = json.loads(res.get_data())

        #TODO: change this harcoded number
        assert res_json['user_id'] == 1
        assert res_json['author'] == author
        assert res_json['content'] == content
        assert res_json['timestamp'] == timestamp

    def test_add_comment_to_inexistent_video(self, client):
        """ POST /videos/video_id/comments
        Should: return 404"""

        author, content, timestamp, inexistent_video_id = 'anotherAuthor', 'this video sucks', '06/18/20 10:39:33', 1000
        res = add_comment_to_video(client, inexistent_video_id, author, content, timestamp)
        assert res.status_code == 404
        res_json = json.loads(res.get_data())
        assert res_json['reason'] == 'Video not found'

    def test_add_comment_with_not_enough_fields(self, client):
        """ POST /videos/video_id/comments
        Should: return 400"""

        res = add_video(client, 1, 'url3', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = int(res_json['id'])

        res =  client.post('/videos/{}/comments'.format(video_id), json={
            'author': 'author',
            'content': 'content'
        })
        assert res.status_code == 400

        res =  client.post('/videos/{}/comments'.format(video_id), json={
            'author': 'author',
            'timestamp': '06/18/20 10:39:33'
        })
        assert res.status_code == 400

        res =  client.post('/videos/{}/comments'.format(video_id), json={
            'timestamp': '06/18/20 10:39:33',
            'content': 'content'
        })
        assert res.status_code == 400

    def test_get_comment_from_video_successful(self, client):
        """ GET /videos/video_id/comments
        Should: return 200"""
        
        res = add_video(client, 1, 'url4', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = int(res_json['id'])

        author, content, timestamp = 'anotherAuthor', 'this video sucks', '06/18/20 10:39:33'
        res = add_comment_to_video(client, video_id, author, content, timestamp)
        assert res.status_code == 201

        res = get_comments_from_video(client, video_id)
        res_json = json.loads(res.get_data())[0]
        
        #TODO: change this harcoded number
        assert res_json['user_id'] == 1
        assert res_json['author'] == author
        assert res_json['content'] == content
        assert res_json['timestamp'] == timestamp

    def test_get_comment_from_video_successful(self, client):
        """ GET /videos/video_id/comments
        Should: return 200"""
        
        res = add_video(client, 1, 'url5', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = int(res_json['id'])

        author, content, timestamp = 'anotherAuthor', 'this video sucks', '06/18/20 10:39:33'
        res = add_comment_to_video(client, video_id, author, content, timestamp)
        assert res.status_code == 201

        res = get_comments_from_video(client, video_id)
        assert res.status_code == 200
        res_json = json.loads(res.get_data())[0]
        
        #TODO: change this harcoded number
        assert res_json['user_id'] == 1
        assert res_json['author'] == author
        assert res_json['content'] == content
        assert res_json['timestamp'] == timestamp

    def test_get_multiple_comments_from_video_successful(self, client):
        """ GET /videos/video_id/comments
        Should: return 200"""
        
        res = add_video(client, 1, 'url6', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = int(res_json['id'])

        second_author, second_content, second_timestamp = 'anotherAuthor', 'this video sucks', '06/20/20 10:39:33'
        res = add_comment_to_video(client, video_id, second_author, second_content, second_timestamp)
        assert res.status_code == 201

        first_author, first_content, first_timestamp = 'otherAuthor', 'this video rocks', '06/18/20 10:39:33'
        res = add_comment_to_video(client, video_id, first_author, first_content, first_timestamp)
        assert res.status_code == 201

        res = get_comments_from_video(client, video_id)
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

        res = get_comments_from_video(client, 100)
        assert res.status_code == 404
        res_json = json.loads(res.get_data())
        assert res_json['reason'] == 'Video not found'        
        
    def test_like_video_successfully(self, client):
        """ PUT /videos/video_id/likes
        Should: return 200"""

        res = add_video(client, 1, 'url7', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = int(res_json['id'])

        liked = True
        res = like_video(client, video_id, liked)
        assert res.status_code == 200

    def test_dislike_video_successfully(self, client):
        """ PUT /videos/video_id/likes
        Should: return 200"""

        res = add_video(client, 1, 'url8', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = int(res_json['id'])

        liked = True
        res = like_video(client, video_id, liked)

        liked = False
        res = like_video(client, video_id, liked)
        assert res.status_code == 200
    
    def test_dislike_video_not_liked_doesnt_return_error(self, client):
        """ PUT /videos/video_id/likes
        Should: return 200"""

        res = add_video(client, 1, 'url9', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = int(res_json['id'])

        liked = False
        res = like_video(client, video_id, liked)
        assert res.status_code == 200

    def test_like_inexistent_video(self, client):
        """ PUT /videos/video_id/likes
        Should: return 404"""

        liked = True
        res = like_video(client, 100, liked)
        assert res.status_code == 404
        res_json = json.loads(res.get_data())
        assert res_json['reason'] == 'Video not found'

    def test_add_like_with_not_enough_fields(self, client):
        """ PUT /videos/video_id/likes
        Should: return 404"""

        res = add_video(client, 1, 'url10', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 201
        res_json = json.loads(res.get_data())
        video_id = int(res_json['id'])

        res = client.put('/videos/{}/likes'.format(video_id), json={})
        assert res.status_code == 400
