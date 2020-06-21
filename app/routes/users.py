import json
from flask import Blueprint, request, jsonify
from flask import current_app as app
from werkzeug.utils import secure_filename
from security.security import token_required
from utils.flask_utils import error_response,success_response

from database.models.video_info import VideoInfo
from database.models.pending_request import PendingRequest
from database.models.friends import Friends

bp_users = Blueprint("bp_users", __name__)

required_post_video_fields = ['url', 'author', 'title', 'visibility', 'user_id']

# -- Endpoints

@bp_users.route('/users/my_requests', methods=['GET'])
@token_required
def user_pending_requests(user_info):
    auth_server = app.config['AUTH_SERVER']
    user_id = user_info["id"]
    pending = PendingRequest.objects.with_id(user_id)
    if pending is None:
        error_response(404,'User pending requests not found')

    response_data = []
    pending_list = pending['requests']
    for p_id in pending_list:
        app.logger.debug("/userId=%s || Sending request to AuthServer",p_id)
        response = auth_server.get_user_profile(p_id)
        app.logger.debug("/userId=%s || Auth Server response %d %s ", p_id, response.status_code, response.data)
        if response.status_code != 200: continue
        pending_info = json.loads(response.get_data())
        response_data.append({"id":pending_info["id"], "username":pending_info["username"]})
    return success_response(200,response_data)


@bp_users.route('/users/<user_id_request>', methods=['GET'])
@token_required
def get_user_profile(user_info, user_id_request):
    auth_server = app.config['AUTH_SERVER']
    app.logger.debug("/userId=%s || Sending request to AuthServer",user_id_request)
    response = auth_server.get_user_profile(user_id_request)
    app.logger.debug("/userId=%s || Auth Server response %d %s ",user_id_request, response.status_code, response.data)

    if user_id_request == user_info["id"] or response.status_code != 200:
        return response

    status = 'no-friends'
    pending = PendingRequest.objects.with_id(user_info["id"])
    if pending is not None:
        pending_list_users = pending['requests']
        if user_id_request in pending_list_users:
            status = 'pending'
    friends = Friends.objects.with_id(user_info["id"])
    if friends is not None:
        friends_list = friends['friends']
        if user_id_request in friends_list:
            status = 'friends'
    response_data = json.loads(response.get_data())
    response_data['friendship_status'] = status
    return success_response(200, response_data)

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
