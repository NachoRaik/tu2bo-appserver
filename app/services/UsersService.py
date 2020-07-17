import json
from datetime import datetime
from database.daos.UserRelationDAO import UserRelationDAO

from database.models.friends import Friends
from database.models.pending_request import PendingRequest

NO_REL_STATUS  = 'no-friends'
FRIENDS_STATUS = 'friends'
PENDING_STATUS = 'pending'
WAITING_STATUS = 'waiting-acceptance'

class UsersService(object):
    def __init__(self, auth_server, db_handler=UserRelationDAO()):
        self.auth_server = auth_server
        self.db_handler = db_handler
    
    def getUserProfile(self, user_id):
        return self.auth_server.get_user_profile(user_id)
    
    def editUserProfile(self, user_id, data):
        return self.auth_server.edit_user_profile(user_id, data)

    def deleteUserProfile(self, user_id):
        user_id_friends = self.getFriends(user_id)
        for user_id_friend in user_id_friends:
            friends = Friends.objects.with_id(user_id_friend)
            friends.friends.remove(user_id)
            friends.save()

        user_id_friends_requests = self.getPendingRequests(user_id)
        for user_id_friend_request in user_id_friends_requests:
            friend_request = PendingRequest.objects.with_id(user_id_friend)
            friend_request.requests.remove(user_id)
            friend_request.save()

        if Friends.objects.with_id(user_id) != None:
            Friends.objects.with_id(user_id).delete()

        if PendingRequest.objects.with_id(user_id) != None:    
            PendingRequest.objects.with_id(user_id).delete()

        return self.auth_server.delete_user_profile(user_id)

    def fetchUsersNames(self, users):
        response_data = []
        for u_id in users:
            res = self.auth_server.get_user_profile(u_id)
            if res.status_code != 200:
                continue
            user_info = json.loads(res.get_data())
            response_data.append({'id': user_info['id'], 'username': user_info['username']})
        return response_data

    def getFriendshipStatus(self, requester_id, user_id):
        status = NO_REL_STATUS
        pending = PendingRequest.objects.with_id(user_id)
        friends = Friends.objects.with_id(user_id)
        my_pendings = PendingRequest.objects.with_id(requester_id)
        if pending is not None and requester_id in pending['requests']:
            status = PENDING_STATUS
        elif friends is not None and requester_id in friends['friends']:
            status = FRIENDS_STATUS
        elif my_pendings is not None and user_id in my_pendings['requests']:
            status = WAITING_STATUS
        return status

    def getPendingRequests(self, user_id):
        pending = PendingRequest.objects.with_id(user_id)
        return pending['requests'] if pending else []
    
    def getFriends(self, user_id):
        user_friends = Friends.objects.with_id(user_id)
        return user_friends['friends'] if user_friends else []

    def sendFriendRequest(self, requester_id, other_id):
        status = self.getFriendshipStatus(requester_id, other_id)
        if status != NO_REL_STATUS:
            return "Can't send friend request to user who is friend, pending or awaiting for acceptance"
        
        pending = PendingRequest.objects.with_id(other_id)
        if pending is None:
            pending = PendingRequest(user_id=other_id,requests=[])
        requests = pending['requests']
        requests.append(requester_id)
        pending.save()
        return None

    def acceptFriendRequest(self, accepter_id, other_id):
        status = self.getFriendshipStatus(accepter_id, other_id)
        if status != WAITING_STATUS:
            return "Can't accept friendship without request from the other user"
        
        dic = {accepter_id:other_id, other_id:accepter_id}
        for u in dic:
            friendship = Friends.objects.with_id(u)
            if friendship is None:
                friendship = Friends(user_id=u,friends=[])
            friends = friendship.friends
            if dic[u] not in friends:
                    friends.append(dic[u])
            friendship.save()
        pending = PendingRequest.objects.with_id(accepter_id)
        pending["requests"].remove(other_id)
        pending.save()
        return None
        
    def resetPassword(self, data):
        return self.auth_server.send_mail(data)
        
    def validateCode(self, code, email):
        return self.auth_server.validate_code(code, email)
        