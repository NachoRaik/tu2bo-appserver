from flask import current_app as app
from functools import wraps
from database.models.video_stat import VideoStat
from datetime import datetime
from services.VideoService import VideoService

TIME_FORMAT = "%m/%d/%y %H:%M:%S"

def should_be_saved():
    is_time = True
    if VideoStat.objects.count() != 0:
        last_record_timestamp = VideoStat.objects.order_by('-id').first().timestamp
        last_record_to_datetime = datetime.strptime(last_record_timestamp, TIME_FORMAT)
        is_time = (datetime.now() - last_record_to_datetime) > app.config['DELAY']
    return is_time

def add_video_stats(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        response = f(*args, **kwargs)
        if response.status_code == 201 and should_be_saved(): 
            media_server = app.config['MEDIA_SERVER']
            service = VideoService(media_server)
            videos = service.listVideos()

            for video in videos:
                video['comments'] = len(service.getCommentsFromVideo(video['id']))

            videos_sorted_by_likes = sorted(videos, key=lambda d: d['likes'], reverse=True)
            id_videos_sorted_by_likes = [v['id'] for v in videos_sorted_by_likes]
            
            videos_sorted_by_comments = sorted(videos, key=lambda d: d['comments'], reverse=True)
            id_videos_sorted_by_comments = [v['id'] for v in videos_sorted_by_comments]
            
            timestamp = datetime.now().strftime(TIME_FORMAT)
            video_stat = VideoStat(videos_sorted_by_likes=id_videos_sorted_by_likes, videos_sorted_by_comments=id_videos_sorted_by_comments, timestamp=timestamp)
            video_stat.save()
        return response
    return decorated