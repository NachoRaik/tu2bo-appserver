import json
from flask import Blueprint, request, jsonify
from flask import current_app as app
from werkzeug.utils import secure_filename

from database.models.user import User

bp_users = Blueprint("bp_users", __name__)

# -- Endpoints

@bp_users.route('/users/<userId>', methods=['GET'])
def get_user_profile(userId):
    userdata = {
        'id': userId,
        'username': 'exampleUser123',
        'videos': []
    }

    user_profile = jsonify(userdata)
    user_profile.status_code = 200
    return user_profile


@bp_users.route('/users/<userId>/videos', methods=['GET', 'POST'])
def user_videos(userId):
    if request.method == 'POST':
        # TODO: add call to mock
        raise Exception("Not implemented yet")
    else:
        media_server = app.config['MEDIA_SERVER']
        videos = media_server.get_author_videos(userId)
        return videos

