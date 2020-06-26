import json
from datetime import datetime
from database.models.comment import Comment
from database.models.video_info import VideoInfo
from utils.flask_utils import error_response

class VideoService(object):
    def __init__(self, media_server, db_handler=None):
        self.media_server = media_server
        self.db_handler = db_handler
    
    def listVideos(self):
        res = self.media_server.get_videos()
        videos = json.loads(res.get_data())
        for video in videos:
            video_id = video['id']
            video_info = VideoInfo.objects.get(video_id=video_id)
            video['likes'] = len(video_info.likes)
        return videos
    
    def getVideo(self, user_id, video_id):
        res = self.media_server.get_video(video_id)
        if res.status_code != 200:
            return None, res
        
        video = json.loads(res.get_data())
        video_id = video['id']
        video_info = VideoInfo.objects.get(video_id=video_id)
        video['likes'] = len(video_info.likes)
        video['user_related_info'] = {'is_liked': user_id in video_info.likes}
        return video, None

    def addCommentToVideo(self, user_id, video_id, fields):
        video = VideoInfo.objects.with_id(video_id)
        if video is None:
            return None, error_response(404, 'Video not found')

        author, content, timestamp = fields['author'], fields['content'], fields['timestamp']
        comment = Comment(author=author, user_id=user_id, content=content, timestamp=timestamp)
        video_info = VideoInfo.objects.get(video_id=video_id)
        video_info.comments.append(comment)
        video_info.save()

        result = {'comment_id': comment.comment_id, 'user_id': user_id, 'author': author, 'content': content, 'timestamp': timestamp}
        return result, None

    def getCommentsFromVideo(self, video_id):
        video = VideoInfo.objects.with_id(video_id)
        if video is None:
            return None, error_response(404, 'Video not found')

        video_info = VideoInfo.objects.get(video_id=video_id)
        comments = video_info.comments
        result = []
        for comment in comments:
            result.append({'comment_id': comment.comment_id, 'user_id': comment.user_id, 'author': comment.author,
            'content': comment.content, 'timestamp': comment.timestamp})
        result.sort(key=lambda d: datetime.strptime(d['timestamp'], '%m/%d/%y %H:%M:%S'))
        return result, None

    def addLikeToVideo(self, user_id, video_id, liked):
        video = VideoInfo.objects.with_id(video_id)
        if video is None:
            return error_response(404, 'Video not found')

        video_info = VideoInfo.objects.get(video_id=video_id)
        likes = video_info.likes
        if not liked and user_id in likes:
            likes.remove(user_id)
        if liked and not user_id in likes:
            likes.append(user_id)
        video_info.save()
        return None