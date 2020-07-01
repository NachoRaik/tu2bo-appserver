from flask import Blueprint, request, jsonify
from flask import current_app as app
from database.models.video_stat import VideoStat
from datetime import datetime

bp_monitor = Blueprint("bp_monitor", __name__)
TIME_FORMAT = "%m/%d/%y %H:%M:%S"

# -- Endpoints

@bp_monitor.route('/ping')
def ping():
    return "AppServer is ~app~ up!"

@bp_monitor.route('/stats')
def stats():
    # TODO: make params not requested
    date = request.args.get('timestamp')
    num = int(request.args.get('num'))
    video_stats = VideoStat.objects
    date_to_timestamp = datetime.strptime(date, TIME_FORMAT)
    response = [
        {"most_liked_videos": stat.videos_sorted_by_likes[:num], "most_commented_videos": stat.videos_sorted_by_comments[:num],
        "timestamp": stat.timestamp}
        for stat in video_stats
        if date_to_timestamp < datetime.strptime(stat.timestamp, TIME_FORMAT)
    ]
    request_response = jsonify(response)
    request_response.status_code = 200
    return request_response


