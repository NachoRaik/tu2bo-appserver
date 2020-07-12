from flask import Blueprint, Response, request, jsonify, make_response
from flask import current_app as app
from functools import wraps
import ast
import json

HEADER_ACCESS_TOKEN = 'access-token'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if HEADER_ACCESS_TOKEN not in request.headers:
            app.logger.debug("/token_required || No token header present")
            return Response(json.dumps({ 'reason':'Token not found' }), status=401, mimetype='application/json')
        token = request.headers[HEADER_ACCESS_TOKEN]

        if token == app.config['WEB_INTERFACE_KEY']:
            return f({}, *args, **kwargs)
            
        auth_server = app.config['AUTH_SERVER']
        app.logger.debug("[%s] Sending request to AuthServer /authorize", f.__name__)
        response = auth_server.authorize_user(token)
        app.logger.debug("[%s] Auth Server authorize response: %d %s ", f.__name__, response.status_code, response.data)
        if response.status_code != 200:
            return Response(json.dumps({ 'reason':'Invalid token' }), status=401, mimetype='application/json')
        user_info = ast.literal_eval(response.data.decode("UTF-8"))
        return f(user_info["user"], *args, **kwargs)
    
    return decorated
