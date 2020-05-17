import json
from flask import Blueprint, request, jsonify
from flask import current_app as app
from werkzeug.utils import secure_filename

from database.models.user import User

bp_users = Blueprint("bp_users", __name__)

# -- Endpoints

@bp_users.route('/users/<userId>', methods=['GET'])
def get_user_profile(userId):
    userdata = {
        'id': userId,
        'username': 'exampleUser123',
        'videos': []
    }

    user_profile = jsonify(userdata)
    user_profile.status_code = 200
    return user_profile


@bp_users.route('/users/<userId>/videos', methods=['GET', 'POST'])
def user_videos(userId):
    if request.method == 'POST':
        raise Exception("Not implemented yet")
        # # check if the post request has the file part
        # if 'file' not in request.files:
        #     app.logger.debug('/user/%s/videos => No file part in request', userId)
        #     return "No file was found", 400
        # file = request.files['file']
        # # if user does not select file, browser also
        # # submit an empty part without filename
        # if file.filename == '':
        #     app.logger.debug('/user/%s/videos => No selected file', userId)
        #     return "No selected file", 400
        # # if file and allowed_file(file.filename):
        # #     filename = secure_filename(file.filename)
        # #     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # #     return redirect(url_for('uploaded_file',
        # #                             filename=filename))
        # return "File uploaded!"
    else:
        media_server = app.config['MEDIA_SERVER']
        videos = media_server.getUserVideos(userId)
        return videos

