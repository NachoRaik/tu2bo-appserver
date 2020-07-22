import os

from shared_servers.AuthServer import AuthServer, MockAuthServer
from shared_servers.MediaServer import MediaServer, MockMediaServer
from datetime import timedelta

class Config(object):
    def __init__(self):
        self.DEBUG = False
        self.TESTING = False
        self.AUTH_SERVER = AuthServer()
        self.MEDIA_SERVER = MediaServer()
        self.MONGODB_SETTINGS = {
	        'db': 'appserver-db',
	        'host': 'mongodb://appserver-db:27017/appserver-db'
        }
        self.WEB_INTERFACE_KEY = 'LCCJ5bMh9DzCYJjnD2Q4TWo0l5FiQnibjM4iQcTO7Bl7faMRkJXDuOxa8zugSByW'
        self.AUTH_API_KEY = 'asdf'

    def __repr__(self):
        printable_fields = ['DEBUG', 'AUTH_SERVER', 'MEDIA_SERVER']
        fields = vars(self)
        output = ""
        for x in printable_fields: 
            output+="\n\t{} = {}".format(x, fields.get(x, "Not setted"))
        return output 

class ProductionConfig(Config):
    def __init__(self):
        super().__init__()
        self.AUTH_API_KEY = os.getenv('AUTH_API_KEY', '')
        self.AUTH_SERVER = AuthServer(url = os.getenv('AUTH_URI', 'localhost:3000'), api_key_value = self.AUTH_API_KEY)
        self.MEDIA_SERVER = MediaServer(url = os.getenv('MEDIA_URI', 'localhost:5005'))
        self.MONGODB_SETTINGS = {
            'host': os.getenv('MONGODB_URI'),
            'retryWrites': False
        }
        self.DELAY = timedelta(days=1)
        self.WEB_INTERFACE_KEY = os.getenv('WEB_INTERFACE_KEY', '')

class DevelopmentConfig(Config):
    def __init__(self):
        super().__init__()
        self.TESTING = True
        self.AUTH_SERVER = MockAuthServer()
        self.MEDIA_SERVER = MockMediaServer()
        self.DELAY = timedelta(minutes=1)

class TestingConfig(Config):
    def __init__(self):
        super().__init__()
        self.TESTING = True
        self.AUTH_SERVER = MockAuthServer()
        self.MEDIA_SERVER = MockMediaServer()
        self.MONGODB_SETTINGS = {
            'db': 'appserver-db-test',
            'host': 'mongomock://localhost',
            'connect': False
        }
        self.DELAY = timedelta(milliseconds=1)

