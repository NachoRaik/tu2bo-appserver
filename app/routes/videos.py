import json
from flask import Blueprint, request, Response
from flask import current_app as app
from werkzeug.utils import secure_filename
from database.models.video_info import VideoInfo
from database.models.comment import Comment

bp_videos = Blueprint("bp_videos", __name__)

required_post_comment_fields = ['author', 'content', 'timestamp']
required_put_likes_field = 'liked'

# -- Endpoints

@bp_videos.route('/videos', methods=['GET'])
def home_videos():
    media_server = app.config['MEDIA_SERVER']
    home_page_videos = media_server.get_videos()
    return home_page_videos

def add_comment_to_video(request, video_id):
    video_id = int(video_id)
    media_server = app.config['MEDIA_SERVER']
    body = request.get_json()
    
    if any(r not in body for r in required_post_comment_fields):
        return Response(json.dumps({'reason':'Fields are incomplete'}), status=400) 

    response = media_server.get_video(video_id)
    if response.status_code == 404:
        return Response(json.dumps({'reason':'Video not found'}), status=404) 

    #TODO: add user_id obtained by the auth server. For now it is harcoded
    user_id = 1

    author, content, timestamp = body['author'], body['content'], body['timestamp']
    comment = Comment(author=author, user_id=user_id, content=content, timestamp=timestamp)
    video_info = VideoInfo.objects.get(video_id=video_id)
    video_info.comments.append(comment)
    video_info.save()

    result = {'comment_id': comment.comment_id, 'user_id': user_id, 'author': author, 'content': content, 'timestamp': timestamp}
    return Response(json.dumps(result), status=200) 

def get_comment_from_video(request, video_id):
    video_id = int(video_id)
    response = media_server.get_video(video_id)
    if response.status_code == 404:
        return Response(json.dumps({'reason':'Video not found'}), status=404) 

    body = request.get_json()
    video_info = VideoInfo.objects.get(video_id=video_id)
    comments = video_info.comments
    
    result = []
    for comment in comments:
        result.append({'comment_id': comment.comment_id, 'user_id': comment.user_id, 'author': comment.author, 
        'content': comment.content, 'timestamp': comment.timestamp})
    return Response(json.dumps(result), status=200) 

@bp_videos.route('/videos/<video_id>/comments', methods=['GET', 'POST'])
def video_comments(video_id):
    video_id = int(video_id)    
    if request.method == 'POST':
        return add_comment_to_video(request, video_id)
    return get_comment_from_video(request, video_id)

@bp_videos.route('/videos/<video_id>/likes', methods=['PUT'])
def video_likes(video_id):
    video_id = int(video_id)
    media_server = app.config['MEDIA_SERVER']
    if required_put_likes_field not in body:
        return Response(json.dumps({'reason':'Fields are incomplete'}), status=400) 

    response = media_server.get_video(video_id)
    if response.status_code == 404:
        return Response(json.dumps({'reason':'Video not found'}), status=404) 

    liked = body['liked']
    
    #TODO: add user_id obtained by the auth server. For now it is harcoded
    user_id = 1

    video_info = VideoInfo.objects.get(video_id=video_id)
    likes = video_info.likes

    if not liked and user_id in likes:
        likes.remove(user_id)
    if liked:
        likes.append(user_id) 
    return Response(json.dumps({'result':'Like updated'}), status=200) 
