import json
from datetime import datetime
from database.daos.VideoInfoDAO import VideoInfoDAO
from utils.flask_utils import error_response, success_response

class VideoService(object):
    def __init__(self, media_server, db_handler=VideoInfoDAO()):
        self.media_server = media_server
        self.db_handler = db_handler
    
    def addNewVideo(self, user_id, fields):
        fields['user_id'] = user_id
        res = self.media_server.add_video(fields)
        if res.status_code == 201:
            response_data = json.loads(res.get_data())
            video_id = response_data['id']
            video_info = self.db_handler.new_video_registered(video_id)
        return res

    def deleteVideo(self, video_id):
        res = self.media_server.delete_video(video_id)
        if res.status_code == 200:
            self.db_handler.delete_video_info(video_id)
        return res
    
    def deleteVideos(self, user_id):
        response = self.listVideosFromUser(user_id)
        if response.status_code != 200:
            return response
        videos_data = json.loads(response.get_data())
        for video in videos_data:
            video_id = video['id']
            response = self.deleteVideo(video_id)
            if response.status_code != 204:
                return response
        return success_response(204, 'Videos deleted successfully')

    def editVideo(self, video_id, data):
        return self.media_server.edit_video(video_id, data)

    def listVideosFromUser(self, user_id, are_friends=True):
        video_searching = {}
        if not are_friends: 
            video_searching['visibility'] = 'public'
        return self.media_server.get_user_videos(user_id, video_searching)

    def listVideos(self, friends_ids=None):
        res = self.media_server.get_videos()
        videos = json.loads(res.get_data())
        for video in videos:
            video['likes'] = len(self.db_handler.get_video_likes(video['id']))
        videos_to_delete = [video for video in videos 
                            if friends_ids != None and video['user_id'] not in friends_ids 
                            and video['visibility'] != 'public'
                        ] 
        for video in videos_to_delete: 
            videos.remove(video)
        return videos
    
    def getVideo(self, user_id, video_id):
        res = self.media_server.get_video(video_id)
        if res.status_code != 200:
            return None, res
        
        video = json.loads(res.get_data())
        likes = self.db_handler.get_video_likes(video['id'])
        video['likes'] = len(likes)
        video['user_related_info'] = {'is_liked': user_id in likes}
        return video, None

    def addCommentToVideo(self, user_id, video_id, fields):
        comment = self.db_handler.add_video_comment(video_id, user_id, fields)
        if comment is None:
            return None, error_response(404, 'Video not found')

        result = comment.to_mongo().to_dict()
        result['comment_id'] = result['_id']
        del result['_id']
        return result, None

    def getCommentsFromVideo(self, video_id):
        comments = self.db_handler.get_video_comments(video_id)
        if comments is None:
            return None, error_response(404, 'Video not found')

        result = []
        for comment in comments:
            result.append({'comment_id': comment.comment_id, 'user_id': comment.user_id, 'author': comment.author,
                           'content': comment.content, 'timestamp': comment.timestamp})
        result.sort(key=lambda d: datetime.strptime(d['timestamp'], '%m/%d/%y %H:%M:%S'))
        return result, None

    def deleteCommentsFromUser(self, user_id):
        res = self.media_server.get_videos()
        videos = json.loads(res.get_data())
        video_ids = [video['id'] for video in videos]

        for video_id in video_ids:
            self.db_handler.delete_comments_from_user(video_id, user_id)
    
    def addLikeToVideo(self, user_id, video_id, has_liked):
        likes = self.db_handler.change_user_like_on_video(video_id, user_id, has_liked)
        if likes is None:
            return error_response(404, 'Video not found')

        return None

    def removeLikesFromUser(self, user_id):
        has_liked = False
        videos = self.listVideos()
        for video in videos:
            video_id = video['id']
            likes = self.db_handler.change_user_like_on_video(video_id, user_id, has_liked)
