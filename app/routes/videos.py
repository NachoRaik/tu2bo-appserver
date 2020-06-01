import json
from flask import Blueprint, request, jsonify
from flask import current_app as app
from werkzeug.utils import secure_filename

bp_videos = Blueprint("bp_videos", __name__)

# -- Endpoints

@bp_videos.route('/videos', methods=['GET'])
def home_videos():
    media_server = app.config['MEDIA_SERVER']
    home_page_videos = media_server.get_videos()
    return home_page_videos

@bp_videos.route('/videos/<videoId>/comments', methods=['GET', 'POST'])
def video_comments(videoId):
    raise Exception('Not implemented yet')

