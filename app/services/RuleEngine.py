from datetime import date, datetime, timedelta

NO_REL_STATUS  = 'no-friends'
FRIENDS_STATUS = 'friends'
PENDING_STATUS = 'pending'
WAITING_STATUS = 'waiting-acceptance'
MAX_PONDERATED = 1
MIN_PONDERATED = 0
MIDDLE_PONDERATED = 0.5
NO_FRIENDS_MULT = 1
PENDING_MULT = 1.5
FRIENDS_MULT = 2
WEEK_BASE_POSITIVE = 7
BIG_VALUE_OF_FRIENDS = 100

class RuleEngine(object):

    def __init__(self, user_service, video_service):
        self.user_service = user_service
        self.video_service = video_service


    def friends_multiplicator(self, user_info, other_user_id):
        if (user_info["id"] == other_user_id):
            return NO_FRIENDS_MULT
        friendship_status = self.user_service.getFriendshipStatus(user_info["id"], other_user_id)
        if friendship_status == NO_REL_STATUS:
            return NO_FRIENDS_MULT
        elif friendship_status == PENDING_STATUS or friendship_status == WAITING_STATUS:
            return PENDING_MULT
        else:
            self.first_five += 1
            return FRIENDS_MULT

    def release_ponderator(self, video_date):
        today = datetime.today()
        video_date = datetime.strptime(video_date,'%m/%d/%y %H:%M:%S')
        delta_time = today - video_date
        return WEEK_BASE_POSITIVE - delta_time.days


    def user_upload_popoularity_ponderator(self, user_id):
        friends = self.user_service.getFriends(user_id)
        if len(friends) == 0:
            return MIN_PONDERATED
        elif len(friends) > MEDIAN_ACTIONS:
            return MAX_PONDERATED
        else:
            return MIDDLE_PONDERATED

    def first_five_ponderator(self):
        return -1*BIG_VALUE_OF_FRIENDS if self.first_five <= 4 else BIG_VALUE_OF_FRIENDS

    def prioritize_videos(self, user_info, videos):
        self.first_five = 0
        for video in videos:
            importance = 0
            importance += video["likes"]
            importance += self.release_ponderator(video["date"])
            importance += len(self.user_service.getFriends(video["user_id"]))
            importance *= self.friends_multiplicator(user_info, video["user_id"])
            importance += self.first_five_ponderator()
            video["importance"] = importance
        return sorted(videos, key= lambda k: k["importance"], reverse= True)
