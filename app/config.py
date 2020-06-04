import os

from shared_servers.AuthServer import AuthServer, MockAuthServer
from shared_servers.MediaServer import MediaServer, MockMediaServer

class Config(object):
    DEBUG = False
    TESTING = False
    AUTH_SERVER = AuthServer()
    MEDIA_SERVER = MediaServer()
    MONGODB_SETTINGS = {
	    'db': 'appserver-db',
	    'host': 'mongodb://appserver-db:27017/appserver-db'
    }

class ProductionConfig(Config):
    DATABASE_URI = 'mysql://user@localhost/foo'
    AUTH_SERVER = AuthServer()

class DevelopmentConfig(Config):
    TESTING = True
    AUTH_SERVER = MockAuthServer()
    MEDIA_SERVER = MockMediaServer()

