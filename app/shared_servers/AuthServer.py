from datetime import datetime, timedelta
import json
import flask
from shared_servers.utils_auth import *

class AuthServer():

    def __init__(self, url = "localhost:3000"):
        self.url = "some_url"
        self.active_sessions = {}

    def login(self, data):
        raise Exception('Not implemented yet')

    def register(self, data):
        raise Exception('Not implemented yet')

    def get_users(self):
        raise Exception('Not implemented yet')

    def authorize_user(self, data):
        # Should request Auth Server to check if token is still valid
        raise Exception('Not implemented yet')

# --- Mocks

class MockAuthServer(AuthServer):
    def __init__(self):
        super().__init__()
        self.db = {}
        init_db(self.db)
        self.next_id = len(self.db)

    def login(self, data):
        email = data['email']
        password = data['password']
        if email not in self.db:
            return flask.Response('Could not find user', status=401)
        if not check_password_hash(password, self.db[email]['password']):
            return flask.Response('Password incorrect', status=401)
        
        user = self.db[email]
        response_data = {'token': get_token(email), 'user': get_fields(user)}
        return flask.Response(json.dumps(response_data), status=200)
    
    def generate_id(self):
        self.next_id += 1
        return self.next_id

    def register(self, data):
        email = data["email"] 
        username = data['username'] 
        password = data['password']
        hashed_password = get_hash(password)
        if email in self.db or any(user['username'] == username for user in self.db.values()):
            return flask.Response('User already registered', status=409)
        if not validate(email):
            return flask.Response('Invalid email address', status=400)
        id = self.generate_id()
        self.db[email] = {'id': id, 'email': email, 'password': hashed_password, 'username': username}
        response_data = {'id': id}
        return flask.Response(json.dumps(response_data), status=200)

    def get_users(self):
        response_data = list(map(lambda user: get_fields(user), self.db.values()))
        return flask.Response(json.dumps(response_data), status=200)

    def authorize_user(self, token): 
        email = get_email(token)
        if email not in self.db:
            return flask.Response("Invalid Token", status=401)
        user = self.db[email]
        response_data = {'user': get_fields(user)}
        return flask.Response(json.dumps(response_data), status=200)

