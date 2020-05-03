from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename

# -- Server setup and config

ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'wav'}

app = Flask(__name__)


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

@app.route('/friendRequests', methods=['POST'])
def friend_request():
    return "This endpoint will work for sending invites"

@app.route('/user/<username>', methods=['GET'])
def user_profile(username):
    return "User profiles are yet very skeletical"

@app.route('/user/<username>/videos', methods=['GET', 'POST'])
def upload_video(username):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            app.logger.info('/user/%s/videos => No file part in request', username)
            return "No file was found", 400
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            app.logger.info('/user/%s/videos => No selected file', username)
            return "No selected file", 400
        # if file and allowed_file(file.filename):
        #     filename = secure_filename(file.filename)
        #     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #     return redirect(url_for('uploaded_file',
        #                             filename=filename))
        return "File uploaded!"
    else:
        return "User {} doesn't have videos yet".format(username)

if __name__ == '__main__':
    app.run()
