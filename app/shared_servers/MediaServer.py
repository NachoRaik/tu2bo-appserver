from datetime import datetime, timedelta
import flask
import json
import requests
from shared_servers.utils_media import *

class MediaServer():
    def __init__(self, url = "localhost:5005"):
        self.url = url
    
    def add_video(self, data):
        raise Exception('Not implemented yet')

    def get_videos(self):
        raise Exception('Not implemented yet')

    def get_user_videos(self, user_id):
        raise Exception('Not implemented yet')

    def delete_video(self, video_id):
        raise Exception('Not implemented yet')

    def change_video_visiblity(self, data):
        raise Exception('Not implemented yet')


# --- Mocks

class MockMediaServer(MediaServer):
    def __init__(self):
        super().__init__()
        self.db = {}
        init_db(self.db)
        self.next_id = len(self.db)

    def generate_id(self):
        self.next_id += 1
        return self.next_id

    def add_video(self, data):
        parsed_data = json.loads(data)
        url = parsed_data['url']
        author = parsed_data['author']
        title = parsed_data['title']
        visibility = parsed_data['visibility']
        user_id = parsed_data['user_id']
        description = parsed_data['description'] if 'description' in data else ''
        thumb = parsed_data['thumb'] if 'thumb' in data else ''

        if any(video['url'] == url for video in self.db.values()):
            return flask.Response('Video already uploaded', status=409)

        date = datetime.strptime(parsed_data['date'], '%m/%d/%y %H:%M:%S')
        if date > datetime.now():
            return flask.Response('Invalid date', status=400)
        if not validate_visibility(parsed_data['visibility']):
            return flask.Response('Invalid visibility', status=400)

        id = self.generate_id()
        self.db[id] = {'author': author, 'title': title, 'description': description, 'date': date, 'visibility': visibility, 
        'url': url, 'thumb': thumb, 'user_id': user_id}
        response_data = {'id': id}
        return flask.Response(json.dumps(response_data), status=200)

    def get_videos(self):
        response_data = [get_fields(video_id, video) for video_id, video in self.db.items()]        
        return flask.Response(json.dumps(response_data), status=200)

    def get_video(self, video_id):
        if not video_id in self.db:
            return flask.Response('Video not found', status=404)
        video = self.db[video_id]
        response_data = [get_fields(video_id, video)]
        return flask.Response(json.dumps(response_data), status=200)

    def get_user_videos(self, user_id):
        if not any(video['user_id'] == user_id for video in self.db.values()):
            return flask.Response('User not found', status=404)

        response_data = []
        for video_id, video in self.db.items():
            if video['user_id'] == user_id:
                response_data.append(get_fields(video_id, video))  
        return flask.Response(json.dumps(response_data), status=200)

    def delete_video(self, video_id):        
        if not video_id in self.db:
            return flask.Response('Video not found', status=404)
                
        self.db = {id:video for id, video in self.db.items() if id != video_id}
        return flask.Response('', status=200)

    def change_video_visiblity(self, data):
        parsed_data = json.loads(data)
        video_id = parsed_data['id']
        visibility = parsed_data['visibility']

        if not video_id in self.db:
            return flask.Response('Video not found', status=404)

        if not validate_visibility(parsed_data['visibility']):
            return flask.Response('Invalid visibility', status=400)
        
        video = self.db[video_id]
        video['visibility'] = visibility
        
        return flask.Response('', status=200)
