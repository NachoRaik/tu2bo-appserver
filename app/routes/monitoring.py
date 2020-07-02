from flask import Blueprint, request, jsonify
from flask import current_app as app
from services.VideoService import VideoService

bp_monitor = Blueprint("bp_monitor", __name__)
TIME_FORMAT = "%m/%d/%y %H:%M:%S"

# -- Endpoints

@bp_monitor.route('/ping')
def ping():
    return "AppServer is ~app~ up!"

@bp_monitor.route('/stats')
def stats():
    num = int(request.args.get('num')) if 'num' in request.args else 1

    media_server = app.config['MEDIA_SERVER']
    service = VideoService(media_server)
    videos = service.listVideos()

    for video in videos:
        video['comments'] = len(service.getCommentsFromVideo(video['id'])[0])

    videos_sorted_by_likes = sorted(videos, key=lambda d: d['likes'], reverse=True)            
    videos_sorted_by_comments = sorted(videos, key=lambda d: d['comments'], reverse=True)
            
    request_response = jsonify(
        {"most_liked_videos": videos_sorted_by_likes[:num], 
        "most_commented_videos": videos_sorted_by_comments[:num]}
    )
    request_response.status_code = 200
    return request_response
