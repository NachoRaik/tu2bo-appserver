from flask import Blueprint, request, jsonify
from flask import current_app as app
from werkzeug.utils import secure_filename

from database.models.user import User

bp_users = Blueprint("bp_users", __name__, url_prefix="/users")

# -- Endpoints

@bp_users.route('/', methods=['GET'], strict_slashes=False)
def get_users():
    users = jsonify(User.objects())
    users.status_code = 200
    return users


@bp_users.route('/', methods=['POST'], strict_slashes=False)
def add_users():
    body = request.get_json()
    user = User(**body).save()
    id = user.id
    response = jsonify({'id': id})
    response.status_code = 200
    return response


@bp_users.route('/<userId>', methods=['GET'])
def get_user_profile(userId):
    userdata = {
        'id': userId,
        'username': 'exampleUser123',
        'videos': []
    }

    user_profile = jsonify(userdata)
    user_profile.status_code = 200
    return user_profile


@bp_users.route('/<userId>/videos', methods=['GET', 'POST'])
def upload_video(userId):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            app.logger.debug('/user/%s/videos => No file part in request', userId)
            return "No file was found", 400
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            app.logger.debug('/user/%s/videos => No selected file', userId)
            return "No selected file", 400
        # if file and allowed_file(file.filename):
        #     filename = secure_filename(file.filename)
        #     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #     return redirect(url_for('uploaded_file',
        #                             filename=filename))
        return "File uploaded!"
    else:
        return "User {} doesn't have videos yet".format(userId)
