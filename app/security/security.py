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
        auth_server = app.config['AUTH_SERVER']
        app.logger.debug("/authorize || Sending request to AuthServer")
        response = auth_server.authorize_user(token)
        app.logger.debug("/authorize || Auth Server response %d %s ", response.status_code, response.data)
        if (response.status_code in (400, 401, 404)):
            return Response(json.dumps({ 'reason':'Invalid token' }), status=401, mimetype='application/json')
        user_info = ast.literal_eval(response.data.decode("UTF-8"))
        return f(user_info["user"],*args, **kwargs)
    
    return decorated
