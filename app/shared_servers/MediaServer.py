import flask
import json
import requests
from datetime import datetime
from shared_servers.utils_media import *
from utils.flask_utils import error_response, success_response, make_flask_response

class MediaServer():
    def __init__(self, url = "localhost:5005"):
        self.url = url
    
    def add_video(self, data):
        response = requests.post(self.url + '/videos', json=data)
        return make_flask_response(response)

    def get_videos(self):
        response = requests.get(self.url + '/videos')
        return make_flask_response(response)

    def get_video(self, video_id):
        response = requests.get('{}/videos/{}'.format(self.url, video_id))
        return make_flask_response(response)

    def get_user_videos(self, user_id):
        response = requests.get('{}/videos?user_id={}'.format(self.url, user_id))
        return make_flask_response(response)

    def delete_video(self, video_id):
        response = requests.delete('{}/videos/{}'.format(self.url, video_id))
        return make_flask_response(response)

    def edit_video(self, video_id, data):
        response = requests.put('{}/videos/{}'.format(self.url, video_id), json=data)
        return make_flask_response(response)

    def __str__(self):
        return "url => {}".format(self.url)


# --- Mocks

class MockMediaServer(MediaServer):
    def __init__(self):
        super().__init__()
        self.db = {}
        self.next_id = len(self.db)

    def generate_id(self):
        self.next_id += 1
        return self.next_id

    def add_video(self, data):
        url = data['url']
        author = data['author']
        title = data['title']
        visibility = data['visibility']
        user_id = data['user_id']
        description = data['description'] if 'description' in data else ''
        thumb = data['thumb'] if 'thumb' in data else ''

        if any(video['url'] == url for video in self.db.values()):
            return error_response(409, 'Video already uploaded')

        date = datetime.strptime(data['date'], '%m/%d/%y %H:%M:%S')
        if date > datetime.now():
            return error_response(400, 'Invalid date')
        if not validate_visibility(data['visibility']):
            return error_response(400, 'Invalid visibility')

        id = self.generate_id()
        self.db[id] = {'author': author, 'title': title, 'description': description, 'date': date, 'visibility': visibility, 
        'url': url, 'thumb': thumb, 'user_id': user_id}
        response_data = {'id': id}
        return success_response(201, response_data)

    def get_videos(self):
        response_data = [get_fields(video_id, video) for video_id, video in self.db.items()]
        return success_response(200, response_data)

    def get_video(self, video_id):
        if not video_id in self.db:
            return error_response(404, 'Video not found')
        video = self.db[video_id]
        response_data = get_fields(video_id, video)
        return success_response(200, response_data)

    def get_user_videos(self, user_id):
        response_data = []
        for video_id, video in self.db.items():
            if video['user_id'] == user_id:
                response_data.append(get_fields(video_id, video))
        return success_response(200, response_data)

    def delete_video(self, video_id):        
        if not video_id in self.db:
            return error_response(404, 'Video not found')
                
        self.db = {id:video for id, video in self.db.items() if id != video_id}
        return flask.Response('', status=204)

    def edit_video(self, video_id, data):
        if any(elemen in data for elemen in ['id', 'author', 'user_id', 'url', 'date']):
            return error_response(400, 'Invalid values')

        if not validate_visibility(data['visibility']):
            return error_response(400, 'Invalid visibility')

        if not video_id in self.db:
            return error_response(404, 'Video not found')
        
        video = self.db[video_id]
        for k,v in data.items():
            if k in video:
                video[k] = v
        
        return success_response(200, get_fields(video_id, video))
