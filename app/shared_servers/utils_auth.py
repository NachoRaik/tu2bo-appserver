from flask import Response
import json
import random

def init_db(db):
    db['email1'] = {'id': '1', 'email': 'email1', 'password': 'hash_password1', 'username': 'user1', 'profile': {'picture': 'picture1'}}
    db['email2'] = {'id': '2', 'email': 'email2', 'password': 'hash_password2', 'username': 'user2', 'profile': {'picture': 'picture2'}}
    db['email3'] = {'id': '3', 'email': 'email3', 'password': 'hash_password3', 'username': 'user3', 'profile': {'picture': 'picture3'}}
    db['email4'] = {'id': '4', 'email': 'email4', 'password': 'hash_password4', 'username': 'user4', 'profile': {'picture': 'picture4'}}

def get_hash(password):
    return 'hash_' + password
    
def get_token(email):
    return 'token_' + email
    
def get_email(token):
    prefix = 'token_'
    return token[len(prefix):]
    
def check_password_hash(password_to_check, password_saved):
    return password_saved == get_hash(password_to_check)
    
def get_fields(user):
    return {'id': user['id'], 'email': user['email'], 'username': user['username'], 'profile': user['profile']}
    
def validate(email):
    return '@' in email and '.' in email

def generate_code(email, db):
    db[email]['code'] = 1111
