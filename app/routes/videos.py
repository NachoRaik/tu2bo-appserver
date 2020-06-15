import json
from flask import Blueprint, request, jsonify
from flask import current_app as app
from werkzeug.utils import secure_filename
from security.security import token_required

bp_videos = Blueprint("bp_videos", __name__)

# -- Endpoints

@bp_videos.route('/videos', methods=['GET'])
def home_videos(user_info):
    media_server = app.config['MEDIA_SERVER']
    home_page_videos = media_server.get_videos()
    return home_page_videos

@bp_videos.route('/videos/<videoId>/comments', methods=['GET', 'POST'])
@token_required
def video_comments(user_info,videoId):
    raise Exception('Not implemented yet')
