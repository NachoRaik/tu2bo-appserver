from datetime import datetime, timedelta
import flask
import json
import requests

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
        self.data = {}
        with open('shared_servers/example_videos.json') as json_file:
            self.data = json.load(json_file)
        
        print(self.data)
        self.videos = {}
        self.videos['1'] = { 
            'videoId1': { 'title': 'AsdfMovie1', 'description': 'Random Video', 'url': 'someurl.com' },
            'videoId2': { 'title': 'AsdfMovie2', 'description': 'Also Random', 'url': 'someurl2.com' }
        }
        self.videos['2'] = { 
            'videoId3': { 'title': 'Anime1', 'description': 'u.u', 'url': 'animeworld.com' },
            'videoId4': { 'title': 'Anime2', 'description': '-.-', 'url': 'animeplanet.com' }
        }
        self.videos['3'] = { 
            'videoId5': { 'title': 'SomeIndieShit', 'description': 'bla', 'url': 'indieshit.com' },
            'videoId6': { 'title': 'SomeIndieShit: 2nd part', 'description': 'blabla', 'url': 'indieshitisback.com' }
        }

    def getVideos(self):
        response_data = {k:v for x in self.videos.values() for k,v in x.items()}
        videos = {'videos': [v for x in self.data['data'] for v in x['videos']]}
        print(videos)
        return flask.Response(json.dumps(videos), status=200)

    def getUserVideos(self, userId):
        if userId not in self.videos:
            return flask.Response(json.dumps({'reason': 'User not found'}), status=404)

        videos = {'videos': [v for x in self.data['data'] if x['userId']==int(userId) for v in x['videos']]}
        return flask.Response(json.dumps(videos), status=200)

    def deleteVideo(self, userId, videoId):
        if userId not in self.videos or videoId not in self.videos[userId]:
            return flask.Response(json.dumps({'reason': 'Video not found'}), status=404)

        return flask.Response(json.dumps(self.videos[userId][videoId]), status=204)

    def changeVideoVisibility(self, userId, videoId, visible = False):
        return flask.Response('', status=200)