import json
from flask import Response

def error_response(code, msg):
    body = json.dumps({ 'reason':msg })
    return Response(body, status=code, mimetype='application/json')

def success_response(code, data):
    body = json.dumps(data)
    return Response(body, status=code, mimetype='application/json')

def make_flask_response(req_response):
    headers = dict(req_response.raw.headers)
    return Response(req_response.content, status=req_response.status_code, headers=headers)