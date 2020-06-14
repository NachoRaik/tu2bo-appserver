from flask import Blueprint, Response, request, jsonify
from flask import current_app as app

HEADER_ACCESS_TOKEN = 'access-token'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if HEADER_ACCESS_TOKEN not in in request.headers:
            return make_response("Token not found",401,{'message':'Unauthorized'})
        token = request.headers[HEADER_ACCESS_TOKEN]
        auth_server = app.config['AUTH_SERVER']

        app.logger.debug("/authorize || Sending request to AuthServer %s ", str(body))
        response = auth_server.authorize(token)
        app.logger.debug("/authorize || Auth Server response %d %s ", response.status_code, response.data)

        if (response.status_code == 401):
            return make_response("Invalid Token",401,{'message':'Unauthorized'})
        return f(*args, **kwargs)
    return decorated