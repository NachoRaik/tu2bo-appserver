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

def construct_blueprint(user_service):
    bp_users = Blueprint("bp_users", __name__)

    service = user_service

    # -- Endpoints

    @bp_users.route('/users/<int:user_id>/friends', methods=['GET','POST'])
    @token_required
    def user_friends(user_info, user_id):
        if request.method == 'POST':
            err = service.acceptFriendRequest(int(user_info["id"]), user_id)
            if err:
                return error_response(400, err)
            return success_response(200, {"message": "Friend accepted successfully"})
        else:
            friends_ids = service.getFriends(user_id)
            app.logger.debug("/users/%d/friends || %d user profiles to fetch from Auth Server", user_id, len(friends_ids))
            response_data = service.fetchUsersNames(friends_ids)
            app.logger.debug("/users/%d/friends || Fetched %d user profiles", user_id, len(response_data))
            return success_response(200, response_data)

    @bp_users.route('/users/<int:user_id>/friend_request', methods=['POST'])
    @token_required
    def user_friend_request(user_info, user_id):
        app.logger.debug("/users/%s/friend_request || Requesting AuthServer for user profile", user_id)
        response = service.getUserProfile(user_id)
        if response.status_code != 200:
            return error_response(404, "Can't send friend request to inexistent user")

        err = service.sendFriendRequest(int(user_info['id']), user_id)
        if err:
            return error_response(400, err)
        return success_response(200, {"message": "Friendship request sent successfully"})

    @bp_users.route('/users/my_requests', methods=['GET'])
    @token_required
    def user_pending_requests(user_info):
        pending_ids = service.getPendingRequests(int(user_info["id"]))
        app.logger.debug("/users/my_requests || %d user profiles to fetch from Auth Server", len(pending_ids))
        response_data = service.fetchUsersNames(pending_ids)
        app.logger.debug("/users/my_requests || Fetched %d user profiles", len(response_data))
        return success_response(200, response_data)

    @bp_users.route('/users/<int:user_id>', methods=['GET', 'PUT'])
    @token_required
    def user_profile(user_info, user_id):
        requester_id = int(user_info["id"])
        if request.method == 'GET':
            app.logger.debug("/users/%s || Requesting AuthServer for user profile", user_id)
            response = service.getUserProfile(user_id)
            if response.status_code != 200 or requester_id == user_id:
                return response

            profile_data = json.loads(response.get_data())
            profile_data['friendship_status'] = service.getFriendshipStatus(requester_id, user_id)
            return success_response(200, profile_data)
        else:
            if requester_id != user_id:
                return error_response(403, 'Forbidden')
            return service.editUserProfile(user_id, request.get_json())

    return bp_users
