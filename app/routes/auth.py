import json
from flask import Blueprint, request, jsonify
from flask import current_app as app
from utils.flask_utils import error_response

bp_auth = Blueprint("bp_auth", __name__)

# -- Endpoints

@bp_auth.route('/login', methods=['POST'], strict_slashes=False)
def login():
    body = request.get_json()
    if 'email' not in body or 'password' not in body:
        return error_response(400, 'Email or password is missing')

    auth_server = app.config['AUTH_SERVER']
    app.logger.debug("/login || Sending request to AuthServer %s ", str(body))
    response = auth_server.login(body)
    app.logger.debug("/login || Auth Server response %d %s ", response.status_code, response.data)
    return response


@bp_auth.route('/oauth2login', methods=['POST'], strict_slashes=False)
def oauth_login():
    body = request.get_json()
    if 'idToken' not in body:
        return error_response(400, 'Oauth data is missing')

    auth_server = app.config['AUTH_SERVER']
    app.logger.debug("/oauth2login || Sending request to AuthServer %s ", str(body))
    response = auth_server.oauth_login(body)
    app.logger.debug("/oauth2login || Auth Server response %d %s ", response.status_code, response.data)
    return response


@bp_auth.route('/register', methods=['POST'], strict_slashes=False)
def register():
    body = request.get_json()
    if 'username' not in body or 'password' not in body or 'email' not in body:
        return error_response(400, 'Fields are incomplete')

    auth_server = app.config['AUTH_SERVER']
    app.logger.debug("/register || Sending request to AuthServer %s ", str(body))
    response = auth_server.register(body)
    app.logger.debug("/register || Auth Server response %d %s ", response.status_code, response.data)
    return response
