from datetime import datetime, timedelta
from flask import make_response, jsonify
from utils_auth import init_db, hash, get_token, get_email, check_password_hash, get_fields, validate

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
        self.db = {}
        init_db(self.db)

    def login(self, data):
        email = data['email']
        password = data['password']
        if email not in self.db:
            return make_response('Could not find user', 401)
        if not check_password_hash(password, db[email]['password']):
            return make_response('Password incorrect', 401)
        
        user = self.db[email]
        return jsonify({'token': get_token(email), 'status': 'OK', 'user': get_fields(user)})
    
    def generate_id(self):
        ids = []
        for value in self.db.values():
            id = value['id']
            ids.append(id)
        return max(ids)

    def register(self, data):
        email = data['email'] 
        username = data['username'] 
        password = data['password']
        hashed_password = hash(password)
        if email in self.db:
            return make_response('User already registered', 409)
        if not validate(email):
            return make_response('Invalid email address', 400)
        self.db[email] = {'id': self.generate_id(), 'email': email, 'password': hashed_password, 'username': username}
        return jsonify({'id': self.generate_id()})

    def get_users(self):
        return jsonify(list(map(lambda user: get_fields(user), self.db.values())))

    def authorize_user(self, data):
        token = data['token']
        email = get_email(token)
        if email not in self.db:
            return make_response("Invalid Token", 401, {'message':'Unauthorized'})
        user = self.db[email]
        return jsonify({'status':'OK', "user": get_fields(user)})
