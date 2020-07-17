import json
from flask import Blueprint, request, jsonify
from flask import current_app as app
from werkzeug.utils import secure_filename
from middlewares.security_wrapper import token_required
from utils.flask_utils import error_response, success_response

from database.models.video_info import VideoInfo
from database.models.pending_request import PendingRequest
from database.models.friends import Friends

from services.UsersService import UsersService
from services.VideoService import VideoService

def construct_blueprint(auth_server, media_server):
    bp_users = Blueprint("bp_users", __name__)
    
    users_service = UsersService(auth_server)
    video_service = VideoService(media_server)

    # -- Endpoints

    @bp_users.route('/users/<int:user_id>/friends', methods=['GET','POST'])
    @token_required
    def user_friends(user_info, user_id):
        if request.method == 'POST':
            err = users_service.acceptFriendRequest(int(user_info["id"]), user_id)
            if err:
                return error_response(400, err)
            return success_response(200, {"message": "Friend accepted successfully"})
        else:
            friends_ids = users_service.getFriends(user_id)
            app.logger.debug("/users/%d/friends || %d user profiles to fetch from Auth Server", user_id, len(friends_ids))
            response_data = users_service.fetchUsersNames(friends_ids)
            app.logger.debug("/users/%d/friends || Fetched %d user profiles", user_id, len(response_data))
            return success_response(200, response_data)

    @bp_users.route('/users/<int:user_id>/friend_request', methods=['POST'])
    @token_required
    def user_friend_request(user_info, user_id):
        app.logger.debug("/users/%s/friend_request || Requesting AuthServer for user profile", user_id)
        response = users_service.getUserProfile(user_id)
        if response.status_code != 200:
            return error_response(404, "Can't send friend request to inexistent user")

        err = users_service.sendFriendRequest(int(user_info['id']), user_id)
        if err:
            return error_response(400, err)
        return success_response(200, {"message": "Friendship request sent successfully"})

    @bp_users.route('/users/my_requests', methods=['GET'])
    @token_required
    def user_pending_requests(user_info):
        pending_ids = users_service.getPendingRequests(int(user_info["id"]))
        app.logger.debug("/users/my_requests || %d user profiles to fetch from Auth Server", len(pending_ids))
        response_data = users_service.fetchUsersNames(pending_ids)
        app.logger.debug("/users/my_requests || Fetched %d user profiles", len(response_data))
        return success_response(200, response_data)

    @bp_users.route('/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
    @token_required
    def user_profile(user_info, user_id):
        if request.method == 'GET':
            requester_id = int(user_info["id"])
            app.logger.debug("/users/%s || Requesting AuthServer for user profile", user_id)
            response = users_service.getUserProfile(user_id)
            if response.status_code != 200 or requester_id == user_id:
                return response
            
            profile_data = json.loads(response.get_data())
            profile_data['friendship_status'] = users_service.getFriendshipStatus(requester_id, user_id)
            return success_response(200, profile_data)
        if request.method == 'PUT':
            requester_id = int(user_info["id"])
            if requester_id != user_id:
                return error_response(403, 'Forbidden')
            return users_service.editUserProfile(user_id, request.get_json())
        if request.method == 'DELETE':
            if user_info != {} and not app.config['TESTING']: #It is only allowed to the webadmin to use
                return error_response(403, 'Forbidden')

            # Delete videos
            video_service.removeLikesFromUser(user_id)
            video_service.deleteCommentsFromUser(user_id)
            response = video_service.deleteVideos(user_id) 
            return response if response.status_code != 204 else users_service.deleteUserProfile(user_id)

    @bp_users.route('/users/reset_password', methods=['POST'])
    @token_required
    def reset_password(user_info):
        return users_service.resetPassword(request.get_json())

    return bp_users


