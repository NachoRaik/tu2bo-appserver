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

    def get_author_videos(self, data):
        raise Exception('Not implemented yet')

    def delete_video(self, data):
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
        url, author, title, visibility = parsed_data['url'], parsed_data['author'], parsed_data['title'], parsed_data['visibility']
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
        self.db[id] = {'author': author, 'title': title, 'description': description, 'date': date, 'visibility': visibility, 'url': url, 'thumb': thumb}
        response_data = {'id': id}
        return flask.Response(json.dumps(response_data), status=200)

    def get_videos(self):
        response_data = list(map(lambda video: get_fields(video), self.db.values()))
        return flask.Response(json.dumps(response_data), status=200)

    def get_author_videos(self, data):
        parsed_data = json.loads(data)
        author = parsed_data['author']
        if not any(video['author'] == author for video in self.db.values()):
            return flask.Response('Author not found', status=404)

        response_data = []
        for video in self.db.values():
            if video['author'] == author:
                response_data.append(get_fields(video))  
        return flask.Response(json.dumps(response_data), status=200)

    def delete_video(self, data):
        parsed_data = json.loads(data)
        url = parsed_data['url']
        
        if not any(video['url'] == url for video in self.db.values()):
            return flask.Response('Video not found', status=404)
                
        self.db = {id:video for id, video in self.db.items() if video['url'] != url}
        return flask.Response('', status=200)

    def change_video_visiblity(self, data):
        parsed_data = json.loads(data)
        url = parsed_data['url']
        visibility = parsed_data['visibility']

        if not any(video['url'] == url for video in self.db.values()):
            return flask.Response('Video not found', status=404)

        if not validate_visibility(parsed_data['visibility']):
            return flask.Response('Invalid visibility', status=400)
        
        for video in self.db.values():
            if video['url'] == url:
                video['visibility'] = visibility
        
        return flask.Response('', status=200)
