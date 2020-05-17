from flask import Flask, request, Response
from database.db import initialize_db
from config import DevelopmentConfig
import logging

# -- Server setup and config

ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'wav'}
JSON_TYPE = "application/json"

# -- App creation

def create_app(config=DevelopmentConfig()):
    app = Flask(__name__)
    app.config.from_object(config)
    app.logger.setLevel(logging.DEBUG)

    db = initialize_db(app)

    # -- Routes registration
    from routes import auth, monitoring, users, videos

    app.register_blueprint(auth.bp_auth)
    app.register_blueprint(monitoring.bp_monitor)
    app.register_blueprint(users.bp_users)
    app.register_blueprint(videos.bp_videos)

    # -- Unassigned endpoints
    @app.route('/')
    def hello():
        return "This is the Application Server!"

    @app.route('/friendRequests', methods=['POST'])
    def friend_request():
        return "This endpoint will work for sending invites"

    return app


# -- Run

app = create_app()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000")