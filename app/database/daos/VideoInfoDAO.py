from database.models.comment import Comment
from database.models.video_info import VideoInfo

class VideoInfoDAO(object):
    def new_video_registered(self, video_id):
        video_info = VideoInfo(video_id=video_id)
        video_info.save()
        return video_info

    def get_video_likes(self, video_id):
        video_info = VideoInfo.objects.get(video_id=video_id)
        return video_info.likes

    def change_user_like_on_video(self, video_id, user_id, has_liked):
        video_info = VideoInfo.objects.with_id(video_id)
        if not video_info:
            return None
        
        likes = video_info.likes
        if not has_liked and user_id in likes:
            likes.remove(user_id)
        if has_liked and not user_id in likes:
            likes.append(user_id)
        video_info.save()
        return likes

    def get_video_comments(self, video_id):
        video_info = VideoInfo.objects.with_id(video_id)
        return video_info.comments if video_info else None

    def add_video_comment(self, video_id, user_id, fields):
        video_info = VideoInfo.objects.with_id(video_id)
        if not video_info:
            return None
        
        author, content, timestamp = fields['author'], fields['content'], fields['timestamp']
        comment = Comment(author=author, user_id=user_id, content=content, timestamp=timestamp)
        video_info.comments.append(comment)
        video_info.save()
        return comment
    
    def delete_video_info(self, video_id):
        video_info = VideoInfo.objects.with_id(video_id)
        video_info.delete()

    def delete_comment(self, video_id, comment_id):
        video_info = VideoInfo.objects.with_id(video_id)
        comments = video_info.comments
        comment_to_remove = None
        for comment in comments:
            if comment.comment_id == comment_id:
                comment_to_remove = comment
        comments.remove(comment_to_remove)
        video_info.save()