import json
from flask import Blueprint, request, jsonify
from flask import current_app as app
from werkzeug.utils import secure_filename
from security.security import token_required
from utils.flask_utils import error_response

from database.models.video_info import VideoInfo

bp_users = Blueprint("bp_users", __name__)

required_post_video_fields = ['url', 'author', 'title', 'visibility', 'user_id']

# -- Endpoints

@bp_users.route('/users/<user_id>', methods=['GET'])
def get_user_profile(user_id):
    raise Exception('Not implemented yet')

@bp_users.route('/users/<int:user_id>/videos', methods=['GET', 'POST'])
@token_required
def user_videos(user_info, user_id):
    media_server = app.config['MEDIA_SERVER']
    if request.method == 'POST':
        if int(user_info["id"]) != user_id:
            return error_response(403, 'Forbidden')
        body = request.get_json()
        body['user_id'] = user_id
        for r in required_post_video_fields:
            if r not in body:
                return error_response(400, 'Fields are incomplete')

        response = media_server.add_video(body)
        if response.status_code == 201:
            response_data = json.loads(response.get_data())
            video_id = response_data['id']
            video_info = VideoInfo(video_id=video_id).save()
        return response
    else:
        videos = media_server.get_user_videos(user_id)
        return videos
