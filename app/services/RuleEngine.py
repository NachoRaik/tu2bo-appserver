from datetime import date, datetime, timedelta


NO_REL_STATUS  = 'no-friends'
FRIENDS_STATUS = 'friends'
PENDING_STATUS = 'pending'
WAITING_STATUS = 'waiting-acceptance'
MAX_PONDERATED = 1
MIN_PONDERATED = 0
MIDDLE_PONDERATED = 0.5
MEDIAN_ACTIONS = 10
TOTAL = 4

class RuleEngine(object):

    def __init__(self, user_service, video_service):
        self.user_service = user_service
        self.video_service = video_service

    def friends_ponderator(self, user_info, other_user_id):
        if (user_info["id"] == other_user_id):
            return MIN_PONDERATED
        friendship_status = self.user_service.getFriendshipStatus(user_info["id"], other_user_id)
        if friendship_status == NO_REL_STATUS:
            return MIN_PONDERATED
        elif friendship_status == PENDING_STATUS or friendship_status == WAITING_STATUS:
            return MIDDLE_PONDERATED
        else:
            return MAX_PONDERATED

    def release_ponderator(self, video_date):
        today = datetime.today()
        video_date = datetime.strptime(video_date,'%m/%d/%y %H:%M:%S')
        if (today - timedelta(days=2)) < video_date:
            return MAX_PONDERATED
        elif (today - timedelta(weeks=1)) < video_date:
            return MIDDLE_PONDERATED
        else:
            return MIN_PONDERATED

    def video_popularity_ponderator(self, likes):
        if likes == 0:
            return MIN_PONDERATED
        elif likes > MEDIAN_ACTIONS:
            return MAX_PONDERATED
        else:
            return MIDDLE_PONDERATED

    def user_upload_popoularity_ponderator(self, user_id):
        friends = self.user_service.getFriends(user_id)
        if len(friends) == 0:
            return MIN_PONDERATED
        elif len(friends) > MEDIAN_ACTIONS:
            return MAX_PONDERATED
        else:
            return MIDDLE_PONDERATED

    def listVideos(self, user_info):
        videos = self.video_service.listVideos()
        for video in videos:
            importance = 0
            importance += self.friends_ponderator(user_info, video["user_id"])
            importance += self.release_ponderator(video["date"])
            importance += self.video_popularity_ponderator(video["likes"])
            importance += self.user_upload_popoularity_ponderator(video["user_id"])
            video["importance"] = importance
        return sorted(videos, key= lambda k: k["importance"], reverse= True)
