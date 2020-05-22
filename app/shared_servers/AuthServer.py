from datetime import datetime, timedelta
import json
import flask
from shared_servers.utils_auth import init_db, get_hash, get_token, get_email, get_fields, validate, check_password_hash

class AuthServer():

    def __init__(self, url = "localhost:3000"):
        self.url = "some_url"
        self.active_sessions = {}

    def login(self, credentials, password):
        raise Exception('Not implemented yet')

    def register(self, registration_parsed_data):
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
        self.db = {}
        init_db(self.db)

    def login(self, data):
        parsed_data = json.loads(data)
        email = parsed_data['email']
        password = parsed_data['password']
        if email not in self.db:
            return flask.Response('Could not find user', status=401)
        if not check_password_hash(password, self.db[email]['password']):
            return flask.Response('Password incorrect', status=401)
        
        user = self.db[email]
        response_data = {'token': get_token(email), 'status': 'OK', 'user': get_fields(user)}
        return flask.Response(json.dumps(response_data), status=200)
    
    def generate_id(self):
        ids = list(map(lambda user: int(user['id']), self.db.values()))
        return max(ids) + 1

    def register(self, data):
        parsed_data = json.loads(data)
        email = parsed_data["email"] 
        username = parsed_data['username'] 
        password = parsed_data['password']
        hashed_password = get_hash(password)
        usernames = list(map(lambda user: user['username'], self.db.values()))
        if email in self.db or username in usernames:
            return flask.Response('User already registered', status=409)
        if not validate(email):
            return flask.Response('Invalid email address', status=400)
        self.db[email] = {'id': self.generate_id(), 'email': email, 'password': hashed_password, 'username': username}
        response_data = {'id': self.generate_id()}
        return flask.Response(json.dumps(response_data), status=200)

    def get_users(self):
        response_data = list(map(lambda user: get_fields(user), self.db.values()))
        return flask.Response(json.dumps(response_data), status=200)

    def authorize_user(self, data):
        parsed_data = json.loads(data)
        token = parsed_data['token']
        email = get_email(token)
        if email not in self.db:
            return flask.Response("Invalid Token", status=401)
        user = self.db[email]
        response_data = {'status':'OK', 'user': get_fields(user)}
        return flask.Response(json.dumps(response_data), status=200)

