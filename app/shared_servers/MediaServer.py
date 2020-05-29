from datetime import datetime, timedelta
import flask
import json
import requests
from shared_servers.utils_media import *

class MediaServer():

    def __init__(self, url = "localhost:5005"):
        self.url = url
    
    def add_video(self):
        raise Exception('Not implemented yet')

    def getVideos(self):
        raise Exception('Not implemented yet')

    def getUserVideos(self, userId):
        raise Exception('Not implemented yet')

    def deleteVideo(self, userId, videoId):
        raise Exception('Not implemented yet')

    def changeVideoVisibility(self, userId, videoId, visible = False):
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
        if date > datetime.now() or not validate_visibility(parsed_data['visibility']):
            return flask.Response('Invalid date', status=400)
        id = self.generate_id()
        self.db[id] = {'author': author, 'title': title, 'description': description, 'date': date, 'visibility': visibility, 'url': url, 'thumb': thumb}
        response_data = {'id': id}
        return flask.Response(json.dumps(response_data), status=200)

    def get_videos(self):
        response_data = {v for v in self.db.values()}
        return flask.Response(json.dumps(response_data), status=200)