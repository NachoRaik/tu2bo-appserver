from flask import Blueprint, request, jsonify
from flask import current_app as app
from database.models.video_stat import VideoStat
from datetime import datetime
from datetime import timedelta

bp_monitor = Blueprint("bp_monitor", __name__)
TIME_FORMAT = "%m/%d/%y %H:%M:%S"

# -- Endpoints

@bp_monitor.route('/ping')
def ping():
    return "AppServer is ~app~ up!"

@bp_monitor.route('/stats')
def stats():
    # TODO: make params not requested
    default_date = (datetime.now() - timedelta(days=1)).strftime(TIME_FORMAT)
    date = request.args.get('timestamp') if 'timestamp' in request.args else default_date
    num = int(request.args.get('num')) if 'num' in request.args else 1
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


