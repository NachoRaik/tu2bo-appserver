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

        res = get_stats(client)
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

        res = get_stats(client)
        assert res.status_code == 200
        body = json.loads(res.get_data())
        assert len(body) == 1
        res_json = body[0]
        assert id in res_json['most_commented_videos']
        assert id in res_json['most_liked_videos']

    def test_stats_with_many_videos(self, client):
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
        
        res = get_stats(client)
        assert res.status_code == 200
        body = json.loads(res.get_data())
        print(body)
