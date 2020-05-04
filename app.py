from flask import Flask, request, redirect, url_for, jsonify, Response
from werkzeug.utils import secure_filename
from database.db import initialize_db
from database.models.user import User

# -- Server setup and config

ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'wav'}
JSON_TYPE = "application/json"

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://localhost/appserver-db'
}

db = initialize_db(app)

# -- Endpoints

@app.route('/')
def hello():
    return "This is the Application Server!"


@app.route('/ping')
def ping():
    return "AppServer is ~app~ up!"


@app.route('/stats')
def stats():
    return "This endpoint will return server stats in a future"


@app.route('/users')
def get_users():
    users = jsonify(User.objects())
    users.status_code = 200
    return users

@app.route('/users', methods=['POST'])
def add_users():
    body = request.get_json()
    user = User(**body).save()
    id = user.id
    response = jsonify({'id': id})
    response.status_code = 200
    return response


@app.route('/friendRequests', methods=['POST'])
def friend_request():
    return "This endpoint will work for sending invites"


@app.route('/user/<userId>', methods=['GET'])
def get_user_profile(userId):
    userdata = {
        'id': userId,
        'username': 'exampleUser123',
        'videos': []
    }

    user_profile = jsonify(userdata)
    user_profile.status_code = 200
    return user_profile


@app.route('/user/<userId>/videos', methods=['GET', 'POST'])
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


if __name__ == '__main__':
    app.run()
