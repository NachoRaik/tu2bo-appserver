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

def generate_response_list(_list):
    auth_server = app.config['AUTH_SERVER']
    response_data = []
    for p_id in _list:
        response = auth_server.get_user_profile(p_id)
        if response.status_code != 200:
            continue
        pending_info = json.loads(response.get_data())
        response_data.append({"id":pending_info["id"], "username":pending_info["username"]})
    return response_data

def add_both_friends_list(user1,user2):
    dic = {user1:user2, user2:user1}
    for u in dic:
        friendship = Friends.objects.with_id(u)
        if friendship is None:
            friendship = Friends(user_id=u,friends=[])
        friends = friendship.friends
        if dic[u] not in friends:
                friends.append(dic[u])
        friendship.save()

@bp_users.route('/users/<user_id_request>/friends', methods=['GET','POST'])
@token_required
def user_friends(user_info,user_id_request):
    if request.method == 'POST':
        user_id = int(user_info["id"])
        user_id_request = int(user_id_request)
        pending = PendingRequest.objects.with_id(user_id)
        if (pending is None) or (user_id_request not in pending["requests"]):
            return  error_response(400,"Can't accept friendship without request")
        my_requests = pending["requests"]
        my_requests.remove(user_id_request)
        pending.save()
        add_both_friends_list(user_id,user_id_request)
        return success_response(200, {"message": "Friend accepted successfully"} )
    else:
        user_id_request = int(user_id_request)
        friendship = Friends.objects.with_id(user_id_request)
        if friendship is None:
            return error_response(404, "User has not friends")
        app.logger.debug("/users/%s/friends || Fetching %d user profiles from AuthServer", user_id_request, len(friendship.friends))
        response_data = generate_response_list(friendship.friends)
        app.logger.debug("/users/%s/friends || Fetched %d user profiles", user_id_request, len(response_data))
        return success_response(200,response_data)

@bp_users.route('/users/<user_id_request>/friend_request', methods=['POST'])
@token_required
def user_friend_request(user_info,user_id_request):
    auth_server = app.config['AUTH_SERVER']
    app.logger.debug("/users/%s || Sending request to AuthServer",user_id_request)
    response = auth_server.get_user_profile(user_id_request)
    app.logger.debug("/users/%s || Auth Server response %d %s ", user_id_request, response.status_code, response.data)
    if response.status_code != 200:
        return error_response(404, "Can't send friend request to inexistent user")

    friendship = Friends.objects.with_id(user_info['id'])
    if friendship is not None and int(user_id_request) in friendship.friends:
        return error_response(400, 'Already friends')
    my_pendings = PendingRequest.objects.with_id(user_info['id'])
    if my_pendings is not None and int(user_id_request) in my_pendings.requests:
        return error_response(400, 'Already pending')

    pending = PendingRequest.objects.with_id(user_id_request)
    if pending is None:
        pending = PendingRequest(user_id=user_id_request,requests=[])
    requests = pending.requests
    if user_info['id'] not in requests:
        requests.append(user_info['id'])
    pending.save()
    return success_response(200,{"message":"Request sent successfully"})

@bp_users.route('/users/my_requests', methods=['GET'])
@token_required
def user_pending_requests(user_info):
    auth_server = app.config['AUTH_SERVER']
    user_id = user_info["id"]
    pending = PendingRequest.objects.with_id(user_id)
    if pending is None:
        return success_response(200,[])
    app.logger.debug("/users/my_requests || Fetching %d user profiles from AuthServer", len(pending["requests"]))
    response_data = generate_response_list(pending["requests"])
    app.logger.debug("/users/my_requests || Fetched %d user profiles", len(response_data))
    return success_response(200,response_data)

@bp_users.route('/users/<user_id_request>', methods=['GET'])
@token_required
def get_user_profile(user_info, user_id_request):
    auth_server = app.config['AUTH_SERVER']
    app.logger.debug("/users/%s || Sending request to AuthServer",user_id_request)
    response = auth_server.get_user_profile(user_id_request)
    app.logger.debug("/users/%s || Auth Server response %d %s ",user_id_request, response.status_code, response.data)

    if user_id_request == user_info["id"] or response.status_code != 200:
        return response

    user_id = int(user_info["id"])
    user_id_request = int(user_id_request)
    status = 'no-friends'
    pending = PendingRequest.objects.with_id(user_id_request)
    friends = Friends.objects.with_id(user_id_request)
    my_pendings = PendingRequest.objects.with_id(user_id)
    if pending is not None and user_id in pending['requests']:
        status = 'pending'
    elif friends is not None and user_id in friends['friends']:
        status = 'friends'
    elif my_pendings is not None and user_id_request in my_pendings['requests']:
        status = 'waiting-acceptance'
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

@bp_users.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def edit_user_profile(user_info, user_id):
    auth_server = app.config['AUTH_SERVER']
    if int(user_info["id"]) != user_id:
            return error_response(403, 'Forbidden')
    body = request.get_json()
    if 'picture' not in body:
        return error_response(400, 'Fields are incomplete')
    
    response = auth_server.edit_user_profile(user_id, body)
    return response