import json
from flask import Blueprint, request, jsonify
from flask import current_app as app
from werkzeug.utils import secure_filename

from database.models.user import User

bp_users = Blueprint("bp_users", __name__)

required_post_video_fields = ['url', 'author', 'title', 'visibility', 'user_id']

# -- Endpoints

@bp_users.route('/users/<user_id>', methods=['GET'])
def get_user_profile(user_id):
    userdata = {
        'id': user_id,
        'username': 'exampleUser123',
        'videos': []
    }

    user_profile = jsonify(userdata)
    user_profile.status_code = 200
    return user_profile


@bp_users.route('/users/<user_id>/videos', methods=['GET', 'POST'])
def user_videos(user_id):
    media_server = app.config['MEDIA_SERVER']
    if request.method == 'POST':
        body = request.get_json()
        body['user_id'] = user_id
        for r in required_post_video_fields:
            if r not in body:
                return Response(json.dumps({'reason':'Fields are incomplete'}), status=400) 
        
        response = media_server.add_video(body)
        return response
    else:
        videos = media_server.get_user_videos(userId)
        return videos

