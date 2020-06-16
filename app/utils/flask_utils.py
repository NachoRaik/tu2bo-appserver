import json
from flask import Response

def error_response(code, msg):
    body = json.dumps({ 'reason':msg })
    return Response(body, status=code, mimetype='application/json')