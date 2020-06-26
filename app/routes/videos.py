from flask import Blueprint, request
from flask import current_app as app
from middlewares.security_wrapper import token_required
from middlewares.body_validation import body_validation
from utils.flask_utils import error_response, success_response

from services.VideoService import VideoService

required_post_comment_fields = ['author', 'content', 'timestamp']
required_put_likes_field = ['liked']

# -- Endpoints
def construct_blueprint(media_server):
    bp_videos = Blueprint("bp_videos", __name__)
    
    service = VideoService(media_server)

    @bp_videos.route('/videos', methods=['GET'])
    def home_videos():
        return success_response(200, service.listVideos())

    @bp_videos.route('/videos/<int:video_id>', methods=['GET'])
    @token_required
    def get_video(user_info, video_id):
        video, err = service.getVideo(int(user_info['id']), video_id)
        if err:
            return err
        return success_response(200, video)

    @bp_videos.route('/videos/<int:video_id>/comments', methods=['GET', 'POST'])
    @token_required
    @body_validation(required_post_comment_fields)
    def video_comments(user_info, video_id):
        if request.method == 'POST':
            result, err = service.addCommentToVideo(int(user_info["id"]), video_id, request.json)
            if err:
                return err
            return success_response(201, result)
        else:
            result, err = service.getCommentsFromVideo(video_id)
            if err:
                return err
            return success_response(200, result)

    @bp_videos.route('/videos/<int:video_id>/likes', methods=['PUT'])
    @token_required
    @body_validation(required_put_likes_field)
    def video_likes(user_info, video_id):
        err = service.addLikeToVideo(int(user_info['id']), video_id, request.json['liked'])
        if err:
            return err
        return success_response(200, {'result':'Like updated'})

    return bp_videos
