import json
from flask import Blueprint, Response, request, jsonify
from flask import current_app as app

bp_auth = Blueprint("bp_auth", __name__)

# -- Endpoints

@bp_auth.route('/login', methods=['POST'], strict_slashes=False)
def login():
    body = request.get_json()
    if 'email' not in body or 'password' not in body:
        return Response(json.dumps({'reason':'Email or password is missing'}), status=400)

    auth_server = app.config['AUTH_SERVER']
    app.logger.debug("/register || Sending request to AuthServer %s ", str(body))
    response = auth_server.login(body)
    app.logger.debug("/login || Auth Server response %d %s ", response.status_code, response.data)
    return response


@bp_auth.route('/register', methods=['POST'], strict_slashes=False)
def register():
    body = request.get_json()
    if 'username' not in body or 'password' not in body or 'email' not in body:
        return Response(json.dumps({'reason':'Fields are incomplete'}), status=400)

    auth_server = app.config['AUTH_SERVER']
    app.logger.debug("/register || Sending request to AuthServer %s ", str(body))
    response = auth_server.register(body)
    app.logger.debug("/register || Auth Server response %d %s ", response.status_code, response.data)
    return response
