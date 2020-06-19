import json
from flask import Response

def error_response(code, msg):
    body = json.dumps({ 'reason':msg })
    return Response(body, status=code, mimetype='application/json')

def success_response(code, data):
    body = json.dumps(data)
    return Response(body, status=code, mimetype='application/json')