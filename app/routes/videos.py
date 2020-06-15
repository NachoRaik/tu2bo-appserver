import json
from flask import Blueprint, request, Response
from flask import current_app as app
from werkzeug.utils import secure_filename
from database.models.video_info import VideoInfo
from database.models.comment import Comment
from datetime import datetime

bp_videos = Blueprint("bp_videos", __name__)

required_post_comment_fields = ['author', 'content', 'timestamp']
required_put_likes_field = 'liked'

# -- Endpoints

@bp_videos.route('/videos', methods=['GET'])
def home_videos():
    media_server = app.config['MEDIA_SERVER']
    res = media_server.get_videos()
    res_json = json.loads(res.get_data())
    for video in res_json:
        user_id = int(video['user_id'])
        video_id = int(video['id'])
        video_info = VideoInfo.objects.get(video_id=video_id)
        video['likes'] = len(video_info.likes)
        video['user_related_info'] = {'is_liked': user_id in video_info.likes}
    return Response(json.dumps(res_json), status=200) 

def add_comment_to_video(request, video_id):
    body = request.get_json()
    
    if any(r not in body for r in required_post_comment_fields):
        return Response(json.dumps({'reason':'Fields are incomplete'}), status=400) 

    video = VideoInfo.objects.with_id(video_id)
    if video is None:
        return Response(json.dumps({'reason':'Video not found'}), status=404) 

    #TODO: add user_id obtained by the auth server. For now it is harcoded
    user_id = 1

    author, content, timestamp = body['author'], body['content'], body['timestamp']
    comment = Comment(author=author, user_id=user_id, content=content, timestamp=timestamp)
    video_info = VideoInfo.objects.get(video_id=video_id)
    video_info.comments.append(comment)
    video_info.save()

    result = {'comment_id': comment.comment_id, 'user_id': user_id, 'author': author, 'content': content, 'timestamp': timestamp}
    return Response(json.dumps(result), status=201) 

def get_comment_from_video(request, video_id):
    video = VideoInfo.objects.with_id(video_id)
    if video is None:
        return Response(json.dumps({'reason':'Video not found'}), status=404) 

    body = request.get_json()
    video_info = VideoInfo.objects.get(video_id=video_id)
    comments = video_info.comments
    
    result = []
    for comment in comments:
        result.append({'comment_id': comment.comment_id, 'user_id': comment.user_id, 'author': comment.author, 
        'content': comment.content, 'timestamp': comment.timestamp})
    result.sort(key=lambda d: datetime.strptime(d['timestamp'], '%m/%d/%y %H:%M:%S'))
    return Response(json.dumps(result), status=200) 

@bp_videos.route('/videos/<int:video_id>/comments', methods=['GET', 'POST'])
def video_comments(video_id):
    if request.method == 'POST':
        return add_comment_to_video(request, video_id)
    return get_comment_from_video(request, video_id)

@bp_videos.route('/videos/<int:video_id>/likes', methods=['PUT'])
def video_likes(video_id):
    body = request.get_json()
    
    if required_put_likes_field not in body:
        return Response(json.dumps({'reason':'Fields are incomplete'}), status=400) 

    video = VideoInfo.objects.with_id(video_id)
    if video is None:
        return Response(json.dumps({'reason':'Video not found'}), status=404)  

    liked = body['liked']
    
    #TODO: add user_id obtained by the auth server. For now it is harcoded
    user_id = 1

    video_info = VideoInfo.objects.get(video_id=video_id)
    likes = video_info.likes

    if not liked and user_id in likes:
        likes.remove(user_id)
    if liked and not user_id in likes:
        likes.append(user_id) 
    video_info.save()

    return Response(json.dumps({'result':'Like updated'}), status=200) 
