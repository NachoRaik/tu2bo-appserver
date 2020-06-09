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

    def __repr__(self):
        printable_fields = ['DEBUG', 'AUTH_SERVER', 'MEDIA_SERVER']
        fields = self.__class__.__dict__
        output = ""
        for x in printable_fields: 
            output+="\n\t{} = {}".format(x, fields.get(x, "Not setted"))
        return output 

class ProductionConfig(Config):
    DEBUG = False
    AUTH_SERVER = AuthServer(url = os.getenv('AUTH_URI', 'localhost:5000'))
    MEDIA_SERVER = MockMediaServer()

class DevelopmentConfig(Config):
    TESTING = True
    AUTH_SERVER = MockAuthServer()
    MEDIA_SERVER = MockMediaServer()

