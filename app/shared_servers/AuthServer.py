from datetime import datetime, timedelta
import json
import flask
import requests
from shared_servers.utils_auth import *
from utils.flask_utils import error_response, success_response, make_flask_response

class AuthServer():

    def __init__(self, url = 'no-host'):
        self.url = url

    def login(self, body):
        response = requests.post(self.url + '/users/login', json=body)
        return make_flask_response(response)

    def oauth_login(self, body):
        response = requests.post(self.url + '/users/oauth2login', json=body)
        return make_flask_response(response)

    def register(self, body):
        response = requests.post(self.url + '/users/register', json=body)
        return make_flask_response(response)

    def get_users(self):
        response = requests.get(self.url + '/users')
        return make_flask_response(response)

    def authorize_user(self, token):
        headers = {'access-token': token}
        response = requests.post(self.url + '/users/authorize', headers=headers)
        return make_flask_response(response)

    def get_user_profile(self,user_id_request):
        response = requests.get(self.url + '/users/' + str(user_id_request))
        return make_flask_response(response)

    def edit_user_profile(self, user_id, body):
        response = requests.put(self.url + '/users/{}'.format(user_id), json=body)
        return make_flask_response(response)

    def delete_user_profile(self, user_id):
        response = requests.delete(self.url + '/users/' + str(user_id))
        return make_flask_response(response)

    def __str__(self):
        return "url => {}".format(self.url)

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
            return error_response(401, 'Wrong credentials')
        if not check_password_hash(password, self.db[email]['password']):
            return error_response(401, 'Wrong credentials')

        user = self.db[email]
        response_data = {'token': get_token(email), 'user': get_fields(user)}
        return success_response(200, response_data)

    def generate_id(self):
        self.next_id += 1
        return self.next_id

    def register(self, data):
        email = data["email"]
        username = data['username']
        password = data['password']
        hashed_password = get_hash(password)
        if email in self.db or any(user['username'] == username for user in self.db.values()):
            return error_response(409, 'User already registered')
        if not validate(email):
            return error_response(400, 'Invalid email address')
        id = self.generate_id()
        self.db[email] = {'id': id, 'email': email, 'password': hashed_password, 'username': username, 'profile':{}}
        response_data = {'id': id}
        return success_response(200, response_data)

    def get_users(self):
        response_data = list(map(lambda user: get_fields(user), self.db.values()))
        return success_response(200, response_data)

    def authorize_user(self, token):
        email = get_email(token)
        if email not in self.db:
            return error_response(401, 'Invalid Token')
        user = self.db[email]
        response_data = {'user': get_fields(user)}
        return success_response(200, response_data)

    def get_user_profile(self, user_id_request):
        for v in self.db.values():
            if v['id'] == str(user_id_request):
                return success_response(200,get_fields(v))
        return error_response(404, "User not found")

    def edit_user_profile(self, user_id, body):
        for v in self.db.values():
            if v['id'] == str(user_id):
                v['profile'] = body
                return success_response(200, get_fields(v))
        return error_response(404, "User not found")

    def delete_user_profile(self, user_id):
        if not any(int(user['id']) == user_id for user in self.db.values()):
            return error_response(404, 'User not found')

        self.db = {email:user for email, user in self.db.items() if int(user['id']) != user_id}
        return flask.Response('', status=204)

    def oauth_login(self, data):
        email = data["idToken"].split("_")[1]
        if email not in self.db:
            id = self.generate_id()
            username = email.split('@')[0]
            username = "o_" + username
            self.db[email] = {'id': id, 'email': email, 'username': username, 'profile':{}}
        user = self.db[email]
        response_data = {'token': get_token(email), 'user': get_fields(user)}
        return success_response(200, response_data)
