import pytest
from json import loads
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

        video_data = {'author': 'anAuthor', 'title': 'aTitle', 'description': 'aDescription', 'date': '09/19/18 13:55:26', 
        'visibility': 'public', 'url': 'anUrl', 'thumb': 'aThumb', 'user_id': '4'}
        response = self.mock_media_server.add_video(video_data)
        json = loads(response.get_data())
        assert json['id'] == 1
        assert response.status_code == 201
    
    def test_add_video_without_thumb_success(self):
        """ Add a video should return 200 """

        video_data = {'author': 'anAuthor', 'title': 'aTitle', 'description': 'aDescription', 'date': '09/19/18 13:55:26', 
        'visibility': 'public', 'url': 'anUrl', 'user_id': '4'}
        response = self.mock_media_server.add_video(video_data)
        json = loads(response.get_data())
        assert json['id'] == 1
        assert response.status_code == 201

    def test_add_video_without_description_success(self):
        """ Add a video should return 200 """

        video_data = {'author': 'anAuthor', 'title': 'aTitle', 'date': '09/19/18 13:55:26', 'visibility': 'public', 
        'url': 'anUrl', 'thumb': 'aThumb', 'user_id': '4'}
        response = self.mock_media_server.add_video(video_data)
        json = loads(response.get_data())
        assert json['id'] == 1
        assert response.status_code == 201
    
    def test_add_video_with_same_url_twice(self):
        """ Add a video already uploaded should return 409 """

        video_data = {'author': 'anAuthor', 'title': 'aTitle', 'date': '09/19/18 13:55:26', 'visibility': 'public', 
        'url': 'anUrl', 'thumb': 'aThumb', 'user_id': '4'}
        self.mock_media_server.add_video(video_data)
        response = self.mock_media_server.add_video(video_data)
        assert b'Video already uploaded' in response.get_data()
        assert response.status_code == 409

    def test_add_video_with_invalid_date(self):
        """ Add a video with invalid date should return 400 """

        video_data = {'author': 'anAuthor', 'title': 'aTitle', 'date': '09/19/50 13:55:26', 'visibility': 'public', 
        'url': 'anUrl', 'thumb': 'aThumb', 'user_id': '4'}
        response = self.mock_media_server.add_video(video_data)
        assert b'Invalid date' in response.get_data()
        assert response.status_code == 400
    
    def test_add_video_with_invalid_visibility(self):
        """ Add a video with invalid visibility should return 400 """

        video_data = {'author': 'anAuthor', 'title': 'aTitle', 'date': '09/19/19 13:55:26', 'visibility': 'invalid', 
        'url': 'anUrl', 'thumb': 'aThumb', 'user_id': '4'}
        response = self.mock_media_server.add_video(video_data)
        assert b'Invalid visibility' in response.get_data()
        assert response.status_code == 400

    def test_get_videos_success(self):
        """ Get all videos should return 200 """

        response = self.mock_media_server.get_videos()
        json = loads(response.get_data())
        assert len(json) == 0
        assert response.status_code == 200

    def test_add_and_get_videos(self):
        """ Get all videos should return 200 """

        author, title, description, date, visibility, url, thumb, user_id = 'anAuthor', 'aTitle', 'aDescription', '09/19/18 13:55:26', 'public', 'anUrl', 'aThumb', '4'
        video_data = {'author': author, 'title': title, 'description': description, 'date': date, 'visibility': visibility, 
                    'url': url, 'thumb': thumb, 'user_id': user_id}
        response = self.mock_media_server.add_video(video_data)
        id = loads(response.get_data())['id']

        response = self.mock_media_server.get_videos()
        json = loads(response.get_data())
        assert len(json) == 1
        assert response.status_code == 200
        video = json[0]
        assert video['author'] == author 
        assert video['title'] == title 
        assert video['description'] == description 
        assert video['date'] == date 
        assert video['visibility'] == visibility 
        assert video['url'] == url 
        assert video['thumb'] == thumb 
        assert video['user_id'] == user_id 
        assert video['id'] == id 

    def test_get_video_by_id_success(self):
        """ Get existent video by id should return 200 """

        author, title, description, date, visibility, url, thumb, user_id = 'anAuthor', 'aTitle', 'aDescription', '09/19/18 13:55:26', 'public', 'anUrl', 'aThumb', '4'
        video_data = {'author': author, 'title': title, 'description': description, 'date': date, 'visibility': visibility, 
                    'url': url, 'thumb': thumb, 'user_id': user_id}
        response = self.mock_media_server.add_video(video_data)
        id = loads(response.get_data())['id']

        response = self.mock_media_server.get_video(id)
        video = loads(response.get_data())
        assert response.status_code == 200
        assert video['author'] == author
        assert video['title'] == title
        assert video['description'] == description
        assert video['date'] == date
        assert video['visibility'] == visibility
        assert video['url'] == url
        assert video['thumb'] == thumb
        assert video['user_id'] == user_id
        assert video['id'] == id

    def test_get_unexistent_video(self):
        """ Get unexistent video by id should return 404 """

        response = self.mock_media_server.get_video('100')
        assert b'Video not found' in response.get_data()
        assert response.status_code == 404

    def test_get_videos_from_user(self):
        """ Get all videos from an existent user should return 200 """

        user_id = '4'
        video_data = {'author': 'anAuthor', 'title': 'aTitle', 'date': '09/19/18 13:55:26', 'visibility': 'public', 
        'url': 'anUrl', 'thumb': 'aThumb', 'user_id': user_id}
        self.mock_media_server.add_video(video_data)

        response = self.mock_media_server.get_user_videos(user_id)
        json = loads(response.get_data())
        assert len(json) == 1
        assert response.status_code == 200

    def test_get_videos_from_inexistent_user(self):
        """ Get all videos from an unexistent user should return 200 and empty list """

        response = self.mock_media_server.get_user_videos('100')
        json = loads(response.get_data())
        assert len(json) == 0
        assert response.status_code == 200

    def test_delete_video_success(self):
        """ Delete an existent video should return 200 """

        video_data = {'author': 'anAuthor', 'title': 'aTitle', 'date': '09/19/18 13:55:26', 'visibility': 'public', 
        'url': 'anUrl', 'thumb': 'aThumb', 'user_id': '4'}
        response = self.mock_media_server.add_video(video_data)
        video_id = loads(response.get_data())['id']

        response = self.mock_media_server.delete_video(video_id)
        assert response.status_code == 204

        response = self.mock_media_server.get_video(video_id)
        assert response.status_code == 404

    def test_delete_unexistent_video(self):
        """ Delete an unexistent video should return 404 """

        response = self.mock_media_server.delete_video(100)
        assert b'Video not found' in response.get_data()
        assert response.status_code == 404

    def test_edit_video_success(self):
        """ Edit video should return 200 """

        video_data = {'author': 'anAuthor', 'title': 'aTitle', 'date': '09/19/18 13:55:26', 'visibility': 'public', 
        'url': 'anUrl', 'thumb': 'aThumb', 'user_id': '4'}
        response = self.mock_media_server.add_video(video_data)
        video_id = loads(response.get_data())['id']

        request_data = { 'visibility': 'private', 'title': 'aNewTitle' }
        response = self.mock_media_server.edit_video(video_id, request_data)
        video = loads(response.get_data())
        assert response.status_code == 200
        assert video['id'] == video_id
        assert video['url'] == 'anUrl'
        assert video['author'] == 'anAuthor'
        assert video['title'] == 'aNewTitle'
        assert video['visibility'] == 'private'

        # Check persistency
        response = self.mock_media_server.get_video(video_id)
        video = loads(response.get_data())
        assert response.status_code == 200
        assert response.status_code == 200
        assert video['id'] == video_id
        assert video['url'] == 'anUrl'
        assert video['author'] == 'anAuthor'
        assert video['title'] == 'aNewTitle'
        assert video['visibility'] == 'private'

    def test_edit_video_with_invalid_fields(self):
        """ Edit video with invalid values should return 400 """

        video_data = {'author': 'anAuthor', 'title': 'aTitle', 'date': '09/19/18 13:55:26', 'visibility': 'public', 
        'url': 'anUrl', 'thumb': 'aThumb', 'user_id': '4'}
        response = self.mock_media_server.add_video(video_data)
        video_id = loads(response.get_data())['id']

        request_data = {'id': '1245'}
        response = self.mock_media_server.edit_video(video_id, request_data)
        assert response.status_code == 400
        assert b'Invalid values' in response.get_data()

        request_data = {'author': 'someThief'}
        response = self.mock_media_server.edit_video(video_id, request_data)
        assert response.status_code == 400
        assert b'Invalid values' in response.get_data()

        request_data = {'date': '01/01/21 00:00:00'}
        response = self.mock_media_server.edit_video(video_id, request_data)
        assert response.status_code == 400
        assert b'Invalid values' in response.get_data()

        request_data = {'url': 'maliciousUrl.com'}
        response = self.mock_media_server.edit_video(video_id, request_data)
        assert response.status_code == 400
        assert b'Invalid values' in response.get_data()

    def test_edit_video_with_invalid_visibility(self):
        """ Edit video with invalid visibility should return 400 """

        video_data = {'author': 'anAuthor', 'title': 'aTitle', 'date': '09/19/18 13:55:26', 'visibility': 'public', 
        'url': 'anUrl', 'thumb': 'aThumb', 'user_id': '4'}
        response = self.mock_media_server.add_video(video_data)
        video_id = loads(response.get_data())['id']

        request_data = {'visibility': 'blabla'}
        response = self.mock_media_server.edit_video(video_id, request_data)
        assert response.status_code == 400
        assert b'Invalid visibility' in response.get_data()

    def test_edit_unexistent_video(self):
        """" Edit unexistent video should return 404 """

        request_data = {'visibility': 'private'}
        response = self.mock_media_server.edit_video(100, request_data)
        assert response.status_code == 404
        assert b'Video not found' in response.get_data()