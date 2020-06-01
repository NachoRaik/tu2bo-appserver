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
        'visibility': 'public', 'url': 'anUrl', 'thumb': 'aThumb', 'user_id': '4'})
        response = self.mock_media_server.add_video(video_data)
        json = loads(response.get_data())
        assert json['id'] == 5
        assert response.status_code == 200
    
    def test_add_video_without_thumb_success(self):
        """ Add a video should return 200 """

        video_data = dumps({'author': 'anAuthor', 'title': 'aTitle', 'description': 'aDescription', 'date': '09/19/18 13:55:26', 
        'visibility': 'public', 'url': 'anUrl', 'user_id': '4'})
        response = self.mock_media_server.add_video(video_data)
        json = loads(response.get_data())
        assert json['id'] == 5
        assert response.status_code == 200

    def test_add_video_without_description_success(self):
        """ Add a video should return 200 """

        video_data = dumps({'author': 'anAuthor', 'title': 'aTitle', 'date': '09/19/18 13:55:26', 'visibility': 'public', 
        'url': 'anUrl', 'thumb': 'aThumb', 'user_id': '4'})
        response = self.mock_media_server.add_video(video_data)
        json = loads(response.get_data())
        assert json['id'] == 5
        assert response.status_code == 200
    
    def test_add_video_with_same_url_twice(self):
        """ Add a video already uploaded should return 409 """

        video_data = dumps({'author': 'anAuthor', 'title': 'aTitle', 'date': '09/19/18 13:55:26', 'visibility': 'public', 
        'url': 'anUrl', 'thumb': 'aThumb', 'user_id': '4'})
        self.mock_media_server.add_video(video_data)
        response = self.mock_media_server.add_video(video_data)
        assert b'Video already uploaded' in response.get_data()
        assert response.status_code == 409

    def test_add_video_with_invalid_date(self):
        """ Add a video with invalid date should return 400 """

        video_data = dumps({'author': 'anAuthor', 'title': 'aTitle', 'date': '09/19/20 13:55:26', 'visibility': 'public', 
        'url': 'anUrl', 'thumb': 'aThumb', 'user_id': '4'})
        response = self.mock_media_server.add_video(video_data)
        assert b'Invalid date' in response.get_data()
        assert response.status_code == 400
    
    def test_add_video_with_invalid_visibility(self):
        """ Add a video with invalid visibility should return 400 """

        video_data = dumps({'author': 'anAuthor', 'title': 'aTitle', 'date': '09/19/19 13:55:26', 'visibility': 'invalid', 
        'url': 'anUrl', 'thumb': 'aThumb', 'user_id': '4'})
        response = self.mock_media_server.add_video(video_data)
        assert b'Invalid visibility' in response.get_data()
        assert response.status_code == 400

    def test_get_videos_success(self):
        """ Get all videos should return 200 """

        response = self.mock_media_server.get_videos()
        json = loads(response.get_data())
        assert len(json) == 4 
        assert response.status_code == 200

    def test_add_and_get_videos(self):
        """ Get all videos should return 200 """

        author, title, description, date, visibility, url, thumb, user_id = 'anAuthor', 'aTitle', 'aDescription', '09/19/18 13:55:26', 'public', 'anUrl', 'aThumb', '4'
        video_data = dumps({'author': author, 'title': title, 'description': description, 'date': date, 'visibility': visibility, 
                    'url': url, 'thumb': thumb, 'user_id': user_id})
        response = self.mock_media_server.add_video(video_data)
        id = loads(response.get_data())['id']

        response = self.mock_media_server.get_videos()
        json = loads(response.get_data())
        assert len(json) == 5
        assert response.status_code == 200
        assert any(video['author'] == author for video in json)
        assert any(video['title'] == title for video in json)
        assert any(video['description'] == description for video in json)
        assert any(video['date'] == date for video in json)
        assert any(video['visibility'] == visibility for video in json)
        assert any(video['url'] == url for video in json)
        assert any(video['thumb'] == thumb for video in json)
        assert any(video['user_id'] == user_id for video in json)
        assert any(video['id'] == id for video in json)

    def test_get_videos_from_user(self):
        """ Get all videos from an existent user should return 200 """

        user_id = '4'
        video_data = dumps({'author': 'anAuthor', 'title': 'aTitle', 'date': '09/19/18 13:55:26', 'visibility': 'public', 
        'url': 'anUrl', 'thumb': 'aThumb', 'user_id': user_id})
        self.mock_media_server.add_video(video_data)

        response = self.mock_media_server.get_user_videos(user_id)
        json = loads(response.get_data())
        assert len(json) == 1
        assert response.status_code == 200

    def test_get_videos_from_inexistent_user(self):
        """ Get all videos from an unexistent user should return 404 """

        response = self.mock_media_server.get_user_videos('100')
        assert b'User not found' in response.get_data()
        assert response.status_code == 404

    def test_delete_video_success(self):
        """ Delete an existent video should return 200 """

        video_data = dumps({'author': 'anAuthor', 'title': 'aTitle', 'date': '09/19/18 13:55:26', 'visibility': 'public', 
        'url': 'anUrl', 'thumb': 'aThumb', 'user_id': '4'})
        response = self.mock_media_server.add_video(video_data)
        id = loads(response.get_data())['id']

        response = self.mock_media_server.delete_video(id)
        assert response.status_code == 200

        response = self.mock_media_server.get_videos()
        json = loads(response.get_data())
        assert len(json) == 4
        assert response.status_code == 200

    def test_delete_unexistent_video(self):
        """ Delete an unexistent video should return 404 """

        response = self.mock_media_server.delete_video(100)
        assert b'Video not found' in response.get_data()
        assert response.status_code == 404

    def test_change_visibility_success(self):
        """ Change visibility of a video should return 200 """

        video_data = dumps({'author': 'anAuthor', 'title': 'aTitle', 'date': '09/19/18 13:55:26', 'visibility': 'public', 
        'url': 'anUrl', 'thumb': 'aThumb', 'user_id': '4'})
        response = self.mock_media_server.add_video(video_data)
        id = loads(response.get_data())['id']

        new_visibility = 'private'
        request_data = dumps({'id': id, 'visibility': new_visibility})
        response = self.mock_media_server.change_video_visiblity(request_data)
        assert response.status_code == 200

        response = self.mock_media_server.get_videos()
        json = loads(response.get_data())
        assert any(video['id'] == id for video in json)  
        for video in json:
            if video['id'] == id:
                assert video['visibility'] == new_visibility

    def test_change_visibility_with_invalid_format(self):
        """ Change visibility of a video with invalid format should return 400 """

        video_data = dumps({'author': 'anAuthor', 'title': 'aTitle', 'date': '09/19/18 13:55:26', 'visibility': 'public', 
        'url': 'anUrl', 'thumb': 'aThumb', 'user_id': '4'})
        response = self.mock_media_server.add_video(video_data)
        id = loads(response.get_data())['id']

        request_data = dumps({'id': id, 'visibility': 'invalid'})
        response = self.mock_media_server.change_video_visiblity(request_data)
        assert b'Invalid visibility' in response.get_data()
        assert response.status_code == 400

    def test_change_visibility_of_unexistent_video(self):
        """" Change visibility of an unexistent video should return 404 """

        request_data = dumps({'id': '100', 'visibility': 'public'})
        response = self.mock_media_server.change_video_visiblity(request_data)
        assert b'Video not found' in response.get_data()
        assert response.status_code == 404