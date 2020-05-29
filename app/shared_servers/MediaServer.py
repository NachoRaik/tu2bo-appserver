from datetime import datetime, timedelta
import flask
import json
import requests
from shared_servers.utils_media import *

class MediaServer():

    def __init__(self, url = "localhost:5005"):
        self.url = url

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
        self.db_metadata = {}
        init_metadata(self.db_metadata)
        self.next_id = len(self.db)

    def generate_id(self):
        self.next_id += 1
        return self.next_id

    def add_video(self, data):
        parsed_data = json.loads(data)
        if any(video['url'] == parsed_data['url'] for video in self.db_metadata.values()):
            return flask.Response('Video already uploaded', status=409)
        date = datetime.strptime(parsed_data['date'], '%m/%d/%y %H:%M:%S')
        if date > datetime.now() or not validate_visibility(parsed_data['visibility']):
            return flask.Response('Invalid date', status=400)
        id = self.generate_id()
        self.db[id] = {'author': parsed_data['author'], 'title': parsed_data['title'], 'description': parsed_data['description'], 
                    'date': parsed_data['date'], 'visibility': parsed_data['visibility']}
        self.db_metadata[id] = {'url': parsed_data['url'], 'thumb': parsed_data['thumb']}
        response_data = {'id': id}
        return flask.Response(json.dumps(response_data), status=200)