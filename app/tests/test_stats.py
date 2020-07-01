import pytest
import json
from mongoengine import connect, disconnect
from mongoengine.connection import _get_db
from tests.utils import *

class TestMonitoringController:
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
        db.drop_collection('video_stat')
        db.drop_collection('video_info')
        disconnect(alias='test')

    def test_stats_empty(self, client):
        """ GET /stats 
        Should: return 200 and stats"""

        res = get_stats(client, timestamp='06/29/20 18:03:31', num=3)
        assert res.status_code == 200

        body = json.loads(res.get_data())
        assert len(body) == 0

    def test_stats_with_one_video(self, client):
        """ GET /stats 
        Should: return 200 and stats"""

        token = login_and_token_user(client)
        res = add_video(client, token, 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        res_json = json.loads(res.get_data())
        id = res_json['id']
        assert res.status_code == 201

        res = get_stats(client, timestamp='06/29/20 18:03:31', num=3)
        assert res.status_code == 200
        body = json.loads(res.get_data())
        assert len(body) == 1
        res_json = body[0]
        assert id in res_json['most_commented_videos']
        assert id in res_json['most_liked_videos']

    def test_stats_with_one_like_and_one_comment(self, client):
        """ GET /stats 
        Should: return 200 and stats"""

        token = login_and_token_user(client)
        res = add_video(client, token, 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        res_json = json.loads(res.get_data())
        first_id = res_json['id']
        assert res.status_code == 201
        
        res = add_video(client, token, 1, 'url2', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        res_json = json.loads(res.get_data())
        second_id = res_json['id']
        assert res.status_code == 201

        author, content, timestamp = 'anotherAuthor', 'this video sucks', '06/18/20 10:39:33'
        res = add_comment_to_video(client, token, second_id, author=author, content=content, timestamp=timestamp)
        
        assert res.status_code == 201

        res = like_video(client, token, second_id, True)
        assert res.status_code == 200
    
        res = get_stats(client, timestamp='06/29/20 18:03:31', num=3)
        assert res.status_code == 200
        body = json.loads(res.get_data())
        last_result = body[-1]
        assert last_result['most_liked_videos'] == [second_id, first_id]
        assert last_result['most_commented_videos'] == [second_id, first_id]

    def test_stats_with_more_than_minimum_videos(self, client):
        """ GET /stats 
        Should: return 200 and stats"""

        token = login_and_token_user(client)
        ids = []
        for i in range(10):
            res = add_video(client, token, 1, 'url{}'.format(i), 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
            res_json = json.loads(res.get_data())
            ids.append(int(res_json['id']))
            assert res.status_code == 201
        
        author, content, timestamp = 'anotherAuthor', 'this video sucks', '06/18/20 10:39:33'

        # One comment to first video
        res = add_comment_to_video(client, token, ids[0], author=author, content=content, timestamp=timestamp)
        assert res.status_code == 201
        
        # Three comments to second video
        res = add_comment_to_video(client, token, ids[1], author=author, content=content, timestamp=timestamp)        
        res = add_comment_to_video(client, token, ids[1], author=author, content=content, timestamp=timestamp)
        res = add_comment_to_video(client, token, ids[1], author=author, content=content, timestamp=timestamp)        
        assert res.status_code == 201

        # Two comments to third video
        res = add_comment_to_video(client, token, ids[2], author=author, content=content, timestamp=timestamp)        
        res = add_comment_to_video(client, token, ids[2], author=author, content=content, timestamp=timestamp)
        assert res.status_code == 201

        for i in range(6, 9):
            res = like_video(client, token, ids[i], True)
            assert res.status_code == 200
    
        res = get_stats(client, timestamp='06/29/20 18:03:31', num=3)
        assert res.status_code == 200
        body = json.loads(res.get_data())
        last_result = body[-1]
        assert last_result['most_commented_videos'] == [ids[1], ids[2], ids[0]]
        assert last_result['most_liked_videos'] == ids[6:9]

    def test_invalid_token_then_0_videos(self, client):
        """ GET /stats 
        Should: return 200 and stats"""

        token = login_and_token_user(client)
        res = add_video(client, token, 100, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 403

        res = get_stats(client, timestamp='06/29/20 18:03:31', num=3)
        assert res.status_code == 200

        body = json.loads(res.get_data())
        assert len(body) == 0

    def test_inexistent_token_then_0_videos(self, client):
        """ GET /stats 
        Should: return 200 and stats"""

        res = add_video(client, 'inexistentToken', 1, 'url', 'someAuthor', 'someTitle', 'public', '06/14/20 16:39:33')
        assert res.status_code == 401

        res = get_stats(client, timestamp='06/29/20 18:03:31', num=3)
        assert res.status_code == 200

        body = json.loads(res.get_data())
        assert len(body) == 0
