from flask import request
from flask import current_app as app
from functools import wraps
from utils.flask_utils import error_response

def body_validation(required_fields, msg='Fields are incomplete', involved_methods=['POST', 'PUT']):
    def _body_validation(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.method in involved_methods:
                body = request.get_json()
                if not body or any(field not in body for field in required_fields):
                    app.logger.debug("[Body Validation] %s failed because %s", f.__name__, msg)
                    return error_response(400, msg)
            return f(*args, **kwargs)
        
        return decorated
    return _body_validation
