from datetime import datetime, timedelta
import flask
import json
import requests

class AuthServer():

    def __init__(self, url = "localhost:3000"):
        self.url = "some_url"
        self.active_sessions = {}

    def login(self, credentials, password):
        raise Exception('Not implemented yet')

    def register(self, registration_data):
        raise Exception('Not implemented yet')

    def validate_token(self, token):
        if self.token_active(token):
            return True
        
        # Should request Auth Server to check if it's still valid
        raise Exception('Not implemented yet')

    def token_active(self, token):
        return token in self.active_sessions and self.active_sessions[token]["ttl"] > datetime.now()


# --- Mocks

class MockAuthServer(AuthServer):

    def __init__(self):
        super().__init__()
        self.active_sessions['token1'] = { 'username': 'user1', 'ttl': datetime.now() + timedelta(days=3) }
        self.active_sessions['token2'] = { 'username': 'user2', 'ttl': datetime.now() + timedelta(days=3) }
        self.active_sessions['token3'] = { 'username': 'user3', 'ttl': datetime.now() + timedelta(days=3) }

    def login(self, credentials, password):
        for k, v in self.active_sessions.items():
            if v['username'] == credentials:
                response_data = { 'userId': '1', 'token': k }
                return flask.Response(json.dumps(response_data), status=200)

        return flask.Response('', status=400)

    def register(self, registration_data):
        return flask.Response('User registered', status=201)

    def validate_token(self, token):
        return token_active(token)