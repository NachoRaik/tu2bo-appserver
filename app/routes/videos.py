import json
from flask import Blueprint, request, jsonify
from flask import current_app as app
from werkzeug.utils import secure_filename
from database.models.video_info import VideoInfo
from database.models.comment import Comment

bp_videos = Blueprint("bp_videos", __name__)

required_post_comment_fields = ['author', 'content', 'timestamp']

# -- Endpoints

@bp_videos.route('/videos', methods=['GET'])
def home_videos():
    media_server = app.config['MEDIA_SERVER']
    home_page_videos = media_server.get_videos()
    return home_page_videos

@bp_videos.route('/videos/<video_id>/comments', methods=['GET', 'POST'])
def video_comments(video_id):
    auth_server = app.config['AUTH_SERVER']
    media_server = app.config['AUTH_SERVER']

    if request.method == 'POST':
        for r in required_post_comment_fields:
            if r not in body:
                return Response(json.dumps({'reason':'Fields are incomplete'}), status=400) 

        body = request.get_json()
        response = media_server.get_video(video_id)
        if response.status == 404:
            return Response(json.dumps({'reason':'Video not found'}), status=404) 

        #TODO: add user_id obtained by the auth server. For now it is harcoded
        user_id = 1

        author, content, timestamp = body['author'], body['content'], body['timestamp']
        comment = Comment(author=author, user_id=user_id, content=content, timestamp=timestamp)

        video_info = VideoInfo(video_id=video_id)
        try:
            video_info = VideoInfo.objects.get(video_id=video_id)
        except VideoInfo.DoesNotExist:
            print("El video fue creado")

        video_info.comments.append(comment)
        video_info.save()

        response = jsonify({'comment_id': comment.comment_id, 'user_id': user_id, 'author': author, 'content': content, 
            'timestamp': timestamp})
        response.status_code = 200
        return response
    else:
        response = media_server.get_video(video_id)
        if response.status == 404:
            return Response(json.dumps({'reason':'Video not found'}), status=404) 

        body = request.get_json()
        video_info = VideoInfo.objects.get(video_id=video_id)
        comments = video_info.comments
        
        result = []
        for comment in comments:
            result.append({'comment_id': comment.comment_id, 'user_id': comment.user_id, 'author': comment.author, 
            'content': comment.content, 'timestamp': comment.timestamp})
        response = jsonify(result)
        response.status_code = 200
        return response