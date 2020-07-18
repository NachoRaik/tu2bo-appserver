import json
from flask import Blueprint, request, jsonify
from flask import current_app as app
from utils.flask_utils import error_response

def construct_blueprint(users_service):
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

    @bp_auth.route('/users/reset_password', methods=['POST'])
    def reset_password():
        return users_service.resetPassword(request.get_json())

    @bp_auth.route('/users/password', methods=['POST', 'GET'])
    def password():
        code = int(request.args.get('code'))
        email = request.args.get('email')
        if request.method == 'GET':
            return users_service.validateCode(code, email)
        return users_service.changePassword(code, email, request.get_json())

    return bp_auth