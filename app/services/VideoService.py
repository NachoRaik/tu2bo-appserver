import json
from datetime import datetime
from database.daos.VideoInfoDAO import VideoInfoDAO
from utils.flask_utils import error_response

class VideoService(object):
    def __init__(self, media_server, db_handler=VideoInfoDAO()):
        self.media_server = media_server
        self.db_handler = db_handler
    
    def listVideos(self):
        res = self.media_server.get_videos()
        videos = json.loads(res.get_data())
        for video in videos:
            video['likes'] = len(self.db_handler.get_video_likes(video['id']))
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

    def addLikeToVideo(self, user_id, video_id, has_liked):
        likes = self.db_handler.change_user_like_on_video(video_id, user_id, has_liked)
        if likes is None:
            return error_response(404, 'Video not found')

        return None