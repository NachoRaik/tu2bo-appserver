import pytest
from json import loads, dumps
from datetime import datetime
from shared_servers.MediaServer import MockMediaServer

class TestMockMediaServer:
    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        self.mock_media_server = MockMediaServer()

    def test_add_video_full_data_success(self):
        """ Add a video should return 200 """
        video_data = dumps({'author': 'anAuthor', 'title': 'aTitle', 'description': 'aDescription', 'date': '09/19/18 13:55:26', 
        'visibility': 'public', 'url': 'anUrl', 'thumb': 'aThumb'})
        response = self.mock_media_server.add_video(video_data)
        json = loads(response.get_data())
        assert json['id'] == 5
        assert response.status_code == 200
    
    def test_add_video_without_thumb_success(self):
        """ Add a video should return 200 """
        video_data = dumps({'author': 'anAuthor', 'title': 'aTitle', 'description': 'aDescription', 'date': '09/19/18 13:55:26', 
        'visibility': 'public', 'url': 'anUrl'})
        response = self.mock_media_server.add_video(video_data)
        json = loads(response.get_data())
        assert json['id'] == 5
        assert response.status_code == 200

    def test_add_video_without_description_success(self):
        """ Add a video should return 200 """
        video_data = dumps({'author': 'anAuthor', 'title': 'aTitle', 'date': '09/19/18 13:55:26', 'visibility': 'public', 
        'url': 'anUrl', 'thumb': 'aThumb'})
        response = self.mock_media_server.add_video(video_data)
        json = loads(response.get_data())
        assert json['id'] == 5
        assert response.status_code == 200
