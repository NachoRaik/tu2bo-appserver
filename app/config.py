import os

class Config(object):
    DEBUG = False
    TESTING = False
    MONGODB_SETTINGS = {
	    'db': 'appserver-db',
	    'host': 'mongodb://localhost/appserver-db'
    }

class ProductionConfig(Config):
    DATABASE_URI = 'mysql://user@localhost/foo'

class DevelopmentConfig(Config):
    TESTING = True